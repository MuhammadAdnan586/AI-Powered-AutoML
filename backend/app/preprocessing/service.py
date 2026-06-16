"""
Module 2 - Preprocessing Service
Handles: Missing Value Handling, Duplicate Removal, Encoding, Data Cleaning
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer
from typing import Dict, Any, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class PreprocessingService:
    
    def __init__(self):
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler = None
        self.imputers: Dict[str, SimpleImputer] = {}
        self.preprocessing_report: Dict[str, Any] = {}

    def load_dataset(self, file_path: str) -> pd.DataFrame:
        """Load CSV or Excel file into DataFrame."""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            logger.info(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise

    def get_dataset_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive dataset information."""
        info = {
            "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
            "missing_percentage": {
                col: round(float(df[col].isnull().sum() / len(df) * 100), 2) 
                for col in df.columns
            },
            "duplicate_rows": int(df.duplicated().sum()),
            "numeric_columns": list(df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
            "unique_counts": {col: int(df[col].nunique()) for col in df.columns},
            "sample_data": df.head(5).to_dict(orient='records')
        }
        return info

    def remove_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """Remove duplicate rows from dataset."""
        original_count = len(df)
        df_clean = df.drop_duplicates()
        removed_count = original_count - len(df_clean)
        
        self.preprocessing_report['duplicates_removed'] = removed_count
        logger.info(f"Removed {removed_count} duplicate rows")
        return df_clean.reset_index(drop=True), removed_count

    def handle_missing_values(
        self, 
        df: pd.DataFrame, 
        strategy: str = 'auto',
        numeric_strategy: str = 'mean',
        categorical_strategy: str = 'most_frequent',
        drop_threshold: float = 0.5
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Handle missing values intelligently.
        
        Strategies:
        - 'auto': Automatically choose best strategy per column
        - 'drop': Drop columns/rows with too many missing values
        - 'impute': Use imputation for all missing values
        """
        missing_report = {}
        df_clean = df.copy()
        
        for col in df_clean.columns:
            missing_pct = df_clean[col].isnull().sum() / len(df_clean)
            
            if missing_pct == 0:
                continue
            
            missing_report[col] = {
                'missing_count': int(df_clean[col].isnull().sum()),
                'missing_percentage': round(float(missing_pct * 100), 2)
            }
            
            if strategy == 'auto':
                if missing_pct > drop_threshold:
                    # Drop column if too many missing values
                    df_clean.drop(columns=[col], inplace=True)
                    missing_report[col]['action'] = f'column dropped (>{drop_threshold*100}% missing)'
                    continue
                
                if df_clean[col].dtype in [np.int64, np.float64, 'float32', 'int32']:
                    # Numeric: use median for skewed data, mean for normal
                    skewness = abs(df_clean[col].skew())
                    imp_strategy = 'median' if skewness > 1 else 'mean'
                    imputer = SimpleImputer(strategy=imp_strategy)
                    df_clean[col] = imputer.fit_transform(df_clean[[col]]).ravel()
                    self.imputers[col] = imputer
                    missing_report[col]['action'] = f'imputed with {imp_strategy}'
                else:
                    # Categorical: use most frequent
                    imputer = SimpleImputer(strategy='most_frequent')
                    df_clean[col] = imputer.fit_transform(df_clean[[col]]).ravel()
                    self.imputers[col] = imputer
                    missing_report[col]['action'] = 'imputed with most frequent'
            
            elif strategy == 'drop':
                if missing_pct > drop_threshold:
                    df_clean.drop(columns=[col], inplace=True)
                    missing_report[col]['action'] = 'column dropped'
                else:
                    df_clean.dropna(subset=[col], inplace=True)
                    missing_report[col]['action'] = 'rows dropped'
            
            elif strategy == 'impute':
                if df_clean[col].dtype in [np.int64, np.float64]:
                    imputer = SimpleImputer(strategy=numeric_strategy)
                else:
                    imputer = SimpleImputer(strategy=categorical_strategy)
                df_clean[col] = imputer.fit_transform(df_clean[[col]]).ravel()
                self.imputers[col] = imputer
                missing_report[col]['action'] = f'imputed with {numeric_strategy if df_clean[col].dtype in [np.int64, np.float64] else categorical_strategy}'
        
        self.preprocessing_report['missing_value_handling'] = missing_report
        return df_clean.reset_index(drop=True), missing_report

    def encode_categorical(
        self, 
        df: pd.DataFrame, 
        target_column: Optional[str] = None,
        encoding_strategy: str = 'auto'
    ) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Encode categorical columns.
        
        Strategies:
        - 'auto': Label encode for low cardinality, one-hot for others
        - 'label': Label encoding for all
        - 'onehot': One-hot encoding for all
        """
        encoding_report = {}
        df_encoded = df.copy()
        
        cat_columns = df_encoded.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remove target column from encoding if specified
        if target_column and target_column in cat_columns:
            cat_columns.remove(target_column)
            # Encode target separately with label encoding
            le = LabelEncoder()
            df_encoded[target_column] = le.fit_transform(df_encoded[target_column].astype(str))
            self.label_encoders[target_column] = le
            encoding_report[target_column] = 'label_encoded (target)'
        
        for col in cat_columns:
            unique_count = df_encoded[col].nunique()
            
            if encoding_strategy == 'auto':
                if unique_count <= 10:
                    # Label encoding for low cardinality
                    le = LabelEncoder()
                    df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                    self.label_encoders[col] = le
                    encoding_report[col] = f'label_encoded ({unique_count} unique values)'
                else:
                    # One-hot encoding for high cardinality (limit to top categories)
                    top_categories = df_encoded[col].value_counts().nlargest(10).index
                    df_encoded[col] = df_encoded[col].where(
                        df_encoded[col].isin(top_categories), other='Other'
                    )
                    dummies = pd.get_dummies(df_encoded[col], prefix=col)
                    df_encoded = pd.concat([df_encoded.drop(columns=[col]), dummies], axis=1)
                    encoding_report[col] = f'one_hot_encoded (top 10 of {unique_count} values)'
            
            elif encoding_strategy == 'label':
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                self.label_encoders[col] = le
                encoding_report[col] = 'label_encoded'
            
            elif encoding_strategy == 'onehot':
                dummies = pd.get_dummies(df_encoded[col], prefix=col)
                df_encoded = pd.concat([df_encoded.drop(columns=[col]), dummies], axis=1)
                encoding_report[col] = 'one_hot_encoded'
        
        self.preprocessing_report['encoding'] = encoding_report
        return df_encoded, encoding_report

    def scale_features(
        self, 
        df: pd.DataFrame, 
        target_column: Optional[str] = None,
        scaling_method: str = 'standard'
    ) -> Tuple[pd.DataFrame, str]:
        """
        Scale numeric features.
        
        Methods: 'standard', 'minmax', 'none'
        """
        df_scaled = df.copy()
        numeric_cols = df_scaled.select_dtypes(include=[np.number]).columns.tolist()
        
        if target_column and target_column in numeric_cols:
            numeric_cols.remove(target_column)
        
        if not numeric_cols or scaling_method == 'none':
            return df_scaled, 'no scaling applied'
        
        if scaling_method == 'standard':
            self.scaler = StandardScaler()
        elif scaling_method == 'minmax':
            self.scaler = MinMaxScaler()
        
        df_scaled[numeric_cols] = self.scaler.fit_transform(df_scaled[numeric_cols])
        self.preprocessing_report['scaling'] = scaling_method
        
        return df_scaled, scaling_method

    def full_preprocessing_pipeline(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Run complete preprocessing pipeline."""
        
        if config is None:
            config = {
                'remove_duplicates': True,
                'missing_strategy': 'auto',
                'encoding_strategy': 'auto',
                'scaling_method': 'standard',
                'drop_threshold': 0.5
            }
        
        report = {'steps': [], 'original_shape': list(df.shape)}
        
        # Step 1: Remove duplicates
        if config.get('remove_duplicates', True):
            df, dupes = self.remove_duplicates(df)
            report['steps'].append({
                'step': 'duplicate_removal',
                'removed': dupes,
                'shape_after': list(df.shape)
            })
        
        # Step 2: Handle missing values
        df, missing_report = self.handle_missing_values(
            df, 
            strategy=config.get('missing_strategy', 'auto'),
            drop_threshold=config.get('drop_threshold', 0.5)
        )
        report['steps'].append({
            'step': 'missing_value_handling',
            'details': missing_report,
            'shape_after': list(df.shape)
        })
        
        # Step 3: Encode categorical columns
        df, encoding_report = self.encode_categorical(
            df, 
            target_column=target_column,
            encoding_strategy=config.get('encoding_strategy', 'auto')
        )
        report['steps'].append({
            'step': 'encoding',
            'details': encoding_report,
            'shape_after': list(df.shape)
        })
        
        # Step 4: Scale features
        df, scaling_method = self.scale_features(
            df, 
            target_column=target_column,
            scaling_method=config.get('scaling_method', 'standard')
        )
        report['steps'].append({
            'step': 'scaling',
            'method': scaling_method,
            'shape_after': list(df.shape)
        })
        
        report['final_shape'] = list(df.shape)
        report['target_column'] = target_column
        self.preprocessing_report = report
        
        logger.info(f"Preprocessing complete. Shape: {df.shape}")
        return df, report


def detect_problem_type(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """
    Auto-detect if problem is Classification or Regression.
    Returns detailed analysis.
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset")
    
    target = df[target_column]
    unique_values = target.nunique()
    total_values = len(target)
    
    result = {
        'target_column': target_column,
        'unique_values': int(unique_values),
        'total_values': int(total_values),
        'ratio': round(float(unique_values / total_values), 4)
    }
    
    # Detection logic
    if target.dtype == 'object' or target.dtype.name == 'category':
        result['problem_type'] = 'classification'
        result['reason'] = 'Target is categorical (string/object type)'
        result['num_classes'] = int(unique_values)
        result['class_names'] = list(target.unique()[:10])
        
        if unique_values == 2:
            result['sub_type'] = 'binary_classification'
        else:
            result['sub_type'] = 'multiclass_classification'
    
    elif unique_values <= 10 or (unique_values / total_values < 0.05):
        result['problem_type'] = 'classification'
        result['reason'] = f'Low cardinality numeric target ({unique_values} unique values)'
        result['num_classes'] = int(unique_values)
        result['class_names'] = [str(v) for v in sorted(target.unique()[:10])]
        
        if unique_values == 2:
            result['sub_type'] = 'binary_classification'
        else:
            result['sub_type'] = 'multiclass_classification'
    
    else:
        result['problem_type'] = 'regression'
        result['reason'] = f'High cardinality numeric target ({unique_values} unique values, ratio: {result["ratio"]})'
        result['sub_type'] = 'regression'
        result['target_stats'] = {
            'min': float(target.min()),
            'max': float(target.max()),
            'mean': float(target.mean()),
            'std': float(target.std()),
            'median': float(target.median())
        }
    
    # Confidence score
    if result['problem_type'] == 'classification':
        if target.dtype == 'object':
            result['confidence'] = 0.99
        elif unique_values <= 5:
            result['confidence'] = 0.95
        else:
            result['confidence'] = 0.85
    else:
        if result['ratio'] > 0.5:
            result['confidence'] = 0.95
        else:
            result['confidence'] = 0.80
    
    return result
