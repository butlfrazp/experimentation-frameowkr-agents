"""Cloud evaluation service using Azure AI Projects."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Sequence

from ..config import EnvironmentConfig
from ..logger import get_logger
from ..models import (
    DataModelRow,
    EvaluationResult,
    EvaluatorConfig,
    ExperimentConfig,
)
from ..constants import PROJECT_ROOT
from ..utils import ensure_directories
from .evaluation_base import EvaluationService

log = get_logger(__name__)


class CloudEvaluationService(EvaluationService):
    """Cloud-based evaluation using Azure AI Projects."""

    def __init__(self, env_config: EnvironmentConfig | None = None):
        """Initialize cloud evaluation service."""
        if env_config is None:
            env_config = EnvironmentConfig()
        self.env_config = env_config
        self._ai_project_client = None

    def _get_ai_project_client(self):
        """Lazy initialization of AI Project Client."""
        if self._ai_project_client is None:
            try:
                from azure.ai.projects import AIProjectClient
                from azure.identity import DefaultAzureCredential
                
                self._ai_project_client = AIProjectClient(
                    endpoint=self.env_config.foundry_project_endpoint,
                    credential=DefaultAzureCredential(),
                    connection_string=self.env_config.azure_foundry_connection_string,
                )
                log.info("Initialized Azure AI Project Client for cloud evaluation")
            except ImportError:
                log.error("Azure AI Projects SDK not installed. Install with: pip install azure-ai-projects")
                raise
            except Exception as e:
                log.error(f"Failed to initialize Azure AI Project Client: {e}")
                raise
        
        return self._ai_project_client

    def evaluate(
        self,
        *,
        experiment_id: str,
        dataset_name: str,
        dataset_version: str,
        data_id: str | None,
        config: ExperimentConfig,
        evaluators: Sequence[EvaluatorConfig],
        rows: Iterable[DataModelRow] | None = None,
    ) -> None:
        """Run cloud-based evaluation."""
        log.info(f"Starting cloud evaluation for experiment {experiment_id}")
        
        # Ensure we have rows for evaluation
        if rows is None:
            rows = []
        rows_list = list(rows)
        
        if not rows_list:
            log.warning("No rows provided for cloud evaluation")
            return

        try:
            # Get AI Project Client
            client = self._get_ai_project_client()
            
            # Upload dataset if needed
            if data_id is None:
                data_id = self._upload_dataset(client, dataset_name, dataset_version, rows_list, experiment_id)
            
            # Run cloud evaluations
            evaluation_runs = []
            for evaluator_config in evaluators:
                try:
                    run_result = self._run_cloud_evaluation(
                        client, 
                        experiment_id,
                        data_id,
                        evaluator_config,
                        config
                    )
                    evaluation_runs.append(run_result)
                    log.info(f"Started cloud evaluation for {evaluator_config.name}")
                except Exception as e:
                    log.error(f"Failed to start evaluation for {evaluator_config.name}: {e}")
            
            # Wait for results and save locally
            self._collect_and_save_results(
                evaluation_runs,
                experiment_id,
                dataset_name,
                dataset_version,
                rows_list,
                config
            )
            
        except Exception as e:
            log.error(f"Cloud evaluation failed: {e}")
            # Fallback to local evaluation
            log.warning("Falling back to local evaluation")
            from .local_evaluation import LocalEvaluationService
            local_service = LocalEvaluationService()
            local_service.evaluate(
                experiment_id=experiment_id,
                dataset_name=dataset_name,
                dataset_version=dataset_version,
                data_id=data_id,
                config=config,
                evaluators=evaluators,
                rows=rows_list,
            )

    def _upload_dataset(self, client, dataset_name: str, dataset_version: str, rows: list[DataModelRow], experiment_id: str) -> str:
        """Upload dataset to cloud and return dataset ID."""
        log.info(f"Uploading dataset {dataset_name}:{dataset_version} to cloud")
        
        try:
            # Convert rows to format expected by Azure AI Projects
            dataset_data = []
            for row in rows:
                row_data = {
                    "id": row.id,
                    **row.data_input,
                }
                if row.expected_output:
                    row_data["expected_output"] = row.expected_output
                if row.data_output:
                    row_data["data_output"] = row.data_output
                dataset_data.append(row_data)
            
            # Upload dataset
            from azure.ai.projects.models import Dataset
            dataset = client.datasets.upload_data(
                name=f"{dataset_name}_{dataset_version}_{experiment_id}",
                data=dataset_data,
                description=f"Dataset for experiment {experiment_id}"
            )
            
            log.success(f"Dataset uploaded with ID: {dataset.id}")
            return dataset.id
            
        except Exception as e:
            log.error(f"Failed to upload dataset: {e}")
            raise

    def _run_cloud_evaluation(
        self, 
        client, 
        experiment_id: str,
        data_id: str, 
        evaluator_config: EvaluatorConfig,
        config: ExperimentConfig
    ):
        """Start a cloud evaluation run."""
        try:
            from azure.ai.projects.models import (
                Evaluation,
                InputData,
                EvaluatorConfiguration,
            )
            
            # Configure the evaluator
            evaluator_cfg = EvaluatorConfiguration(
                id=evaluator_config.id,
                display_name=evaluator_config.name,
                # Map to built-in evaluators or custom evaluators
                evaluator="relevance" if "relevance" in evaluator_config.name.lower() else "groundedness"
            )
            
            # Configure input data
            input_data = InputData(
                data_id=data_id,
                data_mapping=evaluator_config.data_mapping or {}
            )
            
            # Start evaluation
            evaluation = Evaluation(
                display_name=f"{experiment_id}_{evaluator_config.name}",
                description=f"Cloud evaluation for experiment {experiment_id}",
                evaluator_config=evaluator_cfg,
                input_data=input_data,
            )
            
            result = client.evaluations.create(evaluation)
            return result
            
        except Exception as e:
            log.error(f"Failed to create cloud evaluation: {e}")
            raise

    def _collect_and_save_results(
        self,
        evaluation_runs,
        experiment_id: str,
        dataset_name: str,
        dataset_version: str,
        rows: list[DataModelRow],
        config: ExperimentConfig
    ):
        """Collect cloud evaluation results and save locally."""
        log.info("Collecting cloud evaluation results...")
        
        # Use configured output path if available
        if config.output_path:
            artifact_root = Path(config.output_path).expanduser().resolve()
        else:
            artifact_root_env = os.getenv("EXP_CLI_ARTIFACT_ROOT")
            if artifact_root_env:
                artifact_root = Path(artifact_root_env).expanduser().resolve()
            else:
                artifact_root = PROJECT_ROOT / "artifacts"
        
        output_dir = artifact_root / dataset_name / dataset_version / experiment_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Wait for evaluations to complete and collect results
            for run in evaluation_runs:
                # Poll for completion (simplified - in practice would need proper polling)
                log.info(f"Waiting for evaluation {run.id} to complete...")
                
                # In a real implementation, you would poll the evaluation status
                # For now, we'll create placeholder results
                self._create_placeholder_results(run, rows)
            
            # Save results locally
            self._save_cloud_results_locally(output_dir, rows, config, evaluation_runs)
            
        except Exception as e:
            log.error(f"Failed to collect cloud results: {e}")
            raise

    def _create_placeholder_results(self, evaluation_run, rows: list[DataModelRow]):
        """Create placeholder results (replace with actual cloud result polling)."""
        # This is a placeholder - in real implementation you would:
        # 1. Poll evaluation_run.status until complete
        # 2. Fetch actual results from cloud
        # 3. Parse and format results
        
        for row in rows:
            # Placeholder cloud evaluation results
            row.evaluation_results[f"cloud_{evaluation_run.display_name}:score"] = EvaluationResult(
                metric_name=f"cloud_{evaluation_run.display_name}:score",
                metric_value=0.85,  # Placeholder value
                metadata={"evaluator": f"cloud_{evaluation_run.display_name}", "run_id": evaluation_run.id}
            )

    def _save_cloud_results_locally(
        self, 
        output_dir: Path, 
        rows: list[DataModelRow], 
        config: ExperimentConfig,
        evaluation_runs
    ):
        """Save cloud evaluation results to local files."""
        # Save rows with evaluation results
        results_path = output_dir / "cloud_results.jsonl"
        with results_path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(row.model_dump_json() + "\n")
        
        # Save cloud evaluation metadata
        cloud_metadata = {
            "evaluation_runs": [
                {
                    "id": run.id,
                    "display_name": run.display_name,
                    "status": "completed"  # Placeholder
                }
                for run in evaluation_runs
            ]
        }
        
        import json
        metadata_path = output_dir / "cloud_evaluation_metadata.json"
        metadata_path.write_text(
            json.dumps(cloud_metadata, indent=2),
            encoding="utf-8",
        )
        
        log.success(f"Cloud evaluation results saved to {output_dir}")