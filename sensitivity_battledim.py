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

    datasets = [
        Dataset(os.path.join(test_data_folder_datasets, "battledim")),
    ]

    # %%
    derivator = DatasetDerivator(
        datasets,
        os.path.join(test_data_folder_datasets),  # ignore_cache=True
    )

    # Data - Pressure
    derivator.derive_data("pressures", "precision", [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.6])

    derivator.derive_data(
        "pressures",
        "downsample",
        [
            60 * 10,
            60 * 20,
            60 * 30,
            60 * 60,
            60 * 60 * 2,
            60 * 60 * 4,
            60 * 60 * 8,
            60 * 60 * 12,
            60 * 60 * 24,
        ],
    )

    # derivator.derive_data("pressures", "sensitivity", [0.1, 0.5, 1, 2, 3, 5, 10])
    derivator.derive_data("pressures", "sensitivity", [
        {"value": 0.1, "shift": "bottom"},
        {"value": 0.5, "shift": "bottom"},
        {"value": 1, "shift": "bottom"},
        {"value": 2, "shift": "bottom"},
        {"value": 3, "shift": "bottom"},
        {"value": 5, "shift": "bottom"},
        {"value": 10, "shift": "bottom"},
    ])

    # Data - Flows
    derivator.derive_data("flows", "precision", [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.6])

    derivator.derive_data(
        "flows",
        "downsample",
        [
            60 * 10,
            60 * 20,
            60 * 30,
            60 * 60,
            60 * 60 * 2,
            60 * 60 * 4,
            60 * 60 * 8,
            60 * 60 * 12,
        ],
    )

    derivator.derive_data("pressures", "sensitivity", [
        {"value": 0.1, "shift": "bottom"},
        {"value": 0.5, "shift": "bottom"},
        {"value": 1, "shift": "bottom"},
        {"value": 2, "shift": "bottom"},
        {"value": 3, "shift": "bottom"},
        {"value": 5, "shift": "bottom"},
        {"value": 10, "shift": "bottom"},
    ])

    # Both
    derivator.derive_data(
        ["flows", "pressures"],
        "downsample",
        [
            60 * 10,
            60 * 20,
            60 * 30,
            60 * 60,
            60 * 60 * 2,
            60 * 60 * 4,
            60 * 60 * 8,
            60 * 60 * 12,
        ],
    )

    derivator.derive_data(
        ["flows", "pressures"], "precision", [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.6]
    )


    derivator.derive_model("junctions", "elevation", "accuracy", [16, 8, 4, 2, 1, 0.5, 0.1])

    allDerivedDatasets = derivator.get_dervived_datasets(True)


    # %%

    # Best Performance Evaluation
    hyperparameters = {
        "lila": {
            "battledim": {
                "C_threshold": 14,
                "est_length": 168,
                "delta": 4,
                "dma_specific": False,
                "default_flow_sensor": "sum",
            }
        },
        "mnf": {
            "battledim": {
                "window": 5.0,
                "gamma": -0.10000000000000003,
            }
        },
        "dualmethod": {
            "battledim": {
                "est_length": 888.0,
                "C_threshold": 0.8,
                "delta": 3.0,
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

    benchmark.run_benchmark(
        evaluation_mode="evaluation",
        # parallel=True,
        parallel_max_workers=2,
        memory_limit="20g"
        # use_cached=False,
    )

    # %%

    benchmark.evaluate(
        current_only=True,
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
