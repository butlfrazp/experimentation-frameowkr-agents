"""Executable that loads and invokes a Python callable from a module."""

from __future__ import annotations

import importlib.util
import inspect
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

from ..constants import PROJECT_ROOT
from ..logger import get_logger
from ..models import DataModelRow, ModuleExecutableConfig
from .base import BaseExecutable

log = get_logger(__name__)


class ModuleExecutable(BaseExecutable):
    """Load a module from disk and execute a named callable."""

    def __init__(self, row: DataModelRow, config: ModuleExecutableConfig) -> None:
        super().__init__(row, config)
        self._original_sys_path = None
        self._module = self._load_module(config)
        self._target = self._resolve_target(self._module, config.processor)

    def execute(self, **kwargs) -> DataModelRow:
        callable_obj = self._target
        try:
            result = self._invoke_callable(callable_obj, kwargs)
            if isinstance(result, DataModelRow):
                return result
            self._row.data_output = result
            return self._row
        except Exception as exc:  # pragma: no cover - defensive
            from ..models import DataModelRowError

            log.exception("Executable failed", exc_info=exc)
            self._row.error = DataModelRowError(message=str(exc), code=500)
            return self._row
        finally:
            # Cleanup python paths when execution is complete
            self._cleanup_python_paths()

    # ------------------------------------------------------------------
    def _load_module(self, config: ModuleExecutableConfig) -> ModuleType:
        # Setup custom Python paths if specified (keep them for entire execution)
        self._setup_python_paths(config)

        raw_path = Path(config.path)
        if not raw_path.is_absolute():
            # Try current working directory first, then project root
            cwd_path = Path.cwd() / raw_path
            cwd_py_path = Path.cwd() / f"{raw_path}.py"

            if cwd_path.exists():
                raw_path = cwd_path.resolve()
            elif cwd_py_path.exists():
                raw_path = cwd_py_path.resolve()
            else:
                # Fallback to project root
                project_path = PROJECT_ROOT / raw_path
                project_py_path = PROJECT_ROOT / f"{raw_path}.py"
                if project_path.exists():
                    raw_path = project_path.resolve()
                elif project_py_path.exists():
                    raw_path = project_py_path.resolve()
                else:
                    raw_path = (PROJECT_ROOT / raw_path).resolve()

        if raw_path.is_dir():
            raw_path = raw_path / f"{config.processor}.py"
        if not raw_path.exists():
            raise FileNotFoundError(f"Executable module not found: {raw_path}")

        spec = importlib.util.spec_from_file_location(raw_path.stem, raw_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load module from {raw_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[arg-type]
        return module

    def _resolve_target(self, module: ModuleType, attr: str) -> Callable[..., Any]:
        if not hasattr(module, attr):
            raise AttributeError(f"Module '{module.__name__}' does not expose '{attr}'")
        target = getattr(module, attr)
        if inspect.isclass(target):
            instance = target()  # type: ignore[call-arg]
            if hasattr(instance, "run"):
                return instance.run
            raise TypeError(f"Class '{attr}' in module '{module.__name__}' lacks a 'run' method")
        if not callable(target):
            raise TypeError(f"Attribute '{attr}' in module '{module.__name__}' is not callable")
        return target

    def _invoke_callable(self, target: Callable[..., Any], kwargs: dict[str, Any]) -> Any:
        signature = inspect.signature(target)
        bound = {}
        if "row" in signature.parameters:
            bound["row"] = self._row
        elif "data_model_row" in signature.parameters:
            bound["data_model_row"] = self._row
        else:
            # If no row parameter, try passing individual fields and the row via kwargs
            bound.update(kwargs)
            bound["row"] = self._row
            bound["data_model_row"] = self._row
        return target(**bound)

    def _discover_and_import_evaluators(self, path: Path) -> None:
        """Discover and import Python modules in the given path to register evaluators."""
        try:
            # Look for Python files in the directory
            for py_file in path.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue  # Skip __init__.py, __pycache__, etc.

                module_name = py_file.stem
                try:
                    # Import the module to trigger evaluator registration
                    spec = importlib.util.spec_from_file_location(module_name, py_file)
                    if spec is not None and spec.loader is not None:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        log.debug(f"Imported evaluator module: {module_name} from {py_file}")
                except Exception as e:
                    log.debug(f"Failed to import {module_name} from {py_file}: {e}")

        except Exception as e:
            log.debug(f"Error discovering evaluators in {path}: {e}")

    def _setup_python_paths(self, config: ModuleExecutableConfig) -> None:
        """Add custom directories to sys.path for module loading and discover evaluators."""
        if not config.python_path:
            return

        # Store original sys.path for cleanup
        self._original_sys_path = sys.path.copy()

        # Convert relative paths to absolute and add to sys.path
        for path_str in config.python_path:
            path = Path(path_str)
            if not path.is_absolute():
                # Try relative to current working directory first
                cwd_path = Path.cwd() / path
                if cwd_path.exists():
                    path = cwd_path.resolve()
                else:
                    # Fallback to project root
                    path = (PROJECT_ROOT / path).resolve()

            # Add to sys.path if directory exists and not already present
            path_str_resolved = str(path)
            if path.exists() and path.is_dir() and path_str_resolved not in sys.path:
                sys.path.insert(0, path_str_resolved)
                log.debug(f"Added to Python path: {path_str_resolved}")

                # Auto-discover and import Python modules in this path
                self._discover_and_import_evaluators(path)

    def _cleanup_python_paths(self) -> None:
        """Restore original sys.path after module loading."""
        if self._original_sys_path is not None:
            sys.path[:] = self._original_sys_path
            self._original_sys_path = None
