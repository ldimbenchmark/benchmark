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
        "mnf": {
            "synthetic-days-9": {'resample_frequency': '5T', 'window': 5, 'gamma': 0.5},
            "graz-ragnitz": {'resample_frequency': '1s', 'window': 10, 'gamma': 1.2, 'sensor_treatment': 'each', 'night_flow_interval': '1T', 'night_flow_start': '2023-01-01 01:45:00'},
            "gjovik": {'window': 5, 'gamma': 0.15},
            "battledim": {'resample_frequency': '60T', 'window': 10, 'gamma': 1.0}
        },
        "lila": {
            "synthetic-days-9": {'resample_frequency': '5T', 'est_length': 2, 'C_threshold': 2, 'delta': -4, 'dma_specific': False, 'default_flow_sensor': 'sum'},
            "graz-ragnitz": {'leakfree_time_start': '2016-04-12 01:15:00', 'leakfree_time_stop': '2016-04-12 01:29:59', 'resample_frequency': '30s', 'est_length': 1.4, 'C_threshold': 16, 'delta': -2.0, 'dma_specific': False, 'default_flow_sensor': 'wNode_1'},
            "gjovik": {'C_threshold': 1.25, 'delta': 7.0, 'est_length': 24.0, "default_flow_sensor": "sum"},
            "battledim": {'resample_frequency': '5T', 'est_length': 192, 'C_threshold': 14, 'delta': 5, 'dma_specific': False, 'default_flow_sensor': 'sum'}
        },
        "dualmethod": {
            "synthetic-days-9": {'resample_frequency': '5T', 'est_length': 2, 'C_threshold': 2, 'delta': -2},
            "graz-ragnitz": {'resample_frequency': '1T', 'est_length': 1.1, 'C_threshold': 0.7, 'delta': -0.2},
            "gjovik": {
                # Not working yet
                "est_length": 0,
                "C_threshold": 0, 
                "delta": 0,
            },
            "battledim": {'resample_frequency': '5T', 'est_length': 888, 'C_threshold': 0.8, 'delta': 3}
        },
    }

    datasets = [
        # Dataset("./datasets/gjovik"),
        Dataset("./datasets/graz-ragnitz"),
        Dataset("./datasets/battledim"),
        Dataset("./datasets/synthetic-days-9"),
    ]

    benchmark = LDIMBenchmark(
        hyperparameters=param_grid,
        datasets=datasets,
        results_dir="./results",
        debug=False,
    )

    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/mnf:1.2.0"])
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/lila:0.2.0"])
    benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/dualmethod:0.1.0"])

    # # execute benchmark
    benchmark.run_benchmark(
        "evaluation",
        parallel=True,
        parallel_max_workers=3, 
        memory_limit="40g",
    )

    table = benchmark.evaluate(
        write_results=["csv"],
        current_only=False,
        print_results=True
        # resultFilter=lambda results: results[results["F1"].notna()],
    )

    for run_id in table[table["dataset"] != "gjovik"]["_folder"]:
        print(run_id)
        benchmark.evaluate_run(run_id)
        
    benchmark.evaluate_run("mnf_1.2.0_gjovik-b29219f0e52ed3224578c69c66c0ab8d_evaluation_575a6e5d3e3e72a069478607e2d14013")
    benchmark.evaluate_run("mnf_1.2.0_gjovik-b29219f0e52ed3224578c69c66c0ab8d_evaluation_575a6e5d3e3e72a069478607e2d14013")
    benchmark.evaluate_run("lila_0.2.0_gjovik-b29219f0e52ed3224578c69c66c0ab8d_evaluation_b3f873e596385f89d0f241d2fa5a45cf")