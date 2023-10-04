import json
import requests
import os
import subprocess

API_KEY = os.getenv("DBT_CLOUD_API_TOKEN")
ACCOUNT_ID = os.getenv("DBT_CLOUD_ACCOUNT_ID")
PRODUCTION_JOB_ID = os.getenv("DBT_CLOUD_PRODUCTION_JOB_ID")

# get schema override from dbt Cloud pull request job run
JOB_ID = os.getenv("DBT_CLOUD_JOB_ID")  # pull request job
ALPHANUMERIC_CHANGE_BRANCH = os.getenv("ALPHANUMERIC_CHANGE_BRANCH")
CHANGE_ID = os.getenv("CHANGE_ID")
CHANGE_BRANCH = os.getenv("CHANGE_BRANCH")
BUILD_NUMBER = os.getenv("BUILD_NUMBER")
SCHEMA_OVERRIDE = (
    f"dbt_cloud_pr_{ALPHANUMERIC_CHANGE_BRANCH}_{CHANGE_ID}_{BUILD_NUMBER}_{JOB_ID}"
)

env_vars = os.environ.copy()
env_vars["SCHEMA_OVERRIDE"] = SCHEMA_OVERRIDE


def main():
    # download production job manifest.json
    get_job_run_id_artifacts(PRODUCTION_JOB_ID, artifact_name="manifest.json")
    # download pull request job run_results.json to know which dbt nodes to run
    get_job_run_id_artifacts(JOB_ID, artifact_name="run_results.json", path="./target/")
    # get pull request job manifest.json
    get_job_run_id_artifacts(JOB_ID, artifact_name="manifest.json", path="./target/")
    # run Datafold Cloud data diff and point to the production manifest.json to compare against
    subprocess.run(
        ["data-diff", "--dbt", "--cloud", "--state", "manifest.json"],
        env=env_vars,
        check=True,
    )


def get_job_run_id_artifacts(job_id, artifact_name="manifest.json", path="./") -> None:
    print(f"Getting latest job run artifacts [{artifact_name}] for job id: {job_id}")

    remainder = artifact_name
    res = requests.get(
        url=f"https://cloud.getdbt.com/api/v2/accounts/{ACCOUNT_ID}/jobs/{job_id}/artifacts/{remainder}",
        headers={"Authorization": f"Token {API_KEY}", "Accept": "text/html"},
    )

    try:
        res.raise_for_status()
    except:
        print(f"API token (last four): ...{API_KEY[-4:]}")
        raise

    response_payload = res.json()

    # Create the directory if it doesn't exist
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, artifact_name), "w") as outfile:
        json.dump(response_payload, outfile)
        print(f"File written to: {os.path.abspath(outfile.name)}")


if __name__ == "__main__":
    main()
