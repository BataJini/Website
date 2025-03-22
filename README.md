# JobBoard

A Django-based job board application with automated scraping of NoFluffJobs listings.

## Setup

1. **Clone and install dependencies**
```bash
git clone <repository-url>
cd JobBoard
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. **Run the application**
```bash
python manage.py runserver
```

## Features

- Browse job listings with clean interface
- Filter jobs by various criteria
- View detailed job information
- Automated job scraping from NoFluffJobs

## Job Scraping

To import new job listings:

```bash
python script/auto_update_jobs.py
```

This script:
1. Scrapes current job listings from NoFluffJobs
2. Formats the data appropriately
3. Imports them into the database

## Deployment

The application is configured to work on both local and production environments.

## License

This project is proprietary and confidential.
