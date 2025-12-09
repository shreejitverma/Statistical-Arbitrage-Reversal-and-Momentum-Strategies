"""
Performance Analyzer Module
Calculates backtesting metrics and strategy performance analysis.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyzes strategy performance and calculates key metrics."""
    
    def __init__(self):
        """Initialize PerformanceAnalyzer."""
        self.metrics = {}
        
    def calculate_returns(
        self,
        portfolio_weights: pd.DataFrame,
        daily_returns: pd.DataFrame,
        transaction_cost_pct: float = 0.0005
    ) -> pd.Series:
        """
        Calculate strategy returns given portfolio weights and daily returns.
        
        Args:
            portfolio_weights: DataFrame with portfolio weights for each day
            daily_returns: DataFrame with daily returns for each asset
            transaction_cost_pct: Transaction cost as percentage (default 5bps)
            
        Returns:
            Series with daily strategy returns
        """
        # Align data
        weights = portfolio_weights.loc[daily_returns.index]
        returns = daily_returns.loc[weights.index]
        
        # Calculate strategy returns (today's weights, tomorrow's returns)
        strategy_returns = weights.shift(1).mul(returns).sum(axis=1)
        
        # Account for transaction costs
        # Calculate turnover as absolute change in weights
        turnover = weights.diff().abs().sum(axis=1)
        transaction_costs = turnover * transaction_cost_pct
        
        # Subtract transaction costs
        strategy_returns = strategy_returns - transaction_costs
        
        return strategy_returns.dropna()
    
    def calculate_performance_metrics(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series = None,
        periods_per_year: int = 252
    ) -> Dict:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            strategy_returns: Series with daily strategy returns
            benchmark_returns: Series with daily benchmark returns (optional)
            periods_per_year: Number of trading periods per year (default 252)
            
        Returns:
            Dictionary with performance metrics
        """
        if len(strategy_returns) < periods_per_year:
            logger.warning("Insufficient data for annualized metrics")
            
        # Basic metrics
        total_return = (1 + strategy_returns).prod() - 1
        annualized_return = (1 + total_return) ** (periods_per_year / len(strategy_returns)) - 1
        
        daily_volatility = strategy_returns.std()
        annualized_volatility = daily_volatility * np.sqrt(periods_per_year)
        
        sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + strategy_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        win_rate = (strategy_returns > 0).sum() / len(strategy_returns)
        
        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'cumulative_returns': cumulative_returns
        }
        
        # Benchmark comparison
        if benchmark_returns is not None:
            benchmark_returns = benchmark_returns.loc[strategy_returns.index]
            
            # Calculate alpha and beta
            covariance = np.cov(strategy_returns.values, benchmark_returns.values)[0, 1]
            benchmark_variance = benchmark_returns.var()
            
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            alpha = annualized_return - (risk_free_rate := 0) - beta * (benchmark_returns.mean() * periods_per_year - risk_free_rate)
            
            # Correlation
            correlation = strategy_returns.corr(benchmark_returns)
            
            metrics['beta'] = beta
            metrics['alpha'] = alpha
            metrics['correlation'] = correlation
            metrics['benchmark_return'] = benchmark_returns.mean() * periods_per_year
            
        return metrics
    
    def print_performance_summary(self, metrics: Dict, name: str = "Strategy") -> None:
        """
        Print formatted performance summary.
        
        Args:
            metrics: Dictionary with performance metrics
            name: Name of the strategy
        """
        logger.info(f"\n{'='*50}")
        logger.info(f"PERFORMANCE SUMMARY: {name}")
        logger.info(f"{'='*50}")
        
        logger.info(f"Total Return:          {metrics['total_return']*100:.2f}%")
        logger.info(f"Annualized Return:     {metrics['annualized_return']*100:.2f}%")
        logger.info(f"Annualized Volatility: {metrics['annualized_volatility']*100:.2f}%")
        logger.info(f"Sharpe Ratio:          {metrics['sharpe_ratio']:.2f}")
        logger.info(f"Maximum Drawdown:      {metrics['max_drawdown']*100:.2f}%")
        logger.info(f"Win Rate:              {metrics['win_rate']*100:.2f}%")
        
        if 'beta' in metrics:
            logger.info(f"Beta:                  {metrics['beta']:.4f}")
            logger.info(f"Alpha (Annualized):    {metrics['alpha']*100:.2f}%")
            logger.info(f"Correlation:           {metrics['correlation']:.4f}")
            
        logger.info(f"{'='*50}\n")
    
    def compare_strategies(
        self,
        strategies_dict: Dict[str, pd.Series],
        benchmark: pd.Series = None
    ) -> pd.DataFrame:
        """
        Compare multiple strategies and return metrics comparison.
        
        Args:
            strategies_dict: Dictionary of {strategy_name: returns_series}
            benchmark: Optional benchmark series for comparison
            
        Returns:
            DataFrame with metrics for each strategy
        """
        comparison = {}
        
        for name, returns in strategies_dict.items():
            metrics = self.calculate_performance_metrics(returns, benchmark)
            comparison[name] = metrics
            
        return pd.DataFrame(comparison).T
