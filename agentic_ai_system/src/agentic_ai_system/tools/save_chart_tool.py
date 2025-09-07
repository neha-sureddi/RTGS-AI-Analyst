import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from .data_tools import current_dataset

class SaveChartToolInput(BaseModel):
    """Input schema for SaveChartTool."""
    plot_type: str = Field(..., description="Type of plot ('bar', 'line', or 'pie').")
    x_column: str = Field(..., description="The column to be used for the x-axis.")
    y_column: str = Field(..., description="The column to be used for the y-axis.")
    title: str = Field(..., description="The title of the chart.")
    file_name: str = Field(..., description="The filename to save the chart as (e.g., 'district_births.png').")

class SaveChartTool(BaseTool):
    name: str = "Save Chart as Image"
    description: str = "Generate and save a chart (bar, line, or pie) as a PNG file."
    args_schema: Type[BaseModel] = SaveChartToolInput
    
    def _run(self, plot_type: str, x_column: str, y_column: str, title: str, file_name: str) -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded. Use ReadCSVTool first."
        
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
            elif plot_type == 'pie':
                # Pie charts typically use counts, so we'll need a different approach
                counts = current_dataset.groupby(x_column)[y_column].sum()
                ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
            else:
                return "ERROR: Unsupported plot type. Use 'bar', 'line', or 'pie'."

            ax.set_title(title, fontsize=16)
            if plot_type != 'pie':
                ax.set_xlabel(x_column, fontsize=12)
                ax.set_ylabel(y_column, fontsize=12)
                
            plt.tight_layout()
            
            output_path = f"outputs/insights/{file_name}"
            plt.savefig(output_path, dpi=300)
            plt.close()
            return f"CHART SAVED: {output_path}"
        except Exception as e:
            return f"ERROR generating chart: {str(e)}"