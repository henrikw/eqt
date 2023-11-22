# EQT
## Enrich company data

## How the program works:

It starts by fetching company data from the EQT Group website (both current and divestments).
This forms the basis for the company data. Then there are three different ways in which
the company data is enriched: fetching details using the path to create the URL,
then looping through the org data file to find matches, and finally looping through
the funding data file to find matches. 

If extra data exists in any of these places, it is added under the keys `details_from_url`,
`details_from_org_file` and `details_from_funding_file` respectively. Note, only the first
match is used, subsequent matches are ignored.

Finally, it prints the enriched company data as JSON to stdout (sorted in alphabetical order of the
company names).

Logging is enabled by default, so you see that the program is making progress (it takes
a bit over a minute to run).

## Setting up and running the program:

Check out the code from GitHub:

```
git clone git@github.com:henrikw/eqt.git
cd eqt
```

Create and activate a virtual environment:
```
python3 -m venv env
. env/bin/activate
```

Install dependencies (requests and pytest):
```
pip install -r requirements.txt
```

### To run tests:

```     
pytest test_enrich_company_data.py
```

### To run the program:

```
# Copy the two json files below to the eqt directory, then run:
./enrich_company_data.py interview-test-org.json interview-test-funding.json
```
## Future improvements

There are many duplicated records in the data. It needs to be investigated why this is,
and possibly combine the data from the different records into one record. For now, only
the first record is used.

The opposite may also exist - two different companies with the same name. This will need
to be investigated on a case by case basis, or some heuristics may be used to determine
if they are different, and then create two entries.

Also, there may be name mismatches - i.e. it is the same company, but its name
is spelt slightly differently in different places. It is possible to add fuzzy matching to find matches.

Can probably use uuid/org_uuid to match - seems to be the same for the same company name in the different files.

Can add tests that read a small file (both or org and funding types) and checks that the complete output is correct.

Can add a command line flag that enables/disables logging printouts.

Better error handling when reading files - e.g. if content not JSON.

Can add more tests for the logic in the fetch-functions. However, these tests will
never be able to detect if the format of the data changes on the EQT website. Therefore, it
is also important to have logging that can detect unexpected results when
fetching data from the website.
