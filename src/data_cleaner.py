"""
Data Cleaner Module
Handles data cleaning, alignment, and validation for statistical arbitrage strategy.
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans and prepares data for strategy analysis."""
    
    def __init__(self, liquidity_threshold: float = 0.40):
        """Initialize DataCleaner with liquidity threshold."""
        self.liquidity_threshold = liquidity_threshold
        
    def clean_and_align(
        self,
        returns_df: pd.DataFrame,
        volumes_df: pd.DataFrame,
        min_assets: int = 8,
        fillna_method: str = 'ffill'
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Clean and align returns and volume data.
        
        Args:
            returns_df: DataFrame with returns data
            volumes_df: DataFrame with volume data
            min_assets: Minimum number of assets required for start date
            fillna_method: Method for filling missing values ('ffill' or 'bfill')
            
        Returns:
            Tuple of (clean_returns, clean_volumes) aligned DataFrames
        """
        logger.info("Starting data cleaning process...")
        
        # Step 1: Convert to numeric
        returns_numeric = returns_df.apply(pd.to_numeric, errors='coerce')
        volumes_numeric = volumes_df.apply(pd.to_numeric, errors='coerce')
        
        # Step 2: Find first valid date for each asset
        first_valid_dates = {}
        for col in returns_numeric.columns:
            first_valid = returns_numeric[col].first_valid_index()
            first_valid_dates[col] = first_valid
            
        logger.info(f"First valid dates: {first_valid_dates}")
        
        # Step 3: Sort and find suitable start date
        sorted_dates = sorted(first_valid_dates.items(), key=lambda x: x[1])
        
        if len(sorted_dates) < min_assets:
            raise ValueError(f"Insufficient assets. Found {len(sorted_dates)}, need {min_assets}")
            
        start_date = sorted_dates[min_assets - 1][1]
        logger.info(f"Selected start date: {start_date}")
        
        # Step 4: Trim data to start date
        clean_returns = returns_numeric.loc[start_date:].copy()
        clean_volumes = volumes_numeric.loc[start_date:].copy()
        
        # Step 5: Handle missing values
        if fillna_method == 'ffill':
            clean_returns = clean_returns.fillna(method='ffill', limit=5)
            clean_volumes = clean_volumes.fillna(method='ffill', limit=5)
        
        # Backward fill remaining
        clean_returns = clean_returns.bfill()
        clean_volumes = clean_volumes.bfill()
        
        # Step 6: Handle timezone
        if clean_returns.index.tz is None:
            clean_returns.index = pd.to_datetime(clean_returns.index)
        else:
            clean_returns.index = clean_returns.index.tz_localize(None)
            
        if clean_volumes.index.tz is None:
            clean_volumes.index = pd.to_datetime(clean_volumes.index)
        else:
            clean_volumes.index = clean_volumes.index.tz_localize(None)
        
        # Step 7: Verify results
        logger.info(f"Data shape - Returns: {clean_returns.shape}, Volumes: {clean_volumes.shape}")
        logger.info(f"Missing values in returns: {clean_returns.isnull().sum().sum()}")
        logger.info(f"Missing values in volumes: {clean_volumes.isnull().sum().sum()}")
        
        return clean_returns, clean_volumes
    
    def filter_by_liquidity(
        self,
        volumes_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        threshold: float = 0.40
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Filter assets by liquidity threshold.
        
        Args:
            volumes_df: DataFrame with volume data
            returns_df: DataFrame with returns data
            threshold: Liquidity threshold (0-1)
            
        Returns:
            Tuple of (filtered_returns, filtered_volumes)
        """
        logger.info(f"Filtering assets with liquidity threshold: {threshold}")
        
        # Count non-zero volume periods
        zero_volumes = (volumes_df == 0).sum()
        total_periods = len(volumes_df)
        
        valid_volumes = volumes_df.columns[zero_volumes / total_periods <= (1 - threshold)]
        
        # Get base asset names
        base_assets = [col.replace('_Vol', '') for col in valid_volumes]
        
        # Filter returns by valid assets
        valid_returns = [col for col in returns_df.columns if any(asset in col for asset in base_assets)]
        
        filtered_returns = returns_df[valid_returns].copy()
        filtered_volumes = volumes_df[valid_volumes].copy()
        
        logger.info(f"Filtered to {len(valid_returns)} asset pairs from {len(returns_df.columns)}")
        
        return filtered_returns, filtered_volumes
    
    def verify_data_quality(self, returns_df: pd.DataFrame, volumes_df: pd.DataFrame) -> None:
        """
        Verify data quality and print statistics.
        
        Args:
            returns_df: DataFrame with returns data
            volumes_df: DataFrame with volume data
        """
        logger.info("\n=== DATA QUALITY REPORT ===")
        logger.info(f"Date range: {returns_df.index[0]} to {returns_df.index[-1]}")
        logger.info(f"Total trading days: {len(returns_df)}")
        logger.info(f"Assets in returns: {len(returns_df.columns)}")
        logger.info(f"Assets in volumes: {len(volumes_df.columns)}")
        
        logger.info("\nReturns Statistics:")
        logger.info(returns_df.describe().round(4))
        
        logger.info("\nVolumes Statistics:")
        logger.info(volumes_df.describe().round(4))
        
        logger.info("\nMissing values:")
        logger.info(f"Returns: {returns_df.isnull().sum().sum()}")
        logger.info(f"Volumes: {volumes_df.isnull().sum().sum()}")
