import pandas as pd
import numpy as np
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from .data_tools import current_dataset

class DetectOutliersToolInput(BaseModel):
    """Input schema for DetectOutliersTool."""
    column_name: str = Field(..., description="The numeric column to detect outliers in.")
    method: str = Field(default="both", description="Method to use: 'zscore', 'iqr', or 'both'")

class DetectOutliersTool(BaseTool):
    name: str = "DetectOutliersTool"
    description: str = "Detect outliers in numeric columns using Z-score and IQR methods with detailed analysis."
    args_schema: Type[BaseModel] = DetectOutliersToolInput

    def _run(self, column_name: str, method: str = "both") -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded. Use ReadCSVTool first."
        
        try:
            if column_name not in current_dataset.columns:
                available_numeric = current_dataset.select_dtypes(include=[np.number]).columns.tolist()
                return f"Column '{column_name}' not found. Available numeric columns: {available_numeric}"
            
            if not pd.api.types.is_numeric_dtype(current_dataset[column_name]):
                return f"Column '{column_name}' is not numeric. Cannot detect outliers."
                
            series = current_dataset[column_name].dropna()
            if series.empty:
                return f"Column '{column_name}' has no valid data to analyze."

            results = []
            results.append(f"OUTLIER DETECTION REPORT for '{column_name}'")
            results.append("=" * 50)
            
            # Basic statistics
            results.append(f"Total values: {len(series):,}")
            results.append(f"Mean: {series.mean():.3f}")
            results.append(f"Std Dev: {series.std():.3f}")
            results.append(f"Min: {series.min():.3f}")
            results.append(f"Max: {series.max():.3f}")
            results.append("")

            if method in ["zscore", "both"]:
                # Z-score method (values beyond 3 standard deviations)
                z_scores = np.abs((series - series.mean()) / series.std())
                z_score_outliers = series[z_scores > 3]
                z_outlier_count = len(z_score_outliers)
                z_outlier_pct = (z_outlier_count / len(series)) * 100
                
                results.append(f"Z-SCORE METHOD (|z| > 3):")
                results.append(f"  Outliers found: {z_outlier_count:,} ({z_outlier_pct:.2f}%)")
                
                if z_outlier_count > 0:
                    results.append(f"  Outlier range: {z_score_outliers.min():.3f} to {z_score_outliers.max():.3f}")
                    if z_outlier_count <= 10:
                        results.append(f"  Outlier values: {z_score_outliers.tolist()}")
                    else:
                        results.append(f"  Sample outliers: {z_score_outliers.head(5).tolist()}")
                results.append("")

            if method in ["iqr", "both"]:
                # IQR method
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                iqr_outliers = series[(series < lower_bound) | (series > upper_bound)]
                iqr_outlier_count = len(iqr_outliers)
                iqr_outlier_pct = (iqr_outlier_count / len(series)) * 100

                results.append(f"IQR METHOD (1.5 * IQR rule):")
                results.append(f"  Q1: {Q1:.3f}")
                results.append(f"  Q3: {Q3:.3f}")
                results.append(f"  IQR: {IQR:.3f}")
                results.append(f"  Lower bound: {lower_bound:.3f}")
                results.append(f"  Upper bound: {upper_bound:.3f}")
                results.append(f"  Outliers found: {iqr_outlier_count:,} ({iqr_outlier_pct:.2f}%)")
                
                if iqr_outlier_count > 0:
                    results.append(f"  Outlier range: {iqr_outliers.min():.3f} to {iqr_outliers.max():.3f}")
                    if iqr_outlier_count <= 10:
                        results.append(f"  Outlier values: {iqr_outliers.tolist()}")
                    else:
                        results.append(f"  Sample outliers: {iqr_outliers.head(5).tolist()}")
                results.append("")

            # Recommendations
            results.append("RECOMMENDATIONS:")
            if method == "both":
                if z_outlier_count > 0 or iqr_outlier_count > 0:
                    results.append("- Consider investigating these outliers - they may represent:")
                    results.append("  * Data entry errors")
                    results.append("  * Exceptional cases requiring special attention")
                    results.append("  * Measurement errors")
                    results.append("- Before removing outliers, understand their business context")
                else:
                    results.append("- No significant outliers detected by either method")
                    results.append("- Data appears to follow normal distribution patterns")

            return "\n".join(results)

        except Exception as e:
            return f"ERROR during outlier detection: {str(e)}"