from  DTOs.numberify import NumberifyDTO

import requests
from bs4 import BeautifulSoup
import json
import os


print('hello world')

numberifies = []

def scrape_table_to_json(url):
    # Fetch HTML content
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find the table
        table = soup.find('table')

        if table:
            countries = []

            items = soup.select('table tbody tr td:first-child  a:not([class])[title]')

            # for title in items:
            #     titles.append(title.get_text())


            rows = []
            for row in table.find_all('tr'):
                # Extract table cells
                country = row.select('td:first-child  a:not([class])[title]')
                # callingCode = row.select('td:nth-child(2)[rowspan] a[title]')
                callingCode = row.select('table tr td:nth-child(2)

                numberify = NumberifyDTO()

                isUsed = False

                if country: 
                    numberify.Country = [a.text.strip() for a in country]
                    isUsed = True
                if callingCode: 
                    numberify.CallingCode =  [a.text.strip() for a in callingCode]
                    isUsed = True

                if isUsed: numberifies.append(numberify)

            json_data = json.dumps([obj.__dict__ for obj in numberifies], indent=4)

            return json_data
        else:
            return "No table found on the webpage."
    else:
        return "Failed to fetch webpage. Status code: {}".format(response.status_code)


# Example usage
url = 'https://en.wikipedia.org/wiki/List_of_mobile_telephone_prefixes_by_country#Notes'
json_data = scrape_table_to_json(url)
# print(json_data)

file_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'text.txt')
with open(file_path, 'w') as file:
    file.write(json_data)
