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
                "est_length": np.arange(24, 24 * 12, 24).tolist(), # Optimal: Battledim: 168, Graz: x, Gjovik: x
                "C_threshold": np.arange(2, 25, 1).tolist(), # Optimal: Battledim: 15, Graz: x, Gjovik: x
                "delta": np.arange(4, 25, 1).tolist(), # Optimal: Battledim: 12, Graz: x, Gjovik: x
                "default_flow_sensor": ["sum"],
                "resample_frequency": ["5T"], # ["60T", "30T", "10T", "5T", "1T"], # Optimal: Battledim: 5T, Graz: x, Gjovik: 
                # "dma_specific": [True]
            },
            "graz-ragnitz": {
                "leakfree_time_start": ["2016-04-12 01:15:00"],
                "leakfree_time_stop": ["2016-04-12 01:29:59"],
                "est_length": np.around(np.linspace(0.1, 1.7, 17),1).tolist(), 
                "C_threshold": np.arange(1, 20, 1).tolist(),
                "delta": np.arange(-5, -2, 1).tolist() + np.around(np.linspace(-2, 1, 16),1).tolist() + np.arange(1, 5, 1).tolist(),
                "default_flow_sensor": ["wNode_1"],
                "resample_frequency": ["5T", "1T", "30s", "20s", "15s", "10s", "5s"], 
            }
        },
        "mnf": {
            "battledim": {
                # "gamma": np.arange(-10, 10, 1).tolist(),
                "gamma": np.around(np.arange(-0.2, 1.5, 0.05),2).tolist(), # Optimal: Battledim: 1.0, Graz: x, Gjovik: x
                "window": np.arange(1, 19, 1).tolist(), # Optimal: Battledim: 10, Graz: x, Gjovik: x
                "resample_frequency": ["10T", "60T"], # Optimal: Battledim: 5T, Graz: x, Gjovik: x
            },
            "graz-ragnitz": {
                # Not Applicable...
                "gamma": [0], 
                "window": [1],
            }
        },
        "dualmethod": {
            "battledim": {
                "est_length": np.arange(24, 24 * 50, 96).tolist(), # Optimal: Battledim: 888, Graz: x, Gjovik: x
                "C_threshold": np.arange(-3, -1, 1).tolist() + np.around(np.arange(-1, 2, 0.5),1).tolist() + np.arange(2,7, 1).tolist(), # Optimal: Battledim: 0.2, Graz: x, Gjovik: x
                "delta": np.arange(-3, 9, 2).tolist(), # np.around(np.arange(0, 4, 0.2)).tolist() +   # Optimal: Battledim: 4, Graz: x, Gjovik: x
            },
            "graz-ragnitz": {
                "resample_frequency": ["1T"], 
                "est_length": np.around(np.linspace(0.1, 2, 20),1).tolist(),
                "C_threshold": np.around(np.linspace(0, 2, 20),1).tolist(),
                "delta": np.around(np.linspace(-3, 3, 18),1).tolist(),
            },
            "gjovik": {
                "est_length": np.arange(24, 24 * 44, 96).tolist(), # Optimal: Battledim: 888, Graz: x, Gjovik: x
                "C_threshold": np.arange(-3, 9, 3).tolist(), # Optimal: Battledim: 0.2, Graz: x, Gjovik: x
                "delta": np.arange(-3, 9, 3).tolist(), # np.around(np.arange(0, 4, 0.2)).tolist() +   # Optimal: Battledim: 4, Graz: x, Gjovik: x
            },
        },
    }

    datasets = [
        # Dataset("./datasets/gjovik"),
        # Dataset("./datasets/graz-ragnitz"),
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

    # # execute benchmark
    benchmark.run_benchmark(
        "training",
        parallel=True,
        parallel_max_workers=3, 
        memory_limit="20g",
    )

    benchmark.evaluate(
        write_results=["db"],
        current_only=True,
        print_results=False
        # resultFilter=lambda results: results[results["F1"].notna()],
    )

    # benchmark.evaluate_run("lila_0.2.0_graz-ragnitz-8f370b5676ecaad892ba6db24135b6af_evaluation_d995add1b1a1c944318687406fa0b452")