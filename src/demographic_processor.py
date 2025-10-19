import requests
import pandas as pd
import time
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)
WB_API_BASE = "https://api.worldbank.org/v2"

class DemographicProcessor:
    def __init__(self, country_codes: List[str] = None):
        if country_codes is None:
            country_codes = ['DEU', 'ESP', 'FRA']  # Default: Germany, Spain, France
        self.country_codes = country_codes
        self.country_names = {'DEU': 'Germany', 'ESP': 'Spain', 'FRA': 'France'}  # Extend as needed
        self.indicators = {
            'SP.POP.TOTL': 'Total Population',
            'SP.POP.TOTL.MA.ZS': 'Population, male (% of total population)',
            'SP.POP.TOTL.FE.ZS': 'Population, female (% of total population)',
            'SP.POP.0014.TO.ZS': 'Population ages 0-14 (% of total population)',
            'SP.POP.1564.TO.ZS': 'Population ages 15-64 (% of total population)', 
            'SP.POP.65UP.TO.ZS': 'Population ages 65 and above (% of total population)',
            'SP.POP.0014.MA.ZS': 'Population ages 0-14, male (% of male population)',
            'SP.POP.1564.MA.ZS': 'Population ages 15-64, male (% of male population)',
            'SP.POP.65UP.MA.ZS': 'Population ages 65 and above, male (% of male population)',
            'SP.POP.0014.FE.ZS': 'Population ages 0-14, female (% of female population)',
            'SP.POP.1564.FE.ZS': 'Population ages 15-64, female (% of female population)',
            'SP.POP.65UP.FE.ZS': 'Population ages 65 and above, female (% of female population)',
            'SM.POP.NETM': 'Net migration',
            'SM.POP.TOTL.ZS': 'International migrant stock (% of population)'
        }

    def download_demographic_data(self, start_year: int = 2015, end_year: int = 2023) -> pd.DataFrame:
        """Downloads WB data for multiple countries (with logging)."""
        all_data = []
        for country_code in self.country_codes:
            country_name = self.country_names.get(country_code, country_code)
            logger.info(f"Downloading for {country_name} ({country_code})")
            for indicator_code, indicator_name in self.indicators.items():
                logger.info(f"  Fetching: {indicator_name}")
                data = self._get_wb_data(country_code, indicator_code, start_year, end_year)
                for record in data:
                    if record['value'] is not None:
                        all_data.append({
                            'country': country_name,
                            'country_code': record['countryiso3code'],
                            'indicator_code': indicator_code,
                            'indicator_name': indicator_name,
                            'year': record['date'],
                            'value': record['value']
                        })
                time.sleep(0.1)  # Rate limit
        df = pd.DataFrame(all_data)
        logger.info(f"Downloaded {len(df)} records across {len(self.country_codes)} countries")
        return df

    def _get_wb_data(self, country_code: str, indicator_code: str, start_year: int, end_year: int) -> list:
        url = f"{WB_API_BASE}/country/{country_code}/indicator/{indicator_code}"
        params = {'date': f"{start_year}:{end_year}", 'format': 'json', 'per_page': 1000}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200 and len(response.json()) > 1:
                return response.json()[1]
        except Exception as e:
            logger.error(f"Error fetching {indicator_code} for {country_code}: {e}")
        return []

    def process_demographic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processes data and calculates additional demographic metrics (real WB-based)."""
        if df.empty:
            raise ValueError("Empty input DataFrame")
        
        # Group by country
        countries = df['country'].unique()
        all_processed = []
        
        # Map LinkedIn age ranges to World Bank age groups
        linkedin_age_mapping = {
            '18-24': 'age_15_64',  # Best approximation
            '25-34': 'age_15_64',
            '35-54': 'age_15_64', 
            '55+': 'age_65_plus'   # Approximate
        }
        
        for country in countries:
            country_df = df[df['country'] == country]
            latest_year = country_df['year'].max()
            latest_data = country_df[country_df['year'] == latest_year].copy()
            
            # Create a summary table with key metrics
            summary = {}
            for _, row in latest_data.iterrows():
                summary[row['indicator_code']] = row['value']
            
            # Calculate absolute numbers from percentages
            total_pop = summary.get('SP.POP.TOTL', 0)
            
            # Calculate age group populations
            age_0_14_pct = summary.get('SP.POP.0014.TO.ZS', 0) / 100
            age_15_64_pct = summary.get('SP.POP.1564.TO.ZS', 0) / 100
            age_65_plus_pct = summary.get('SP.POP.65UP.TO.ZS', 0) / 100
            
            # Calculate gender split
            male_pct = summary.get('SP.POP.TOTL.MA.ZS', 0) / 100
            female_pct = summary.get('SP.POP.TOTL.FE.ZS', 0) / 100
            
            wb_age_populations = {
                'age_0_14': total_pop * age_0_14_pct,
                'age_15_64': total_pop * age_15_64_pct,
                'age_65_plus': total_pop * age_65_plus_pct
            }
            
            # Create processed data for this country
            processed_country = []
            for age_range in ['All', '18-24', '25-34', '35-54', '55+']:
                for gender in ['All', 'male', 'female']:
                    
                    # Calculate population estimate
                    if age_range == 'All':
                        age_pop = total_pop
                    else:
                        wb_age_group = linkedin_age_mapping.get(age_range, 'age_15_64')
                        age_pop = wb_age_populations[wb_age_group]
                        
                        # Rough approximation for specific LinkedIn age ranges within 15-64
                        if age_range in ['18-24', '25-34', '35-54'] and wb_age_group == 'age_15_64':
                            # Assume roughly equal distribution within working age
                            age_pop = age_pop / 3  # Divide by 3 age groups
                    
                    if gender == 'All':
                        pop_estimate = age_pop
                    elif gender == 'male':
                        pop_estimate = age_pop * male_pct
                    else:  # female
                        pop_estimate = age_pop * female_pct
                    
                    processed_country.append({
                        'location': country,
                        'age_range': age_range,
                        'gender': gender,
                        'wb_population_estimate': int(pop_estimate),
                        'wb_year': latest_year,
                        'wb_total_population': int(total_pop),
                        'wb_male_percentage': male_pct * 100,
                        'wb_female_percentage': female_pct * 100
                    })
            all_processed.extend(processed_country)
        
        processed_df = pd.DataFrame(all_processed)
        logger.info(f"Processed {len(processed_df)} segments across {len(countries)} countries")
        return processed_df

    def join_with_linkedin_data(self, wb_df: pd.DataFrame, linkedin_file: str) -> pd.DataFrame:
        """Joins WB data with LinkedIn (handles multi-country, with quality check)."""
        try:
            linkedin_df = pd.read_csv(linkedin_file)
            logger.info(f"Loaded LinkedIn data: {len(linkedin_df)} rows")
        except FileNotFoundError:
            logger.error(f"LinkedIn data file {linkedin_file} not found!")
            return pd.DataFrame()
        
        # Cross-match on location, age_range, gender
        combined_list = []
        for _, wb_row in wb_df.iterrows():
            mask = (
                (linkedin_df['location'] == wb_row['location']) &
                (linkedin_df['age_range'] == wb_row['age_range']) &
                (linkedin_df['gender'] == wb_row['gender'])
            )
            matches = linkedin_df[mask]
            if not matches.empty:
                for _, li_row in matches.iterrows():
                    new_row = li_row.copy()
                    new_row['wb_population_estimate'] = wb_row['wb_population_estimate']
                    new_row['wb_year'] = wb_row['wb_year']
                    new_row['wb_total_population'] = wb_row['wb_total_population']
                    new_row['wb_male_percentage'] = wb_row['wb_male_percentage']
                    new_row['wb_female_percentage'] = wb_row['wb_female_percentage']
                    combined_list.append(new_row)
        
        combined = pd.DataFrame(combined_list)
        if not combined.empty:
            # Calculate penetration rates (handle div-by-zero)
            combined['linkedin_penetration_rate'] = (
                combined.apply(lambda row: (row['audience_count'] / row['wb_population_estimate'] * 100) if row['wb_population_estimate'] > 0 else 0, axis=1)
            ).round(2)
            
            # Add analysis columns
            combined['audience_per_million_population'] = (
                combined['audience_count'] / (combined['wb_total_population'] / 1_000_000)
            ).round(0)
            
            # Validation: Flag low counts
            combined['data_quality_flag'] = combined['audience_count'].apply(lambda x: 'low' if x < 100 else 'ok')
            low_count = sum(combined['data_quality_flag'] == 'low')
            logger.info(f"Joined {len(combined)} rows. Flagged {low_count} low-quality entries.")
        else:
            logger.warning("No matches found in join—check location/age/gender alignment.")
        
        return combined