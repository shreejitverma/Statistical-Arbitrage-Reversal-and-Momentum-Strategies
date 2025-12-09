"""
Main Strategy Module
Orchestrates the statistical arbitrage momentum strategy workflow.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple
from datetime import datetime

from data_fetcher import DataFetcher
from data_cleaner import DataCleaner
from signal_generator import SignalGenerator
from performance_analyzer import PerformanceAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StatArbitrageStrategy:
    """
    Statistical Arbitrage Momentum Strategy
    Implements momentum-based long-short trading across cryptocurrency universe.
    """
    
    def __init__(
        self,
        start_date: str = "2018-01-01",
        end_date: str = None,
        symbols: list = None,
        liquidity_threshold: float = 0.40,
        transaction_cost_pct: float = 0.0005,
        momentum_windows: list = [60, 120, 252]
    ):
        """
        Initialize the strategy.
        
        Args:
            start_date: Strategy start date (YYYY-MM-DD)
            end_date: Strategy end date (YYYY-MM-DD), default is today
            symbols: List of cryptocurrency pairs
            liquidity_threshold: Liquidity threshold for asset filtering
            transaction_cost_pct: Transaction costs as percentage
            momentum_windows: Momentum windows to analyze (in days)
        """
        self.start_date = start_date
        self.end_date = end_date or datetime.utcnow().strftime('%Y-%m-%d')
        self.liquidity_threshold = liquidity_threshold
        self.transaction_cost_pct = transaction_cost_pct
        self.momentum_windows = momentum_windows
        
        # Default symbols if not provided
        if symbols is None:
            self.symbols = [
                "BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT",
                "XRPUSDT", "SOLUSDT", "DOGEUSDT", "MATICUSDT",
                "LINKUSDT", "UNIUSDT", "AAVEUSDT", "ATOMUSDT"
            ]
        else:
            self.symbols = symbols
            
        # Initialize components
        self.fetcher = DataFetcher()
        self.cleaner = DataCleaner(liquidity_threshold=liquidity_threshold)
        self.signal_generator = SignalGenerator()
        self.analyzer = PerformanceAnalyzer()
        
        # Data storage
        self.returns = None
        self.volumes = None
        self.benchmark_returns = None
        
        logger.info(f"Initialized strategy with {len(self.symbols)} symbols")
        
    def fetch_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetch cryptocurrency data from Binance API.
        
        Returns:
            Tuple of (returns_df, volumes_df)
        """
        logger.info("Fetching cryptocurrency data...")
        
        returns_dict, volumes_dict = self.fetcher.fetch_cryptocurrency_data(
            symbols=self.symbols,
            start_date=self.start_date,
            end_date=self.end_date,
            interval="1d"
        )
        
        # Convert dictionaries to DataFrames
        self.returns = pd.DataFrame(returns_dict)
        self.volumes = pd.DataFrame(volumes_dict)
        
        logger.info(f"Fetched data: {self.returns.shape[0]} days, {self.returns.shape[1]} assets")
        
        return self.returns, self.volumes
    
    def prepare_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Clean and prepare data for analysis.
        
        Returns:
            Tuple of (clean_returns, clean_volumes)
        """
        if self.returns is None:
            logger.error("No data fetched. Call fetch_data() first.")
            return None, None
            
        logger.info("Preparing and cleaning data...")
        
        self.returns, self.volumes = self.cleaner.clean_and_align(
            self.returns,
            self.volumes,
            min_assets=8
        )
        
        # Verify data quality
        self.cleaner.verify_data_quality(self.returns, self.volumes)
        
        return self.returns, self.volumes
    
    def generate_signals(self) -> Dict:
        """
        Generate momentum trading signals.
        
        Returns:
            Dictionary with momentum signals and portfolio weights
        """
        if self.returns is None:
            logger.error("No data prepared. Call prepare_data() first.")
            return None
            
        logger.info("Generating momentum signals...")
        
        self.momentum_signals = self.signal_generator.generate_momentum_signals(
            returns=self.returns,
            windows=self.momentum_windows
        )
        
        # Print signal statistics
        for window, signals in self.momentum_signals.items():
            weights = signals['portfolio_weights']
            logger.info(f"\nSignal statistics for {window}:")
            logger.info(f"  Mean concentration: {weights.abs().max().mean():.4f}")
            logger.info(f"  Avg turnover: {weights.diff().abs().sum(axis=1).mean():.4f}")
        
        return self.momentum_signals
    
    def backtest(self) -> Dict:
        """
        Run backtest and calculate performance metrics.
        
        Returns:
            Dictionary with performance metrics for each strategy
        """
        if self.momentum_signals is None:
            logger.error("No signals generated. Call generate_signals() first.")
            return None
            
        logger.info("Running backtest...")
        
        # Fetch BTC returns as benchmark
        btc_returns_dict, _ = self.fetcher.fetch_cryptocurrency_data(
            symbols=["BTCUSDT"],
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.benchmark_returns = btc_returns_dict["BTCUSDT_Close"]
        
        # Calculate strategy returns and metrics for each window
        performance_results = {}
        
        for window, signals in self.momentum_signals.items():
            weights = signals['portfolio_weights']
            
            # Calculate strategy returns
            strategy_returns = self.analyzer.calculate_returns(
                portfolio_weights=weights,
                daily_returns=self.returns,
                transaction_cost_pct=self.transaction_cost_pct
            )
            
            # Calculate metrics
            metrics = self.analyzer.calculate_performance_metrics(
                strategy_returns=strategy_returns,
                benchmark_returns=self.benchmark_returns
            )
            
            performance_results[f"mom_{window}"] = {
                'returns': strategy_returns,
                'metrics': metrics
            }
            
            # Print results
            self.analyzer.print_performance_summary(metrics, f"Momentum {window}")
        
        return performance_results
    
    def run_full_pipeline(self) -> Dict:
        """
        Execute complete strategy workflow.
        
        Returns:
            Dictionary with all results
        """
        logger.info("="*60)
        logger.info("STATISTICAL ARBITRAGE MOMENTUM STRATEGY")
        logger.info("="*60)
        
        # Execute pipeline
        self.fetch_data()
        self.prepare_data()
        self.generate_signals()
        results = self.backtest()
        
        logger.info("Strategy execution complete!")
        
        return results


if __name__ == "__main__":
    # Run the strategy
    strategy = StatArbitrageStrategy()
    results = strategy.run_full_pipeline()
