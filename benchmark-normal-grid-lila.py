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

try:
    if __name__ == "__main__":
        param_grid = {
            "lila": {
                "battledim": {
                    "est_length": np.arange(24, 24 * 12, 24).tolist(), # Optimal: Battledim: 168, Graz: x, Gjovik: x
                    "C_threshold": np.arange(0, 25, 1).tolist(), # Optimal: Battledim: 15, Graz: x, Gjovik: x
                    "delta": np.arange(1, 25, 1).tolist(), # Optimal: Battledim: 12, Graz: x, Gjovik: x
                    "default_flow_sensor": ["PUMP_1"],
                    "resample_frequency": ["5T"], # ["60T", "30T", "10T", "5T", "1T"], # Optimal: Battledim: 5T, Graz: x, Gjovik: 
                    "dma_specific": [True]
                },
                "graz-ragnitz": {
                    "leakfree_time_start": ["2016-04-12 01:15:00"],
                    "leakfree_time_stop": ["2016-04-12 01:29:59"],
                    "est_length": np.around(np.linspace(0.1, 1.7, 17),1).tolist(), 
                    "C_threshold": np.arange(1, 20, 1).tolist(),
                    "delta": np.arange(-5, -2, 1).tolist() + np.around(np.linspace(-2, 1, 16),1).tolist() + np.arange(1, 5, 1).tolist(),
                    "default_flow_sensor": ["wNode_1"],
                    "resample_frequency": ["5T", "1T", "30s", "20s", "15s", "10s", "5s"], 
                },
                "gjovik": {

                }
            },
            "mnf": {
                "battledim": {
                    # "gamma": np.arange(-10, 10, 1).tolist(),
                    "gamma": np.around(np.arange(-0.5, 1.5, 0.05),2).tolist(), # Optimal: Battledim: 1.0, Graz: x, Gjovik: x
                    "window": np.arange(1, 24, 1).tolist(), # Optimal: Battledim: 10, Graz: x, Gjovik: x
                    "resample_frequency": ["10T", "60T"], # Optimal: Battledim: 5T, Graz: x, Gjovik: x
                    "sensor_treatment": ["each", "first", "sum"]
                },
                "graz-ragnitz": {
                    "resample_frequency": ["1s", "2s", "4s", "5s", "10s", "15s"],
                    "night_flow_interval": ["1T"],
                    "night_flow_start": ["2023-01-01 01:45:00"],
                    "gamma": np.around(np.linspace(0, 2.6, 25), 1).tolist(),
                    "window": [1, 2, 3, 4, 5, 8, 10, 12, 14, 15],
                },
                "gjovik": {

                }
            },
            "dualmethod": {
                "battledim": {
                    "est_length": np.arange(24, 24 * 50, 72).tolist(), # Optimal: Battledim: 888, Graz: x, Gjovik: x
                    "C_threshold": np.arange(-3, -1, 1).tolist() + np.around(np.arange(-1, 2, 0.2),1).tolist() + np.arange(2,7, 1).tolist(), # Optimal: Battledim: 0.2, Graz: x, Gjovik: x
                    "delta": np.arange(-3, 9, 1).tolist(), # np.around(np.arange(0, 4, 0.2)).tolist() +   # Optimal: Battledim: 4, Graz: x, Gjovik: x
                },
                "graz-ragnitz": {
                    "resample_frequency": ["1T"], 
                    "est_length": np.around(np.linspace(0.1, 2, 20),1).tolist(),
                    "C_threshold": np.around(np.linspace(-3, 2, 20),1).tolist(),
                    "delta": np.around(np.linspace(-5, 3, 18),1).tolist(),
                },
                "gjovik": {
                    "est_length": np.arange(24, 24 * 44, 144).tolist(), # Optimal: Battledim: 888, Graz: x, Gjovik: x
                    "C_threshold": np.arange(-3, 9, 2).tolist(), # Optimal: Battledim: 0.2, Graz: x, Gjovik: x
                    "delta": np.arange(-3, 9, 2).tolist(), # np.around(np.arange(0, 4, 0.2)).tolist() +   # Optimal: Battledim: 4, Graz: x, Gjovik: x
                    "resample_frequency": ["60T"], 
                },
            },
        }

        # Run seperate benchmarks

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

        # benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/mnf:1.4.0"])
        benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/lila:0.2.1"])
        # benchmark.add_docker_methods(["ghcr.io/ldimbenchmark/dualmethod:0.1.1"])


        max_ram = "10g"
        max_workers = 28
        # # execute benchmark
        benchmark.run_benchmark(
            "evaluation",
            parallel=True,
            parallel_max_workers=max_workers, 
            memory_limit=max_ram,
        )

        benchmark.evaluate(
            write_results=["db", "png"],
            current_only=True,
            print_results=False
        )

        # benchmark.run_benchmark(
        #     "training",
        #     parallel=True,
        #     parallel_max_workers=max_workers, 
        #     memory_limit=max_ram,
        # )
        # benchmark.evaluate(
        #     write_results=["db"],
        #     current_only=False,
        #     print_results=False
        # )


except Exception as e:
    logging.exception(e)
    raise e