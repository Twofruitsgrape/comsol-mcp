"""
Configuration management for the COMSOL MCP server.

Design goals (portability):
  * Works from ANY working directory. COMSOL is located via COMSOL_HOME first,
    then an automatic search across native Windows, WSL and Linux/macOS layouts.
  * Logs and temporary artifacts NEVER land in the current working directory;
    they go to COMSOL_MCP_LOG_DIR (default: system temp / "comsol_mcp").
  * All model paths are supplied by the caller (absolute, or relative to
    COMSOL_MCP_WORK_DIR).
"""

import logging
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("comsol_mcp")


@dataclass
class ComsolInstall:
    """Location of the COMSOL Multiphysics installation."""

    root: Optional[Path] = None
    comsolcompile: Optional[Path] = None
    comsolbatch: Optional[Path] = None
    comsolgui: Optional[Path] = None
    found: bool = False

    def as_dict(self) -> dict:
        return {
            "root": str(self.root) if self.root else None,
            "comsolcompile": str(self.comsolcompile) if self.comsolcompile else None,
            "comsolbatch": str(self.comsolbatch) if self.comsolbatch else None,
            "comsolgui": str(self.comsolgui) if self.comsolgui else None,
            "found": self.found,
        }


def _check_comsol_root(root: Path) -> ComsolInstall:
    """Inspect a Multiphysics root directory for the executables we need."""
    install = ComsolInstall(root=root, found=False)
    bin_dir = root / "bin"
    if not bin_dir.exists():
        return install

    if sys.platform == "win32":
        exe_dir = bin_dir / "win64"
        if not exe_dir.exists():
            exe_dir = bin_dir
        cc = exe_dir / "comsolcompile.exe"
        cb = exe_dir / "comsolbatch.exe"
        cg = exe_dir / "comsol.exe"
    else:
        exe_dir = bin_dir
        cc = exe_dir / "comsolcompile"
        cb = exe_dir / "comsolbatch"
        cg = exe_dir / "comsol"

    if cc.exists():
        install.comsolcompile = cc
    if cb.exists():
        install.comsolbatch = cb
    if cg.exists():
        install.comsolgui = cg
    if install.comsolcompile or install.comsolbatch or install.comsolgui:
        install.found = True
    return install


def _iter_version_dirs(base: Path):
    """Yield Multiphysics roots from a COMSOL base directory."""
    if not base.exists():
        return
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        if "COMSOL" not in child.name.upper():
            continue
        mp = child / "Multiphysics"
        if mp.exists():
            yield mp


def _resolve_comsol_home(value: str) -> ComsolInstall:
    """Resolve a user-supplied COMSOL_HOME to a valid install.

    Tolerant of the user pointing at the *base* dir (.../COMSOL), a *version*
    dir (.../COMSOL62), or the *Multiphysics* dir itself.
    """
    p = Path(value)
    if not p.exists():
        return ComsolInstall(found=False)
    # case A: directly the Multiphysics dir
    r = _check_comsol_root(p)
    if r.found:
        return r
    # case B: a version dir (has a Multiphysics child)
    r = _check_comsol_root(p / "Multiphysics")
    if r.found:
        return r
    # case C: a base dir -> scan version subdirs
    if p.is_dir():
        for mp in _iter_version_dirs(p):
            r = _check_comsol_root(mp)
            if r.found:
                return r
    return ComsolInstall(found=False)


def _registry_comsol_bases():
    """Yield candidate base/install dirs from the Windows registry.

    Catches custom install locations (e.g. non-default drives) that the fixed
    drive list misses.
    """
    if sys.platform != "win32":
        return
    try:
        import winreg
    except ImportError:
        return
    for hive, sub in (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\COMSOL"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\COMSOL"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\COMSOL"),
    ):
        try:
            with winreg.OpenKey(hive, sub) as key:
                i = 0
                while True:
                    try:
                        name = winreg.EnumKey(key, i)
                    except OSError:
                        break
                    i += 1
                    try:
                        with winreg.OpenKey(key, name) as vkey:
                            for val_name in ("COMSOLROOT", "InstallDir", "InstDir"):
                                try:
                                    inst = winreg.QueryValueEx(vkey, val_name)[0]
                                except OSError:
                                    continue
                                if inst:
                                    yield Path(inst)
                    except OSError:
                        continue
        except OSError:
            continue


