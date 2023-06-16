import numpy as np
import pandas as pd
from ldimbenchmark.benchmark import LDIMBenchmark
from ldimbenchmark.classes import LDIMMethodBase
from typing import Dict, List
from ldimbenchmark.evaluation_metrics import f1Score
from ldimbenchmark.methods import LILA, MNF, DUALMethod
from ldimbenchmark.datasets import Dataset, DatasetLibrary, DATASETS
import itertools
import logging

logLevel = "INFO"

numeric_level = getattr(logging, logLevel, None)
if not isinstance(numeric_level, int):
    raise ValueError("Invalid log level: %s" % logLevel)

logging.basicConfig(
    level=numeric_level,
    handlers=[logging.StreamHandler(), logging.FileHandler("benchmark.log")],
    format="%(asctime)s %(levelname)-8s %(message)s",
)
logging.getLogger().setLevel(numeric_level)

if __name__ == "__main__":
    param_grid = {
        "lila": {
            "battledim": {
                "est_length": np.arange(24, 24 * 8, 24).tolist(), # Optimal: Battledim: 168, Graz: x, Gjovik: x
                "C_threshold": np.arange(2, 16, 1).tolist(), # Optimal: Battledim: 15, Graz: x, Gjovik: x
                "delta": np.arange(4, 14, 1).tolist(), # Optimal: Battledim: 12, Graz: x, Gjovik: x
                "default_flow_sensor": ["sum"],
                "resample_frequency": ["60T", "30T", "5T", "1T"], # Optimal: Battledim: 5T, Graz: x, Gjovik: 
            },
            "graz-ragnitz": {
                "est_length": np.arange(24, 24 * 8, 24).tolist(), 
                "C_threshold": np.arange(2, 16, 1).tolist(),
                "delta": np.arange(4, 14, 1).tolist(),
                "default_flow_sensor": ["wNode_1"],
                "resample_frequency": ["5T", "1T", "30s", "20s", "15s", "10s", "5s"], 
            }
        },
        "mnf": {
            "battledim": {
                # "gamma": np.arange(-10, 10, 1).tolist(),
                "gamma": np.arange(-0.3, 1, 0.05).tolist(), # Optimal: Battledim: 1.0, Graz: x, Gjovik: x
                "window": [1, 5, 10, 20], # Optimal: Battledim: 10, Graz: x, Gjovik: x
                # "resample_frequency": ["60T"], # Optimal: Battledim: 5T, Graz: x, Gjovik: x
            },
            "graz-ragnitz": {
                # Not Applicable...
                "gamma": [0], 
                "window": [1],
            }
        },
        "dualmethod": {
            "battledim": {
                "est_length": np.arange(24, 24 * 40, 48).tolist(), # Optimal: Battledim: 888, Graz: x, Gjovik: x
                "C_threshold": np.arange(0, 1, 0.2).tolist() + np.arange(2, 6, 1).tolist(), # Optimal: Battledim: 0.2, Graz: x, Gjovik: x
                "delta": np.arange(0, 4, 0.2).tolist() + np.arange(2, 6, 1).tolist(), # Optimal: Battledim: 4, Graz: x, Gjovik: x
            },
            "graz-ragnitz": {
                 "est_length": np.arange(24, 24 * 40, 48).tolist(), # Optimal: Battledim: 888, Graz: x, Gjovik: x
                "C_threshold": np.arange(0, 1, 0.2).tolist() + np.arange(2, 6, 1).tolist(), # Optimal: Battledim: 0.2, Graz: x, Gjovik: x
                "delta": np.arange(0, 4, 0.2).tolist() + np.arange(2, 6, 1).tolist(), # Optimal: Battledim: 4, Graz: x, Gjovik: x
            }
        },
    }

    datasets = [
        # Dataset("./datasets/gjovik"),
        Dataset("./datasets/graz-ragnitz"),
        Dataset("./datasets/battledim"),
    ]

    benchmark = LDIMBenchmark(
        hyperparameters=param_grid,
        datasets=datasets,
        results_dir="./grid-search",
        debug=False,
        multi_parameters=True,
    )

    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/mnf:1.2.0"])
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/lila:0.2.0"])
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/dualmethod:0.1.0"])

    # execute benchmark
    benchmark.run_benchmark(
        "training",
        parallel=True,
        # parallel_max_workers=8, 
        memory_limit="10g",
    )

    benchmark.evaluate(
        write_results="db",
        current_only=False,
        print_results=False
        # resultFilter=lambda results: results[results["F1"].notna()],
    )
