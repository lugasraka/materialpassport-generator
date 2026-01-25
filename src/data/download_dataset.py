"""
Dataset Download and Preparation Script
==========================================

This script downloads the Concrete Compressive Strength dataset from UCI ML Repository
and prepares it for analysis.

Dataset Info:
- Source: UCI Machine Learning Repository
- ID: 165
- Instances: 1,030
- Features: 8 inputs + 1 output
- License: CC BY 4.0
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatasetDownloader:
    """Download and prepare Concrete Compressive Strength dataset"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / 'raw'
        self.processed_dir = self.data_dir / 'processed'
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
    def download_dataset(self):
        """Download dataset using ucimlrepo package"""
        try:
            from ucimlrepo import fetch_ucirepo
            
            logger.info("Downloading Concrete Compressive Strength dataset from UCI ML Repository...")
            
            # Fetch dataset
            concrete = fetch_ucirepo(id=165)
            
            # Extract data
            X = concrete.data.features
            y = concrete.data.targets
            
            # Combine features and target
            df = pd.concat([X, y], axis=1)
            
            # Save raw data
            raw_path = self.raw_dir / 'concrete_data.csv'
            df.to_csv(raw_path, index=False)
            logger.info(f"✓ Dataset saved to {raw_path}")
            
            # Save metadata
            metadata_path = self.raw_dir / 'metadata.txt'
            with open(metadata_path, 'w') as f:
                f.write("Dataset Metadata\n")
                f.write("="*50 + "\n\n")
                f.write(str(concrete.metadata) + "\n\n")
                f.write("Variable Information\n")
                f.write("="*50 + "\n\n")
                f.write(str(concrete.variables))
            
            logger.info(f"✓ Metadata saved to {metadata_path}")
            
            return df
            
        except ImportError:
            logger.error("ucimlrepo package not found. Install with: pip install ucimlrepo")
            return None
        except Exception as e:
            logger.error(f"Error downloading dataset: {e}")
            return None
    
    def prepare_data(self, df=None):
        """Prepare and enrich dataset with sustainability metrics"""
        
        if df is None:
            # Load from file
            raw_path = self.raw_dir / 'concrete_data.csv'
            if not raw_path.exists():
                logger.error("Raw data not found. Run download_dataset() first.")
                return None
            df = pd.read_csv(raw_path)
        
        logger.info("Preparing dataset with sustainability features...")
        
        # Rename columns for clarity
        column_mapping = {
            'Cement': 'cement',
            'Blast Furnace Slag': 'slag',
            'Fly Ash': 'fly_ash',
            'Water': 'water',
            'Superplasticizer': 'superplasticizer',
            'Coarse Aggregate': 'coarse_aggregate',
            'Fine Aggregate': 'fine_aggregate',
            'Age': 'age',
            'Concrete compressive strength': 'strength'
        }
        
        # Apply mapping if columns match
        df_renamed = df.copy()
        if all(col in df.columns for col in column_mapping.keys()):
            df_renamed = df.rename(columns=column_mapping)
        
        # Calculate sustainability metrics
        df_enriched = self.calculate_sustainability_metrics(df_renamed)
        
        # Save processed data
        processed_path = self.processed_dir / 'concrete_enriched.csv'
        df_enriched.to_csv(processed_path, index=False)
        logger.info(f"✓ Enriched dataset saved to {processed_path}")
        
        # Generate summary statistics
        self.generate_summary(df_enriched)
        
        return df_enriched
    
    def calculate_sustainability_metrics(self, df):
        """Calculate sustainability and circularity metrics"""
        
        df_metrics = df.copy()
        
        # 1. Recycled Content Percentage
        # Slag and Fly Ash are industrial waste byproducts
        df_metrics['recycled_content_kg'] = df_metrics['slag'] + df_metrics['fly_ash']
        df_metrics['total_binder'] = df_metrics['cement'] + df_metrics['slag'] + df_metrics['fly_ash']
        df_metrics['recycled_content_pct'] = (df_metrics['recycled_content_kg'] / df_metrics['total_binder'] * 100).round(2)
        
        # 2. Water-Cement Ratio (important for durability and sustainability)
        df_metrics['water_cement_ratio'] = (df_metrics['water'] / 
                                           (df_metrics['cement'] + 0.001)).round(3)  # avoid division by zero
        
        # 3. Cement Intensity (kg cement per MPa of strength)
        # Lower is better for sustainability
        df_metrics['cement_intensity'] = (df_metrics['cement'] / 
                                         (df_metrics['strength'] + 0.001)).round(3)
        
        # 4. Circularity Score (0-100)
        # Based on recycled content and cement replacement
        max_recycled = df_metrics['recycled_content_pct'].max()
        df_metrics['circularity_score'] = (
            (df_metrics['recycled_content_pct'] / max_recycled * 60) +  # 60% weight to recycled content
            (40 * (1 - df_metrics['cement_intensity'] / df_metrics['cement_intensity'].max()))  # 40% to efficiency
        ).round(1)
        
        # 5. Sustainability Category
        df_metrics['sustainability_grade'] = pd.cut(
            df_metrics['circularity_score'],
            bins=[0, 30, 50, 70, 100],
            labels=['Low', 'Medium', 'High', 'Excellent']
        )
        
        # 6. Estimated CO2 Emissions (simplified)
        # Cement production: ~0.9 kg CO2 per kg cement
        # Slag/Fly ash: ~0.05 kg CO2 per kg (much lower)
        CEMENT_CO2 = 0.9
        RECYCLED_CO2 = 0.05
        
        df_metrics['estimated_co2_kg_per_m3'] = (
            df_metrics['cement'] * CEMENT_CO2 +
            df_metrics['recycled_content_kg'] * RECYCLED_CO2
        ).round(2)
        
        return df_metrics
    
    def generate_summary(self, df):
        """Generate and save dataset summary"""
        
        summary_path = self.processed_dir / 'dataset_summary.txt'
        
        with open(summary_path, 'w') as f:
            f.write("CONCRETE COMPRESSIVE STRENGTH DATASET - SUMMARY\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Total Instances: {len(df)}\n")
            f.write(f"Total Features: {len(df.columns)}\n\n")
            
            f.write("BASIC STATISTICS\n")
            f.write("-"*60 + "\n")
            f.write(df.describe().to_string())
            f.write("\n\n")
            
            f.write("SUSTAINABILITY METRICS SUMMARY\n")
            f.write("-"*60 + "\n")
            f.write(f"Average Recycled Content: {df['recycled_content_pct'].mean():.2f}%\n")
            f.write(f"Max Recycled Content: {df['recycled_content_pct'].max():.2f}%\n")
            f.write(f"Average Circularity Score: {df['circularity_score'].mean():.2f}/100\n")
            f.write(f"Average CO2 Emissions: {df['estimated_co2_kg_per_m3'].mean():.2f} kg/m³\n\n")
            
            f.write("SUSTAINABILITY GRADE DISTRIBUTION\n")
            f.write("-"*60 + "\n")
            f.write(df['sustainability_grade'].value_counts().to_string())
            f.write("\n\n")
            
            f.write("MISSING VALUES\n")
            f.write("-"*60 + "\n")
            f.write(df.isnull().sum().to_string())
            f.write("\n")
        
        logger.info(f"✓ Summary statistics saved to {summary_path}")
        
        # Also print to console
        print("\n" + "="*60)
        print("DATASET LOADED SUCCESSFULLY!")
        print("="*60)
        print(f"Shape: {df.shape}")
        print(f"Sustainability Grades Distribution:")
        print(df['sustainability_grade'].value_counts())
        print("="*60 + "\n")


def main():
    """Main execution function"""
    
    print("\n" + "="*60)
    print("MATERIAL PASSPORT GENERATOR - Dataset Preparation")
    print("="*60 + "\n")
    
    # Initialize downloader
    downloader = DatasetDownloader()
    
    # Download dataset
    df_raw = downloader.download_dataset()
    
    if df_raw is not None:
        # Prepare and enrich data
        df_enriched = downloader.prepare_data(df_raw)
        
        print("\n✓ Dataset preparation complete!")
        print(f"  - Raw data: data/raw/concrete_data.csv")
        print(f"  - Enriched data: data/processed/concrete_enriched.csv")
        print(f"  - Summary: data/processed/dataset_summary.txt")
        print("\nNext steps:")
        print("  1. Open notebooks/01_data_exploration.ipynb")
        print("  2. Explore the data and sustainability metrics")
        print("  3. Build baseline ML models")
        
    else:
        print("\n✗ Dataset download failed. Please check your internet connection")
        print("   and ensure 'ucimlrepo' package is installed.")


if __name__ == "__main__":
    main()
