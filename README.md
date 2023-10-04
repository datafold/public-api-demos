# public-sapi-demo

## Description
Demo to show how to use the Datafold API to run data diffs in CI pipelines in all kinds of ways.


## Example 1: Running Datafold Cloud in a Jenkins Pipeline

### Tech Stack
- dbt Cloud
- BigQuery
- Datafold
- python 3.9.6
- Jenkins (as reference)

### Run Locally

```shell
# setup python venv
pip install --upgrade pip
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
source venv/bin/activate

### test in a personal repo
git clone https://github.com/sungchun12/dbt_bigquery_example.git
cd dbt_bigquery_example
git checkout demo/bigquery-pr
```

```shell
# add these Datafold configs to your `dbt_project.yml`
```

```shell
# export env vars for a local run
# you'll inject these in the jenkins file, these are exported locally for testing
export DBT_CLOUD_PRODUCTION_JOB_ID=<your_dbt_cloud_job_id>
export DATAFOLD_API_KEY=<your_datafold_api_key>
export DBT_CLOUD_API_TOKEN=<your_dbt_cloud_api_token>
export DATA_SOURCE_ID=<your_data_source_id>
```

```shell
# run the script
python ../datafold_ci.py

Getting latest job run artifacts [manifest.json] for job id: 428271
File written to: /Users/sung/api-demo/dbt_bigquery_example/manifest.json
Getting latest job run artifacts [run_results.json] for job id: 428275
File written to: /Users/sung/api-demo/dbt_bigquery_example/target/run_results.json
Getting latest job run artifacts [manifest.json] for job id: 428275
File written to: /Users/sung/api-demo/dbt_bigquery_example/target/manifest.json
Running with data-diff=0.8.4 (Update 0.9.1 is available!)
Cloud datafold host: https://app.datafold.com
Saving the API key to the system keyring service

Diffs in progress...


dbt-demo-386220.dbt_sung_prod.order_payments <> 
dbt-demo-386220.dbt_cloud_pr_ALPHANUMERIC_CHANGE_BRANCH_CHANGE_ID_BUILD_NUMBER_428275.order_payments 
Skipped due to unknown primary key. Add uniqueness tests, meta, or tags.

fct_orders: https://app.datafold.com/datadiffs/2262836/overview
stg_orders: https://app.datafold.com/datadiffs/2262837/overview
stg_payments: https://app.datafold.com/datadiffs/2262838/overview

dbt-demo-386220.dbt_sung_prod.fct_orders <> 
dbt-demo-386220.dbt_cloud_pr_ALPHANUMERIC_CHANGE_BRANCH_CHANGE_ID_BUILD_NUMBER_428275.fct_orders 

https://app.datafold.com/datadiffs/2262836/overview
 
  Rows Added    Rows Removed
------------  --------------
          10               0

Updated Rows: 0
Unchanged Rows: 10

Value Match Percent: 


dbt-demo-386220.dbt_sung_prod.stg_orders <> 
dbt-demo-386220.dbt_cloud_pr_ALPHANUMERIC_CHANGE_BRANCH_CHANGE_ID_BUILD_NUMBER_428275.stg_orders 

https://app.datafold.com/datadiffs/2262837/overview
No row differences



dbt-demo-386220.dbt_sung_prod.stg_payments <> 
dbt-demo-386220.dbt_cloud_pr_ALPHANUMERIC_CHANGE_BRANCH_CHANGE_ID_BUILD_NUMBER_428275.stg_payments 

https://app.datafold.com/datadiffs/2262838/overview
No row differences

```