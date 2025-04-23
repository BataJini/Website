import json

def extract_company_links():
    # Read nofluff_data.json
    with open('script/nofluff_data.json', 'r', encoding='utf-8') as f:
        nofluff_data = json.load(f)
    
    # Extract company links
    company_links = []
    for job in nofluff_data:
        if 'company' in job and 'job_post_url' in job:
            company_links.append({
                'company': job['company'],
                'url': job['job_post_url']
            })
    
    # Print first 15 unique company links
    seen_companies = set()
    print("\nCompany Links from nofluff_data.json:")
    for link in company_links:
        if link['company'] not in seen_companies:
            print(f"Company: {link['company']}")
            print(f"URL: {link['url']}")
            print("-" * 50)
            seen_companies.add(link['company'])
            if len(seen_companies) >= 15:
                break

if __name__ == "__main__":
    extract_company_links() 