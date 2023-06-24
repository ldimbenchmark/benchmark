# %%
# %load_ext autoreload
# %autoreload 2
# Fix https://github.com/numpy/numpy/issues/5752

import os
from ldimbenchmark.datasets.analysis import DatasetAnalyzer
from ldimbenchmark.datasets import Dataset, DatasetLibrary, DATASETS
from ldimbenchmark.datasets.derivation import DatasetDerivator
from ldimbenchmark.generator import generateDatasetForTimeSpanDays
from ldimbenchmark.methods import MNF, LILA

from ldimbenchmark.benchmark import LDIMBenchmark
import logging
from matplotlib import pyplot as plt
import numpy as np

test_data_folder_datasets = os.path.join("datasets")

logLevel = "INFO"

numeric_level = getattr(logging, logLevel, None)
if not isinstance(numeric_level, int):
    raise ValueError("Invalid log level: %s" % logLevel)

logging.basicConfig(
    level=numeric_level,
    handlers=[logging.StreamHandler(), logging.FileHandler("analysis.log")],
)
logging.getLogger().setLevel(numeric_level)

if __name__ == "__main__":

    # %%

    datasets = [
        Dataset(os.path.join(test_data_folder_datasets, "graz-ragnitz")),
    ]

    allDerivedDatasets = datasets

    # %%
    derivator = DatasetDerivator(
        datasets,
        os.path.join(test_data_folder_datasets),  # ignore_cache=True
    )

    derivator.derive_data("pressures", "precision", [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.6])

    derivator.derive_data(
        "pressures",
        "downsample",
        [
            5,
            10,
            30,
            60,
            60 * 2,
            60 * 5,
        ],
    )

    # derivator.derive_data("pressures", "sensitivity", [0.1, 0.5, 1, 2, 3])
    derivator.derive_data("pressures", "sensitivity", [
        {"value": 0.1, "shift": "bottom"},
        {"value": 0.5, "shift": "bottom"},
        {"value": 1, "shift": "bottom"},
        {"value": 2, "shift": "bottom"},
        {"value": 3, "shift": "bottom"},
        {"value": 5, "shift": "bottom"},
        {"value": 10, "shift": "bottom"},
    ])

    derivator.derive_data("flows", "precision", [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.6])
    derivator.derive_data(
        "flows",
        "downsample",
        [
            5,
            10,
            30,
            60,
            60 * 2,
            60 * 5,
        ],
    )
    derivator.derive_data("flows", "sensitivity", [
        {"value": 0.1, "shift": "bottom"},
        {"value": 0.5, "shift": "bottom"},
        {"value": 1, "shift": "bottom"},
        {"value": 2, "shift": "bottom"},
        {"value": 3, "shift": "bottom"},
        {"value": 5, "shift": "bottom"},
        {"value": 10, "shift": "bottom"},
    ])

    derivator.derive_data(
        ["flows", "pressures"],
        "downsample",
        [
            5,
            10,
            30,
            60,
            60 * 2,
            60 * 5,
        ],
    )

    derivator.derive_data(
        ["flows", "pressures"], "precision", [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.6]
    )


    derivator.derive_model("junctions", "elevation", "accuracy", [16, 8, 4, 2, 1, 0.5, 0.1])
    allDerivedDatasets = allDerivedDatasets + derivedDatasets

    allDerivedDatasets = derivator.get_dervived_datasets(True)
    # %%


    hyperparameters = {
        "lila": {
            # Best Performances
            "graz-ragnitz": {
                # Overall
                # "resample_frequency": "1T",
                "est_length": 0.19999999999999998,
                "C_threshold": 5.25,
                "delta": -1.0,
            },
        },
        "mnf": {
            # not applicable
        },
        "dualmethod": {
            "graz-ragnitz": {
                # Best Performance Overall
                "resample_frequency": "1T",
                "est_length": 0.12000000000000001,
                "C_threshold": 1.8,
                "delta": -2.0,
            },
        },
    }

    benchmark = LDIMBenchmark(
        hyperparameters,
        allDerivedDatasets,
        # derivedDatasets[0],
        # dataset,
        results_dir="./sensitivity-analysis",
        # debug=True,
    )
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/mnf:1.2.0"])
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/lila:0.2.1"])
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/dualmethod:0.1.0"])

    # benchmark.add_local_methods([MNF()])
    # benchmark.add_local_methods([LILA()])

    benchmark.run_benchmark(
        evaluation_mode="evaluation",
        parallel=True,
        parallel_max_workers=3,
        memory_limit="20g"
        # use_cached=False,
    )

    benchmark.evaluate(
        True,
        write_results="db",
    )

    # %%
    benchmark.evaluate_derivations()


    # %%
    analyzer = DatasetAnalyzer("sensitivity-analysis")

    # # Precision
    # analyzer.compare([datasets[0], allDerivedDatasets[4]], "pressures", True)
    # # Downsample
    # analyzer.compare([datasets[0], allDerivedDatasets[10]], "pressures", True)
    # Sensitivity
    analyzer.compare([datasets[0], allDerivedDatasets[17]], "pressures", True)

    # %%