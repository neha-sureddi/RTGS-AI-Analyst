from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import json
import os
from typing import Any, Dict
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import io
import warnings
warnings.filterwarnings('ignore')

# Global state with better management
current_dataset = None
dataset_metadata = {}
transformation_log = []

class ReadCSVToolInput(BaseModel):
    """Input schema for ReadCSVTool."""
    file_path: str = Field(..., description="Path to the CSV file to load")

class ReadCSVTool(BaseTool):
    name: str = "Read CSV Dataset"
    description: str = "Load a CSV file into memory for analysis. Handles various CSV formats and encodings."
    args_schema: Type[BaseModel] = ReadCSVToolInput
    
    def _run(self, file_path: str) -> str:
        global current_dataset, dataset_metadata, transformation_log
        
        # Reset state
        transformation_log = []
        
        try:
            # Try different encodings and separators
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            separators = [',', ';', '\t', '|']
            
            dataset_loaded = False
            for encoding in encodings:
                for sep in separators:
                    try:
                        current_dataset = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        if current_dataset.shape[1] > 1:  # Ensure proper separation
                            dataset_loaded = True
                            break
                    except:
                        continue
                if dataset_loaded:
                    break
            
            if not dataset_loaded:
                current_dataset = pd.read_csv(file_path)  # Last attempt with defaults
            
            dataset_metadata = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'loaded_at': pd.Timestamp.now().isoformat(),
                'original_shape': current_dataset.shape
            }
            
            # Clean column names
            current_dataset.columns = current_dataset.columns.str.strip().str.replace('\n', ' ').str.replace('\r', ' ')
            
            summary = (
                f"DATASET LOADED: {os.path.basename(file_path)}\n"
                f"ROWS: {current_dataset.shape[0]:,}\n"
                f"COLUMNS: {current_dataset.shape[1]}\n"
                f"MEMORY: {current_dataset.memory_usage(deep=True).sum() / 1024**2:.1f} MB\n\n"
                f"COLUMN NAMES:\n{list(current_dataset.columns)}\n\n"
                f"DATA TYPES:\n{current_dataset.dtypes.to_string()}\n\n"
                f"FIRST 3 ROWS:\n{current_dataset.head(3).to_string()}"
            )
            return summary
        except Exception as e:
            return f"ERROR loading {file_path}: {str(e)}. Please check file path and format."

class InspectDataToolInput(BaseModel):
    """Input schema for InspectDataTool."""
    aspect: str = Field(default="overview", description="Aspect to inspect: overview, missing, types, duplicates")

class InspectDataTool(BaseTool):
    name: str = "Inspect Dataset Structure"
    description: str = "Get detailed information about the loaded dataset including data types, missing values, and duplicates"
    args_schema: Type[BaseModel] = InspectDataToolInput
    
    def _run(self, aspect: str = "overview") -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded. Use ReadCSVTool first."
        
        try:
            if aspect == "overview":
                buffer = io.StringIO()
                current_dataset.info(buf=buffer)
                info_str = buffer.getvalue()
                
                null_counts = current_dataset.isnull().sum()
                duplicates = current_dataset.duplicated().sum()
                numeric_cols = current_dataset.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = current_dataset.select_dtypes(include=['object']).columns.tolist()
                
                return (
                    f"DATASET OVERVIEW:\n{info_str}\n\n"
                    f"NUMERIC COLUMNS ({len(numeric_cols)}): {numeric_cols}\n\n"
                    f"CATEGORICAL COLUMNS ({len(categorical_cols)}): {categorical_cols}\n\n"
                    f"NULL VALUES:\n{null_counts[null_counts > 0].to_string()}\n\n"
                    f"DUPLICATES: {duplicates} rows ({duplicates/len(current_dataset)*100:.1f}%)"
                )
            
            elif aspect == "missing":
                missing = current_dataset.isnull().sum()
                missing_pct = (missing / len(current_dataset) * 100).round(2)
                result = "MISSING VALUE ANALYSIS:\n"
                for col in missing.index:
                    if missing[col] > 0:
                        result += f"- {col}: {missing[col]} ({missing_pct[col]}%)\n"
                return result or "No missing values found."
            
            elif aspect == "types":
                return f"DATA TYPES:\n{current_dataset.dtypes.to_string()}"
                
            elif aspect == "duplicates":
                duplicates = current_dataset.duplicated()
                dup_count = duplicates.sum()
                return f"DUPLICATE ANALYSIS:\nTotal duplicates: {dup_count} ({dup_count/len(current_dataset)*100:.1f}%)"
            
            return "Available aspects: overview, missing, types, duplicates"
            
        except Exception as e:
            return f"ERROR: {str(e)}"

