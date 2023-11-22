#!/usr/bin/python3 -u

import json
import requests
import sys
from datetime import datetime

BASE_URL = "https://eqtgroup.com/page-data"
TAIL_URL = "page-data.json"

CURRENT_PORTFOLIO = BASE_URL + "/current-portfolio/" + TAIL_URL
DIVESTMENTS = BASE_URL + "/current-portfolio/divestments/" + TAIL_URL


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


def enrich_companies_from_url(companies_dict, timestamp, fetcher=fetch_company_json):
    # Using a fetcher function to make it easier to mock it in unit tests.
    details_key = 'details_from_url'
    for company in sorted(companies_dict.keys()):
        companies_dict[company]['url_fetched_at'] = timestamp
        print_message(f'Getting url data for {company}')
        if companies_dict[company].get('path'):
            company_url = BASE_URL + companies_dict[company].get('path') + TAIL_URL
            company_details = fetcher(company_url)
            if not company_details:
                msg = f'No details from for company {company} with url {company_url}'
                print_message(msg)
                companies_dict[company][details_key] = msg
                continue
            details_from_url = dict()
            keys_to_extract = ['board', 'heading', 'management', 'preamble', 'website']
            for detail in company_details.keys():
                if detail in keys_to_extract:
                    details_from_url[detail] = company_details[detail]
            companies_dict[company][details_key] = details_from_url
        else:
            msg = f'No url for company {company}'
            print_message(msg)
            companies_dict[company][details_key] = msg


def enrich_companies_from_dict(companies_dict, data_dict, file_type, match_key):
    company_name = data_dict[match_key]
    if company_name not in companies_dict:
        return False, None
    details_key = 'details_from_' + file_type
    if companies_dict[company_name].get(details_key):
        return False, f'Duplicate company name: {company_name}, not overwriting'
    companies_dict[company_name][details_key] = data_dict
    return True, None


def enrich_companies_from_file(file_name, companies_dict, file_type, match_key):
    counter = 0
    line_counter = 0
    with open(file_name, 'r') as file:
        for line in file:
            line_counter += 1
            data = json.loads(line)
            updated, msg = enrich_companies_from_dict(companies_dict, data, file_type, match_key)
            if msg:
                print_message(msg + f' ({file_name} ({file_type}), line number: {line_counter})')
            if updated:
                counter += 1
    print_message(f'Updated {counter} companies from {file_name}')


def output_result(companies_dict):
    print_message(f'Number of companies: {len(companies_dict)}')
    for company in sorted(companies_dict.keys()):
        print(json.dumps(companies_dict[company]))


def print_message(message):
    print(f'### {message}')


def now_as_string():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M.%S")


def print_error(message):
    print(f'### ERROR: {message}')


def print_usage():
    print("Usage: ./enrich_company_data.py <org filename> <funding filename>")


def main(org_filename, funding_filename):
    companies_dict = dict()  # Key: company name, value: company data (added in different steps below).

    fetch_companies_json(CURRENT_PORTFOLIO, companies_dict)
    fetch_companies_json(DIVESTMENTS, companies_dict)

    enrich_companies_from_url(companies_dict, now_as_string())

    enrich_companies_from_file(org_filename, companies_dict, 'org_file', 'name')
    enrich_companies_from_file(funding_filename, companies_dict, 'funding_file', 'org_name')

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
