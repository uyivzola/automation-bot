import requests
from bs4 import BeautifulSoup
import os, re

# Base URL
base_url = "https://fom.uz/en/org"

# Create a folder to store downloaded files
folder_path = "price_lists_companies"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


async def sanitize_filename(file_name):
    # Remove "OOO" and numbers from the filename
    file_name = re.sub(r'OOO|\d+', '', file_name)
    # Replace other invalid characters with underscores
    invalid_chars = '[<>:"/\\|?*]'
    sanitized_filename: str = re.sub(invalid_chars, '', file_name)
    return await sanitized_filename.strip('_')


async def extract_data_from_page(url, update, context):
    chat_id = update.message.chat_id

    # Send HTTP request
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        # Find all company blocks
        company_blocks = soup.find_all("div", class_="block company-list")
        # Loop through each company block
        for company_block in company_blocks:
            # Extract company details
            company_name = company_block.find("div", class_="title").text.strip()
            company_name = sanitize_filename(company_name)
            # Check if the download link exists
            download_link_tag = company_block.find("div", class_="price").find("a")
            if download_link_tag:
                download_link = download_link_tag["href"]
                # Get the file extension from the download link
                file_extension = os.path.splitext(download_link)[1]
                # Download price file
                price_response = requests.get(download_link)
                if price_response.status_code == 200:
                    filename = f"{company_name}{file_extension}"
                    with open(os.path.join(folder_path, filename), "wb") as f:
                        f.write(price_response.content)
                        await context.bot.send_document(chat_id, document=filename, caption=company_name.title())
            else:
                print(f"No download link found for {company_name}")
        # Find next page link if exists
        next_page_link = soup.find("li", class_="next").find("a")
        if next_page_link:
            # Remove the duplicated "/en/org" part from the next page URL
            next_page_url = url.split("/en/org")[0] + next_page_link["href"]
            # Recursively extract data from the next page
            await extract_data_from_page(next_page_url)
    else:
        print(f"Failed to retrieve data from the page: {url}")


# Start extracting data from the base URL
extract_data_from_page(base_url)
