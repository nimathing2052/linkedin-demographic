# LinkedIn Demographic Analysis Pipeline

A Python pipeline that combines LinkedIn audience data with World Bank demographic data to analyze digital penetration rates and demographic insights.

## Features

- **LinkedIn API Integration**: Scrapes real audience data from LinkedIn Campaign Manager
- **World Bank Data**: Downloads and processes demographic data from World Bank API
- **Data Analysis**: Combines datasets and generates insights about digital penetration
- **Visualizations**: Creates charts and analysis reports

## Prerequisites

- Python 3.8+
- LinkedIn Campaign Manager access
- Fresh authentication cookies and headers

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd linkedin-demographic
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Authentication Setup

**Important**: You need to capture fresh cookies and headers from your LinkedIn Campaign Manager session.

### Method 1: Browser Developer Tools

1. Open LinkedIn Campaign Manager in your browser
2. Open Developer Tools (F12)
3. Go to Network tab
4. Make an audience search request
5. Find the `campaignManagerAudienceCounts` request
6. Copy cookies and headers from the request

### Method 2: Create Authentication Files

Copy the example files and fill in your actual values:

```bash
cp example_cookies.yaml cookies.yaml
cp example_headers.yaml headers.yaml
```

Then edit the files with your actual LinkedIn session data:

**cookies.yaml**:
```yaml
li_at: "your-actual-li-at-cookie-value"
JSESSIONID: "your-actual-jsessionid-value"
# ... other cookies
```

**headers.yaml**:
```yaml
accept: "application/vnd.linkedin.normalized+json+2.1"
accept-language: "en-US,en;q=0.9"
csrf-token: "your-actual-csrf-token"
# ... other headers
```

## Usage

### Quick Start (One-Click Demo)

Run the pipeline with mock data immediately:

```bash
python scripts/run_pipeline.py
```

This will run the complete pipeline using realistic mock data, so you can see how it works without needing LinkedIn authentication.

### Using Real LinkedIn Data

For real LinkedIn API data, you'll need to provide authentication:

```bash
python scripts/run_pipeline.py \
  --cookies-file cookies.yaml \
  --headers-file headers.yaml \
  --output-dir data/outputs
```

### Force Mock Data

To explicitly use mock data even if authentication files exist:

```bash
python scripts/run_pipeline.py --use-mock-data
```

### Output Files

The pipeline generates:
- `linkedin_audience_data.csv` - LinkedIn audience data (real or mock)
- `wb_demographic_raw.csv` - Raw World Bank data
- `wb_demographic_processed.csv` - Processed demographic data
- `combined_linkedin_wb_data.csv` - Combined analysis
- `linkedin_demographics_analysis.png` - Visualization

## Current Capabilities

- **One-Click Demo**: Runs immediately with realistic mock data
- **Real API Integration**: Uses LinkedIn Campaign Manager API when authentication provided
- **Working Combination**: Germany + English language
- **Audience Count**: Real LinkedIn API data or realistic mock data (24M users)
- **Demographic Analysis**: World Bank population data
- **Penetration Rate**: LinkedIn users / Total population (28.6% for Germany)

## Project Structure

```
linkedin-demographic/
├── src/
│   ├── linkedIn_scraper.py      # LinkedIn API integration
│   ├── demographic_processor.py # World Bank data processing
│   └── analysis.py              # Data analysis and visualization
├── scripts/
│   └── run_pipeline.py          # Main pipeline script
├── config/
│   └── targeting.yaml           # Targeting configuration
├── data/
│   ├── outputs/                 # Generated data files
│   └── cache/                   # Cache directory
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Important Notes

- **Authentication**: Cookies and headers expire frequently. You'll need to refresh them regularly.
- **Rate Limiting**: The pipeline includes delays to respect LinkedIn's rate limits.
- **Data Quality**: Currently optimized for Germany + English combination.

## Future Enhancements

- Support for more location/language combinations
- Automated authentication refresh
- Enhanced demographic analysis
- Real-time data collection

## 📝 License

This project is for research and educational purposes. Please respect LinkedIn's Terms of Service and rate limits.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Disclaimer

This tool is for research purposes only. Users are responsible for complying with LinkedIn's Terms of Service and applicable data protection regulations.