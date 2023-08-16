import pandas as pd
from hamilton import base, driver
from function_modules import prepare_data, train_model, evaluate_model


def main():
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

    raw_df = pd.read_csv("./data/Absenteeism_at_work.csv", sep=";")

    results = dr.execute(
        final_vars=prepare_data.ALL_FEATURES + ["absenteeism_time_in_hours"],
        inputs={"raw_df": raw_df}
    )
    print(results)


if __name__ == "__main__":
    main()
