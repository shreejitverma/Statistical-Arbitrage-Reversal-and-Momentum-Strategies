# Statistical Arbitrage Momentum Strategy

A comprehensive quantitative research project investigating statistical arbitrage strategies leveraging reversal and momentum signals across a broad universe of cryptocurrencies.

## Overview

This project conducts an in-depth analysis of momentum-based trading strategies on cryptocurrency markets. By analyzing 7+ years of historical price and volume data (January 2018 - Present) across 15+ cryptocurrencies, we demonstrate that a 120-day momentum strategy can generate superior risk-adjusted returns compared to traditional buy-and-hold approaches.

### Key Results

- **Annualized Return**: 155.76% (vs 49.30% BTC buy-and-hold)
- **Sharpe Ratio**: 1.94 (vs 0.96 for BTC)
- **Correlation with BTC**: 0.20 (low systematic risk)
- **Maximum Drawdown**: -51.34%
- **Alpha (Annualized)**: 7,669.91

## Project Structure

```
statistical-arbitrage-momentum/
├── README.md
├── LICENSE.md
├── requirements.txt
├── config.yaml
├── main.py
├── strategy.py
├── data/
│   └── .gitkeep
├── src/
│   ├── data_fetcher.py          # Binance API data retrieval
│   ├── data_cleaner.py          # Data cleaning and alignment
│   ├── signal_generator.py      # Reversal and momentum signal construction
│   ├── performance_analyzer.py  # Metrics and backtesting analysis
└── tests/
    └── test_strategy.py
```

## Features

### 1. **Data Acquisition**
- Fetches historical OHLCV data from Binance API
- Supports 15+ major cryptocurrencies by market cap
- Configurable data frequency (daily bars)
- Automatic handling of timezone conversions

### 2. **Data Processing**
- Robust missing value handling (forward/backward fill)
- Liquidity threshold filtering (40% threshold)
- Timezone alignment and look-ahead bias removal
- Comprehensive data validation and verification

### 3. **Signal Generation**
- **Reversal Signals**: Short-term mean-reversion exploitation
- **Momentum Signals**: Long-term trend-following strategies
- Multiple timeframes: 1d, 5d, 10d, 20d, 60d, 120d, 252d
- Dollar-neutral portfolio construction

### 4. **Strategy Implementation**
- Equal-weighted long-short positions
- Transaction cost modeling
- Risk metrics: Sharpe ratio, maximum drawdown, beta, alpha
- BTC benchmark comparison

### 5. **Performance Analysis**
- Comprehensive backtest metrics
- Visualization of cumulative returns
- Correlation and distribution analysis
- Strategy comparison across timeframes

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

```bash
# Clone the repository
git clone https://github.com/shreejitverma/statistical-arbitrage-momentum.git
cd statistical-arbitrage-momentum

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# Data Configuration
data:
  start_date: "2018-01-01"
  end_date: "2024-12-31"
  frequency: "1d"  # Daily bars
  
# Asset Configuration
assets:
  primary: ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT"]
  expanded: ["XRPUSDT", "SOLUSDT", "DOGEUSDT", "MATICUSDT", "LINKUSDT", "UNIUSDT", "AAVEUSDT", "ATOMUSDT"]
  
# Strategy Configuration
strategy:
  liquidity_threshold: 0.40  # 40% threshold
  momentum_windows: [60, 120, 252]  # Days
  reversal_windows: [1, 5, 10, 20]  # Days
  transaction_cost_pct: 0.0005  # 5 bps
```

## Usage

### Basic Usage

```python
from strategy import StatArbitrageStrategy

# Initialize strategy
strategy = StatArbitrageStrategy()

# Fetch data
strategy.fetch_data()

# Clean and prepare data
strategy.prepare_data()

# Generate signals
strategy.generate_signals()

# Run backtest
performance = strategy.backtest()
```

### Running the Full Pipeline

```bash
python main.py
```

## Module Documentation

### `data_fetcher.py`
Handles data retrieval from Binance API with error handling and validation.

```python
from src.data_fetcher import DataFetcher

fetcher = DataFetcher()
returns, volumes = fetcher.fetch_cryptocurrency_data(
    symbols=['BTCUSDT', 'ETHUSDT'],
    start_date='2018-01-01'
)
```

### `data_cleaner.py`
Performs comprehensive data cleaning, alignment, and validation.

```python
from src.data_cleaner import DataCleaner

cleaner = DataCleaner()
clean_returns, clean_volumes = cleaner.clean_and_align(
    returns_df, 
    volumes_df,
    liquidity_threshold=0.40
)
```

### `signal_generator.py`
Generates momentum and reversal trading signals.

```python
from src.signal_generator import SignalGenerator

generator = SignalGenerator()
signals = generator.generate_momentum_signals(
    returns=clean_returns,
    windows=[60, 120, 252]
)
```

### `performance_analyzer.py`
Comprehensive backtesting and performance metrics.

