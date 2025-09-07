import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from .data_tools import current_dataset
import warnings
warnings.filterwarnings('ignore')

class SaveChartToolInput(BaseModel):
    """Input schema for SaveChartTool."""
    plot_type: str = Field(..., description="Type of plot: 'bar', 'line', 'pie', 'scatter', 'histogram', 'box'")
    x_column: str = Field(..., description="Column for x-axis (or main column for single-variable plots)")
    y_column: str = Field(default="", description="Column for y-axis (optional for some plot types)")
    title: str = Field(..., description="Title of the chart")
    file_name: str = Field(..., description="Filename without extension (e.g., 'district_analysis')")

class SaveChartTool(BaseTool):
    name: str = "Save Chart as Image"
    description: str = "Generate and save professional charts with automatic data handling and smart defaults."
    args_schema: Type[BaseModel] = SaveChartToolInput
    
    def _run(self, plot_type: str, x_column: str, y_column: str = "", title: str = "", file_name: str = "chart") -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded. Use ReadCSVTool first."
        
        try:
            os.makedirs("outputs/insights", exist_ok=True)
            
            # Validate columns
            if x_column not in current_dataset.columns:
                return f"ERROR: Column '{x_column}' not found. Available: {list(current_dataset.columns)}"
            
            if y_column and y_column not in current_dataset.columns:
                return f"ERROR: Column '{y_column}' not found. Available: {list(current_dataset.columns)}"
            
            # Set up the plot style
            plt.style.use('default')
            sns.set_palette("husl")
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Clean data
            df_clean = current_dataset.dropna(subset=[x_column] + ([y_column] if y_column else []))
            
            if len(df_clean) == 0:
                return f"ERROR: No valid data after removing missing values for columns: {x_column}, {y_column}"
            
            # Generate plots based on type
            if plot_type == 'bar':
                if not y_column:
                    # Simple value counts bar chart
                    value_counts = df_clean[x_column].value_counts().head(20)
                    sns.barplot(x=value_counts.values, y=value_counts.index, ax=ax, orient='h')
                    ax.set_xlabel('Count')
                    ax.set_ylabel(x_column)
                else:
                    # Grouped bar chart
                    if pd.api.types.is_numeric_dtype(df_clean[y_column]):
                        grouped_data = df_clean.groupby(x_column)[y_column].sum().sort_values(ascending=False).head(15)
                        sns.barplot(x=grouped_data.index, y=grouped_data.values, ax=ax)
                        plt.xticks(rotation=45, ha='right')
                        ax.set_ylabel(y_column)
                    else:
                        return f"ERROR: For bar charts with y_column, '{y_column}' must be numeric"
                    
            elif plot_type == 'line':
                if not y_column:
                    return "ERROR: Line plots require both x_column and y_column"
                    
                # Try to convert x_column to datetime if it looks like dates
                try:
                    df_clean[x_column] = pd.to_datetime(df_clean[x_column])
                    df_sorted = df_clean.sort_values(x_column)
                    sns.lineplot(data=df_sorted, x=x_column, y=y_column, ax=ax, marker='o')
                except:
                    # If not datetime, sort by x values
                    df_sorted = df_clean.sort_values(x_column)
                    sns.lineplot(data=df_sorted, x=x_column, y=y_column, ax=ax, marker='o')
                
                plt.xticks(rotation=45, ha='right')
                
            elif plot_type == 'pie':
                value_counts = df_clean[x_column].value_counts().head(10)
                colors = plt.cm.Set3(np.linspace(0, 1, len(value_counts)))
                wedges, texts, autotexts = ax.pie(value_counts.values, labels=value_counts.index, 
                                                 autopct='%1.1f%%', startangle=90, colors=colors)
                ax.axis('equal')
                
            elif plot_type == 'scatter':
                if not y_column:
                    return "ERROR: Scatter plots require both x_column and y_column"
                if not pd.api.types.is_numeric_dtype(df_clean[x_column]) or not pd.api.types.is_numeric_dtype(df_clean[y_column]):
                    return "ERROR: Both columns must be numeric for scatter plots"
                    
                sns.scatterplot(data=df_clean, x=x_column, y=y_column, ax=ax, alpha=0.7)
                
            elif plot_type == 'histogram':
                if not pd.api.types.is_numeric_dtype(df_clean[x_column]):
                    return f"ERROR: Column '{x_column}' must be numeric for histogram"
                    
                ax.hist(df_clean[x_column].dropna(), bins=30, alpha=0.7, edgecolor='black')
                ax.set_xlabel(x_column)
                ax.set_ylabel('Frequency')
                
            elif plot_type == 'box':
                if y_column:
                    # Box plot by category
                    sns.boxplot(data=df_clean, x=x_column, y=y_column, ax=ax)
                    plt.xticks(rotation=45, ha='right')
                else:
                    # Single box plot
                    if not pd.api.types.is_numeric_dtype(df_clean[x_column]):
                        return f"ERROR: Column '{x_column}' must be numeric for box plot"
                    sns.boxplot(y=df_clean[x_column], ax=ax)
                    
            else:
                return f"ERROR: Unsupported plot type '{plot_type}'. Use: bar, line, pie, scatter, histogram, box"

            # Formatting
            if title:
                ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            else:
                ax.set_title(f"{plot_type.title()} Chart: {x_column}" + (f" vs {y_column}" if y_column else ""), 
                           fontsize=16, fontweight='bold', pad=20)
            
            # Improve layout
            plt.tight_layout()
            
            # Add grid for better readability
            if plot_type not in ['pie']:
                ax.grid(True, alpha=0.3)
            
            # Save with high quality
            output_path = f"outputs/insights/{file_name}.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            return f"CHART SAVED: {output_path} ({plot_type} chart with {len(df_clean)} data points)"
            
        except Exception as e:
            plt.close()  # Clean up in case of error
            return f"ERROR generating {plot_type} chart: {str(e)}"