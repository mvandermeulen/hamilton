# Since this is not in plugins we need to import it *before* doing anything else
import importlib

import click

importlib.import_module("adapters")

from components import feature_data, model_evaluation, model_training

from hamilton import base, driver
from hamilton.function_modifiers import source
from hamilton.io.materialization import from_, to


@click.group()
def cli():
    pass


modules = {
    "features_processed": [feature_data],
    "model_trained": [feature_data, model_training],
    "metrics_captured": [feature_data, model_training, model_evaluation],
}


def get_materializers(which_stage: str):
    materializers = [
        from_.csv(path=source("location"), target="titanic_data"),
        to.pickle(
            id="save_trained_model", dependencies=["trained_model"], path="./model_saved.pickle"
        ),
        to.csv(
            id="save_training_data",
            dependencies=["train_set"],
            combine=base.PandasDataFrameResult(),
            path="./training_data.csv",
        ),
        to.png(
            id="save_confusion_matrix_plot",
            dependencies=["confusion_matrix_test_plot"],
            path="./confusion_matrix_plot.png",
        ),
    ]
    if which_stage == "features_processed":
        materializers = [materializers[0], materializers[2]]
    elif which_stage == "model_trained":
        materializers = materializers[0:3]
    return materializers


@cli.command()
@click.option(
    "--which-stage",
    type=click.Choice(["features_processed", "model_trained", "metrics_captured"]),
    required=True,
)
def run(which_stage: str):
    dr = driver.Driver({}, *modules[which_stage])
    materializers = get_materializers(which_stage)
    out = dr.materialize(
        *materializers,
        inputs={"location": "./data/titanic.csv", "test_size": 0.2, "random_state": 42}
    )
    print(out)


@cli.command()
@click.option(
    "--which-stage",
    type=click.Choice(["features_processed", "model_trained", "metrics_captured"]),
    required=True,
)
def visualize(which_stage: str):
    dr = driver.Driver({}, *modules[which_stage])
    materializers = get_materializers(which_stage)
    dr.visualize_materialization(*materializers)


if __name__ == "__main__":
    run()
