#!/usr/bin/python3

import json
import requests
import sys
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

        data = response.json()
        company_nodes = data['result']['data']['allSanityCompanyPage']['nodes']

        for node in company_nodes:
            if node['title'] in companies_dict:
                print_error(f"Duplicate company name: {node['title']}, not overwriting (from {url})")
            else:
                companies_dict[node['title']] = node

    except requests.RequestException as e:
        print_error(f"Error fetching data: {e}")


def fetch_company_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

        data = response.json()
        company_json = data['result']['data']['sanityCompanyPage']

        return company_json

    except requests.RequestException as e:
        print_error(f"Error fetching data: {e}")


def add_details_from_path(companies_dict, timestamp):
    counter = 0

    for company_name in sorted(companies_dict.keys()):
        counter += 1
        if counter > 5:
            break
        companies_dict[company_name]['fetched_at'] = timestamp
        print_message(f'Getting path data for {company_name}')
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


def enrich_companies_from_dict(companies_dict, data, file_name, file_type, line_counter):
    company_name = data['name']
    if company_name not in companies_dict:
        return False
    if companies_dict[company_name].get('details_from_' + file_type):
        print_message(f'Duplicate company name: {company_name}, in {file_type}, not overwriting ({file_name}, line number: {line_counter})')
        return False
    companies_dict[company_name]['details_from_org_file'] = data
    return True


def enrich_companies_from_org_file(org_filename, companies_dict):
    counter = 0
    line_counter = 0
    print("### Here is the first 3 lines of the org file")
    with open(org_filename, 'r') as file:
        for line in file:
            line_counter += 1
            data = json.loads(line)
            updated = enrich_companies_from_dict(companies_dict, data, org_filename, 'org_file', line_counter)
            if updated:
                counter += 1
                if counter > 500:
                    break


def enrich_companies_from_funding_file(funding_filename, companies_dict):
    pass  # TODO implement


def output_result(companies_dict):
    print_message(f'Number of companies: {len(companies_dict)}')
    counter = 0
    for company in sorted(companies_dict.keys()):
        counter += 1
        if counter > 20:
            break
        print(json.dumps(companies_dict[company]))
        print()


def print_message(message):
    print(f'###: {message}')


def now_as_string():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M.%S")


def print_error(message):
    print(f'### ERROR: {message}')


def print_usage():
    print("Usage: ./enrich_company_data.py <org filename> <funding filename>")


def main(org_filename, funding_filename):
    companies_dict = dict()
    fetch_companies_json(CURRENT_PORTFOLIO, companies_dict)
    fetch_companies_json(DIVESTMENTS, companies_dict)

    add_details_from_path(companies_dict, now_as_string())

    enrich_companies_from_org_file(org_filename, companies_dict)
    enrich_companies_from_funding_file(funding_filename, companies_dict)

    output_result(companies_dict)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print_usage()
        exit(1)

    org_file = sys.argv[1]
    funding_file = sys.argv[2]
    print_message(f'Started at: {now_as_string()}')
    print_message(f'Using org file: {org_file}, funding file: {funding_file}')
    main(org_file, funding_file)
