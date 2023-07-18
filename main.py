from contextlib import redirect_stderr
from idlelib.debugger_r import restart_subprocess_debugger

import requests
import fake_headers
import bs4
import re
import json

from pkg_resources import safe_name

headers = fake_headers.Headers(browser='firefox', os='win')
headers_dict = headers.generate()
response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=headers_dict)
html = response.text
soup = bs4.BeautifulSoup(html, 'lxml')
main_div = soup.find('div', id='a11y-main-content')

result = {}
items_div = main_div.find_all('div', class_="vacancy-serp-item__layout")
# print(f'Всего найдено - {len(items_div)}')
for item_ in items_div:
    h3_name_a_tag = item_.find('h3', class_="bloko-header-section-3")
    a_tag_vacancy = h3_name_a_tag.find('a')
    company_tag = item_.find('div', class_="vacancy-serp-item-company")
    company_text = company_tag.find('div', class_="vacancy-serp-item__meta-info-company")
    company_name = company_text.find('a').text
    link = a_tag_vacancy['href']
    name = a_tag_vacancy.text
    salary_tag = item_.find('span', class_="bloko-header-section-3")
    salary_min = 0
    salary_max = 0
    currency = ''
    town_text = ''
    if salary_tag is not None:
        salary_text = salary_tag.text
        if salary_text[:2] == 'от':
            salary_min = ''.join(re.findall(r'\S+', salary_text[2:].strip()))
            currency = salary_min[-1]
            salary_min = salary_min[:-1]
        elif salary_text[:2] == 'до':
            salary_max = ''.join(re.findall(r'\S+', salary_text[2:].strip()))
            currency = salary_max[-1]
            salary_max = salary_max[:-1]
        else:
            salary_min = salary_text[:salary_text.find('–')].strip()
            salary_min = ''.join(salary_min.split())
            salary_max = salary_text[salary_text.find('–')+1:-1].strip()
            salary_max = ''.join(salary_max.split())
            currency = salary_text[-1]
        # print(salary_text, salary_min, salary_max, currency)
    sub_html = requests.get(link, headers=headers.generate()).text
    sub_soup = bs4.BeautifulSoup(sub_html, 'lxml')
    key_div = sub_soup.find('div', class_="bloko-tag-list")
    key_words = []
    if key_div is not None:
        keys_divs = key_div.find_all('div', class_="bloko-tag bloko-tag_inline")
        key_words = []
        for key in keys_divs:
            key_words.append(key.find('span').text)
    # print(name, key_words)
    if 'Django' in key_words or 'Flask' in key_words:
        town_tag = sub_soup.find('div', class_="vacancy-company-redesigned")
        if town_tag is not None:
            town = town_tag.find('p')
            if town is not None:
                town_text = town.text
        result[link] = {'Vacancy_name': name, 'Company_name': company_name, 'salary': [salary_min, salary_max, currency], 'city': town_text}
print(result)

with open('result.json','w') as f:
    json.dump(result, f)