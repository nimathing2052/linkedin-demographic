import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

def analyze_combined_data(combined_file: str) -> pd.DataFrame:
    """Full analysis (multi-country support, with logs/prints)."""
    try:
        df = pd.read_csv(combined_file)
    except FileNotFoundError:
        logger.error(f"Combined file {combined_file} not found!")
        return pd.DataFrame()
    
    logger.info(f"Analysis started: {len(df)} records")
    print("=== Combined LinkedIn + World Bank Data Analysis (Multi-Country) ===")
    print(f"Total records: {len(df)}")
    print(f"Countries: {', '.join(df['location'].unique())}")
    print(f"World Bank data from {df['wb_year'].iloc[0] if 'wb_year' in df.columns and not df.empty else 'N/A'}")
    
    # Native languages per country (for dynamic analysis)
    native_langs = {'Germany': ['German', 'English'], 'Spain': ['Spanish', 'English'], 'France': ['French', 'English']}
    
    # 1. LinkedIn penetration by language
    print("\n=== LinkedIn Penetration by Language (All Demographics) ===")
    all_ages_all_genders = df[(df['age_range'] == 'All') & (df['gender'] == 'All')]
    
    for location in sorted(df['location'].unique()):
        print(f"\n{location}:")
        loc_data = all_ages_all_genders[all_ages_all_genders['location'] == location]
        if loc_data.empty:
            print("  No data available.")
            continue
        language_analysis = loc_data[['language', 'audience_count', 'linkedin_penetration_rate']].copy()
        language_analysis = language_analysis.sort_values('audience_count', ascending=False)
        
        for _, row in language_analysis.iterrows():
            print(f"  {row['language']:8}: {row['audience_count']:>9,} LinkedIn users ({row['linkedin_penetration_rate']:>5.2f}% of population)")
    
    # 2. Gender distribution analysis
    print("\n=== Gender Distribution Analysis ===")
    for location in sorted(df['location'].unique()):
        print(f"\n{location}:")
        loc_df = df[df['location'] == location]
        if loc_df.empty:
            print("  No data available.")
            continue
        male_linkedin = loc_df[(loc_df['age_range'] == 'All') & (loc_df['gender'] == 'male')]['audience_count'].sum()
        female_linkedin = loc_df[(loc_df['age_range'] == 'All') & (loc_df['gender'] == 'female')]['audience_count'].sum()
        total_linkedin = male_linkedin + female_linkedin
        
        wb_male_pct = loc_df['wb_male_percentage'].iloc[0] if 'wb_male_percentage' in loc_df.columns else 50
        wb_female_pct = loc_df['wb_female_percentage'].iloc[0] if 'wb_female_percentage' in loc_df.columns else 50
        
        # Compute percentages outside f-string to avoid division/format issues
        male_pct = (male_linkedin / total_linkedin * 100) if total_linkedin > 0 else 0
        female_pct = (female_linkedin / total_linkedin * 100) if total_linkedin > 0 else 0
        
        print(f"  Population - Male: {wb_male_pct:.1f}%, Female: {wb_female_pct:.1f}%")
        print(f"  LinkedIn   - Male: {male_pct:.1f}%, Female: {female_pct:.1f}%")
        print(f"  LinkedIn representation: Male {male_linkedin:,}, Female {female_linkedin:,}")
    
    # 3. Age group analysis (native speakers only)
    print("\n=== Age Group Analysis (Native/English Speakers Only) ===")
    age_order = ['18-24', '25-34', '35-54', '55+', 'All']
    for location in sorted(df['location'].unique()):
        print(f"\n{location} (natives: {', '.join(native_langs.get(location, []))}):")
        native_speakers = df[(df['language'].isin(native_langs.get(location, []))) & (df['gender'] == 'All') & (df['location'] == location)]
        if native_speakers.empty:
            print("  No data available.")
            continue
        
        age_analysis = native_speakers.groupby('age_range').agg({
            'audience_count': 'sum',
            'wb_population_estimate': 'first',
            'linkedin_penetration_rate': 'mean'
        }).round(2)
        
        age_analysis = age_analysis.reindex(age_order)
        
        for age_range, row in age_analysis.iterrows():
            if age_range != 'All':  # Skip 'All' as it's the sum
                print(f"  {age_range:>6}: {row['audience_count']:>9,} LinkedIn users, "
                      f"penetration: {row['linkedin_penetration_rate']:>5.2f}%")
    
    # 4. Language-specific insights (focus on foreign languages)
    print("\n=== Language-Specific Insights ===")
    for location in sorted(df['location'].unique()):
        print(f"\n{location} (foreign excl. {', '.join(native_langs.get(location, []))}):")
        foreign_languages = df[(~df['language'].isin(native_langs.get(location, []))) & 
                              (df['age_range'] == 'All') & 
                              (df['gender'] == 'All') & 
                              (df['location'] == location)]
        if foreign_languages.empty:
            print("  No data available.")
            continue
        
        for _, row in foreign_languages.sort_values('audience_count', ascending=False).iterrows():
            print(f"  {row['language']:8}: {row['audience_count']:>6,} users ({row['linkedin_penetration_rate']:.2f}% of total population)")
    
    # 5. Professional networking insights
    print("\n=== Professional Networking Insights ===")
    for location in sorted(df['location'].unique()):
        print(f"\n{location} (working-age 25-54, natives):")
        working_age = df[(df['age_range'].isin(['25-34', '35-54'])) & 
                        (df['gender'] == 'All') &
                        (df['language'].isin(native_langs.get(location, []))) &
                        (df['location'] == location)]
        if working_age.empty:
            print("  No data available.")
            continue
        
        working_age_summary = working_age.groupby('language').agg({
            'audience_count': 'sum',
            'wb_population_estimate': 'sum',
            'linkedin_penetration_rate': 'mean'
        }).round(2)
        
        for language, row in working_age_summary.iterrows():
            print(f"  {language}: {row['linkedin_penetration_rate']:.1f}% penetration")
    
    # 6. International community analysis
    print("\n=== International Community Analysis ===")
    for location in sorted(df['location'].unique()):
        print(f"\n{location}:")
        international_df = df[(df['gender'] == 'All') & 
                             (~df['language'].isin(native_langs.get(location, []))) &
                             (df['age_range'] != 'All') &
                             (df['location'] == location)]
        if international_df.empty:
            print("  No data available.")
            continue
        
        intl_pivot = international_df.pivot_table(
            index='language', 
            columns='age_range', 
            values='audience_count',
            fill_value=0
        )
        
        age_cols = ['18-24', '25-34', '35-54', '55+']
        intl_pivot = intl_pivot.reindex(columns=age_cols)
        
        print(intl_pivot.to_string())
        
        total_international = df[(~df['language'].isin(native_langs.get(location, []))) & 
                               (df['age_range'] == 'All') & 
                               (df['gender'] == 'All') & 
                               (df['location'] == location)]['audience_count'].sum()
        
        total_native = df[(df['language'].isin(native_langs.get(location, []))) & 
                         (df['age_range'] == 'All') & 
                         (df['gender'] == 'All') & 
                         (df['location'] == location)]['audience_count'].sum()
        
        print(f"  Total international LinkedIn community: {total_international:,}")
        print(f"  Total native LinkedIn community: {total_native:,}")
        print(f"  International share: {total_international/(total_international+total_native)*100:.1f}%" if total_native > 0 else "  No native data")
    
    # 7. Cross-country comparison (English as benchmark)
    print("\n=== Cross-Country Comparison (English Speakers, All Demographics) ===")
    cross_country = df[(df['age_range'] == 'All') & (df['gender'] == 'All') & (df['language'] == 'English')].groupby('location').agg({
        'audience_count': 'sum',
        'wb_total_population': 'first',
        'linkedin_penetration_rate': 'mean'
    }).round(2)
    if not cross_country.empty:
        print(cross_country.to_string())
    else:
        print("  No English data available.")
    
    logger.info("Research Insight: This pipeline reveals LinkedIn's role in mapping digital expat communities, aiding CSS studies on societal transformation via ad targeting as behavioral proxy.")
    return df

