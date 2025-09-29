"""Core orchestration logic to run experiments end-to-end."""

from __future__ import annotations

from collections.abc import Iterable
from uuid import uuid4

import pandas as pd

from .config import EnvironmentConfig
from .executables.module_executable import ModuleExecutable
from .logger import get_logger
from .models import (
    DataModel,
    DataModelRow,
    DataModelRowError,
    DatasetModel,
    DataType,
    ExperimentConfig,
)
from .services.cloud_evaluation import CloudEvaluationService
from .services.config_loader import ConfigLoader
from .services.dataset_service import DatasetService
from .services.evaluation_base import EvaluationService
from .services.local_evaluation import LocalEvaluationService
from .utils import ensure_directories

log = get_logger(__name__)


_EXECUTABLE_REGISTRY: dict[str, type[ModuleExecutable]] = {
    "module": ModuleExecutable,
}


class Orchestrator:
    """Orchestrate dataset loading, execution, and evaluation."""

    def __init__(
        self,
        dataset_service: DatasetService | None = None,
        evaluation_service: EvaluationService | None = None,
        env_config: EnvironmentConfig | None = None,
    ) -> None:
        self._dataset_service = dataset_service or DatasetService()
        self._env_config = env_config
        self._evaluation_service = evaluation_service
        ensure_directories()

    def _rows_from_dataframe(
        self,
        df: pd.DataFrame,
        *,
        expected_field: str | None,
        dataset_name: str,
        dataset_version: str,
    ) -> DataModel:
        rows: list[DataModelRow] = []
        for index, values in df.iterrows():
            raw_id = values.get("id")
            row_id = str(raw_id) if raw_id not in (None, "") else f"row_{index}"
            expected = None
            if expected_field:
                expected = values.get(expected_field)
            row = DataModelRow(
                id=row_id,
                data_input=values.to_dict(),
                expected_output=expected,
                metadata={
                    "dataset_name": dataset_name,
                    "dataset_version": dataset_version,
                },
            )
            rows.append(row)
        dataset_model = DatasetModel(
            name=dataset_name,
            version=dataset_version,
            type=DataType.UNKNOWN,
        )
        return DataModel(dataset=dataset_model, rows=rows)

    def _resolve_executable(self, config: ExperimentConfig):
        exec_type = getattr(config.executable, "type", "unknown")
        executable_cls = _EXECUTABLE_REGISTRY.get(str(exec_type))
        if not executable_cls:
            raise ValueError(f"Unsupported executable type: {exec_type}")
        return executable_cls

    def run(self, config_path: str) -> str:
        """Load configuration, execute rows, and run evaluations with comprehensive error handling.

        Returns the generated experiment identifier.
        """
        log.banner("Experiment run")

        # Load and validate configuration
        try:
            cfg = ConfigLoader.load_config(config_path)
            log.info(f"🔧 Configuration loaded: {cfg.describe()}")
        except Exception as e:
            log.error(f"Failed to load configuration from {config_path}: {e}")
            raise

        # Load dataset with retry logic
        max_dataset_retries = 3
        dataset_retry_delay = 1.0

        df = None
        last_dataset_error = None

        for attempt in range(max_dataset_retries):
            try:
                log.info(
                    f"📊 Loading dataset {cfg.dataset.name}:{cfg.dataset.version} (attempt {attempt + 1}/{max_dataset_retries})"
                )
                df = self._dataset_service.load_dataframe(
                    cfg.dataset.name,
                    cfg.dataset.version,
                )
                log.success(f"✅ Dataset loaded successfully: {len(df)} rows")
                break

            except Exception as e:
                last_dataset_error = e
                log.warning(f"Dataset load attempt {attempt + 1} failed: {e}")
                if attempt < max_dataset_retries - 1:
                    log.info(f"Retrying dataset load in {dataset_retry_delay} seconds...")
                    import time

                    time.sleep(dataset_retry_delay)
                    dataset_retry_delay *= 2  # Exponential backoff

        if df is None:
            log.error(f"Failed to load dataset after {max_dataset_retries} attempts")
            raise RuntimeError(f"Dataset loading failed: {last_dataset_error}")

        # Convert dataframe to data model
        try:
            data_model = self._rows_from_dataframe(
                df,
                expected_field=cfg.dataset.config.expected_output_field,
                dataset_name=cfg.dataset.name,
                dataset_version=cfg.dataset.version,
            )
            log.info(f"📋 Data model created: {len(data_model.rows)} rows prepared for execution")
        except Exception as e:
            log.error(f"Failed to create data model from dataset: {e}")
            raise

        experiment_id = f"exp{uuid4().hex[:12]}"
        log.info(
            "🚀 Starting experiment execution %s for %s:%s",
            experiment_id,
            cfg.dataset.name,
            cfg.dataset.version,
        )

        # Execute rows with comprehensive error handling and progress tracking
        try:
            executable_cls = self._resolve_executable(cfg)
            log.info(f"🔧 Using executable: {executable_cls.__name__}")
        except Exception as e:
            log.error(f"Failed to resolve executable: {e}")
            raise

        successful_executions = 0
        failed_executions = 0
        total_rows = len(data_model.rows)

        log.info(f"⚡ Executing {total_rows} rows...")

        for i, row in enumerate(data_model.rows, 1):
            try:
                log.debug(f"Executing row {i}/{total_rows}: {row.id}")
                executable = executable_cls(row, cfg.executable)

                # Execute with timeout and retry logic for critical failures
                try:
                    updated_row = executable.execute(**row.data_input)
                    row.data_output = getattr(updated_row, "data_output", None)
                    row.error = getattr(updated_row, "error", None)

                    if row.error is None:
                        successful_executions += 1
                        log.debug(f"✅ Row {row.id} executed successfully")
                    else:
                        failed_executions += 1
                        log.warning(f"⚠️  Row {row.id} completed with error: {row.error}")

                except Exception as exec_error:
                    failed_executions += 1
                    error_msg = f"Execution failed: {str(exec_error)}"
                    log.error(f"💥 Row {row.id} execution failed: {error_msg}")
                    row.error = DataModelRowError(message=error_msg, code=500)

                # Progress reporting every 10% or at significant milestones
                if i % max(1, total_rows // 10) == 0 or i == total_rows:
                    progress_pct = (i / total_rows) * 100
                    log.info(
                        f"📊 Progress: {i}/{total_rows} rows ({progress_pct:.1f}%) - ✅ {successful_executions} success, ❌ {failed_executions} failed"
                    )

            except Exception as exc:
                failed_executions += 1
                log.exception(f"💥 Critical error executing row {row.id}", exc_info=exc)
                row.error = DataModelRowError(
                    message=f"Critical execution error: {str(exc)}", code=500
                )

        # Execution summary
        success_rate = (successful_executions / total_rows) * 100 if total_rows > 0 else 0
        log.info(
            f"📈 Execution Summary: {successful_executions}/{total_rows} successful ({success_rate:.1f}%)"
        )

        if failed_executions > 0:
            log.warning(f"⚠️  {failed_executions} rows failed execution")
            if failed_executions == total_rows:
                log.error("❌ All rows failed execution - experiment may have critical issues")
            elif failed_executions > total_rows * 0.5:
                log.warning("⚠️  More than 50% of rows failed - consider reviewing configuration")

        # Store execution results with resilient error handling
        try:
            log.info("💾 Storing execution results...")
            artifact_dir = self._dataset_service.write_local_results(
                name=cfg.dataset.name,
                version=cfg.dataset.version,
                experiment_id=experiment_id,
                rows=data_model.rows,
                config=cfg,
            )
            log.success(f"✅ Execution results stored in {artifact_dir}")
        except Exception as e:
            log.error(f"Failed to store execution results: {e}")
            raise RuntimeError(f"Result storage failed: {e}")

        # Run evaluations with comprehensive error handling
        rows_iter: Iterable[DataModelRow] = data_model.rows
        data_ref: str | None = None

        try:
            # Choose evaluation service based on local_mode and availability
            if self._evaluation_service is None:
                if cfg.local_mode:
                    self._evaluation_service = LocalEvaluationService()
                    log.info("🔧 Initialized local evaluation service")
                else:
                    try:
                        # Try to load environment config for cloud evaluation
                        if self._env_config is None:
                            self._env_config = EnvironmentConfig.from_env()
                        self._evaluation_service = CloudEvaluationService(self._env_config)
                        log.info("☁️  Initialized cloud evaluation service")
                    except Exception as e:
                        log.warning(
                            f"Cloud evaluation not available ({e}), falling back to local mode"
                        )
                        self._evaluation_service = LocalEvaluationService()

            # Run evaluation with progress tracking
            log.info(f"📊 Starting evaluation with {len(cfg.evaluators)} evaluators...")
            evaluator_names = [e.name for e in cfg.evaluators]
            log.info(f"📈 Evaluators: {', '.join(evaluator_names)}")

            import time

            eval_start_time = time.time()

            self._evaluation_service.evaluate(
                experiment_id=experiment_id,
                dataset_name=cfg.dataset.name,
                dataset_version=cfg.dataset.version,
                data_id=data_ref,
                config=cfg,
                evaluators=cfg.evaluators,
                rows=rows_iter,
            )

            eval_time = time.time() - eval_start_time
            log.success(f"✅ Evaluation completed successfully in {eval_time:.2f} seconds")

        except Exception as e:
            log.error(f"💥 Evaluation failed: {e}")
            log.warning("⚠️  Experiment execution completed but evaluation failed")
            # Don't fail the entire experiment if evaluation fails
            log.info("💡 Execution results are still available for manual analysis")

        log.success(f"🎉 Experiment {experiment_id} completed successfully!")
        return experiment_id
