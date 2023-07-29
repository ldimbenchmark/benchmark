from ldimbenchmark.methods import LILA, MNF, DUALMethod
from ldimbenchmark import LDIMBenchmark

methods = [
    "ghcr.io/ldimbenchmark/mnf:1.4.0",
    "ghcr.io/ldimbenchmark/lila:0.2.1",
    "ghcr.io/ldimbenchmark/dualmethod:0.1.1",
]

benchmark = LDIMBenchmark(
    {"lila": {"default_flow_sensor": "sum"}}, [], results_dir="./benchmark-results"
)
benchmark.add_local_methods(methods)

benchmark.run_complexity_analysis(
    methods=methods,
    style="periods",
    n_max=366,
    n_measures=60,
    n_repeats=5
)
