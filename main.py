"""
Main entry point for Statistical Arbitrage Momentum Strategy
"""

import pandas as pd
import matplotlib.pyplot as plt
import logging
import os
from strategy import StatArbitrageStrategy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def plot_results(results: dict) -> None:
    """
    Plot strategy performance results.
    
    Args:
        results: Dictionary with strategy results
    """
    if not results:
        logger.warning("No results to plot")
        return
        
    # Create output directory
    os.makedirs("./plots", exist_ok=True)
    
    # Plot cumulative returns
    plt.figure(figsize=(14, 8))
    
    for strategy_name, strategy_data in results.items():
        cumulative_returns = strategy_data['metrics']['cumulative_returns']
        plt.plot(cumulative_returns.index, cumulative_returns.values, label=strategy_name, linewidth=2)
    
    plt.title("Strategy Cumulative Returns Comparison", fontsize=14, fontweight='bold')
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Cumulative Return", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("./plots/cumulative_returns.png", dpi=300, bbox_inches='tight')
    logger.info("Saved plot: ./plots/cumulative_returns.png")
    plt.close()
    
    # Plot Sharpe ratios comparison
    sharpe_ratios = {name: data['metrics']['sharpe_ratio'] 
                     for name, data in results.items()}
    
    plt.figure(figsize=(10, 6))
    strategies = list(sharpe_ratios.keys())
    sharpes = list(sharpe_ratios.values())
    
    colors = ['green' if s > 0 else 'red' for s in sharpes]
    plt.bar(strategies, sharpes, color=colors, alpha=0.7)
    
    plt.title("Sharpe Ratio Comparison", fontsize=14, fontweight='bold')
    plt.ylabel("Sharpe Ratio", fontsize=12)
    plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("./plots/sharpe_ratios.png", dpi=300, bbox_inches='tight')
    logger.info("Saved plot: ./plots/sharpe_ratios.png")
    plt.close()


def save_results(results: dict) -> None:
    """
    Save results to CSV files.
    
    Args:
        results: Dictionary with strategy results
    """
    os.makedirs("./results", exist_ok=True)
    
    # Save metrics summary
    metrics_list = []
    for strategy_name, strategy_data in results.items():
        metrics = strategy_data['metrics'].copy()
        metrics['strategy'] = strategy_name
        
        # Convert Series to scalar
        if 'cumulative_returns' in metrics:
            metrics.pop('cumulative_returns')
            
        metrics_list.append(metrics)
    
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv("./results/performance_metrics.csv", index=False)
    logger.info("Saved metrics: ./results/performance_metrics.csv")
    
    # Save returns for each strategy
    for strategy_name, strategy_data in results.items():
        returns = strategy_data['returns']
        returns.to_csv(f"./results/{strategy_name}_returns.csv")
        logger.info(f"Saved returns: ./results/{strategy_name}_returns.csv")


def main():
    """Main execution function."""
    
    logger.info("="*70)
    logger.info("STATISTICAL ARBITRAGE MOMENTUM STRATEGY - BACKTEST")
    logger.info("="*70)
    
    # Initialize and run strategy
    strategy = StatArbitrageStrategy(
        start_date="2020-09-01",  # From paper
        momentum_windows=[60, 120, 252]
    )
    
    # Execute full pipeline
    results = strategy.run_full_pipeline()
    
    # Save and plot results
    if results:
        save_results(results)
        plot_results(results)
        
        logger.info("="*70)
        logger.info("Backtest completed successfully!")
        logger.info("Results saved to ./results/")
        logger.info("Plots saved to ./plots/")
        logger.info("="*70)
    else:
        logger.error("Backtest failed - no results returned")


if __name__ == "__main__":
    main()
