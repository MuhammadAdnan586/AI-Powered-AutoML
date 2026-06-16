"""
Module 2 - MLflow Tracking Service
Tracks experiments, parameters, metrics, and artifacts
"""

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.lightgbm
from typing import Dict, Any, List, Optional
import logging
import os

logger = logging.getLogger(__name__)

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///artifacts/mlflow.db")
MLFLOW_ARTIFACT_ROOT = os.getenv("MLFLOW_ARTIFACT_ROOT", "./artifacts/mlflow")


class MLflowTracker:
    
    def __init__(self, experiment_name: str = "AutoML_Experiment"):
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        self.experiment_name = experiment_name
        
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                self.experiment_id = mlflow.create_experiment(
                    experiment_name,
                    artifact_location=MLFLOW_ARTIFACT_ROOT
                )
            else:
                self.experiment_id = experiment.experiment_id
        except Exception as e:
            logger.warning(f"MLflow setup warning: {str(e)}")
            self.experiment_id = None
        
        mlflow.set_experiment(experiment_name)

    def start_automl_run(
        self, 
        session_id: str,
        dataset_info: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Optional[str]:
        """Start MLflow run for AutoML session."""
        try:
            with mlflow.start_run(run_name=f"automl_{session_id}") as run:
                # Log dataset info
                mlflow.log_params({
                    "session_id": session_id,
                    "dataset_rows": dataset_info.get("rows", 0),
                    "dataset_columns": dataset_info.get("columns", 0),
                    "target_column": dataset_info.get("target_column", ""),
                    "problem_type": dataset_info.get("problem_type", ""),
                    "test_size": config.get("test_size", 0.2),
                    "hyperparameter_tuning": config.get("hyperparameter_tuning", False)
                })
                
                return run.info.run_id
        except Exception as e:
            logger.error(f"MLflow run start error: {str(e)}")
            return None

    def log_model_result(
        self,
        run_id: str,
        model_name: str,
        metrics: Dict[str, Any],
        params: Dict[str, Any],
        model_object=None
    ):
        """Log individual model training result."""
        try:
            with mlflow.start_run(run_id=run_id, nested=True) as run:
                # Log params
                safe_params = {k: str(v)[:250] for k, v in params.items()}
                mlflow.log_params(safe_params)
                
                # Log metrics
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)) and metric_name != 'confusion_matrix':
                        mlflow.log_metric(f"{model_name}_{metric_name}", float(metric_value))
                
                # Log model artifact
                if model_object is not None:
                    try:
                        if 'xgb' in model_name.lower():
                            mlflow.xgboost.log_model(model_object, f"models/{model_name}")
                        elif 'lgb' in model_name.lower() or 'lightgbm' in model_name.lower():
                            mlflow.lightgbm.log_model(model_object, f"models/{model_name}")
                        else:
                            mlflow.sklearn.log_model(model_object, f"models/{model_name}")
                    except Exception as me:
                        logger.warning(f"Could not log model object: {me}")
        
        except Exception as e:
            logger.error(f"MLflow logging error for {model_name}: {str(e)}")

    def log_leaderboard(self, run_id: str, leaderboard: List[Dict[str, Any]]):
        """Log final leaderboard as artifact."""
        try:
            import json, tempfile
            with mlflow.start_run(run_id=run_id):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(leaderboard, f, indent=2)
                    tmp_path = f.name
                
                mlflow.log_artifact(tmp_path, "leaderboard")
                os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"Error logging leaderboard: {str(e)}")

    def log_best_model_summary(
        self,
        run_id: str,
        best_model_name: str,
        best_metrics: Dict[str, Any],
        problem_type: str
    ):
        """Log summary of best model."""
        try:
            with mlflow.start_run(run_id=run_id):
                mlflow.log_param("best_model", best_model_name)
                
                for k, v in best_metrics.items():
                    if isinstance(v, (int, float)) and k != 'confusion_matrix':
                        mlflow.log_metric(f"best_{k}", float(v))
        except Exception as e:
            logger.error(f"Error logging best model summary: {str(e)}")

    def get_experiments(self) -> List[Dict[str, Any]]:
        """Get list of all MLflow experiments."""
        try:
            experiments = mlflow.search_experiments()
            return [
                {
                    "experiment_id": e.experiment_id,
                    "name": e.name,
                    "artifact_location": e.artifact_location,
                    "lifecycle_stage": e.lifecycle_stage
                }
                for e in experiments
            ]
        except Exception as e:
            logger.error(f"Error fetching experiments: {str(e)}")
            return []

    def get_runs(self, experiment_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all runs for an experiment."""
        try:
            exp_name = experiment_name or self.experiment_name
            runs = mlflow.search_runs(experiment_names=[exp_name])
            
            if runs.empty:
                return []
            
            return runs.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Error fetching runs: {str(e)}")
            return []
