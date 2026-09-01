"""Heat-transfer example for comsol-mcp.

This script shows the *backend API* that the MCP tools wrap. It runs the full
pipeline: new model -> block geometry -> heat-transfer physics -> mesh ->
stationary study -> solve -> evaluate.

Run it directly:
    python examples/heat_transfer_example.py

With COMSOL installed it performs a real solve; without COMSOL it runs in
dry-run mode and returns simulated data (so the example is always runnable).
The same calls are what the MCP tools (add_block, add_physics, run_solver,
evaluate, ...) expose to an AI client.
"""

import os
import sys

# Make the example runnable directly from the repo root without `pip install`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comsol_mcp.backends import get_backend


def main() -> None:
    be = get_backend()

    print("== new model ==")
    print(be.new_model("6.2"))

    print("== add block geometry ==")
    print(be.add_block("geom1", 3, [0.1, 0.1, 0.1], [0, 0, 0]))

    print("== add heat transfer physics ==")
    print(be.add_physics("ht", "ht", {"T": 293.15}))

    print("== build mesh ==")
    print(be.build_mesh("mesh1"))

    print("== add stationary study ==")
    print(be.add_study("std1", "Stationary"))

    print("== run solver ==")
    print(be.run_solver("std1"))

    print("== evaluate temperature T ==")
    print(be.evaluate("T", "dset1"))

    print("== save model ==")
    print(be.save_model("heat_transfer_example.mph"))

    print("\nModel info:")
    print(be.model_info())


if __name__ == "__main__":
    main()