```python
from src.performance_analyzer import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()
metrics = analyzer.calculate_performance_metrics(
    strategy_returns,
    benchmark_returns,
    transaction_costs=0.05
)
```

## Methodology

### 1. **Data Selection**
- Start date: January 1, 2018 (sufficient data availability)
- Assets: Top 15 cryptocurrencies by market cap
- Frequency: Daily OHLCV bars

### 2. **Rolling Returns Analysis**
- Multiple time horizons for reversal and momentum signals
- Short-term windows (1-20d) for mean-reversion exploitation
- Long-term windows (60-252d) for momentum capitalization

### 3. **Signal Processing**
- Ranking and demeaning of returns
- Dollar-neutral portfolio construction
- Equal weighting to reduce idiosyncratic risk

### 4. **Transaction Costs**
- 5 basis points (0.05%) per trade
- Realistic representation of market execution

### 5. **Performance Metrics**
- **Annualized Return**: Average annual return
- **Volatility**: Annualized standard deviation
- **Sharpe Ratio**: Risk-adjusted return (annualized)
- **Maximum Drawdown**: Peak-to-trough decline
- **Beta**: Sensitivity to BTC benchmark
- **Alpha**: Excess return vs benchmark

## Key Results

### Strategy Performance Summary (Sep 2020 - Present)

#### Stat Arb 120-Day Momentum Strategy
| Metric | Value |
|--------|-------|
| Annualized Return | 155.76% |
| Annualized Volatility | 80.41% |
| Sharpe Ratio | 1.94 |
| Maximum Drawdown | -51.34% |
| Beta to BTC | 0.01 |
| Alpha (Annualized) | 7,669.91 |

#### BTC Buy-and-Hold Benchmark
| Metric | Value |
|--------|-------|
| Annualized Return | 49.30% |
| Annualized Volatility | 51.53% |
| Sharpe Ratio | 0.96 |
| Maximum Drawdown | -76.63% |

### Key Findings

1. **Momentum Outperformance**: 120-day momentum strategy delivers 155.76% annual returns vs 49.30% for BTC hold
2. **Risk-Adjusted Returns**: Sharpe ratio of 1.94 vs 0.96 for BTC, indicating superior risk-adjusted performance
3. **Low Correlation**: Beta of 0.01 demonstrates minimal systematic risk to BTC
4. **Significant Alpha**: 7,669.91 points of annualized alpha indicate true excess returns

## Limitations

- **Backtest Period**: Analysis based on historical data (Jan 2018 - Dec 2024)
- **Transaction Costs**: Assumes 5bps per trade; actual costs may vary
- **Market Impact**: Does not account for slippage on large positions
- **Liquidity Changes**: Cryptocurrency market liquidity has evolved significantly
- **Regime Changes**: Strategy performance may vary in different market regimes

## Future Enhancements

- [ ] Add regime detection (bull/bear/sideways markets)
- [ ] Implement dynamic position sizing based on volatility
- [ ] Machine learning signal enhancement
- [ ] Multi-factor analysis and optimization
- [ ] Live trading integration with order execution
- [ ] Portfolio-level risk constraints
- [ ] Walk-forward analysis and parameter optimization

## Risk Disclaimer

**This is a research project for educational purposes only.** The strategy is based on historical backtesting and does not guarantee future performance. Cryptocurrency markets are highly volatile and risky. Trading involves substantial risk of loss. Always:

- Understand the strategies before implementation
- Test thoroughly with paper trading
- Use proper risk management (position sizing, stop losses)
- Never risk capital you cannot afford to lose
- Consult with financial advisors

## References

### Academic Papers
- Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). "Time series momentum." Journal of Financial Economics, 104(2), 228-250.
- Bender, J., Sun, X., Thomas, R., & Zdorovtsov, V. (2018). "The promises and pitfalls of factor timing." Research Affiliates.

### Data Sources
- Binance API Documentation: https://binance-docs.github.io/apidocs/
- CoinGecko API: https://www.coingecko.com/en/api

## Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Author

**Shreejit Verma**

- GitHub: [@shreejitverma](https://github.com/shreejitverma)
- LinkedIn: [Shreejit Verma](https://linkedin.com/in/shreejitverma)

## Citation

If you use this research in your work, please cite:

```bibtex
@misc{verma2024statarb,
  author={Verma, Shreejit},
  title={Statistical Arbitrage Momentum Strategy: A Quantitative Analysis},
  year={2024},
  url={https://github.com/shreejitverma/statistical-arbitrage-momentum}
}
```

## Acknowledgments

- Binance for providing cryptocurrency market data
- Python community for excellent data science libraries (pandas, numpy, matplotlib)
- Quantitative finance community for foundational research

## Changelog

### Version 1.0.0 (Aug 2025)
- Initial release
- Core strategy implementation
- Backtest engine
- Comprehensive documentation

---

**Last Updated**: Aug 2025  
**Status**: Active Development

For questions, issues, or suggestions, please open a GitHub issue or contact the author.
