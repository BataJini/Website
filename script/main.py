import asyncio
# from curl_cffi import AsyncSession
import curl_cffi
import json
from lxml import html
import time

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
            return f"Salary in {currency}"
                
        # Default fallback
        return str(salary_data)
    except Exception as e:
        print(f'Error formatting salary: {str(e)}')
        return "Salary not specified"

# Define ASCII-safe headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://nofluffjobs.com/',
    'Origin': 'https://nofluffjobs.com',
    'Connection': 'keep-alive',
}

cookies = {
    'nfj_new_user': 'true',
    'nfj_abt': 'salaryMatchCopy%2C0%2C0',
    'nfj_consents': '{%22consent_initialized%22:false%2C%22consent_analytics_storage%22:false%2C%22consent_ad_storage%22:false%2C%22consent_functionality_storage%22:false}',
    'AMP_MKTG_53ff6cd964': 'JTdCJTdE',
    'lastSearches': 'false',
    'nfj_visited_pl': 'true',
    'country_iso': 'IN',
    'nfj_session_id': '8ad5107f-48e3-4c3f-aace-18f940c1981a.1742462162589',
    'AMP_53ff6cd964': 'JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI4YWQ1MTA3Zi00OGUzLTRjM2YtYWFjZS0xOGY5NDBjMTk4MWElMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzQyNDYyMTYyNTg5JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlN0Q=',
    'nfj_last': '1742462162631',
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

response = curl_cffi.get('https://nofluffjobs.com/api/joboffers/main', params=params, cookies=cookies, headers=headers)
data = response.json()

nofluff_data = []
desc_data_arr = []

for pageNum in range(1, 5):  # Increase to scrape 4 pages instead of 1
    params['pageTo'] = pageNum
    headers['referer'] = "https://nofluffjobs.com/"
    response = curl_cffi.get('https://nofluffjobs.com/api/joboffers/main', params=params, cookies=cookies, headers=headers)
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
            response = curl_cffi.get(f"https://nofluffjobs.com/api/posting/{posting['url']}", params=params, headers=safe_headers)
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
        except Exception as e:
            print(f"Error processing job {posting.get('title', 'Unknown')}: {str(e)}")
            continue

with open("desc_data.json", "w", encoding = "utf-8") as file:
    json.dump(desc_data_arr[0], file, indent=4)

with open("nofluff_data.json", "w", encoding="utf-8") as file:
    print("items scraped", len(nofluff_data))
    json.dump(nofluff_data, file, indent=4)

with open("nofluff_response.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)
