"""MCP tool surface for COMSOL.

Every tool delegates to a :class:`~comsol_mcp.backends.base.ModelBackend`
selected by :func:`comsol_mcp.backends.get_backend`, so the same tool works
live (GUI bridge), headless (batch) or in dry-run mode.
"""

import os
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from comsol_mcp.backends import get_backend
from comsol_mcp.backends.session import (
    connect_gui as sess_connect_gui,
    gui_status as sess_gui_status,
    launch_gui as sess_launch_gui,
    shutdown_gui as sess_shutdown_gui,
)

mcp = FastMCP("comsol-mcp")


def _opt(value: str) -> Optional[str]:
    return value if value else None


# ----------------------------------------------------------------------
# Session / GUI control
# ----------------------------------------------------------------------

@mcp.tool()
def launch_gui(model_path: str = "", port: int = 0) -> Dict[str, Any]:
    """Launch the COMSOL desktop GUI with the live bridge loaded.

    Operations issued afterwards drive the visible GUI in real time.
    """
    return sess_launch_gui(_opt(model_path), port or None)


@mcp.tool()
def connect_gui(port: int = 0, host: str = "localhost") -> Dict[str, Any]:
    """Connect to an already-running COMSOL GUI bridge."""
    return sess_connect_gui(port or None, host)


@mcp.tool()
def gui_status() -> Dict[str, Any]:
    """Report the current GUI/bridge session state."""
    return sess_gui_status()


@mcp.tool()
def shutdown_gui() -> Dict[str, Any]:
    """Stop the COMSOL GUI bridge session."""
    return sess_shutdown_gui()


# ----------------------------------------------------------------------
# Model read/write
# ----------------------------------------------------------------------

@mcp.tool()
def load_model(path: str) -> Dict[str, Any]:
    """Load a .mph model from disk."""
    return get_backend().load_model(path)


@mcp.tool()
def save_model(path: str = "") -> Dict[str, Any]:
    """Save the current model to a .mph file."""
    return get_backend().save_model(_opt(path))


@mcp.tool()
def new_model(version: str = "6.2") -> Dict[str, Any]:
    """Create a new empty model."""
    return get_backend().new_model(version)


@mcp.tool()
def model_info() -> Dict[str, Any]:
    """Return the structure of the current model."""
    return get_backend().model_info()


# ----------------------------------------------------------------------
# Geometry
# ----------------------------------------------------------------------

@mcp.tool()
def add_block(geom_tag: str, dims: int, size: List[float], pos: List[float], tag: str = "") -> Dict[str, Any]:
    """Add a block (box) to a geometry sequence."""
    return get_backend().add_block(geom_tag, dims, size, pos, _opt(tag))


@mcp.tool()
def add_cylinder(geom_tag: str, dims: int, r: float, h: float, pos: List[float], axis: str = "z", tag: str = "") -> Dict[str, Any]:
    """Add a cylinder to a geometry sequence."""
    return get_backend().add_cylinder(geom_tag, dims, r, h, pos, axis, _opt(tag))


@mcp.tool()
def add_sphere(geom_tag: str, dims: int, r: float, pos: List[float], tag: str = "") -> Dict[str, Any]:
    """Add a sphere to a geometry sequence."""
    return get_backend().add_sphere(geom_tag, dims, r, pos, _opt(tag))


@mcp.tool()
def boolean_op(geom_tag: str, operation: str, inputs: List[str]) -> Dict[str, Any]:
    """Boolean combine geometry features (union|intersect|difference)."""
    return get_backend().boolean_op(geom_tag, operation, inputs)


@mcp.tool()
def import_geometry(geom_tag: str, filename: str, type: str = "") -> Dict[str, Any]:
    """Import a geometry from a CAD/file format."""
    return get_backend().import_geometry(geom_tag, filename, _opt(type))


# ----------------------------------------------------------------------
# Physics & materials
# ----------------------------------------------------------------------

@mcp.tool()
def add_physics(tag: str, interface: str, settings: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Add a physics interface (ht, spf, tds, es, solid, ...)."""
    return get_backend().add_physics(tag, interface, settings or {})


@mcp.tool()
def add_material(tag: str, material: str, selection: str = "") -> Dict[str, Any]:
    """Add a material to the model."""
    return get_backend().add_material(tag, material, _opt(selection))


# ----------------------------------------------------------------------
# Mesh / studies / solve
# ----------------------------------------------------------------------

@mcp.tool()
def build_mesh(mesh_tag: str = "mesh1") -> Dict[str, Any]:
    """Build the mesh."""
    return get_backend().build_mesh(mesh_tag)


@mcp.tool()
def add_study(tag: str, study_type: str, settings: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Add a study (Stationary|TimeDependent|Parametric|Eigenfrequency)."""
    return get_backend().add_study(tag, study_type, settings or {})


@mcp.tool()
def run_solver(study_tag: str) -> Dict[str, Any]:
    """Run the solver for a study."""
    return get_backend().run_solver(study_tag)


@mcp.tool()
def solver_status(study_tag: str) -> Dict[str, Any]:
    """Report whether a study has been solved."""
    return get_backend().solver_status(study_tag)


# ----------------------------------------------------------------------
# Post-processing
# ----------------------------------------------------------------------

@mcp.tool()
def evaluate(expr: str, dataset: str = "dset1") -> Dict[str, Any]:
    """Evaluate an expression (or global evaluation) and return data."""
    return get_backend().evaluate(expr, dataset)


@mcp.tool()
def export_results(export_type: str, filename: str, settings: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Export results (plot/data) to a file."""
    return get_backend().export_results(export_type, filename, settings or {})


# ----------------------------------------------------------------------
# Generic escape hatch
# ----------------------------------------------------------------------

@mcp.tool()
def exec_model_api(code: str) -> Dict[str, Any]:
    """Run arbitrary COMSOL Java API code.

    Provide either a full class with `public static String run(Model model)`,
    or a Java snippet body; it will be wrapped automatically and executed in
    the COMSOL JVM (best-effort in live mode, always via compile+run in
    batch mode).
    """
    return get_backend().exec_model_api(code)


@mcp.tool()
def generate_model_java(
    filepath: str,
    class_name: str = "GeneratedModel",
    model_version: str = "6.2",
    spec: Dict[str, Any] = {},
) -> Dict[str, Any]:
    """Generate a standalone, compilable COMSOL Java model source file.

    Works WITHOUT COMSOL installed. Use it on a COMSOL-less machine to prepare a
    Java model, then move the file to a COMSOL machine and compile it:
        comsolcompile <file>.java
        comsolbatch -java <ClassName>
    ``spec`` may carry geometries/physics/materials/studies/save to shape the code.
    The produced file still needs COMSOL to actually compile into a .mph.
    """
    from comsol_mcp.java_gen import write_model_java

    return write_model_java(filepath, class_name, model_version, spec or {})


if __name__ == "__main__":
    mcp.run()
