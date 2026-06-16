"""
Module 2 - AutoML Service
Handles: Multiple Model Training, Benchmark Leaderboard, Hyperparameter Tuning
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score, confusion_matrix,
    classification_report
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, Any, List, Optional, Tuple
import time
import logging
import json
import os
import pickle

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Model Registry — all models available for AutoML
# ─────────────────────────────────────────────────────────────

CLASSIFICATION_MODELS = {
    "xgboost": {
        "model": xgb.XGBClassifier,
        "params": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 6, "use_label_encoder": False, "eval_metric": "logloss", "random_state": 42},
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 6, 9],
            "learning_rate": [0.01, 0.1, 0.3]
        },
        "display_name": "XGBoost",
        "category": "Boosting"
    },
    "lightgbm": {
        "model": lgb.LGBMClassifier,
        "params": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": -1, "random_state": 42, "verbose": -1},
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "max_depth": [-1, 6, 9],
            "learning_rate": [0.01, 0.1, 0.2]
        },
        "display_name": "LightGBM",
        "category": "Boosting"
    },
    "random_forest": {
        "model": RandomForestClassifier,
        "params": {"n_estimators": 100, "max_depth": None, "random_state": 42, "n_jobs": -1},
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "max_depth": [None, 10, 20],
            "min_samples_split": [2, 5, 10]
        },
        "display_name": "Random Forest",
        "category": "Ensemble"
    },
    "gradient_boosting": {
        "model": GradientBoostingClassifier,
        "params": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3, "random_state": 42},
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.05, 0.1, 0.2],
            "max_depth": [3, 5, 7]
        },
        "display_name": "Gradient Boosting",
        "category": "Boosting"
    },
    "logistic_regression": {
        "model": LogisticRegression,
        "params": {"max_iter": 1000, "random_state": 42, "n_jobs": -1},
        "param_grid": {
            "C": [0.01, 0.1, 1.0, 10.0],
            "solver": ["lbfgs", "saga"],
            "penalty": ["l2"]
        },
        "display_name": "Logistic Regression",
        "category": "Linear"
    },
    "decision_tree": {
        "model": DecisionTreeClassifier,
        "params": {"max_depth": 10, "random_state": 42},
        "param_grid": {
            "max_depth": [5, 10, 20, None],
            "min_samples_split": [2, 5, 10],
            "criterion": ["gini", "entropy"]
        },
        "display_name": "Decision Tree",
        "category": "Tree"
    },
    "knn": {
        "model": KNeighborsClassifier,
        "params": {"n_neighbors": 5, "n_jobs": -1},
        "param_grid": {
            "n_neighbors": [3, 5, 7, 11],
            "weights": ["uniform", "distance"],
            "metric": ["euclidean", "manhattan"]
        },
        "display_name": "K-Nearest Neighbors",
        "category": "Distance"
    },
    "naive_bayes": {
        "model": GaussianNB,
        "params": {},
        "param_grid": {"var_smoothing": [1e-9, 1e-8, 1e-7]},
        "display_name": "Naive Bayes",
        "category": "Probabilistic"
    },
    "svm": {
        "model": SVC,
        "params": {"probability": True, "random_state": 42},
        "param_grid": {
            "C": [0.1, 1.0, 10.0],
            "kernel": ["rbf", "linear"],
            "gamma": ["scale", "auto"]
        },
        "display_name": "Support Vector Machine",
        "category": "Kernel"
    }
}

REGRESSION_MODELS = {
    "xgboost": {
        "model": xgb.XGBRegressor,
        "params": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 6, "random_state": 42},
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 6, 9],
            "learning_rate": [0.01, 0.1, 0.3]
        },
        "display_name": "XGBoost",
        "category": "Boosting"
    },
    "lightgbm": {
        "model": lgb.LGBMRegressor,
        "params": {"n_estimators": 100, "learning_rate": 0.1, "random_state": 42, "verbose": -1},
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "max_depth": [-1, 6, 9],
            "learning_rate": [0.01, 0.1, 0.2]
        },
        "display_name": "LightGBM",
        "category": "Boosting"
    },
    "random_forest": {
        "model": RandomForestRegressor,
        "params": {"n_estimators": 100, "max_depth": None, "random_state": 42, "n_jobs": -1},
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "max_depth": [None, 10, 20]
        },
        "display_name": "Random Forest",
        "category": "Ensemble"
    },
    "gradient_boosting": {
        "model": GradientBoostingRegressor,
        "params": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3, "random_state": 42},
        "param_grid": {
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.05, 0.1, 0.2]
        },
        "display_name": "Gradient Boosting",
        "category": "Boosting"
    },
    "linear_regression": {
        "model": LinearRegression,
        "params": {"n_jobs": -1},
        "param_grid": {},
        "display_name": "Linear Regression",
        "category": "Linear"
    },
    "ridge": {
        "model": Ridge,
        "params": {"alpha": 1.0},
        "param_grid": {"alpha": [0.1, 1.0, 10.0, 100.0]},
        "display_name": "Ridge Regression",
        "category": "Linear"
    },
    "lasso": {
        "model": Lasso,
        "params": {"alpha": 1.0, "max_iter": 1000},
        "param_grid": {"alpha": [0.001, 0.01, 0.1, 1.0]},
        "display_name": "Lasso Regression",
        "category": "Linear"
    },
    "decision_tree": {
        "model": DecisionTreeRegressor,
        "params": {"max_depth": 10, "random_state": 42},
        "param_grid": {
            "max_depth": [5, 10, 20, None],
            "min_samples_split": [2, 5, 10]
        },
        "display_name": "Decision Tree",
        "category": "Tree"
    },
    "knn": {
        "model": KNeighborsRegressor,
        "params": {"n_neighbors": 5, "n_jobs": -1},
        "param_grid": {
            "n_neighbors": [3, 5, 7, 11],
            "weights": ["uniform", "distance"]
        },
        "display_name": "K-Nearest Neighbors",
        "category": "Distance"
    }
}


class AutoMLService:
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        self.trained_models: Dict[str, Any] = {}
        self.leaderboard: List[Dict[str, Any]] = []
        self.best_model_name: Optional[str] = None
        self.best_model = None

    def smart_model_recommendation(
        self, 
        df: pd.DataFrame, 
        problem_type: str,
        n_samples: int,
        n_features: int
    ) -> List[str]:
        """
        Recommend best models based on dataset characteristics.
        Returns ordered list of recommended model names.
        """
        recommendations = []
        
        if problem_type == 'classification':
            # Always recommend XGBoost and LightGBM for most datasets
            if n_samples > 1000:
                recommendations = ['xgboost', 'lightgbm', 'random_forest', 
                                   'gradient_boosting', 'logistic_regression',
                                   'decision_tree', 'knn', 'naive_bayes']
            else:
                # Small datasets: simpler models work better
                recommendations = ['logistic_regression', 'random_forest', 
                                   'decision_tree', 'naive_bayes', 'knn', 
                                   'xgboost', 'lightgbm']
            
            # For high-dimensional data, avoid KNN
            if n_features > 50:
                recommendations = [m for m in recommendations if m != 'knn']
                if 'svm' not in recommendations:
                    recommendations.insert(-1, 'svm')
        
        else:  # regression
            if n_samples > 1000:
                recommendations = ['xgboost', 'lightgbm', 'random_forest',
                                   'gradient_boosting', 'ridge', 'lasso',
                                   'linear_regression', 'decision_tree', 'knn']
            else:
                recommendations = ['ridge', 'lasso', 'linear_regression',
                                   'random_forest', 'decision_tree', 
                                   'xgboost', 'lightgbm']
        
        return recommendations

    def train_single_model(
        self,
        model_name: str,
        X_train, X_test, y_train, y_test,
        problem_type: str,
        hyperparameter_tuning: bool = False
    ) -> Dict[str, Any]:
        """Train a single model and return metrics."""
        
        model_registry = CLASSIFICATION_MODELS if problem_type == 'classification' else REGRESSION_MODELS
        
        if model_name not in model_registry:
            raise ValueError(f"Model '{model_name}' not found in registry")
        
        config = model_registry[model_name]
        model_class = config['model']
        model_params = config['params'].copy()
        
        start_time = time.time()
        
        if hyperparameter_tuning and config.get('param_grid'):
            model = GridSearchCV(
                model_class(**model_params),
                param_grid=config['param_grid'],
                cv=3,
                n_jobs=-1,
                scoring='accuracy' if problem_type == 'classification' else 'neg_mean_squared_error'
            )
        else:
            model = model_class(**model_params)
        
        try:
            model.fit(X_train, y_train)
            training_time = round(time.time() - start_time, 2)
            
            if hyperparameter_tuning and hasattr(model, 'best_estimator_'):
                best_params = model.best_params_
                model = model.best_estimator_
            else:
                best_params = model_params
            
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            if problem_type == 'classification':
                metrics = self._calculate_classification_metrics(y_test, y_pred, model, X_test)
            else:
                metrics = self._calculate_regression_metrics(y_test, y_pred)
            
            # Cross-validation score
            cv_scores = cross_val_score(
                model, 
                np.vstack([X_train, X_test]), 
                np.hstack([y_train, y_test]),
                cv=5,
                scoring='accuracy' if problem_type == 'classification' else 'r2'
            )
            
            result = {
                'model_name': model_name,
                'display_name': config['display_name'],
                'category': config['category'],
                'metrics': metrics,
                'training_time_seconds': training_time,
                'best_params': best_params,
                'cv_mean': round(float(cv_scores.mean()), 4),
                'cv_std': round(float(cv_scores.std()), 4),
                'hyperparameter_tuned': hyperparameter_tuning,
                'status': 'success'
            }
            
            self.trained_models[model_name] = model
            return result
        
        except Exception as e:
            logger.error(f"Error training {model_name}: {str(e)}")
            return {
                'model_name': model_name,
                'display_name': config['display_name'],
                'status': 'failed',
                'error': str(e)
            }

    def _calculate_classification_metrics(self, y_test, y_pred, model, X_test) -> Dict[str, Any]:
        """Calculate classification metrics."""
        metrics = {
            'accuracy': round(float(accuracy_score(y_test, y_pred)), 4),
            'precision': round(float(precision_score(y_test, y_pred, average='weighted', zero_division=0)), 4),
            'recall': round(float(recall_score(y_test, y_pred, average='weighted', zero_division=0)), 4),
            'f1_score': round(float(f1_score(y_test, y_pred, average='weighted', zero_division=0)), 4),
        }
        
        # ROC AUC (for binary classification only)
        try:
            if hasattr(model, 'predict_proba') and len(np.unique(y_test)) == 2:
                y_proba = model.predict_proba(X_test)[:, 1]
                metrics['roc_auc'] = round(float(roc_auc_score(y_test, y_proba)), 4)
        except Exception:
            pass
        
        # Confusion matrix
        try:
            cm = confusion_matrix(y_test, y_pred)
            metrics['confusion_matrix'] = cm.tolist()
        except Exception:
            pass
        
        return metrics

    def _calculate_regression_metrics(self, y_test, y_pred) -> Dict[str, Any]:
        """Calculate regression metrics."""
        mse = mean_squared_error(y_test, y_pred)
        return {
            'r2_score': round(float(r2_score(y_test, y_pred)), 4),
            'mae': round(float(mean_absolute_error(y_test, y_pred)), 4),
            'mse': round(float(mse), 4),
            'rmse': round(float(np.sqrt(mse)), 4),
        }

    def run_automl(
        self,
        df: pd.DataFrame,
        target_column: str,
        problem_type: str,
        test_size: float = 0.2,
        models_to_train: Optional[List[str]] = None,
        hyperparameter_tuning: bool = False,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main AutoML function — trains all models and returns leaderboard.
        """
        
        logger.info(f"Starting AutoML for {problem_type} with {len(df)} rows")
        
        # Prepare features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Only use numeric features
        X = X.select_dtypes(include=[np.number])
        
        # Handle any remaining NaN
        X = X.fillna(0)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, 
            stratify=y if problem_type == 'classification' else None
        )
        
        # Get model recommendations
        if models_to_train is None:
            models_to_train = self.smart_model_recommendation(
                df, problem_type, len(df), len(X.columns)
            )
        
        # Train all models
        results = []
        total_models = len(models_to_train)
        
        for idx, model_name in enumerate(models_to_train):
            logger.info(f"Training model {idx+1}/{total_models}: {model_name}")
            
            result = self.train_single_model(
                model_name, X_train, X_test, y_train, y_test,
                problem_type, hyperparameter_tuning
            )
            results.append(result)
        
        # Build leaderboard
        successful_results = [r for r in results if r.get('status') == 'success']
        failed_results = [r for r in results if r.get('status') == 'failed']
        
        # Sort by primary metric
        if problem_type == 'classification':
            sort_key = lambda x: x['metrics'].get('accuracy', 0)
        else:
            sort_key = lambda x: x['metrics'].get('r2_score', -999)
        
        successful_results.sort(key=sort_key, reverse=True)
        
        # Rank models
        for rank, result in enumerate(successful_results, 1):
            result['rank'] = rank
        
        self.leaderboard = successful_results
        
        # Best model
        if successful_results:
            self.best_model_name = successful_results[0]['model_name']
            self.best_model = self.trained_models.get(self.best_model_name)
            
            # Save best model
            if session_id and self.best_model:
                model_path = os.path.join(self.models_dir, f"{session_id}_best_model.pkl")
                with open(model_path, 'wb') as f:
                    pickle.dump({
                        'model': self.best_model,
                        'model_name': self.best_model_name,
                        'problem_type': problem_type,
                        'feature_columns': list(X.columns),
                        'target_column': target_column
                    }, f)
        
        # Summary
        summary = {
            'session_id': session_id,
            'problem_type': problem_type,
            'dataset_shape': list(df.shape),
            'feature_count': len(X.columns),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'models_trained': len(successful_results),
            'models_failed': len(failed_results),
            'best_model': self.best_model_name,
            'best_score': successful_results[0]['metrics'].get(
                'accuracy' if problem_type == 'classification' else 'r2_score', 0
            ) if successful_results else 0,
            'leaderboard': successful_results,
            'failed_models': failed_results,
            'hyperparameter_tuning': hyperparameter_tuning
        }
        
        return summary

    def get_feature_importance(self, model_name: str, feature_names: List[str]) -> Optional[List[Dict]]:
        """Get feature importance for tree-based models."""
        model = self.trained_models.get(model_name)
        if model is None:
            return None
        
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df.head(20).to_dict(orient='records')
        
        elif hasattr(model, 'coef_'):
            coefs = model.coef_
            if coefs.ndim > 1:
                coefs = np.abs(coefs).mean(axis=0)
            
            importance_df = pd.DataFrame({
                'feature': feature_names[:len(coefs)],
                'importance': np.abs(coefs)
            }).sort_values('importance', ascending=False)
            
            return importance_df.head(20).to_dict(orient='records')
        
        return None
