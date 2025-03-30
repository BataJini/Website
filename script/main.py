import asyncio
# from curl_cffi import AsyncSession
import curl_cffi
import json
from lxml import html
import time
import os
import random
from urllib.parse import urlparse

# Helper function for retrying requests
def make_request_with_retry(url, method='get', max_retries=3, delay=2, **kwargs):
    """Make a request with retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Add proxy configuration if on PythonAnywhere
            if 'pythonanywhere.com' in os.environ.get('HOSTNAME', ''):
                # Use PythonAnywhere's proxy
                proxy = os.environ.get('HTTP_PROXY', 'http://proxy.server:3128')
                kwargs['proxies'] = {'http': proxy, 'https': proxy}
                
            # Randomize user agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
            ]
            if 'headers' in kwargs:
                kwargs['headers']['User-Agent'] = random.choice(user_agents)
            
            # Make the request
            if method.lower() == 'get':
                response = curl_cffi.get(url, **kwargs)
            else:
                response = curl_cffi.post(url, **kwargs)
            
            return response
            
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise  # Re-raise the last exception
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(delay * (attempt + 1))  # Exponential backoff
            continue

# Helper function to format salaries
def format_salary(salary_data):
    """Format salary information in a human-readable format"""
    if not salary_data:
        return "Salary not specified"
        
    try:
        # Handle dictionary format
        if isinstance(salary_data, dict):
            # For salary ranges with from/to values
            if 'from' in salary_data and salary_data.get('from'):
                salary_from = int(salary_data.get('from', 0))
                salary_to = int(salary_data.get('to', 0)) if salary_data.get('to') else 0
                currency = salary_data.get('currency', 'PLN')
                
                # Format the salary range
                if salary_from and salary_to:
                    return f"{salary_from}-{salary_to} {currency}"
                elif salary_from:
                    return f"From {salary_from} {currency}"
                elif salary_to:
                    return f"Up to {salary_to} {currency}"
            
            # For other dictionary formats (where 'from'/'to' might not exist)
            currency = salary_data.get('currency', 'PLN')
            return "Undisclosed"
                
        # Default fallback
        return str(salary_data)
    except Exception as e:
        print(f'Error formatting salary: {str(e)}')
        return "Salary not specified"

# Define ASCII-safe headers
headers = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://nofluffjobs.com/',
    'Origin': 'https://nofluffjobs.com',
    'Connection': 'keep-alive',
}

cookies = {
    'nfj_new_user': 'true',
    'nfj_consents': '{%22consent_initialized%22:false%2C%22consent_analytics_storage%22:false%2C%22consent_ad_storage%22:false%2C%22consent_functionality_storage%22:false}',
    'country_iso': 'PL',
}

params = {
    'pageTo': '1',
    'pageSize': '20',
    'withSalaryMatch': 'true',
    'salaryCurrency': 'PLN',
    'salaryPeriod': 'month',
    'region': 'pl',
    'language': 'en-US',
}

try:
    # Initial test request
    response = make_request_with_retry('https://nofluffjobs.com/api/joboffers/main', params=params, cookies=cookies, headers=headers)
    data = response.json()

    nofluff_data = []
    desc_data_arr = []

    for pageNum in range(1, 5):  # Scrape 4 pages
        params['pageTo'] = pageNum
        headers['referer'] = "https://nofluffjobs.com/"
        
        try:
            response = make_request_with_retry('https://nofluffjobs.com/api/joboffers/main', params=params, cookies=cookies, headers=headers)
            data = response.json()
            
            for posting in data["postings"]:
                try:
                    job_desc_url = f"https://nofluffjobs.com/job/{posting['url']}"
                    safe_headers = headers.copy()
                    safe_headers['Referer'] = job_desc_url
                    desc_param = {
                        'salaryCurrency': 'PLN',
                        'salaryPeriod': 'month',
                        'region': 'pl',
                        'language': 'en-US',
                    }
                    
                    # Add delay between requests
                    time.sleep(random.uniform(1, 3))
                    
                    response = make_request_with_retry(
                        f"https://nofluffjobs.com/api/posting/{posting['url']}", 
                        params=params, 
                        headers=safe_headers
                    )
                    desc_data = response.json()

                    desc_data_arr.append(desc_data)

                    expiresAt = desc_data.get("expiresAt", None)

                    nofluff_data.append({
                        "title": posting["title"],
                        "logo": posting.get("logo", {}).get("original", ""),
                        "salary_range": format_salary(posting.get("salary", {})),
                        "location": posting.get("location", ""),
                        "company": posting.get("name", ""),
                        "must_haves": posting.get("tiles", {}).get("values", []),
                        "job_post_url": f"https://nofluffjobs.com/job/{posting['url']}",
                        "region": posting.get("regions", [""])[0] if posting.get("regions") else "",
                        "expiresAt": expiresAt,
                        "full_description": desc_data.get("requirements", {}).get("description", ""),
                        "responsibilities": desc_data.get("specs", {}).get("dailyTasks", ""),
                    })
                    print(f"Successfully processed job: {posting['title']}")
                    
                except Exception as e:
                    print(f"Error processing job {posting.get('title', 'Unknown')}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error processing page {pageNum}: {str(e)}")
            continue

    # Save the data
    with open("desc_data.json", "w", encoding="utf-8") as file:
        json.dump(desc_data_arr[0] if desc_data_arr else {}, file, indent=4)

    with open("nofluff_data.json", "w", encoding="utf-8") as file:
        print("Items scraped:", len(nofluff_data))
        json.dump(nofluff_data, file, indent=4)

    with open("nofluff_response.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

except Exception as e:
    print(f"Fatal error: {str(e)}")
    raise
