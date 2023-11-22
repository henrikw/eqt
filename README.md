# eqt
## Enrich company data


### To run the script:

Create and activate a virtual environment:
. venv/bin/activate

```
pip install -r requirements.txt
```

### To run tests:

```     
pytest test_enrich_company_data.py
```

## Future improvements

There are many duplicated records in the data. It needs to be investigated why this is,
and possibly combine the data from the different records into one record. For now, only
the first record is used.

The opposite may also exist - two different companies with the same name. This will need
to be investigated on a case by case basis, or some heuristics may be used to determine
if they are different, and then create two entries.

Also, there may be name mismatches. It is possible to use fuzzy matching to find matches.

Can probably use uuid/org_uuid to match - seems to be the same for the same company name in the different files.
