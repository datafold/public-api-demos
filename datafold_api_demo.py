"""
Demo script to run a Datafold data diff in Snowflake with simple API calls
"""

import os
import time
from pydantic import BaseModel, field_validator
from typing import Any, List
import requests
from tabulate import tabulate
from termcolor import colored
from halo import Halo


# TODO: replace with your own Datafold API key and host URL
host = os.getenv("HOST_URL", "app.datafold.com")
datafold_api_key = os.getenv(
    "DATAFOLD_API_KEY"
)  # replace with your own Datafold API key

# TODO: replace with your own data diff configs
data_source1_id = 4932  # replace with your own data source id
data_source2_id = 4932  # replace with your own data source id
table1 = ["DEMO", "CORE", "DIM_ORGS"]
table2 = ["DEMO", "PR", "DIM_ORGS"]
pk_columns = ["ORG_ID"]  # replace with your own primary key columns


class DataDiffConfigs(BaseModel):
    data_source1_id: int
    data_source2_id: int
    table1: List[str]
    table2: List[str]
    pk_columns: List[str]

    @field_validator("table1", "table2")
    def validate_table(cls, value):
        if len(value) != 3:
            raise ValueError(
                'Exactly 3 objects are required for table1 and table2 inputs: ["DATABASE", "SCHEMA", "TABLE/VIEW NAME"]'
            )
        return value


data_diff_configs = DataDiffConfigs(
    data_source1_id=data_source1_id,
    data_source2_id=data_source2_id,
    table1=table1,
    table2=table2,
    pk_columns=pk_columns
)


class DataDiff:
    def __init__(
        self, host: str, datafold_api_key: str
    ):
        self.session = requests.Session()
        self.host = host
        self.session.headers["Authorization"] = f"Key {datafold_api_key}"

    def create_diff(self, data_diff_configs: DataDiffConfigs) -> int:
        resp = self.session.post(
            f"https://{self.host}/api/v1/datadiffs", json=data_diff_configs.model_dump()
        )
        resp.raise_for_status()
        data = resp.json()
        url = colored(f"https://{self.host}/datadiffs/{data['id']}", "blue")
        print(f"Started Datafold Data Diff: {url}")
        return data["id"]

    def get_diff_summary(self, id: int) -> dict[str, Any]:
        resp = self.session.get(
            f"https://{self.host}/api/v1/datadiffs/{id}/summary_results"
        )
        resp.raise_for_status()
        data = resp.json()
        return data

    def wait_for_results(self, id: int) -> dict[str, Any]:
        spinner = Halo(text="Running", spinner="dots", color="green")
        start_time = time.time()
        try:
            spinner.start()
            while True:
                summary = self.get_diff_summary(id)
                if summary["status"] in ("success", "error"):
                    elapsed_time = format(time.time() - start_time, ".2f")
                    spinner.succeed(
                        f"Completed with status: {summary['status']}. Total run time: {elapsed_time} seconds"
                    )
                    return summary

                elapsed_seconds = int(time.time() - start_time)
                spinner.text = f"Running... {elapsed_seconds} seconds"
                time.sleep(1)
        finally:
            spinner.stop()

    def print_diff_summary(self, results: dict[str, Any], data_diff_configs: DataDiffConfigs):
        # For "pks"
        headers_pks = ["Stats", data_diff_configs.table1, data_diff_configs.table2]
        rows_pks = []
        for key, value in results["pks"].items():
            rows_pks.append([key] + value)
        print(f"\nData Diff For Primary Keys: {data_diff_configs.pk_columns}")
        print(tabulate(rows_pks, headers=headers_pks, tablefmt="grid"))

        # For "values"
        headers_values = ["Stats", "Values"]
        rows_values = []
        for key, value in results["values"].items():
            if key != "columns_diff_stats" and not isinstance(value, list):
                rows_values.append([key, value])
        print("\nData Diff Values Summary:")
        print(tabulate(rows_values, headers=headers_values, tablefmt="grid"))

        # For "columns_diff_stats"
        headers_diff_stats = ["Column Name", "Match"]
        rows_diff_stats = []
        for diff_stat in results["values"]["columns_diff_stats"]:
            rows_diff_stats.append([diff_stat["column_name"], diff_stat["match"]])
        print("\nData Diff Column Difference Statistics:")
        print(tabulate(rows_diff_stats, headers=headers_diff_stats, tablefmt="grid"))

        # Dependencies
        print("\nDependencies:")
        for key, value in results["dependencies"].items():
            print(f"{key.capitalize()}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey.capitalize()}: {', '.join(map(str, subvalue))}")
        
        # Schema
        headers_schema = ["Stats", data_diff_configs.table1, data_diff_configs.table2]
        rows_schema = []
        for key, value in results["schema"].items():
            if isinstance(value, list) and len(value) == 2:
                rows_schema.append([key, value[0], value[1]])
            else:
                rows_schema.append([key, value, ''])
        print("\nSchema Diff Summary:")
        print(tabulate(rows_schema, headers=headers_schema, tablefmt="grid"))

    def run_data_diff(self, data_diff_configs: DataDiffConfigs):
        diff_id = self.create_diff(data_diff_configs)
        results = self.wait_for_results(diff_id)
        self.print_diff_summary(results, data_diff_configs)


if __name__ == "__main__":
    datadiff = DataDiff(host, datafold_api_key)
    datadiff.run_data_diff(data_diff_configs)