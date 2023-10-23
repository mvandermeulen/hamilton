from hamilton import driver
from hamilton.io.materialization import from_, to

dr = driver.Driver({}, ...)

dr.materialize(
    from_.csv(
        target="node_to_load_to",
        path="./input_data.csv",
    ),
    to.csv(id="data_saving_node", dependencies=["col_1", "col_2", "col_"], path="./path.csv"),
)
