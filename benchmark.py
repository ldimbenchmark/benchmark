from ldimbenchmark.methods import LILA, MNF, DUALMethod
from ldimbenchmark import LDIMBenchmark

methods = [
    "ghcr.io/ldimbenchmark/dualmethod:0.2.23",
    "ghcr.io/ldimbenchmark/lila:0.2.23",
    "ghcr.io/ldimbenchmark/mnf:0.2.23",
]

benchmark = LDIMBenchmark(
    {"lila": {"default_flow_sensor": "sum"}}, [], results_dir="./benchmark-results"
)
benchmark.add_local_methods(methods)

benchmark.run_complexity_analysis(
    methods=methods,
    style="time",
    n_max=181,
    n_measures=30,
    n_repeats=5
)

benchmark.run_complexity_analysis(
    methods=methods,
    style="junctions",
    n_max=181,
    n_measures=30,
    n_repeats=5
)
