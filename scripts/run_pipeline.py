#!/usr/bin/env python3
"""
Working LinkedIn Pipeline - Simplified Version

This pipeline only tests the combinations that we know work with fresh authentication.
"""

import click
import yaml
import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.linkedIn_scraper import LinkedInScraper
from src.demographic_processor import DemographicProcessor
from src.analysis import analyze_combined_data, create_visualizations

@click.command()
@click.option('--cookies-file', default=None, help='YAML file with cookies dict (optional, uses mock data if not provided)')
@click.option('--headers-file', default=None, help='YAML file with headers dict (optional, uses mock data if not provided)')
@click.option('--output-dir', default='data/outputs', help='Output directory')
@click.option('--use-mock-data', is_flag=True, help='Force use of mock data instead of real LinkedIn API')
def run_working_pipeline(cookies_file, headers_file, output_dir, use_mock_data):
    """Run the working pipeline with mock data or real LinkedIn API."""
    
    print(" LinkedIn Demographic Analysis Pipeline")
    print("=" * 50)
    
    # Determine if we should use real API or mock data
    use_real_api = not use_mock_data and cookies_file and headers_file
    
    if use_real_api:
        print("🔐 Using real LinkedIn API with provided authentication...")
        try:
            with open(cookies_file, 'r') as f:
                cookies = yaml.safe_load(f)
            with open(headers_file, 'r') as f:
                headers = yaml.safe_load(f)
        except FileNotFoundError as e:
            print(f"Authentication file not found: {e}")
            print("Falling back to mock data...")
            use_real_api = False
    else:
        print("🎭 Using mock data for demonstration...")
        cookies = {}
        headers = {}
    
    # Step 1: Get LinkedIn data (real or mock)
    print("\n Getting LinkedIn audience data...")
    scraper = LinkedInScraper(cookies, headers)
    
    if use_real_api:
        # Test the working combination
        result = scraper.get_audience_count('Germany', language='English')
        
        if result['success']:
            print(f"LinkedIn API working! Audience count: {result['count']:,}")
            audience_count = result['count']
            success = True
            error = ''
        else:
            print(f"LinkedIn API failed: {result['error']}")
            print("Falling back to mock data...")
            audience_count = 24000000  # Mock data
            success = False
            error = result['error']
    else:
        # Use mock data
        audience_count = 24000000  # Realistic mock data for Germany + English
        success = True
        error = ''
        print(f" Mock data generated! Audience count: {audience_count:,}")
    
    # Create dataset
    working_data = [{
        'location': 'Germany',
        'age_range': 'All',
        'gender': 'All', 
        'language': 'English',
        'audience_count': audience_count,
        'success': success,
        'error': error,
        'timestamp': datetime.now().isoformat(),
        'data_source': 'real_api' if use_real_api and success else 'mock_data'
    }]
    
    # Save LinkedIn data
    linkedin_df = pd.DataFrame(working_data)
    linkedin_file = f"{output_dir}/linkedin_audience_data.csv"
    linkedin_df.to_csv(linkedin_file, index=False)
    print(f"Saved LinkedIn data to {linkedin_file}")
    
    # Step 2: Process World Bank data
    print("\n Processing World Bank demographic data...")
    processor = DemographicProcessor()
    
    try:
        wb_raw = processor.download_demographic_data()
        wb_raw.to_csv(f"{output_dir}/wb_demographic_raw.csv", index=False)
        print(f"Downloaded {len(wb_raw)} World Bank records")
        
        wb_processed = processor.process_demographic_data(wb_raw)
        wb_processed.to_csv(f"{output_dir}/wb_demographic_processed.csv", index=False)
        print(f"Processed demographic data: {len(wb_processed)} records")
        
    except Exception as e:
        print(f"World Bank processing failed: {e}")
        return
    
    # Step 3: Combine data
    print("\n🔗 Combining LinkedIn and World Bank data...")
    try:
        combined = processor.join_with_linkedin_data(wb_processed, linkedin_file)
        combined_file = f"{output_dir}/combined_linkedin_wb_data.csv"
        combined.to_csv(combined_file, index=False)
        print(f"Combined data saved to {combined_file}")
        
    except Exception as e:
        print(f"Data combination failed: {e}")
        return
    
    # Step 4: Analysis
    print("\n Running analysis...")
    try:
        df = analyze_combined_data(combined_file)
        create_visualizations(df)
        print("Analysis and visualizations completed")
        
    except Exception as e:
        print(f" Analysis failed: {e}")
        return
    
    # Final summary
    print(f"\n Pipeline completed successfully!")
    print(f" Output files in: {output_dir}/")
    print(f"   - linkedin_audience_data.csv")
    print(f"   - wb_demographic_raw.csv") 
    print(f"   - wb_demographic_processed.csv")
    print(f"   - combined_linkedin_wb_data.csv")
    print(f"   - linkedin_demographics_analysis.png")
    
    if not use_real_api:
        print(f"\n💡 To use real LinkedIn data:")
        print(f"   1. Capture fresh cookies and headers from LinkedIn Campaign Manager")
        print(f"   2. Create cookies.yaml and headers.yaml files")
        print(f"   3. Run: python scripts/run_pipeline.py --cookies-file cookies.yaml --headers-file headers.yaml")

if __name__ == '__main__':
    run_working_pipeline()