class ViewColumnToolInput(BaseModel):
    """Input schema for ViewColumnTool."""
    column_name: str = Field(..., description="Name of the column to examine")

class ViewColumnTool(BaseTool):
    name: str = "Examine Specific Column"
    description: str = "Look at a specific column in detail including statistics and sample values"
    args_schema: Type[BaseModel] = ViewColumnToolInput
    
    def _run(self, column_name: str) -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            if column_name not in current_dataset.columns:
                available_cols = list(current_dataset.columns)
                return f"Column '{column_name}' not found. Available columns: {available_cols}"
            
            col = current_dataset[column_name]
            
            # Basic info
            result = (
                f"COLUMN: {column_name}\n"
                f"TYPE: {col.dtype}\n"
                f"UNIQUE VALUES: {col.nunique():,}\n"
                f"NULL COUNT: {col.isnull().sum():,} ({col.isnull().sum()/len(col)*100:.1f}%)\n"
                f"TOTAL ROWS: {len(col):,}\n\n"
            )
            
            # Statistics for numeric columns
            if pd.api.types.is_numeric_dtype(col):
                stats = col.describe()
                result += f"STATISTICS:\n{stats.to_string()}\n\n"
            
            # Value counts
            value_counts = col.value_counts().head(10)
            result += f"TOP 10 VALUES:\n{value_counts.to_string()}\n\n"
            
            # Sample values
            sample_values = col.dropna().head(10).tolist()
            result += f"SAMPLE VALUES:\n{sample_values}"
            
            return result
        except Exception as e:
            return f"ERROR: {str(e)}"

class SafeExecuteToolInput(BaseModel):
    """Input schema for SafeExecuteTool."""
    operation: str = Field(..., description="Pandas operation to execute on the dataset")
    save_name: str = Field(default="cleaned", description="Name to save the cleaned dataset")

class SafeExecuteTool(BaseTool):
    name: str = "Execute Safe Pandas Operation"
    description: str = "Execute pandas operations with safety restrictions and automatic saving"
    args_schema: Type[BaseModel] = SafeExecuteToolInput
    
    def _run(self, operation: str, save_name: str = "cleaned") -> str:
        global current_dataset, transformation_log
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            # Enhanced safety checks
            dangerous_terms = ['import', 'exec', 'eval', '__', 'open', 'file', 'os.', 'sys.', 'subprocess']
            if any(term in operation.lower() for term in dangerous_terms):
                return f"UNSAFE OPERATION BLOCKED: {operation}"
            
            # Create safe environment with more pandas methods
            safe_env = {
                'df': current_dataset.copy(),
                'pd': pd,
                'np': np,
                '__builtins__': {},
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'len': len,
                'range': range,
                'enumerate': enumerate
            }
            
            original_shape = current_dataset.shape
            
            # Execute operation
            result_df = eval(f"df.{operation}", safe_env)
            
            if isinstance(result_df, pd.DataFrame):
                current_dataset = result_df
                
                # Log transformation
                log_entry = f"Applied: {operation} | Shape: {original_shape} -> {current_dataset.shape}"
                transformation_log.append(log_entry)
                
                # Save cleaned dataset
                output_path = f"outputs/cleaned_data/{save_name}.csv"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                current_dataset.to_csv(output_path, index=False)
                
                return (
                    f"EXECUTED: df.{operation}\n"
                    f"ORIGINAL SHAPE: {original_shape}\n"
                    f"NEW SHAPE: {current_dataset.shape}\n"
                    f"ROWS CHANGED: {original_shape[0] - current_dataset.shape[0]}\n"
                    f"SAVED TO: {output_path}"
                )
            else:
                return f"Operation returned {type(result_df)}, not DataFrame. Result: {result_df}"
                
        except Exception as e:
            return f"EXECUTION ERROR: {str(e)}"

class CalculateStatsToolInput(BaseModel):
    """Input schema for CalculateStatsTool."""
    stat_type: str = Field(..., description="Type of statistics: describe, correlation, groupby, value_counts")
    parameters: str = Field(default="", description="Additional parameters for specific statistics")

