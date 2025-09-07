import pandas as pd
import numpy as np
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from .data_tools import current_dataset

class TrendAnalysisToolInput(BaseModel):
    """Input schema for TrendAnalysisTool."""
    date_column: str = Field(..., description="The date column for trend analysis")
    value_column: str = Field(..., description="The numeric column to analyze trends for")
    frequency: str = Field(default="M", description="Frequency: 'D' (daily), 'M' (monthly), 'Y' (yearly), 'Q' (quarterly)")

class TrendAnalysisTool(BaseTool):
    name: str = "TrendAnalysisTool"
    description: str = "Analyze time series trends with statistical insights, seasonal patterns, and growth rates."
    args_schema: Type[BaseModel] = TrendAnalysisToolInput

    def _run(self, date_column: str, value_column: str, frequency: str = "M") -> str:
        global current_dataset
        if current_dataset is None:
            return "ERROR: No dataset loaded. Use ReadCSVTool first."
        
        try:
            # Validate columns exist
            if date_column not in current_dataset.columns:
                return f"ERROR: Date column '{date_column}' not found. Available: {list(current_dataset.columns)}"
            
            if value_column not in current_dataset.columns:
                return f"ERROR: Value column '{value_column}' not found. Available: {list(current_dataset.columns)}"
            
            # Work with a copy
            temp_df = current_dataset[[date_column, value_column]].copy()
            
            # Convert date column
            temp_df[date_column] = pd.to_datetime(temp_df[date_column], errors='coerce', infer_datetime_format=True)
            temp_df = temp_df.dropna(subset=[date_column])
            
            if temp_df.empty:
                return f"ERROR: No valid dates found in column '{date_column}'"
            
            # Ensure numeric value column
            temp_df[value_column] = pd.to_numeric(temp_df[value_column], errors='coerce')
            temp_df = temp_df.dropna(subset=[value_column])
            
            if temp_df.empty:
                return f"ERROR: No valid numeric values found in column '{value_column}'"
            
            # Sort by date
            temp_df = temp_df.sort_values(date_column)
            
            # Group by frequency
            freq_map = {
                'D': 'D',   # Daily
                'M': 'M',   # Monthly  
                'Q': 'Q',   # Quarterly
                'Y': 'Y'    # Yearly
            }
            
            if frequency not in freq_map:
                return f"ERROR: Invalid frequency '{frequency}'. Use: D, M, Q, Y"
            
            # Create period index and group
            temp_df['period'] = temp_df[date_column].dt.to_period(freq_map[frequency])
            grouped = temp_df.groupby('period')[value_column].agg(['sum', 'mean', 'count']).round(2)
            
            if grouped.empty:
                return "ERROR: No data available after grouping"
            
            results = []
            results.append(f"TREND ANALYSIS REPORT")
            results.append(f"Column: {value_column} by {date_column}")
            results.append(f"Frequency: {frequency} ({'Daily' if frequency=='D' else 'Monthly' if frequency=='M' else 'Quarterly' if frequency=='Q' else 'Yearly'})")
            results.append("=" * 60)
            
            # Date range
            date_range = f"{temp_df[date_column].min().strftime('%Y-%m-%d')} to {temp_df[date_column].max().strftime('%Y-%m-%d')}"
            results.append(f"Date Range: {date_range}")
            results.append(f"Total Periods: {len(grouped)}")
            results.append("")
            
            # Trend data (limit to last 20 periods for readability)
            results.append("TREND DATA (Most Recent 20 Periods):")
            results.append("-" * 40)
            trend_display = grouped.tail(20)
            
            for period, row in trend_display.iterrows():
                results.append(f"{str(period):>10} | Sum: {row['sum']:>10.1f} | Mean: {row['mean']:>8.2f} | Count: {int(row['count']):>5}")
            
            results.append("")
            
            # Statistical Summary
            results.append("STATISTICAL SUMMARY:")
            results.append("-" * 30)
            total_sum = grouped['sum'].sum()
            total_mean = grouped['sum'].mean()
            total_std = grouped['sum'].std()
            
            results.append(f"Total Value: {total_sum:,.2f}")
            results.append(f"Average per Period: {total_mean:,.2f}")
            results.append(f"Standard Deviation: {total_std:,.2f}")
            results.append(f"Coefficient of Variation: {(total_std/total_mean)*100:.1f}%")
            results.append("")
            
            # Growth Analysis (if we have enough periods)
            if len(grouped) >= 3:
                results.append("GROWTH ANALYSIS:")
                results.append("-" * 20)
                
                # Calculate period-over-period growth
                grouped['growth_rate'] = grouped['sum'].pct_change() * 100
                avg_growth = grouped['growth_rate'].mean()
                
                results.append(f"Average Growth Rate: {avg_growth:.2f}% per period")
                
                # Overall trend direction
                first_period = grouped['sum'].iloc[0]
                last_period = grouped['sum'].iloc[-1]
                overall_growth = ((last_period - first_period) / first_period) * 100
                
                results.append(f"Overall Growth: {overall_growth:.2f}% (from first to last period)")
                
                # Trend direction
                if overall_growth > 10:
                    trend_direction = "Strong Upward Trend"
                elif overall_growth > 2:
                    trend_direction = "Moderate Upward Trend"
                elif overall_growth < -10:
                    trend_direction = "Strong Downward Trend"
                elif overall_growth < -2:
                    trend_direction = "Moderate Downward Trend"
                else:
                    trend_direction = "Stable/Flat Trend"
                
                results.append(f"Trend Direction: {trend_direction}")
                results.append("")
                
                # Identify peaks and valleys
                max_period = grouped['sum'].idxmax()
                min_period = grouped['sum'].idxmin()
                max_value = grouped['sum'].max()
                min_value = grouped['sum'].min()
                
                results.append("NOTABLE PERIODS:")
                results.append("-" * 20)
                results.append(f"Highest Value: {max_value:,.2f} in {max_period}")
                results.append(f"Lowest Value: {min_value:,.2f} in {min_period}")
                results.append("")
            
            # Recent trend (last 6 periods if available)
            if len(grouped) >= 6:
                recent_data = grouped.tail(6)['sum']
                recent_trend = recent_data.iloc[-1] - recent_data.iloc[0]
                recent_growth = (recent_trend / recent_data.iloc[0]) * 100
                
                results.append("RECENT TREND (Last 6 Periods):")
                results.append("-" * 35)
                results.append(f"Recent Change: {recent_growth:.2f}%")
                
                if recent_growth > 5:
                    recent_direction = "Accelerating"
                elif recent_growth < -5:
                    recent_direction = "Declining"
                else:
                    recent_direction = "Stable"
                
                results.append(f"Recent Direction: {recent_direction}")
                results.append("")
            
            # Data Quality Notes
            results.append("DATA QUALITY NOTES:")
            results.append("-" * 25)
            original_count = len(current_dataset)
            valid_count = len(temp_df)
            data_completeness = (valid_count / original_count) * 100
            
            results.append(f"Data Completeness: {data_completeness:.1f}% ({valid_count:,}/{original_count:,} records)")
            
            if data_completeness < 90:
                results.append("⚠️  Warning: Low data completeness may affect trend reliability")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"ERROR during trend analysis: {str(e)}"