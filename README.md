# JobBoard Web Scraper

This project includes a web scraper for job listings and a Django-based job board application.

## Setup Instructions

1. **Clone the Repository**
```bash
git clone <repository-url>
cd JobBoard
```

2. **Create and Activate Virtual Environment**

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Requirements**
```bash
pip install -r requirements.txt
```

4. **Install Chrome Browser**
The scraper uses Chrome WebDriver. Make sure you have Google Chrome installed on your system.
- Download Chrome from: https://www.google.com/chrome/

5. **Run the Job Scraper**
```bash
python scripts/JobScraper.py
```

The scraper will:
- Launch Chrome in headless mode
- Scrape job listings from specified websites
- Save the results in the `job_data` directory

6. **Import Jobs to Database**
```bash
python scripts/job_scraper.py
```

## Features

- Automated job scraping from NoFluffJobs
- Handles duplicate job listings
- Extracts detailed job information including:
  - Job title
  - Company name
  - Location
  - Salary
  - Job type
  - Required skills

## Requirements

- Python 3.8 or higher
- Google Chrome browser
- All Python packages listed in requirements.txt

## Troubleshooting

If you encounter any issues:

1. **WebDriver Issues**
   - The script uses `webdriver_manager` which should automatically download the correct ChromeDriver
   - If you get WebDriver errors, try updating Chrome to the latest version

2. **Package Installation Issues**
   - Make sure you're using the latest pip: `python -m pip install --upgrade pip`
   - If a package fails to install, try installing it separately

3. **Permission Issues**
   - On Linux/macOS, you might need to run commands with sudo
   - Make sure the script has write permissions in the job_data directory

## Notes

- The scraper is configured to run in headless mode by default
- Job data is saved in JSON format
- Duplicate jobs are automatically filtered out
- The scraper includes error handling and retry mechanisms