class CalculateStatsTool(BaseTool):
    name: str = "Calculate Statistics"
    description: str = "Calculate various statistics on the dataset including descriptive stats, correlations, and groupby operations"
    args_schema: Type[BaseModel] = CalculateStatsToolInput
    
    def _run(self, stat_type: str, parameters: str = "") -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            if stat_type == "describe":
                desc = current_dataset.describe(include='all')
                return f"DESCRIPTIVE STATISTICS:\n{desc.to_string()}"
            
            elif stat_type == "correlation":
                numeric_df = current_dataset.select_dtypes(include=[np.number])
                if numeric_df.empty:
                    return "No numeric columns for correlation analysis"
                
                corr = numeric_df.corr()
                # Find strong correlations
                strong_corr = []
                for i in range(len(corr.columns)):
                    for j in range(i+1, len(corr.columns)):
                        val = corr.iloc[i, j]
                        if abs(val) > 0.5:
                            strong_corr.append(f"{corr.columns[i]} <-> {corr.columns[j]}: {val:.3f}")
                
                result = f"CORRELATION MATRIX:\n{corr.to_string()}\n\n"
                if strong_corr:
                    result += f"STRONG CORRELATIONS (|r| > 0.5):\n" + "\n".join(strong_corr)
                return result
            
            elif stat_type == "groupby" and parameters:
                parts = [p.strip() for p in parameters.split(',')]
                if len(parts) < 3:
                    return "Format: group_column,value_column,agg_function"
                
                group_col, value_col, agg_func = parts[:3]
                
                if group_col not in current_dataset.columns:
                    return f"Group column '{group_col}' not found"
                if value_col not in current_dataset.columns:
                    return f"Value column '{value_col}' not found"
                
                grouped = current_dataset.groupby(group_col)[value_col]
                
                if agg_func == "sum":
                    result = grouped.sum().sort_values(ascending=False)
                elif agg_func == "mean":
                    result = grouped.mean().sort_values(ascending=False)
                elif agg_func == "count":
                    result = grouped.count().sort_values(ascending=False)
                elif agg_func == "std":
                    result = grouped.std().sort_values(ascending=False)
                else:
                    return "Available functions: sum, mean, count, std"
                
                return f"GROUPED {agg_func.upper()} - {group_col} by {value_col}:\n{result.to_string()}"
            
            elif stat_type == "value_counts" and parameters:
                col = parameters.strip()
                if col not in current_dataset.columns:
                    return f"Column '{col}' not found"
                    
                counts = current_dataset[col].value_counts().head(20)
                percentages = (current_dataset[col].value_counts(normalize=True) * 100).head(20)
                
                result_df = pd.DataFrame({
                    'Count': counts,
                    'Percentage': percentages.round(2)
                })
                
                return f"VALUE COUNTS for '{col}':\n{result_df.to_string()}"
            
            return "Available stats: describe, correlation, groupby (group_col,value_col,agg_func), value_counts (column_name)"
            
        except Exception as e:
            return f"ERROR calculating statistics: {str(e)}"

class SaveSchemaToolInput(BaseModel):
    """Input schema for SaveSchemaTool."""
    dummy: str = Field(default="", description="Dummy parameter - not used")

