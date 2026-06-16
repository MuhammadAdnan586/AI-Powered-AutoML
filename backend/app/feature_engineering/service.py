"""
Module 2 - Feature Engineering Service
Auto-generate useful features from existing data
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.feature_selection import SelectKBest, f_classif, f_regression, mutual_info_classif
from sklearn.decomposition import PCA
import logging

logger = logging.getLogger(__name__)


class FeatureEngineeringService:
    
    def __init__(self):
        self.new_features: List[str] = []
        self.removed_features: List[str] = []
        self.feature_report: Dict[str, Any] = {}

    def auto_generate_features(
        self, 
        df: pd.DataFrame, 
        target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Automatically generate new features based on existing columns.
        """
        df_fe = df.copy()
        new_features = []
        
        numeric_cols = df_fe.select_dtypes(include=[np.number]).columns.tolist()
        if target_column and target_column in numeric_cols:
            numeric_cols.remove(target_column)
        
        # 1. Polynomial features for numeric columns (pairs)
        if len(numeric_cols) >= 2:
            for i in range(min(len(numeric_cols), 5)):
                for j in range(i + 1, min(len(numeric_cols), 5)):
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    
                    # Interaction feature
                    feat_name = f"{col1}_x_{col2}"
                    df_fe[feat_name] = df_fe[col1] * df_fe[col2]
                    new_features.append({'name': feat_name, 'type': 'interaction'})
                    
                    # Ratio feature (avoid division by zero)
                    if df_fe[col2].replace(0, np.nan).notna().all():
                        feat_name2 = f"{col1}_div_{col2}"
                        df_fe[feat_name2] = df_fe[col1] / (df_fe[col2].replace(0, np.nan))
                        df_fe[feat_name2].fillna(0, inplace=True)
                        new_features.append({'name': feat_name2, 'type': 'ratio'})
        
        # 2. Statistical features for numeric columns
        for col in numeric_cols[:10]:  # Limit to first 10
            # Log transform (for positive values)
            if df_fe[col].min() > 0:
                feat_name = f"{col}_log"
                df_fe[feat_name] = np.log1p(df_fe[col])
                new_features.append({'name': feat_name, 'type': 'log_transform'})
            
            # Square root (for positive values)
            if df_fe[col].min() >= 0:
                feat_name = f"{col}_sqrt"
                df_fe[feat_name] = np.sqrt(df_fe[col])
                new_features.append({'name': feat_name, 'type': 'sqrt_transform'})
            
            # Squared feature
            feat_name = f"{col}_squared"
            df_fe[feat_name] = df_fe[col] ** 2
            new_features.append({'name': feat_name, 'type': 'polynomial'})
        
        # 3. Aggregate statistical features (row-wise)
        if len(numeric_cols) >= 3:
            df_fe['row_mean'] = df_fe[numeric_cols].mean(axis=1)
            df_fe['row_std'] = df_fe[numeric_cols].std(axis=1)
            df_fe['row_max'] = df_fe[numeric_cols].max(axis=1)
            df_fe['row_min'] = df_fe[numeric_cols].min(axis=1)
            df_fe['row_range'] = df_fe['row_max'] - df_fe['row_min']
            
            for feat in ['row_mean', 'row_std', 'row_max', 'row_min', 'row_range']:
                new_features.append({'name': feat, 'type': 'row_aggregate'})
        
        self.new_features = [f['name'] for f in new_features]
        
        report = {
            'original_features': len(df.columns),
            'new_features_generated': len(new_features),
            'total_features': len(df_fe.columns),
            'features_added': new_features
        }
        
        logger.info(f"Generated {len(new_features)} new features")
        return df_fe, report

    def select_best_features(
        self, 
        df: pd.DataFrame, 
        target_column: str,
        problem_type: str = 'classification',
        k: int = 20,
        method: str = 'auto'
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Select the K best features using statistical tests.
        
        Methods: 'f_test', 'mutual_info', 'auto'
        """
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found")
        
        feature_cols = [col for col in df.columns if col != target_column]
        X = df[feature_cols].select_dtypes(include=[np.number])
        y = df[target_column]
        
        if len(X.columns) == 0:
            return df, {'error': 'No numeric features to select from'}
        
        k = min(k, len(X.columns))
        
        # Choose scoring function
        if problem_type == 'classification':
            if method == 'mutual_info' or (method == 'auto' and k > 15):
                score_func = mutual_info_classif
            else:
                score_func = f_classif
        else:
            score_func = f_regression
        
        selector = SelectKBest(score_func=score_func, k=k)
        X_selected = selector.fit_transform(X, y)
        
        selected_features = X.columns[selector.get_support()].tolist()
        scores = selector.scores_
        
        # Create feature importance dataframe
        feature_scores = pd.DataFrame({
            'feature': X.columns,
            'score': scores
        }).sort_values('score', ascending=False)
        
        # Keep target + selected features
        selected_cols = selected_features + [target_column]
        # Also keep non-numeric columns (not in X)
        non_numeric = [col for col in df.columns if col not in X.columns and col != target_column]
        final_cols = list(set(selected_features + non_numeric + [target_column]))
        
        df_selected = df[[col for col in final_cols if col in df.columns]]
        
        self.removed_features = [col for col in X.columns if col not in selected_features]
        
        report = {
            'original_feature_count': len(feature_cols),
            'selected_feature_count': len(selected_features),
            'removed_features': self.removed_features,
            'selected_features': selected_features,
            'feature_scores': feature_scores.head(20).to_dict(orient='records'),
            'selection_method': method,
            'k': k
        }
        
        logger.info(f"Selected {len(selected_features)} features from {len(feature_cols)}")
        return df_selected, report

    def remove_low_variance_features(
        self, 
        df: pd.DataFrame, 
        target_column: Optional[str] = None,
        threshold: float = 0.01
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Remove features with very low variance."""
        from sklearn.feature_selection import VarianceThreshold
        
        feature_cols = [col for col in df.columns if col != target_column]
        X = df[feature_cols].select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            return df, []
        
        selector = VarianceThreshold(threshold=threshold)
        selector.fit(X)
        
        low_var_features = X.columns[~selector.get_support()].tolist()
        df_clean = df.drop(columns=low_var_features)
        
        logger.info(f"Removed {len(low_var_features)} low-variance features")
        return df_clean, low_var_features

    def remove_correlated_features(
        self, 
        df: pd.DataFrame, 
        target_column: Optional[str] = None,
        threshold: float = 0.95
    ) -> Tuple[pd.DataFrame, List[str], pd.DataFrame]:
        """Remove highly correlated features."""
        feature_cols = [col for col in df.columns if col != target_column]
        X = df[feature_cols].select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            return df, [], pd.DataFrame()
        
        corr_matrix = X.corr().abs()
        
        # Upper triangle of correlation matrix
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Find features with correlation > threshold
        to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
        
        df_clean = df.drop(columns=to_drop)
        
        logger.info(f"Removed {len(to_drop)} highly correlated features")
        return df_clean, to_drop, corr_matrix

    def full_feature_engineering_pipeline(
        self,
        df: pd.DataFrame,
        target_column: str,
        problem_type: str = 'classification',
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Run complete feature engineering pipeline."""
        
        if config is None:
            config = {
                'auto_generate': True,
                'remove_low_variance': True,
                'remove_correlated': True,
                'select_best': True,
                'k_best': 20,
                'variance_threshold': 0.01,
                'correlation_threshold': 0.95
            }
        
        report = {'steps': [], 'original_shape': list(df.shape)}
        
        # Step 1: Auto generate features
        if config.get('auto_generate', True):
            df, gen_report = self.auto_generate_features(df, target_column)
            report['steps'].append({
                'step': 'feature_generation',
                'details': gen_report,
                'shape_after': list(df.shape)
            })
        
        # Step 2: Remove low variance
        if config.get('remove_low_variance', True):
            df, removed = self.remove_low_variance_features(
                df, target_column, 
                threshold=config.get('variance_threshold', 0.01)
            )
            report['steps'].append({
                'step': 'low_variance_removal',
                'removed_features': removed,
                'shape_after': list(df.shape)
            })
        
        # Step 3: Remove correlated features
        if config.get('remove_correlated', True):
            df, removed_corr, _ = self.remove_correlated_features(
                df, target_column,
                threshold=config.get('correlation_threshold', 0.95)
            )
            report['steps'].append({
                'step': 'correlation_removal',
                'removed_features': removed_corr,
                'shape_after': list(df.shape)
            })
        
        # Step 4: Select best features
        if config.get('select_best', True):
            df, select_report = self.select_best_features(
                df, target_column, problem_type,
                k=config.get('k_best', 20)
            )
            report['steps'].append({
                'step': 'feature_selection',
                'details': select_report,
                'shape_after': list(df.shape)
            })
        
        report['final_shape'] = list(df.shape)
        return df, report
