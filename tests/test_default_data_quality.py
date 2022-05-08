from typing import Any, Type

import numpy
import numpy as np
import pandas as pd
import pytest

from hamilton import node
from hamilton.data_quality.base import DataValidator
from hamilton.data_quality.default_validators import resolve_default_validators
from hamilton.function_modifiers import check_output

from resources.dq_dummy_examples import DUMMY_VALIDATORS_FOR_TESTING, SampleDataValidator2, SampleDataValidator1, SampleDataValidator3


@pytest.mark.parametrize('level', ['warn', 'fail'])
def test_validate_importance_level(level):
    DataValidator.validate_importance_level(level)


@pytest.mark.parametrize(
    'output_type, kwargs, importance, expected',
    [
        (int, {'equal_to': 1}, 'warn', [SampleDataValidator1(importance='warn', equal_to=1)]),
        (int, {'equal_to': 5}, 'fail', [SampleDataValidator1(importance='fail', equal_to=5)]),
        (pd.Series, {'dataset_length': 1}, 'warn', [SampleDataValidator2(importance='warn', dataset_length=1)]),
        (pd.Series, {'dataset_length': 5}, 'fail', [SampleDataValidator2(importance='fail', dataset_length=5)]),
        (
            pd.Series,
            {'dataset_length': 1, 'dtype' : np.int64},
            'warn',
            [
                SampleDataValidator2(importance='warn', dataset_length=1),
                SampleDataValidator3(importance='warn', dtype=np.int64)
            ]
        ),
    ],
)
def test_resolve_default_validators(output_type, kwargs, importance, expected):
    resolved_validators = resolve_default_validators(
        output_type=output_type,
        importance=importance,
        available_validators=DUMMY_VALIDATORS_FOR_TESTING,
        **kwargs
    )
    assert resolved_validators == expected


@pytest.mark.parametrize(
    'output_type, kwargs, importance',
    [
        (str, {'dataset_length': 1}, 'warn'),
        (pd.Series, {'equal_to': 1}, 'warn')
    ],
)
def test_resolve_default_validators_error(output_type, kwargs, importance):
    with pytest.raises(ValueError):
        resolve_default_validators(
            output_type=output_type,
            importance=importance,
            available_validators=DUMMY_VALIDATORS_FOR_TESTING,
            **kwargs)


def test_data_quality_node_transform():
    decorator = check_output(
        importance='warn',
        default_decorator_candidates=DUMMY_VALIDATORS_FOR_TESTING,
        dataset_length=1,
        dtype=numpy.int64
    )

    def fn(input: pd.Series) -> pd.Series:
        return input

    node_ = node.Node.from_fn(fn)
    subdag = decorator.transform_node(node_, config={}, fn=fn)
    assert 4 == len(subdag)
    # TODO -- assert shape of DAG

