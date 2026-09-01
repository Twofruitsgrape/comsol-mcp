"""Exception hierarchy for the COMSOL MCP package."""


class ComsolMCPError(Exception):
    """Base error for all COMSOL MCP operations."""


class ComsolNotFoundError(ComsolMCPError):
    """COMSOL installation could not be located."""


class BridgeError(ComsolMCPError):
    """Communication with the live COMSOL GUI bridge failed."""


class CompilationError(ComsolMCPError):
    """Compiling a COMSOL Java model failed."""


class SolveError(ComsolMCPError):
    """The solver failed or did not converge."""


class ModelError(ComsolMCPError):
    """The model is in an invalid state for the requested operation."""
