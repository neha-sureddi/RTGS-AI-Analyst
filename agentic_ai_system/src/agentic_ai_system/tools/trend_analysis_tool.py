import pandas as pd
from crewai.tools import BaseTool
from .data_tools import current_dataset
from typing import Type
from pydantic import BaseModel, Field

class TrendAnalysisToolInput(BaseModel):
    """Input schema for TrendAnalysisTool."""
    date_column: str = Field(..., description="The date column for trend analysis.")
    value_column: str = Field(..., description="The numeric column to analyze trends for.")
    frequency: str = Field("M", description="Frequency of the trend ('M' for monthly, 'Y' for yearly, 'Q' for quarterly).")

class TrendAnalysisTool(BaseTool):
    name: str = "TrendAnalysisTool"
    description: str = "Analyze time series trends for a given date and value column."
    args_schema: Type[BaseModel] = TrendAnalysisToolInput

    def _run(self, date_column: str, value_column: str, frequency: str = "M") -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded."
        
        try:
            temp_df = current_dataset.copy()
            temp_df[date_column] = pd.to_datetime(temp_df[date_column], errors='coerce')
            temp_df.dropna(subset=[date_column], inplace=True)
            
            if not pd.api.types.is_numeric_dtype(temp_df[value_column]):
                return f"Value column '{value_column}' is not numeric."

            grouped = temp_df.groupby(temp_df[date_column].dt.to_period(frequency))[value_column].sum()
            
            report = [
                f"Trend Analysis Report for '{value_column}' by '{date_column}' ({frequency}):",
                "--------------------------------------------------",
                grouped.to_string(),
                "--------------------------------------------------",
                "Summary Statistics of the Trend:",
                grouped.describe().to_string()
            ]

            return "\n".join(report)
        except Exception as e:
            return f"ERROR during trend analysis: {str(e)}"