def create_visualizations(df: pd.DataFrame, output_file: str = 'data/outputs/linkedin_demographics_analysis.png'):
    """Create visualizations (multi-country aggregated)."""
    if df.empty:
        logger.warning("Empty DataFrame—no visualizations created.")
        return
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('LinkedIn Demographics vs World Bank Data (Multi-Country)', fontsize=16)
    
    # Aggregate for multi-country where needed
    all_demo = df[(df['age_range'] == 'All') & (df['gender'] == 'All')]
    
    # 1. Language penetration (averaged across countries)
    if not all_demo.empty:
        lang_avg = all_demo.groupby('language')['linkedin_penetration_rate'].mean().round(2)
        axes[0,0].bar(lang_avg.index, lang_avg.values)
        axes[0,0].set_title('Avg LinkedIn Penetration Rate by Language (All Countries)')
        axes[0,0].set_ylabel('Penetration Rate (%)')
        axes[0,0].set_yscale('log')
        axes[0,0].tick_params(axis='x', rotation=45)
    else:
        axes[0,0].text(0.5, 0.5, 'No data', ha='center', va='center', transform=axes[0,0].transAxes)
    
    # 2. Gender balance by age group (stacked, aggregated)
    gender_age_data = df[(df['gender'] != 'All') & (df['age_range'] != 'All')]
    if not gender_age_data.empty:
        gender_age_pivot = gender_age_data.groupby(['age_range', 'gender'])['audience_count'].sum().unstack('gender', fill_value=0)
        gender_age_pct = gender_age_pivot.div(gender_age_pivot.sum(axis=1), axis=0) * 100
        gender_age_pct.plot(kind='bar', ax=axes[0,1], stacked=True, color=['lightblue', 'lightcoral'], width=0.8)
        axes[0,1].set_title('LinkedIn Gender Balance by Age Group (All Countries)')
        axes[0,1].set_ylabel('Percentage (%)')
        axes[0,1].set_ylim(0, 100)
        axes[0,1].tick_params(axis='x', rotation=45)
        axes[0,1].legend(title='Gender')
    else:
        axes[0,1].text(0.5, 0.5, 'No data', ha='center', va='center', transform=axes[0,1].transAxes)
    
    # 3. Gender balance by language (stacked percentage bars)
    gender_lang_data = df[(df['age_range'] == 'All') & (df['gender'] != 'All')]
    if not gender_lang_data.empty:
        gender_lang_pivot = gender_lang_data.pivot_table(index='language', columns='gender', values='audience_count', aggfunc='sum')
        gender_lang_pct = gender_lang_pivot.div(gender_lang_pivot.sum(axis=1), axis=0) * 100
        gender_lang_pct.plot(kind='bar', ax=axes[1,0], stacked=True, color=['lightblue', 'lightcoral'])
        axes[1,0].set_title('LinkedIn Gender Balance by Language (All Countries)')
        axes[1,0].set_ylabel('Percentage (%)')
        axes[1,0].set_ylim(0, 100)
        axes[1,0].tick_params(axis='x', rotation=45)
        axes[1,0].legend(title='Gender')
    else:
        axes[1,0].text(0.5, 0.5, 'No data', ha='center', va='center', transform=axes[1,0].transAxes)
    
    # 4. World Bank Gender Balance (averaged across countries)
    wb_male_avg = df['wb_male_percentage'].mean() if 'wb_male_percentage' in df.columns else 50
    wb_female_avg = df['wb_female_percentage'].mean() if 'wb_female_percentage' in df.columns else 50
    languages = sorted(df['language'].unique()) if 'language' in df.columns else ['N/A']
    wb_gender_data = pd.DataFrame({
        'male': [wb_male_avg] * len(languages),
        'female': [wb_female_avg] * len(languages)
    }, index=languages)
    wb_gender_data.plot(kind='bar', ax=axes[1,1], stacked=True, color=['lightblue', 'lightcoral'])
    axes[1,1].set_title('Avg World Bank Population Gender Balance by Language')
    axes[1,1].set_ylabel('Percentage (%)')
    axes[1,1].set_ylim(0, 100)
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].legend(title='Gender')
    axes[1,1].axhline(y=50, color='gray', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Main visualization saved as '{output_file}'")
    logger.info(f"Visualizations saved to {output_file}")
    
    # Bonus: Separate cross-country viz
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    cross_viz = df[(df['age_range'] == 'All') & (df['gender'] == 'All') & (df['language'] == 'English')]
    if not cross_viz.empty:
        sns.barplot(data=cross_viz, x='location', y='linkedin_penetration_rate', ax=ax2)
        ax2.set_title('English-Speaking LinkedIn Penetration by Country')
        ax2.set_ylabel('Penetration Rate (%)')
        plt.savefig('data/outputs/cross_country_penetration.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Cross-country visualization saved as 'data/outputs/cross_country_penetration.png'")
    else:
        logger.warning("No cross-country data for visualization.")