def find_comsol_install() -> ComsolInstall:
    """Locate a COMSOL installation.

    Search order:
      1. COMSOL_HOME environment variable.
      2. Native Windows: C:/Program Files/COMSOL, D:/..., E:/...
      3. Linux / macOS / WSL: /usr/local/comsol, /opt/comsol, ~/comsol,
         and /mnt/{c,d,e}/Program Files/COMSOL (WSL mounts).
    """
    comsol_home = os.getenv("COMSOL_HOME")
    if comsol_home:
        result = _resolve_comsol_home(comsol_home)
        if result.found:
            return result

    if sys.platform == "win32":
        # Registry first (custom installs), then well-known bases.
        bases = list(_registry_comsol_bases()) + [
            Path("C:/Program Files/COMSOL"),
            Path("C:/Program Files (x86)/COMSOL"),
            Path("D:/Program Files/COMSOL"),
            Path("E:/Program Files/COMSOL"),
        ]
    else:
        home = Path.home()
        bases = [
            Path("/usr/local/comsol"),
            Path("/opt/comsol"),
            home / "comsol",
            Path("/mnt/c/Program Files/COMSOL"),
            Path("/mnt/d/Program Files/COMSOL"),
            Path("/mnt/e/Program Files/COMSOL"),
        ]

    for base in bases:
        try:
            # `base` may itself be the Multiphysics directory.
            direct = _check_comsol_root(base)
            if direct.found:
                return direct
            for mp in _iter_version_dirs(base):
                result = _check_comsol_root(mp)
                if result.found:
                    return result
        except OSError:
            continue

    return ComsolInstall(found=False)


class Config:
    """Runtime configuration, sourced from environment variables with sane
    portable defaults."""

    def __init__(self) -> None:
        self.comsol_install = find_comsol_install()

        if not self.comsol_install.found:
            log.warning(
                "COMSOL installation NOT detected -> running in dry-run mode. "
                "Set COMSOL_HOME (point at the .../Multiphysics directory) in the MCP "
                "server env to enable real .mph operations."
            )

        log_dir = os.getenv("COMSOL_MCP_LOG_DIR")
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path(tempfile.gettempdir()) / "comsol_mcp"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        work_dir = os.getenv("COMSOL_MCP_WORK_DIR")
        self.work_dir = Path(work_dir) if work_dir else Path(os.getcwd())

        self.bridge_port = int(os.getenv("BRIDGE_PORT", "8731"))
        self.web_port = int(os.getenv("WEB_PORT", "8080"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        dry = os.getenv("COMSOL_MCP_DRYRUN", "").lower()
        self.dry_run = dry in ("1", "true", "yes") or (not self.comsol_install.found)

        # Optional override template for launching the COMSOL GUI with the
        # bridge class. Available placeholders: {comsol_gui}, {class_file},
        # {port}. When empty, a default command is built from the install.
        self.gui_launch_template = os.getenv("COMSOL_GUI_LAUNCH", "")

    def to_dict(self) -> dict:
        return {
            "comsol_install": self.comsol_install.as_dict(),
            "log_dir": str(self.log_dir),
            "work_dir": str(self.work_dir),
            "bridge_port": self.bridge_port,
            "web_port": self.web_port,
            "log_level": self.log_level,
            "dry_run": self.dry_run,
        }


config = Config()


def get_bridge_java_path() -> Path:
    """Absolute path to the shipped ComsolBridge.java (works from any cwd)."""
    try:
        from importlib.resources import files

        p = files("comsol_mcp.bridge").joinpath("ComsolBridge.java")
        if p.exists():
            return Path(str(p))
    except Exception:
        pass
    return Path(__file__).resolve().parent / "bridge" / "ComsolBridge.java"


def get_comsolops_java_path() -> Path:
    """Absolute path to the shipped ComsolOps.java."""
    try:
        from importlib.resources import files

        p = files("comsol_mcp.bridge").joinpath("ComsolOps.java")
        if p.exists():
            return Path(str(p))
    except Exception:
        pass
    return Path(__file__).resolve().parent / "bridge" / "ComsolOps.java"
