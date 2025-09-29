"""Executable that loads and invokes a Python callable from a module."""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from ..constants import PROJECT_ROOT
from ..logger import get_logger
from ..models import DataModelRow, ModuleExecutableConfig
from .base import BaseExecutable

log = get_logger(__name__)


class ModuleExecutable(BaseExecutable):
    """Load a module from disk and execute a named callable."""

    def __init__(self, row: DataModelRow, config: ModuleExecutableConfig) -> None:
        super().__init__(row, config)
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

    # ------------------------------------------------------------------
    def _load_module(self, config: ModuleExecutableConfig) -> ModuleType:
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
            raise AttributeError(
                f"Module '{module.__name__}' does not expose '{attr}'"
            )
        target = getattr(module, attr)
        if inspect.isclass(target):
            instance = target()  # type: ignore[call-arg]
            if hasattr(instance, "run"):
                return getattr(instance, "run")
            raise TypeError(
                f"Class '{attr}' in module '{module.__name__}' lacks a 'run' method"
            )
        if not callable(target):
            raise TypeError(
                f"Attribute '{attr}' in module '{module.__name__}' is not callable"
            )
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
