"""
Data Fetcher Module
Handles fetching cryptocurrency data from Binance API with robust error handling.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches cryptocurrency OHLCV data from Binance API."""
    
    BASE_URL = "https://api.binance.com/api/v3/klines"
    
    def __init__(self, timeout: int = 30):
        """Initialize DataFetcher with timeout parameter."""
        self.timeout = timeout
        self.session = requests.Session()
        
    def fetch_cryptocurrency_data(
        self,
        symbols: list,
        start_date: str,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> Tuple[Dict[str, pd.Series], Dict[str, pd.Series]]:
        """
        Fetch cryptocurrency data from Binance API.
        
        Args:
            symbols: List of cryptocurrency pairs (e.g., ['BTCUSDT', 'ETHUSDT'])
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (default: today)
            interval: Kline interval (default: '1d' for daily)
            
        Returns:
            Tuple of (returns_dict, volumes_dict) with pd.Series for each symbol
        """
        if end_date is None:
            end_date = datetime.utcnow().strftime('%Y-%m-%d')
            
        returns_data = {}
        volumes_data = {}
        
        for symbol in symbols:
            try:
                logger.info(f"Fetching data for {symbol}...")
                
                # Convert dates to milliseconds
                start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
                end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)
                
                # Fetch all data for the symbol
                klines = self._fetch_klines(symbol, interval, start_ts, end_ts)
                
                if not klines:
                    logger.warning(f"No data received for {symbol}")
                    continue
                    
                # Process klines into dataframe
                df = pd.DataFrame(klines, columns=[
                    'open_time', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'num_trades',
                    'taker_buy_base', 'taker_buy_quote', 'ignore'
                ])
                
                # Convert to numeric types
                df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
                df['close'] = pd.to_numeric(df['close'], errors='coerce')
                df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
                
                # Set date as index and calculate returns
                df.set_index('open_time', inplace=True)
                
                # Calculate daily returns
                returns = df['close'].pct_change()
                returns.name = f"{symbol}_Close"
                
                # Extract volumes
                volumes = df['volume']
                volumes.name = f"{symbol}_Vol"
                
                returns_data[f"{symbol}_Close"] = returns
                volumes_data[f"{symbol}_Vol"] = volumes
                
                logger.info(f"Successfully processed {symbol}: {len(df)} records")
                
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                continue
                
        return returns_data, volumes_data
    
    def _fetch_klines(self, symbol: str, interval: str, start_ts: int, end_ts: int, limit: int = 1000):
        """
        Fetch klines from Binance API with pagination.
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval
            start_ts: Start timestamp in milliseconds
            end_ts: End timestamp in milliseconds
            limit: Number of klines per request (max 1000)
            
        Returns:
            List of klines data
        """
        all_klines = []
        current_start = start_ts
        
        while current_start < end_ts:
            try:
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'startTime': current_start,
                    'endTime': end_ts,
                    'limit': limit
                }
                
                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                klines = response.json()
                
                if not klines:
                    break
                    
                all_klines.extend(klines)
                
                # Update start time for next request
                current_start = klines[-1][0] + 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API error for {symbol}: {str(e)}")
                break
                
        return all_klines
    
    def close(self):
        """Close the session."""
        self.session.close()
