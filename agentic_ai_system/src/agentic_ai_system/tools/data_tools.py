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

current_dataset = None
dataset_metadata = {}

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."

class ReadCSVTool(BaseTool):
    name: str = "Read CSV Dataset"
    description: str = "Load a CSV file into memory for analysis"
    
    def _run(self, file_path: str) -> str:
        global current_dataset, dataset_metadata
        try:
            current_dataset = pd.read_csv(file_path)
            dataset_metadata = {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'loaded_at': pd.Timestamp.now().isoformat()
            }
            
            summary = (
                f"DATASET LOADED: {os.path.basename(file_path)}\n"
                f"ROWS: {current_dataset.shape[0]:,}\n"
                f"COLUMNS: {current_dataset.shape[1]}\n"
                f"MEMORY: {current_dataset.memory_usage(deep=True).sum() / 1024**2:.1f} MB\n\n"
                f"COLUMN NAMES:\n{list(current_dataset.columns)}\n\n"
                f"FIRST 3 ROWS:\n{current_dataset.head(3).to_string()}"
            )
            return summary
        except Exception as e:
            return f"ERROR loading {file_path}: {str(e)}"

class InspectDataTool(BaseTool):
    name: str = "Inspect Dataset Structure"
    description: str = "Get detailed information about the loaded dataset"
    
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
                
                return (
                    f"DATASET INFO:\n{info_str}\n\n"
                    f"NULL VALUES:\n{null_counts[null_counts > 0].to_string()}\n\n"
                    f"DUPLICATES: {duplicates} rows"
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
            
            return "Available aspects: overview, missing, types"
            
        except Exception as e:
            return f"ERROR: {str(e)}"

class ViewColumnTool(BaseTool):
    name: str = "Examine Specific Column"
    description: str = "Look at a specific column in detail"
    
    def _run(self, column_name: str) -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            if column_name not in current_dataset.columns:
                return f"Column '{column_name}' not found. Available: {list(current_dataset.columns)}"
            
            col = current_dataset[column_name]
            value_counts = col.value_counts().head(10)
            
            return (
                f"COLUMN: {column_name}\n"
                f"TYPE: {col.dtype}\n"
                f"UNIQUE VALUES: {col.nunique():,}\n"
                f"NULL COUNT: {col.isnull().sum():,}\n"
                f"TOTAL ROWS: {len(col):,}\n\n"
                f"TOP 10 VALUES:\n{value_counts.to_string()}\n\n"
                f"SAMPLE VALUES:\n{col.dropna().head(10).tolist()}"
            )
        except Exception as e:
            return f"ERROR: {str(e)}"

class SafeExecuteTool(BaseTool):
    name: str = "Execute Safe Pandas Operation"
    description: str = "Execute pandas operations with safety restrictions"
    
    def _run(self, operation: str, save_name: str = "cleaned") -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            # Whitelist of safe operations
            safe_operations = ['drop_duplicates', 'dropna', 'fillna', 'rename', 'drop', 'astype', 'replace', 'strip', 'lower', 'upper', 'to_datetime', 'apply']
            
            # Basic safety check
            dangerous_terms = ['import', 'exec', 'eval', '__', 'open', 'file']
            if any(term in operation.lower() for term in dangerous_terms):
                return f"UNSAFE OPERATION: {operation}"
            
            # Execute in restricted environment
            safe_env = {
                'df': current_dataset,
                'pd': pd,
                'np': np,
                '__builtins__': {},
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple
            }
            
            original_shape = current_dataset.shape
            result_df = eval(f"df.{operation}", safe_env)
            
            if isinstance(result_df, pd.DataFrame):
                current_dataset = result_df
                
                # Save cleaned dataset
                output_path = f"outputs/cleaned_data/{save_name}.csv"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                current_dataset.to_csv(output_path, index=False)
                
                return (
                    f"EXECUTED: df.{operation}\n"
                    f"ORIGINAL SHAPE: {original_shape}\n"
                    f"NEW SHAPE: {current_dataset.shape}\n"
                    f"SAVED TO: {output_path}"
                )
            else:
                return f"Operation returned {type(result_df)}, not DataFrame"
                
        except Exception as e:
            return f"EXECUTION ERROR: {str(e)}"

class CalculateStatsTool(BaseTool):
    name: str = "Calculate Statistics"
    description: str = "Calculate specific statistics on the dataset"
    
    def _run(self, stat_type: str, parameters: str = "") -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            if stat_type == "describe":
                return f"DESCRIPTIVE STATS:\n{current_dataset.describe(include='all').to_string()}"
            
            elif stat_type == "correlation":
                numeric_df = current_dataset.select_dtypes(include=[np.number])
                if numeric_df.empty:
                    return "No numeric columns for correlation"
                corr = numeric_df.corr()
                return f"CORRELATION MATRIX:\n{corr.to_string()}"
            
            elif stat_type == "groupby" and parameters:
                parts = parameters.split(',')
                if len(parts) < 3:
                    return "Format: group_column,value_column,agg_function"
                
                group_col, value_col, agg_func = [p.strip() for p in parts]
                
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
                else:
                    return "Available functions: sum, mean, count"
                
                return f"GROUPED {agg_func.upper()} - {group_col} by {value_col}:\n{result.to_string()}"
            
            elif stat_type == "value_counts" and parameters:
                col = parameters.strip()
                if col not in current_dataset.columns:
                    return f"Column '{col}' not found"
                counts = current_dataset[col].value_counts().head(15)
                return f"VALUE COUNTS for {col}:\n{counts.to_string()}"
            
            return "Available stats: describe, correlation, groupby, value_counts"
            
        except Exception as e:
            return f"ERROR: {str(e)}"

class SaveSchemaTool(BaseTool):
    name: str = "Save Dataset Schema"
    description: str = "Save schema mapping as JSON and Markdown"
    
    def _run(self, _: str = "") -> str:
        global current_dataset, dataset_metadata
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            schema_info = {
                'dataset_name': dataset_metadata.get('file_name', 'unknown'),
                'shape': current_dataset.shape,
                'columns': current_dataset.columns.tolist(),
                'dtypes': current_dataset.dtypes.astype(str).to_dict(),
                'missing_counts': current_dataset.isnull().sum().to_dict(),
                'generated_at': pd.Timestamp.now().isoformat()
            }
            
            # Save JSON schema
            os.makedirs("outputs/logs", exist_ok=True)
            with open("outputs/logs/schema_map.json", "w") as f:
                json.dump(schema_info, f, indent=2)
            
            # Save Markdown schema
            with open("outputs/logs/schema_map.md", "w") as f:
                f.write(f"# Schema Map - {schema_info['dataset_name']}\n\n")
                f.write(f"**Generated:** {schema_info['generated_at']}\n\n")
                f.write(f"**Shape:** {schema_info['shape'][0]:,} rows × {schema_info['shape'][1]} columns\n\n")
                f.write("## Column Details\n\n")
                
                for col in current_dataset.columns:
                    dtype = current_dataset[col].dtype
                    unique_count = current_dataset[col].nunique()
                    null_count = current_dataset[col].isnull().sum()
                    
                    f.write(f"### {col}\n")
                    f.write(f"- **Type:** {dtype}\n")
                    f.write(f"- **Unique Values:** {unique_count:,}\n")
                    f.write(f"- **Missing Values:** {null_count:,}\n\n")
            
            return "SCHEMA SAVED: outputs/logs/schema_map.json and schema_map.md"
            
        except Exception as e:
            return f"ERROR: {str(e)}"

class LogTransformationTool(BaseTool):
    name: str = "Log Transformation Step"
    description: str = "Log a data transformation step"
    
    def _run(self, message: str) -> str:
        try:
            os.makedirs("outputs/logs", exist_ok=True)
            with open("outputs/logs/transformation_log.md", "a") as f:
                timestamp = pd.Timestamp.now().strftime("%H:%M:%S")
                f.write(f"- **{timestamp}:** {message}\n")
            return f"LOGGED: {message}"
        except Exception as e:
            return f"ERROR: {str(e)}"

class SaveReportTool(BaseTool):
    name: str = "Save Analysis Report"
    description: str = "Save analysis reports to files"
    
    def _run(self, content: str, file_name: str = "report.md") -> str:
        try:
            if not file_name.endswith('.md'):
                file_name += '.md'
                
            os.makedirs("outputs/reports", exist_ok=True)
            file_path = f"outputs/reports/{file_name}"
            
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(content)
            return f"REPORT SAVED: {file_path}"
        except Exception as e:
            return f"ERROR: {str(e)}"

class SaveChartTool(BaseTool):
    name: str = "Save Chart as Image"
    description: str = "Generate and save a chart (bar, line, etc.) as a PNG file"
    
    def _run(self, plot_type: str, x_column: str, y_column: str, title: str, file_name: str) -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            os.makedirs("outputs/insights", exist_ok=True)
            
            plt.style.use('seaborn-v0_8-whitegrid')
            fig, ax = plt.subplots(figsize=(10, 6))

            if plot_type == 'bar':
                sns.barplot(x=x_column, y=y_column, data=current_dataset, ax=ax)
                plt.xticks(rotation=45, ha='right')
            elif plot_type == 'line':
                sns.lineplot(x=x_column, y=y_column, data=current_dataset, ax=ax)
                plt.xticks(rotation=45, ha='right')
            else:
                return "ERROR: Unsupported plot type. Use 'bar' or 'line'."

            ax.set_title(title, fontsize=16)
            ax.set_xlabel(x_column, fontsize=12)
            ax.set_ylabel(y_column, fontsize=12)
            plt.tight_layout()
            
            output_path = f"outputs/insights/{file_name}.png"
            plt.savefig(output_path, dpi=300)
            plt.close()

            return f"CHART SAVED: {output_path}"
        except Exception as e:
            return f"ERROR generating chart: {str(e)}"