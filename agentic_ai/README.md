# RTGS Agentic System - Real-Time Governance System

## 🎯 Overview

The **Real-Time Governance System (RTGS)** is an agentic AI system designed to process government datasets from the Telangana Open Data Portal and generate actionable insights for policymakers. Built using CrewAI framework with Ollama LLM.

## 🏗️ System Architecture

### Agents
- **Data Ingestion Agent**: Loads and profiles datasets, creates standardized schemas
- **Data Cleaning Agent**: Handles data quality issues, missing values, and outliers
- **Insight Generation Agent**: Analyzes data and creates visualizations
- **Documentation Agent**: Generates comprehensive documentation and logs

### Tools
- **Data Ingestion Tool**: CSV loading and profiling
- **Data Cleaning Tool**: Data quality improvement and transformation
- **Insight Generation Tool**: Statistical analysis and visualization
- **Documentation Tool**: Report generation and logging

## 📊 Dataset Support

Currently tested with:
- **Birth Registration Data** (2023-2024): 6,075 records from Telangana districts
- **Multi-sector compatibility**: Agriculture, transport, health, education datasets

### Prerequisites
- Python 3.10+
- UV package manager
- Ollama setup (local LLM)
- Crew AI

## 🔧 Technical Details

- **Framework**: CrewAI 0.177.0
- **LLM**: Ollama (local)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **Package Manager**: UV

## 📈 Generated Outputs

The system generates:
- **Data Profile Reports**: JSON metadata and statistics
- **Cleaned Datasets**: Processed CSV files
- **Cleaning Logs**: Detailed transformation records
- **Insights Reports**: Analysis findings and recommendations
- **Visualizations**: Charts and graphs (PNG format)
- **Documentation**: Comprehensive workflow documentation

## 🔍 Sample Analysis Results

For the birth data (6,075 records):
- **Districts**: 33 Telangana districts covered
- **Time Period**: January 2023 - January 2024
- **Gender Distribution**: Male/Female birth ratios
- **Geographic Patterns**: District-wise birth trends
- **Temporal Analysis**: Monthly and yearly patterns

## 🚀 Next Steps

1. **Test with Multiple Datasets**: Agriculture, transport, health sectors
2. **Enhanced Visualizations**: Interactive charts and dashboards
3. **Policy Recommendations**: AI-generated policy suggestions
4. **Real-time Processing**: Live data integration
5. **Cross-sector Analysis**: Multi-dataset correlation analysis

## Features

- **Agentic Architecture**: Multi-agent coordination with CrewAI
- **Data Agnostic**: Works with any Telangana government dataset
- **Comprehensive Logging**: Full audit trail of data transformations
- **Policy-Ready Insights**: Clear, actionable recommendations
- **CLI-First Design**: Terminal-based interface for policymakers
- **Reproducible**: Single command execution for full pipeline

---
 Transforming government data into actionable insights for better governance.