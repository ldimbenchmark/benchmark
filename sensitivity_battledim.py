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


datasets = [
    Dataset(os.path.join(test_data_folder_datasets, "battledim")),
]

# %%
if __name__ == "__main__":
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

    derivator.derive_data("pressures", "count", [
        3.64,
        3.6,
        2.0,
        1.0,
        0.1,
        0
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

    derivator.derive_data("flows", "sensitivity", [
        {"value": 0.1, "shift": "bottom"},
        {"value": 0.5, "shift": "bottom"},
        {"value": 1, "shift": "bottom"},
        {"value": 2, "shift": "bottom"},
        {"value": 3, "shift": "bottom"},
        {"value": 5, "shift": "bottom"},
        {"value": 10, "shift": "bottom"},
    ])

    derivator.derive_data("flows", "count", [
        0.33,
        0.25,
        0.2,
        0.1,
        0
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
    derivator.derive_data(["flows", "pressures"], "sensitivity", [
        {"value": 0.1, "shift": "bottom"},
        {"value": 0.5, "shift": "bottom"},
        {"value": 1, "shift": "bottom"},
        {"value": 2, "shift": "bottom"},
        {"value": 3, "shift": "bottom"},
        {"value": 5, "shift": "bottom"},
        {"value": 10, "shift": "bottom"},
    ])


    derivator.derive_model("junctions", "elevation", "accuracy", [16, 8, 4, 2, 1, 0.5, 0.1])
    derivator.derive_model("pipes", "diameter", "accuracy", [30/1000, 16/1000, 8/1000, 4/1000, 2/1000, 1/1000, 0.5/1000, 0.1/1000])
    derivator.derive_model("pipes", "roughness", "accuracy", [20, 16, 8, 4, 2, 1, 0.5, 0.1, 0.2,0.5, 1])
    derivator.derive_model("pipes", "length", "accuracy", [100, 50, 16, 8, 4, 2, 1, 0.5, 0.1])

    allDerivedDatasets = derivator.get_dervived_datasets(True)


    # %%

    # Best Performance Evaluation
    hyperparameters = {
        "lila": {
            "battledim": {
                "C_threshold": 12, 
                "resample_frequency": "5T",
                "est_length": 120,
                "delta": 18,
                "dma_specific": True,
                "default_flow_sensor": "PUMP_1"
            }
        },
        "mnf": {
            "battledim": {'resample_frequency': '60T', 'window': 7, 'gamma': -0.1, 'sensor_treatment': 'sum'}
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
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/mnf:1.4.0"])
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/lila:0.2.1"])
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/dualmethod:0.1.0"])

    benchmark.run_benchmark(
        evaluation_mode="evaluation",
        parallel=True,
        parallel_max_workers=5,
        memory_limit="20g"
        # use_cached=False,
    )

    # %%

    benchmark.evaluate(
        current_only=True,
        write_results="db",
        print_results=False
    )

    # %%
    benchmark.evaluate_derivations()


    # %%
    analyzer = DatasetAnalyzer("sensitivity-analysis")
    derivator = DatasetDerivator(
        datasets,
        os.path.join(test_data_folder_datasets),  # ignore_cache=True
    )

    derivator.derive_data("pressures", "precision", [0.1])

    derivator.derive_data("pressures", "downsample", [60 * 10])

    derivator.derive_data("pressures", "sensitivity", [
        {"value": 1, "shift": "middle"},
    ])

    derivator.derive_data("flows", "precision", [0.1])
    derivator.derive_data("flows", "downsample", [60 * 10])
    derivator.derive_data("flows", "sensitivity", [
        {"value": 1, "shift": "middle"},
    ])

    allDerivedDatasets = derivator.get_dervived_datasets()

    # # Precision
    analyzer.compare([datasets[0], allDerivedDatasets[0]], "pressures", True)
    # # Downsample
    analyzer.compare([datasets[0], allDerivedDatasets[1]], "pressures", True)
    # Sensitivity
    analyzer.compare([datasets[0], allDerivedDatasets[2]], "pressures", True)

    analyzer.compare([datasets[0], allDerivedDatasets[3]], "flows", True)
    analyzer.compare([datasets[0], allDerivedDatasets[4]], "flows", True)
    analyzer.compare([datasets[0], allDerivedDatasets[5]], "flows", True)

    # %%
