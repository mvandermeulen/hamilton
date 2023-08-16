import numpy as np
import scipy.stats as stats
from sklearn.metrics import get_scorer


def validation_score(scorer_name: str, y_validation: np.ndarray, val_pred: np.ndarray) -> float:
    """Compute the metric `scorer_name` from scikit-learn for the validation predictions"""
    scorer = get_scorer(scorer_name)
    score = np.abs(scorer._score_func(y_validation, val_pred))
    return score


def bootstrap_metric_sample(
    scorer_name: str, y_validation: np.ndarray, bootstrap_iter: int = 1000
) -> np.ndarray:
    """Bootstrap the `scorer_name` metric for a number of `bootstrap_iter` iterations
    based on the empirical label distribution of `y_validation`
    """
    scorer = get_scorer(scorer_name)

    n_examples = y_validation.shape[0]
    unique_val, count_val = np.unique(y_validation, return_counts=True)

    scores = []
    for _ in range(bootstrap_iter):
        random_draw = np.random.choice(unique_val, n_examples, p=count_val / count_val.sum())

        score = np.abs(scorer._score_func(y_validation, random_draw))
        scores.append(score)

    return np.asarray(scores)


def statistical_ttest_one_sample(
    bootstrap_metric_sample: np.ndarray,
    validation_score: float,
    higher_is_better: bool = True,
) -> dict:
    """Since we are dealing with scores, the model metric is always 'higher is better'"""

    if higher_is_better:
        sample_hypothesis = "less"
    else:
        sample_hypothesis = "greater"

    statistic, pvalue = stats.ttest_1samp(
        bootstrap_metric_sample, validation_score, alternative=sample_hypothesis
    )
    return dict(test="one_sample_ttest", stat=statistic, pvalue=pvalue)


def model_results(
    task: str,
    label: str,
    scorer_name: str,
    validation_score: float,
    bootstrap_iter: int,
    statistical_ttest_one_sample: dict,
) -> dict:
    """Collect key metrics and results into a single JSON serializable file"""
    return {
        "task": task,
        "label": label,
        "scorer_name": scorer_name,
        "validation_score": validation_score,
        "significance": statistical_ttest_one_sample,
        "bootstrap_iter": bootstrap_iter,
    }
