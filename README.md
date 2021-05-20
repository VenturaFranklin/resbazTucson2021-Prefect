# Prefect for data pipelines in Python
Workshop materials for Prefect for data pipelines in Python for the Research Bazaar Tucson, AZ 2021

#### Presentation
[<img src="docs/PresentationTitle.png" width="25%" height="25%" />](Presentation.pdf)

# Setup
0. Install Python 3.6+
    - Optionally: Install Docker with docker compose
1. Setup a virtual environment
2. Run in your environment: 
    
    `pip install -r requirements.txt`

3. Download the data using the [get_data.sh](get_data.sh)
4. If you will work with the Prefect server start the download of the server Docker files
    - `prefect backend server`
    - `prefect server start`

## Workshop: Getting started with Prefect
1. Starting with [pipeline.py](pipeline.py) first convert functions to Prefect tasks and create a Prefect flow.
    - Solution is [pipeline_prefect.py](solutions/pipeline_prefect.py)
#### Flow visualization serial
[<img src="docs/flow_serial.png" width="25%" height="25%" />](docs/flow_serial.png)

2. Building on the pipeline_prefect solution, parallelize tasks in flow.
    - Solution is [pipeline_prefect_parallel.py](solutions/pipeline_prefect_parallel.py)

#### Flow visualization parallel
[<img src="docs/flow_parallel.png" width="25%" height="25%" />](docs/flow_parallel.png)

3. Building on the pipeline_prefect_parallel solution, change executor to LocalDaskExecutor
    - Solution is [pipeline_prefect_parallel.py](solutions/pipeline_prefect_parallel.py)
4. Building on the pipeline_prefect_parallel solution, set up Prefect server running
    - Solution is [pipeline_prefect_parallel_server.py](solutions\pipeline_prefect_parallel_server.py)

#### Flow visualization parallel in Prefect Server
[<img src="docs/flow_schematic.png" width="25%" height="25%" />](docs/flow_schematic.png)

#### Flow timeline in Prefect Server
[<img src="docs/flow_timeline.png" width="50%" height="50%" />](docs/flow_timeline.png)


## Notes for running comparison
A comparison of running the pipeline with different configurations. 

While the pure Python implementations are certainly faster, the benefits that Prefect provides in orchestration, monitoring, logging, etc are worth the extra execution time. There are also likely other optimizations that can be done.

Script  |       Type         | Execution Time   | File Run
------- |--------------------|------------------|----------
Prefect |    Parallel        | 20 seconds       | [pipeline_prefect_parallel.py](solutions/pipeline_prefect_parallel.py)
Prefect |    Parallel Dask   | 10 seconds       | [pipeline_prefect_parallel.py](solutions/pipeline_prefect_parallel.py)
Prefect |    Serial          | 23 seconds       | [pipeline_prefect.py](solutions/pipeline_prefect.py)
Python  |    Serial          | 15 seconds       | [pipeline.py](pipeline.py)
Python  |    Parallel        | 6 seconds        | [pipeline_parallel.py](pipeline_parallel.py)

## Prefect Setup for Server

Commands to get started with Prefect server running locally.

```
prefect backend server

prefect create project "Image QC"

# Run next two commands in separate terminals

prefect server start

prefect agent local start
```
