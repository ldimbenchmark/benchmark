from ldimbenchmark.methods import LILA, MNF, DUALMethod
from ldimbenchmark import LDIMBenchmark
from ldimbenchmark.datasets import Dataset
import logging

logLevel = "INFO"

numeric_level = getattr(logging, logLevel, None)
if not isinstance(numeric_level, int):
    raise ValueError("Invalid log level: %s" % logLevel)

logging.basicConfig(
    level=numeric_level,
    handlers=[logging.StreamHandler(), logging.FileHandler("complexity.log")],
    format="%(asctime)s %(levelname)-8s %(message)s",
)
logging.getLogger().setLevel(numeric_level)

if __name__ == '__main__':

    methods = [
        "ghcr.io/ldimbenchmark/mnf:1.4.0",
        "ghcr.io/ldimbenchmark/lila:0.2.1",
        "ghcr.io/ldimbenchmark/dualmethod:0.1.1",
    ]

    benchmark = LDIMBenchmark(
        {"lila": {"default_flow_sensor": "sum"}}, [], results_dir="./benchmark-results"
    )
    benchmark.add_local_methods(methods)

    # benchmark.run_benchmark(
    #     evaluation_mode="evaluation",
    # )

    benchmark.run_complexity_analysis(
        methods=methods,
        style="periods",
        n_max=366,
        n_measures=60,
        n_repeats=5
    )
