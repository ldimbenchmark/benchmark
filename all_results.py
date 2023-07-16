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

    benchmark = LDIMBenchmark(
        hyperparameters={},
        datasets=[],
        results_dir="./grid-search",
        debug=False,
        multi_parameters=True,
    )

    benchmark.evaluate(
        write_results=["db"],
        current_only=False,
        print_results=False
        # resultFilter=lambda results: results[results["F1"].notna()],
    )