# RTGS Agentic System - Real-Time Governance System

## 🎯 Overview

The **Real-Time Governance System (RTGS)** is an agentic AI system designed to process government datasets from the Telangana Open Data Portal and generate actionable insights for policymakers. Built using CrewAI framework with Gemini 1.5 Flash LLM.

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

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- UV package manager
- Gemini API key

### Installation

1. **Clone and setup**:
```bash
cd rtgs_agentic_system
uv sync
```

2. **Configure API key** (already set in .env):
```bash
# Gemini API key is already configured
```

### Usage

#### Run with Birth Data
```bash
uv run python src/rtgs_agentic_system/main.py --dataset src/rtgs_agentic_system/dataset/birth_data_2023-01-01_2024-01-31.csv --output-dir ./birth_analysis
```

#### Run Demo Mode
```bash
uv run python src/rtgs_agentic_system/main.py demo
```

#### Available Commands
- `--dataset <path>`: Specify CSV dataset path
- `--output-dir <dir>`: Output directory for results
- `--verbose`: Enable verbose output
- `demo`: Run with sample data
- `train`: Train the crew
- `replay`: Replay from specific task
- `test`: Test the crew

## 📁 Project Structure

```
rtgs_agentic_system/
├── src/rtgs_agentic_system/
│   ├── config/
│   │   ├── agents.yaml          # Agent configurations
│   │   └── tasks.yaml           # Task definitions
│   ├── tools/                   # Custom tools
│   │   ├── data_tools.py        # Data ingestion
│   │   ├── cleaning_tools.py    # Data cleaning
│   │   ├── insight_tools.py     # Analysis & visualization
│   │   └── documentation_tools.py # Documentation
│   ├── dataset/                 # Sample datasets
│   │   └── birth_data_2023-01-01_2024-01-31.csv
│   ├── crew.py                  # Main crew definition
│   └── main.py                  # CLI interface
├── .venv/                       # Virtual environment
├── pyproject.toml              # Dependencies
└── README.md                   # This file
```

## 🔧 Technical Details

- **Framework**: CrewAI 0.177.0
- **LLM**: Gemini 1.5 Flash
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

## 🎯 Hackathon Compliance

✅ **Dataset Selection**: Telangana birth registration data (2023-2024)
✅ **Ingestion & Standardization**: Automated data profiling and schema creation
✅ **Cleaning & Transformation**: Missing value handling, outlier detection, type conversion
✅ **Insights Output**: Statistical analysis, correlations, policy recommendations
✅ **Logs & Documentation**: Comprehensive logging and human-readable reports
✅ **CLI-Accessible Results**: Terminal interface with file outputs
✅ **Data-Agnostic Design**: Works with any CSV dataset from Telangana portal

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

## 📝 Usage Examples

### Basic Analysis
```bash
# Analyze birth data
uv run python src/rtgs_agentic_system/main.py --dataset src/rtgs_agentic_system/dataset/birth_data_2023-01-01_2024-01-31.csv
```

### Custom Output Directory
```bash
# Save results to custom directory
uv run python src/rtgs_agentic_system/main.py --dataset data.csv --output-dir ./my_analysis
```

### Demo Mode
```bash
# Run with sample data
uv run python src/rtgs_agentic_system/main.py demo
```

## 🏆 Hackathon Features

- **Agentic Architecture**: Multi-agent coordination with CrewAI
- **Data Agnostic**: Works with any Telangana government dataset
- **Comprehensive Logging**: Full audit trail of data transformations
- **Policy-Ready Insights**: Clear, actionable recommendations
- **CLI-First Design**: Terminal-based interface for policymakers
- **Reproducible**: Single command execution for full pipeline

---

**Built for the RTGS Hackathon** - Transforming government data into actionable insights for better governance.