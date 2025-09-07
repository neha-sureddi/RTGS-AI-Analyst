import pandas as pd
from crewai.tools import BaseTool
from .data_tools import current_dataset
from typing import Type
from pydantic import BaseModel, Field

class DetectOutliersToolInput(BaseModel):
    """Input schema for DetectOutliersTool."""
    column_name: str = Field(..., description="The numeric column to detect outliers in.")

class DetectOutliersTool(BaseTool):
    name: str = "DetectOutliersTool"
    description: str = "Detect outliers in a specific numeric column using Z-score and IQR methods."
    args_schema: Type[BaseModel] = DetectOutliersToolInput

    def _run(self, column_name: str) -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        if column_name not in current_dataset.columns or not pd.api.types.is_numeric_dtype(current_dataset[column_name]):
            return f"Column '{column_name}' not found or is not a numeric column."
            
        series = current_dataset[column_name].dropna()
        if series.empty:
            return f"Column '{column_name}' has no data to analyze."

        # Z-score method
        z_scores = (series - series.mean()) / series.std()
        z_score_outliers = z_scores.abs() > 3
        
        # IQR method
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        iqr_outliers = (series < lower_bound) | (series > upper_bound)

        report = [
            f"Outlier Detection Report for '{column_name}':",
            f" - Total Z-score Outliers: {z_score_outliers.sum()} ({z_score_outliers.sum()/len(series):.2%})",
            f" - Total IQR Outliers: {iqr_outliers.sum()} ({iqr_outliers.sum()/len(series):.2%})",
            " - Z-score Outliers (Sample):\n" + series[z_score_outliers].to_string(),
            " - IQR Outliers (Sample):\n" + series[iqr_outliers].to_string()
        ]
        return "\n".join(report)
