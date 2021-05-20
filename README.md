# resbazTucson2021-Prefect
Workshop materials for Prefect for data pipelines in Python for the Research Bazaar Tucson, AZ 2021

# Setup
0. Python 3.6+
    - Optionally: Docker with docker compose
1. Setup a virtual environment
2. Run in your environment: 
    
    `pip install -r requirements.txt`

3. Download the data using the [get_data.sh](get_data.sh)
4. Is you will work with the server start the download of the server docker files
    - `prefect backend server`
    - `prefect server start`

## Notes for running comparison

Script | Type | Execution Time
-------|------|-----------------
Prefect |    Parallel        | 20 seconds
Prefect |    Parallel Dask   | 10 seconds
Prefect |    Serial          | 23 seconds
Python  |    Serial          | 15 seconds
Python  |    Parallel        | 6 seconds

## Prefect Setup for Server

prefect backend server

prefect create project "Image QC"

prefect server start

prefect agent local start

