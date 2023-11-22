#!/usr/bin/python3

import pytest

from enrich_company_data import enrich_companies_from_url, enrich_companies_from_dict

# From URL


def test_enrich_companies_from_url__no_path():
    def mock_url_fetcher(url):
        return {'not_stored': 'a_value'}

    timestamp = '2023-11-22 15:21.29'
    companies_dict = {'Company-A': {}}
    enrich_companies_from_url(companies_dict, timestamp, fetcher=mock_url_fetcher)
    assert companies_dict['Company-A'] == {
        'details_from_url': 'No url for company Company-A',
        'url_fetched_at': timestamp
    }


def test_enrich_companies_from_url__with_path_but_no_details():
    def mock_url_fetcher(url):
        return {}

    timestamp = '2023-11-22 15:21.29'
    companies_dict = {'Company-A': {'path': '/company-a/'}}
    enrich_companies_from_url(companies_dict, timestamp, fetcher=mock_url_fetcher)
    print(companies_dict)
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
        'details_from_url': 'No details from for company Company-A with url https://eqtgroup.com/page-data/company-a/page-data.json',
        'url_fetched_at': timestamp
    }


def test_enrich_companies_from_url__with_path_and_details():
    def mock_url_fetcher(url):
        return {'website': 'https://campany-a.com', 'not_stored': 'a_value'}

    timestamp = '2023-11-22 15:21.29'
    companies_dict = {'Company-A': {'path': '/company-a/'}}
    enrich_companies_from_url(companies_dict, timestamp, fetcher=mock_url_fetcher)
    print(companies_dict)
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
        'details_from_url': {'website': 'https://campany-a.com'},
        'url_fetched_at': timestamp
    }


# From org file


def test_enrich_companies_from_dict__org_file_no_match():
    companies_dict = {'Company-A': {'path': '/company-a/'}}
    data_dict = {'name': 'Company-B', 'country_code': 'USA', 'founded_on': '2021-04-11'}
    added, msg = enrich_companies_from_dict(companies_dict, data_dict, 'org_file', 'name')
    assert added is False
    assert msg is None
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
    }


def test_enrich_companies_from_dict__org_file_match():
    companies_dict = {'Company-A': {'path': '/company-a/'}}
    data_dict = {'name': 'Company-A', 'country_code': 'USA', 'founded_on': '2021-04-11'}
    added, msg = enrich_companies_from_dict(companies_dict, data_dict, 'org_file', 'name')
    assert added is True
    assert msg is None
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
        'details_from_org_file': {'name': 'Company-A', 'country_code': 'USA', 'founded_on': '2021-04-11'},
    }


def test_enrich_companies_from_dict__org_file_duplicate():
    companies_dict = {'Company-A': {'path': '/company-a/', 'details_from_org_file': {'name': 'Company-A', 'country_code': 'SE', 'founded_on': '2019-05-22'}}}
    data_dict = {'name': 'Company-A', 'country_code': 'USA', 'founded_on': '2021-04-11'}
    added, msg = enrich_companies_from_dict(companies_dict, data_dict, 'org_file', 'name')
    assert added is False
    assert msg == 'Duplicate company name: Company-A, not overwriting'
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
        'details_from_org_file': {'name': 'Company-A', 'country_code': 'SE', 'founded_on': '2019-05-22'},
    }


# From funding file


def test_enrich_companies_from_dict__funding_file_no_match():
    companies_dict = {'Company-A': {'path': '/company-a/'}}
    data_dict = {'org_name': 'Company-B', 'investor_count': 1, 'founded_on': '2021-04-11'}
    added, msg = enrich_companies_from_dict(companies_dict, data_dict, 'funding_file', 'org_name')
    assert added is False
    assert msg is None
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
    }


def test_enrich_companies_from_dict__funding_file_match():
    companies_dict = {'Company-A': {'path': '/company-a/'}}
    data_dict = {'org_name': 'Company-A', 'investor_count': 1, 'founded_on': '2021-04-11'}
    added, msg = enrich_companies_from_dict(companies_dict, data_dict, 'funding_file', 'org_name')
    assert added is True
    assert msg is None
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
        'details_from_funding_file': {'org_name': 'Company-A', 'investor_count': 1, 'founded_on': '2021-04-11'},
    }


def test_enrich_companies_from_dict__funding_file_duplicate():
    companies_dict = {'Company-A': {'path': '/company-a/', 'details_from_funding_file': {'org_name': 'Company-A', 'investor_count': 1, 'founded_on': '2021-04-11'}}}
    data_dict = {'org_name': 'Company-A', 'investor_count': 5, 'founded_on': '2023-11-22'}
    added, msg = enrich_companies_from_dict(companies_dict, data_dict, 'funding_file', 'org_name')
    assert added is False
    assert msg == 'Duplicate company name: Company-A, not overwriting'
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
        'details_from_funding_file': {'org_name': 'Company-A', 'investor_count': 1, 'founded_on': '2021-04-11'},
    }
