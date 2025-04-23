import curl_cffi
from lxml import html
import json

url = "https://justjoin.it/job-offers/all-locations?with-salary=yes"

response = curl_cffi.get(url, impersonate="chrome")

data = []

if response.status_code == 200:
    tree = html.fromstring(response.content)
    divs = tree.xpath(".//div[@data-index]")

    for div in divs:
        try:
            posting_url = div.xpath("./div/div/a/@href")
            if not posting_url:
                continue
            posting_url = f"https://justjoin.it{posting_url[0]}"

            logo_url = div.xpath(".//img/@src")
            logo_url = logo_url[0] if logo_url else None

            job_data_div = div.xpath("./div/div/div[2]")
            if not job_data_div:
                continue

            job_title = job_data_div[0].xpath(".//h3/text()")
            job_title = job_title[0] if job_title else "No Title"

            salary_div = job_data_div[0].xpath(".//div[contains(@class, 'salary') or div[contains(text(),'PLN')]]")
            salary = salary_div[0].xpath(".//span/text()") if salary_div else []

            location_div = div.xpath(".//svg[contains(@data-testid,'PlaceOutlinedIcon')]/following-sibling::div/span/text()")
            location = location_div[0] if location_div else "Remote"

            data.append({
                "job_post_url": posting_url,
                "logo": logo_url,
                "title": job_title,
                "salary": salary,
                "location": location
            })
        except Exception as e:
            print(f"Error parsing job div: {e}")
            continue

print("Appended initial data:", len(data))

for d in data:
    try:
        print("Getting data for", d["job_post_url"])
        response = curl_cffi.get(d["job_post_url"], impersonate="chrome")
        if response.status_code != 200:
            continue

        tree = html.fromstring(response.content)

        # Extract position details
        position_details = tree.xpath('//div[@class="MuiBox-root css-ktfb40"]/text()')
        if len(position_details) >= 4:
            d["type_of_work"] = position_details[0]
            d["experience"] = position_details[1]
            d["employment_type"] = position_details[2]
            d["operating_type"] = position_details[3]
        else:
            d["type_of_work"] = d["experience"] = d["employment_type"] = d["operating_type"] = "N/A"

        d["position_details"] = position_details

        # Tech stack
        ul_list = tree.xpath('//ul[@class="css-vdxqko"]')
        tech_stack = [l.xpath(".//h4/text()") for l in ul_list]
        d["tech_stack"] = tech_stack[0] if tech_stack else []

        # Description
        desc_tags = tree.xpath("//div[@class='MuiBox-root css-16nvqld']")
        if len(desc_tags) > 1:
            desc_tag = desc_tags[1]
            p_tags = desc_tag.xpath(".//p/text()")
            li_tags = desc_tag.xpath(".//li/text()")
            p_text = [text.strip() for text in p_tags if text.strip()]
            li_text = [text.strip() for text in li_tags if text.strip()]
            desc_text = p_text + li_text
            d["description"] = desc_text
        else:
            d["description"] = []

    except Exception as e:
        print(f"Error fetching details for {d['job_post_url']}: {e}")
        continue

# Save to JSON
with open("justjoin_it.json", "w", encoding="utf-8") as file:
    print("Items scraped:", len(data))
    json.dump(data, file, indent=4, ensure_ascii=False)
