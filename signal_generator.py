"""
Signal Generator Module
Generates momentum and reversal trading signals for statistical arbitrage.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generates momentum and reversal signals across multiple timeframes."""
    
    def __init__(self):
        """Initialize SignalGenerator."""
        self.signals = {}
        
    def generate_momentum_signals(
        self,
        returns: pd.DataFrame,
        windows: list = [60, 120, 252]
    ) -> Dict:
        """
        Generate momentum signals (positive for uptrends).
        
        Args:
            returns: DataFrame with daily returns
            windows: List of rolling window sizes in days
            
        Returns:
            Dictionary with momentum signals for each window
        """
        logger.info(f"Generating momentum signals for windows: {windows}")
        
        momentum_signals = {}
        
        for window in windows:
            # Calculate rolling returns (momentum)
            rolling_returns = returns.rolling(window=window).mean()
            
            # Rank across assets (higher return = higher rank)
            ranked = rolling_returns.rank(axis=1)
            
            # Demean the ranked returns
            demeaned = ranked.subtract(ranked.mean(axis=1), axis=0)
            
            # Normalize to get portfolio weights
            portfolio_weights = demeaned.div(demeaned.abs().sum(axis=1), axis=0)
            
            momentum_signals[f"{window}d"] = {
                'returns': rolling_returns,
                'ranked': ranked,
                'demeaned': demeaned,
                'portfolio_weights': portfolio_weights
            }
            
            logger.info(f"Generated momentum signals for {window}d window")
            
        return momentum_signals
    
    def generate_reversal_signals(
        self,
        returns: pd.DataFrame,
        windows: list = [1, 5, 10, 20]
    ) -> Dict:
        """
        Generate reversal signals (negative for mean reversion).
        
        Args:
            returns: DataFrame with daily returns
            windows: List of rolling window sizes in days
            
        Returns:
            Dictionary with reversal signals for each window
        """
        logger.info(f"Generating reversal signals for windows: {windows}")
        
        reversal_signals = {}
        
        for window in windows:
            # Calculate rolling returns
            rolling_returns = returns.rolling(window=window).mean()
            
            # Negate for reversal (exploit mean reversion)
            negated = -rolling_returns
            
            # Rank across assets
            ranked = negated.rank(axis=1)
            
            # Demean the ranked returns
            demeaned = ranked.subtract(ranked.mean(axis=1), axis=0)
            
            # Normalize to get portfolio weights
            portfolio_weights = demeaned.div(demeaned.abs().sum(axis=1), axis=0)
            
            reversal_signals[f"{window}d"] = {
                'returns': rolling_returns,
                'negated': negated,
                'ranked': ranked,
                'demeaned': demeaned,
                'portfolio_weights': portfolio_weights
            }
            
            logger.info(f"Generated reversal signals for {window}d window")
            
        return reversal_signals
    
    def calculate_signal_statistics(self, signals: Dict) -> pd.DataFrame:
        """
        Calculate statistics for generated signals.
        
        Args:
            signals: Dictionary of signals from signal generation
            
        Returns:
            DataFrame with signal statistics
        """
        stats = {}
        
        for window, signal_data in signals.items():
            weights = signal_data['portfolio_weights'].dropna()
            
            stats[window] = {
                'mean_long_weight': weights[weights > 0].mean().mean(),
                'mean_short_weight': weights[weights < 0].mean().mean(),
                'max_concentration': weights.abs().max().max(),
                'avg_turnover': weights.diff().abs().sum().mean()
            }
            
        return pd.DataFrame(stats).T