class SaveSchemaTool(BaseTool):
    name: str = "Save Dataset Schema"
    description: str = "Save comprehensive schema mapping as JSON and Markdown with data profiling"
    args_schema: Type[BaseModel] = SaveSchemaToolInput
    
    def _run(self, dummy: str = "") -> str:
        global current_dataset, dataset_metadata
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            # Enhanced schema with data profiling
            numeric_cols = current_dataset.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = current_dataset.select_dtypes(include=['object']).columns.tolist()
            datetime_cols = current_dataset.select_dtypes(include=['datetime']).columns.tolist()
            
            schema_info = {
                'dataset_name': dataset_metadata.get('file_name', 'unknown'),
                'shape': current_dataset.shape,
                'columns': current_dataset.columns.tolist(),
                'dtypes': current_dataset.dtypes.astype(str).to_dict(),
                'missing_counts': current_dataset.isnull().sum().to_dict(),
                'column_types': {
                    'numeric': numeric_cols,
                    'categorical': categorical_cols,
                    'datetime': datetime_cols
                },
                'data_quality': {
                    'duplicates': int(current_dataset.duplicated().sum()),
                    'completeness': float((current_dataset.notna().sum().sum() / current_dataset.size) * 100)
                },
                'generated_at': pd.Timestamp.now().isoformat()
            }
            
            # Save JSON schema
            os.makedirs("outputs/logs", exist_ok=True)
            with open("outputs/logs/schema_map.json", "w") as f:
                json.dump(schema_info, f, indent=2, default=str)
            
            # Save enhanced Markdown schema
            with open("outputs/logs/schema_map.md", "w") as f:
                f.write(f"# Dataset Schema Analysis - {schema_info['dataset_name']}\n\n")
                f.write(f"**Generated:** {schema_info['generated_at']}\n\n")
                f.write(f"**Shape:** {schema_info['shape'][0]:,} rows × {schema_info['shape'][1]} columns\n\n")
                f.write(f"**Data Quality Score:** {schema_info['data_quality']['completeness']:.1f}%\n\n")
                
                f.write("## Data Type Summary\n\n")
                f.write(f"- **Numeric Columns ({len(numeric_cols)}):** {numeric_cols}\n")
                f.write(f"- **Categorical Columns ({len(categorical_cols)}):** {categorical_cols}\n")
                f.write(f"- **DateTime Columns ({len(datetime_cols)}):** {datetime_cols}\n\n")
                
                f.write("## Column Details\n\n")
                
                for col in current_dataset.columns:
                    dtype = current_dataset[col].dtype
                    unique_count = current_dataset[col].nunique()
                    null_count = current_dataset[col].isnull().sum()
                    null_pct = (null_count / len(current_dataset)) * 100
                    
                    f.write(f"### {col}\n")
                    f.write(f"- **Type:** {dtype}\n")
                    f.write(f"- **Unique Values:** {unique_count:,}\n")
                    f.write(f"- **Missing Values:** {null_count:,} ({null_pct:.1f}%)\n")
                    
                    if pd.api.types.is_numeric_dtype(current_dataset[col]):
                        stats = current_dataset[col].describe()
                        f.write(f"- **Range:** {stats['min']:.2f} to {stats['max']:.2f}\n")
                        f.write(f"- **Mean:** {stats['mean']:.2f}\n")
                    
                    f.write("\n")
            
            return "ENHANCED SCHEMA SAVED: outputs/logs/schema_map.json and schema_map.md with data profiling"
            
        except Exception as e:
            return f"ERROR saving schema: {str(e)}"

class LogTransformationToolInput(BaseModel):
    """Input schema for LogTransformationTool."""
    message: str = Field(..., description="Message to log about the transformation")

class LogTransformationTool(BaseTool):
    name: str = "Log Transformation Step"
    description: str = "Log a data transformation step with timestamp and context"
    args_schema: Type[BaseModel] = LogTransformationToolInput
    
    def _run(self, message: str) -> str:
        global transformation_log
        try:
            os.makedirs("outputs/logs", exist_ok=True)
            timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"**{timestamp}:** {message}"
            
            transformation_log.append(log_entry)
            
            with open("outputs/logs/transformation_log.md", "a", encoding='utf-8') as f:
                f.write(f"- {log_entry}\n")
            return f"LOGGED: {message}"
        except Exception as e:
            return f"ERROR logging transformation: {str(e)}"

class SaveReportToolInput(BaseModel):
    """Input schema for SaveReportTool."""
    content: str = Field(..., description="Content of the report to save")
    file_name: str = Field(default="report.md", description="Name of the file to save")

class SaveReportTool(BaseTool):
    name: str = "Save Analysis Report"
    description: str = "Save analysis reports to files with proper formatting and metadata"
    args_schema: Type[BaseModel] = SaveReportToolInput
    
    def _run(self, content: str, file_name: str = "report.md") -> str:
        try:
            if not file_name.endswith('.md'):
                file_name += '.md'
                
            os.makedirs("outputs/reports", exist_ok=True)
            file_path = f"outputs/reports/{file_name}"
            
            # Add metadata header
            timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            header = f"<!-- Generated on {timestamp} -->\n\n"
            
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(header + content)
                
            return f"REPORT SAVED: {file_path} ({len(content)} characters)"
        except Exception as e:
            return f"ERROR saving report: {str(e)}"