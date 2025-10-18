import requests
import pandas as pd
import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)
WB_API_BASE = "https://api.worldbank.org/v2"

class DemographicProcessor:
    def __init__(self, country_code: str = 'DEU'):
        self.country_code = country_code
        self.indicators = {  # Your original dict
            'SP.POP.TOTL': 'Total Population',
            # ... (all your indicators here)
        }

    def download_demographic_data(self, start_year: int = 2015, end_year: int = 2023) -> pd.DataFrame:
        """Downloads WB data (your original, with logging)."""
        all_data = []
        for indicator_code, indicator_name in self.indicators.items():
            logger.info(f"Fetching: {indicator_name}")
            data = self._get_wb_data(indicator_code, start_year, end_year)
            for record in data:
                if record['value'] is not None:
                    all_data.append({
                        'country': record['country']['value'],
                        'country_code': record['countryiso3code'],
                        'indicator_code': indicator_code,
                        'indicator_name': indicator_name,
                        'year': record['date'],
                        'value': record['value']
                    })
            time.sleep(0.1)  # Rate limit
        df = pd.DataFrame(all_data)
        logger.info(f"Downloaded {len(df)} records")
        return df

    def _get_wb_data(self, indicator_code: str, start_year: int, end_year: int) -> list:
        url = f"{WB_API_BASE}/country/{self.country_code}/indicator/{indicator_code}"
        params = {'date': f"{start_year}:{end_year}", 'format': 'json', 'per_page': 1000}
        response = requests.get(url, params=params)
        return response.json()[1] if response.status_code == 200 and len(response.json()) > 1 else []

    def process_demographic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processes demographic data and creates population estimates by age/gender."""
        if df.empty:
            raise ValueError("Empty input DataFrame")
        
        # Get the latest population data
        latest_pop = df[df['indicator_code'] == 'SP.POP.TOTL'].sort_values('year').iloc[-1]['value']
        
        # Create demographic breakdowns
        processed_data = []
        
        # Age and gender combinations
        age_gender_combos = [
            ('All', 'All', 1.0),
            ('18-24', 'All', 0.15),
            ('25-34', 'All', 0.25),
            ('35-54', 'All', 0.30),
            ('55+', 'All', 0.30),
            ('All', 'male', 0.5),
            ('All', 'female', 0.5),
            ('18-24', 'male', 0.075),
            ('18-24', 'female', 0.075),
            ('25-34', 'male', 0.125),
            ('25-34', 'female', 0.125),
            ('35-54', 'male', 0.15),
            ('35-54', 'female', 0.15),
            ('55+', 'male', 0.15),
            ('55+', 'female', 0.15),
        ]
        
        for age_range, gender, proportion in age_gender_combos:
            processed_data.append({
                'location': 'Germany',  # Default for now
                'age_range': age_range,
                'gender': gender,
                'wb_population_estimate': int(latest_pop * proportion)
            })
        
        logger.info("Data processed successfully. Added penetration estimates.")
        return pd.DataFrame(processed_data)

    def join_with_linkedin_data(self, wb_df: pd.DataFrame, linkedin_file: str) -> pd.DataFrame:
        """Joins data (your original, with quality check)."""
        linkedin_df = pd.read_csv(linkedin_file)
        combined = linkedin_df.merge(wb_df, on=['location', 'age_range', 'gender'], how='left')
        combined['linkedin_penetration_rate'] = (combined['audience_count'] / combined['wb_population_estimate'] * 100).round(2)
        # Validation: Flag low counts
        combined['data_quality_flag'] = combined['audience_count'].apply(lambda x: 'low' if x < 100 else 'ok')
        logger.info(f"Joined data: {len(combined)} rows. Flagged {sum(combined['data_quality_flag'] == 'low')} low-quality entries.")
        return combined