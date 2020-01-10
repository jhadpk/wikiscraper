import requests
import datetime
import pandas as pd
from datetime import date, timedelta
from bs4 import BeautifulSoup


class WikiScraper:
    def scrape_url(self, url):
        html = requests.get(url)
        b = BeautifulSoup(html.text, 'lxml')
        for table in b.find_all(name='table', class_='wikitable', limit=1):
            df = self.parse_wiki_table(table)
        start_date = date(2019, 1, 1)
        end_date = date(2019, 12, 31)
        delta = timedelta(days=1)
        result = {}
        while start_date <= end_date:
            key = start_date.strftime("%Y-%m-%dT%H:%M:%S")
            if len(df[df.Date == key]) == 0:
                result[key] = 0
            else:
                result[key] = int(df[df.Date == key].Outcomes)
            start_date += delta
        self.write_to_csv(result)

    def parse_wiki_table(self, table):
        report = {}
        last_date = ''
        outcome = ["Successful", "Operational", "En route"]
        for row in table.find_all('tr'):
            cells = row.findAll(["td"])
            if len(cells) == 5:
                date_wiki = cells[0].getText().split("[")[0].strip()
                if date_wiki.find('(') != -1:
                    # 29th Aug has brackets
                    date_wiki = date_wiki.split('(')[0].strip()
                count_of_colon = date_wiki.count(':')
                # date format is not followed
                if count_of_colon == 0:
                    dt_format = '%d %B'
                elif count_of_colon == 1:
                    dt_format = '%d %B%H:%M'
                else:
                    dt_format = '%d %B%H:%M:%S'
                date_time_obj = datetime.datetime.strptime(date_wiki, dt_format)
                updated_date = date_time_obj.replace(year=2019, hour=0, minute=0, second=0, microsecond=0)
                last_date = str(updated_date.date()) + 'T' + str(updated_date.time())
            elif len(cells) == 6:
                count = report.get(last_date, 0)
                if cells[5].getText().split('[')[0].strip() in outcome:
                    count = count + 1
                    report[last_date] = count

        df = pd.DataFrame(report.items(), columns=['Date', 'Outcomes'])
        return df

    def write_to_csv(self, result):
        with open('output.csv', 'w') as file:
            for date_key, outcome in result.items():
                file.write(str(date_key) + "," + str(outcome) + "\n")


WikiScraper().scrape_url("https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches")
