#!/usr/bin/python3

import requests
from datetime import datetime

# Give input files as arguments
# TODO: need to pip install requests
# TODO: Add file to GitHub
# TODO: sort the output alphabetically
# TODO: How add good tests?
# curl https://eqtgroup.com/page-data/current-portfolio/funds/page-data.json
# https://eqtgroup.com/current-portfolio/funds/
# https://eqtgroup.com/current-portfolio/funds/eqt-vii/
# curl https://eqtgroup.com/page-data/current-portfolio/funds/eqt-vii/page-data.json

BASE_URL = "https://eqtgroup.com/page-data"
TAIL_URL = "page-data.json"

COMPANY_URL = "https://eqtgroup.com/page-data/current-portfolio/aig-hospitals/page-data.json"
CURRENT_PORTFOLIO = "https://eqtgroup.com/page-data/current-portfolio/page-data.json"
DIVESTMENTS = "https://eqtgroup.com/page-data/current-portfolio/divestments/page-data.json"


def fetch_companies_json(url, companies_dict):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

        # Parse JSON data
        data = response.json()
        company_nodes = data['result']['data']['allSanityCompanyPage']['nodes']

        for node in company_nodes:
            if node['title'] in companies_dict:
                print_error(f"Duplicate company name: {node['title']}, not overwriting")
            else:
                companies_dict[node['title']] = node

    except requests.RequestException as e:
        print_error(f"Error fetching data: {e}")


def fetch_company_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

        # Parse JSON data
        data = response.json()
        company_json = data['result']['data']['sanityCompanyPage']

        return company_json

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")


def add_details_from_path(companies_dict, timestamp):
    counter = 0

    for company_name in companies_dict.keys():
        counter += 1
        if counter > 5:
            break
        companies_dict[company_name]['fetched_at'] = timestamp
        print(company_name)
        if companies_dict[company_name].get('path'):
            company_url = BASE_URL + companies_dict[company_name].get('path') + TAIL_URL
            company_details = fetch_company_json(company_url)
            if not company_details:
                msg = f'No details for company {company_name}'
                print_error(msg)
                companies_dict[company_name]['details_from_path'] = msg
                continue
            details_from_path = dict()
            keys_to_extract = ['board', 'heading', 'management', 'preamble', 'website']
            for detail in company_details.keys():
                if detail in keys_to_extract:
                    details_from_path[detail] = company_details[detail]
            companies_dict[company_name]['details_from_path'] = details_from_path
        else:
            msg = f'No path for company {company_name}'
            print_error(msg)
            companies_dict[company_name]['details_from_path'] = msg


def print_error(message):
    print(f'### ERROR: {message}')


def main():
    companies_dict = dict()
    fetch_companies_json(CURRENT_PORTFOLIO, companies_dict)
    fetch_companies_json(DIVESTMENTS, companies_dict)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M.%S")
    add_details_from_path(companies_dict, timestamp)

    print(f'Number of companies: {len(companies_dict)}')


if __name__ == '__main__':
    main()

