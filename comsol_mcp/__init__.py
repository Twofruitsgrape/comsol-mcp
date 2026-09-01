"""comsol-mcp: drive COMSOL Multiphysics from AI agents.

A Model Context Protocol server with live GUI control and a full
modeling -> definition -> computation -> post-processing pipeline.
"""

__version__ = "0.1.0"

from comsol_mcp.config import config  # noqa: F401  (safe even without COMSOL)

__all__ = ["__version__", "config"]
