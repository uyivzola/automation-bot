from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from bs4 import BeautifulSoup


class OrgInfoScraper:
    def __init__(self, input_file, output_file, max_workers=16):
        self.input_file = input_file
        self.output_file = output_file
        self.max_workers = max_workers
        self.df = pd.read_excel(self.input_file)
        self.df['Location'] = None

    def fetch_location(self, client_inn):
        url = f"https://orginfo.uz/en/search/all/?q={client_inn}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                location_tag = soup.find('p', class_='text-body-tertiary mb-0')
                if location_tag:
                    return client_inn, location_tag.get_text(strip=True)
        except Exception as e:
            print(f"Error fetching data for {client_inn}: {e}")
        return client_inn, None

    def process_row(self, index, row):
        client_inn = row['ClientINN']
        return index, self.fetch_location(client_inn)

    def scrape_locations(self):
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.process_row, index, row) for index, row in self.df.iterrows()]
            for future in as_completed(futures):
                index, (client_inn, location) = future.result()
                if location:
                    self.df.at[index, 'Location'] = location

    def save_to_excel(self):
        self.df.to_excel(self.output_file, index=False)

    def run(self):
        self.scrape_locations()
        self.save_to_excel()


if __name__ == "__main__":
    input_file = 'client_inn.xlsx'
    output_file = 'updated_excel_file.xlsx'
    scraper = OrgInfoScraper(input_file, output_file)
    scraper.run()
