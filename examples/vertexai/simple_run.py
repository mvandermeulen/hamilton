from typing import NamedTuple

import google.cloud.aiplatform as aip
from kfp.v2 import dsl, compiler

BUCKET_URI = "hamilton-bucket"
PIPELINE_ROOT = f"gs://{BUCKET_URI}/pipeline_root/"


@dsl.component
def hamilton_task() -> NamedTuple("Outputs", [
    ("results_json", str),
]):
    """Load external data, preprocess dataset, and store cleaned data"""
    import json
    import pandas as pd
    from hamilton import base, driver
    from function_modules import prepare_data, train_model, evaluate_model

    hamilton_config = dict(
        development_flag=True,
        task="binary_classification",
        label="absenteeism_time_in_hours",
        feature_set=[
            "age_zero_mean_unit_variance",
            "has_children",
            "has_pet",
            "is_summer",
            "service_time",
        ],
        validation_user_ids=[
            "1",
            "2",
            "4",
            "15",
            "17",
            "24",
            "36",
        ],
        model_config={},
        scorer_name="accuracy",
        bootstrap_iter=1000,
    )

    dr = (
        driver.Builder()
        .with_modules(prepare_data, train_model, evaluate_model)
        .with_config(hamilton_config)
        .with_adapter(base.SimplePythonDataFrameGraphAdapter())
        .build()
    )

    raw_df = pd.read_csv("./data/Absenteeism_at_work.csv")

    results = dr.execute(
        final_vars=[prepare_data.ALL_FEATURES] + ["absenteeism_time_in_hours"],
        inputs={"raw_df": raw_df}
    )

    print(results.shape)
    print(results.head())

    return json.dumps(results)


@dsl.pipeline(
    name="hamilton-absenteeism-prediction",
    description="Predict absenteeism using Hamilton and VertexAI",
    pipeline_root=PIPELINE_ROOT,
)
def pipeline() -> None:
    hamilton_task()


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path="pipeline_package.json"
    )

    aip.init(
        project="omega-branch-382917",
        location="us-east1"
    )

    job = aip.PipelineJob(
        display_name="Hamilton + VertexAI Run",
        template_path="pipeline_package.json",
        pipeline_root=PIPELINE_ROOT,
        parameter_values=dict(),
    )

    job.submit(service_account="thierry@dagworks.io")
