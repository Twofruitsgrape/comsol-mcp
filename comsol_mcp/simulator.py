"""In-memory model used when COMSOL is not available (dry-run mode).

This lets the entire tool pipeline be exercised, imported and unit-tested
without a COMSOL installation. It does NOT perform real physics; it only
tracks the operations that were issued and returns plausible mock results.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SimModel:
    """A fake COMSOL model that records operations."""

    geometries: List[Dict[str, Any]] = field(default_factory=list)
    physics: List[Dict[str, Any]] = field(default_factory=list)
    materials: List[Dict[str, Any]] = field(default_factory=list)
    mesh_built: bool = False
    studies: List[Dict[str, Any]] = field(default_factory=list)
    solved_studies: List[str] = field(default_factory=list)
    model_path: Optional[str] = None
    ops_log: List[str] = field(default_factory=list)

    def _log(self, op: str, **kw) -> Dict[str, Any]:
        entry = {"op": op, **kw}
        self.ops_log.append(entry)
        return entry

    # ---- model lifecycle ----
    def new(self, version: str = "6.2") -> Dict[str, Any]:
        self.__init__()
        return self._log("new", version=version)

    def load(self, path: str) -> Dict[str, Any]:
        self.model_path = str(path)
        return self._log("load", path=path)

    def save(self, path: Optional[str] = None) -> Dict[str, Any]:
        target = path or self.model_path
        if not target:
            raise ValueError("no path given and no model loaded")
        self.model_path = str(target)
        return self._log("save", path=target)

    # ---- geometry ----
    def add_block(self, geom_tag: str, dims: int, size, pos, tag: Optional[str] = None) -> Dict[str, Any]:
        ftag = tag or f"blk{len(self.geometries) + 1}"
        self.geometries.append({"type": "Block", "geom": geom_tag, "tag": ftag, "dims": dims, "size": list(size), "pos": list(pos)})
        return self._log("add_block", tag=ftag, geom=geom_tag)

    def add_cylinder(self, geom_tag: str, dims: int, r: float, h: float, pos, axis: str = "z", tag: Optional[str] = None) -> Dict[str, Any]:
        ftag = tag or f"cyl{len(self.geometries) + 1}"
        self.geometries.append({"type": "Cylinder", "geom": geom_tag, "tag": ftag, "r": r, "h": h, "pos": list(pos), "axis": axis})
        return self._log("add_cylinder", tag=ftag, geom=geom_tag)

    def add_sphere(self, geom_tag: str, dims: int, r: float, pos, tag: Optional[str] = None) -> Dict[str, Any]:
        ftag = tag or f"sph{len(self.geometries) + 1}"
        self.geometries.append({"type": "Sphere", "geom": geom_tag, "tag": ftag, "r": r, "pos": list(pos)})
        return self._log("add_sphere", tag=ftag, geom=geom_tag)

    def boolean_op(self, geom_tag: str, operation: str, inputs) -> Dict[str, Any]:
        ftag = f"bool{len(self.geometries) + 1}"
        self.geometries.append({"type": "Boolean", "geom": geom_tag, "tag": ftag, "op": operation, "inputs": list(inputs)})
        return self._log("boolean_op", tag=ftag, op=operation)

    def import_geometry(self, geom_tag: str, filename: str, type: Optional[str] = None) -> Dict[str, Any]:
        ftag = f"imp{len(self.geometries) + 1}"
        self.geometries.append({"type": "Import", "geom": geom_tag, "tag": ftag, "filename": filename})
        return self._log("import_geometry", tag=ftag, filename=filename)

    # ---- physics ----
    def add_physics(self, tag: str, interface: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.physics.append({"tag": tag, "interface": interface, "settings": settings or {}})
        return self._log("add_physics", tag=tag, interface=interface)

    def add_material(self, tag: str, material: str, selection: Optional[str] = None) -> Dict[str, Any]:
        self.materials.append({"tag": tag, "material": material, "selection": selection})
        return self._log("add_material", tag=tag, material=material)

    # ---- mesh / study / solve ----
    def build_mesh(self, mesh_tag: str = "mesh1") -> Dict[str, Any]:
        self.mesh_built = True
        return self._log("build_mesh", tag=mesh_tag)

    def add_study(self, tag: str, study_type: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.studies.append({"tag": tag, "type": study_type, "settings": settings or {}})
        return self._log("add_study", tag=tag, type=study_type)

    def solve(self, study_tag: str) -> Dict[str, Any]:
        if not any(s["tag"] == study_tag for s in self.studies):
            raise ValueError(f"study {study_tag} does not exist")
        self.solved_studies.append(study_tag)
        return self._log("solve", tag=study_tag)

    def evaluate(self, expr: str, dataset: str = "dset1") -> Dict[str, Any]:
        # Deterministic-ish mock so callers get structured data.
        rows = [[0.0, 293.15], [1.0, 301.20], [2.0, 310.55]]
        return {
            "op": "evaluate",
            "expr": expr,
            "dataset": dataset,
            "columns": ["t", "value"],
            "rows": rows,
        }

    def export_results(self, export_type: str, filename: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._log("export", type=export_type, filename=filename)

    def model_info(self) -> Dict[str, Any]:
        return {
            "loaded": self.model_path is not None,
            "path": self.model_path,
            "geometries": [g["tag"] for g in self.geometries],
            "physics": [p["tag"] for p in self.physics],
            "materials": [m["tag"] for m in self.materials],
            "mesh_built": self.mesh_built,
            "studies": [s["tag"] for s in self.studies],
            "solved": list(self.solved_studies),
        }


_sim_instance: Optional[SimModel] = None


def get_simulator() -> SimModel:
    """Return a shared in-memory model for the dry-run backend."""
    global _sim_instance
    if _sim_instance is None:
        _sim_instance = SimModel()
    return _sim_instance
