# RTGS Agentic System - Real-Time Governance System

## 🎯 Overview

The **Real-Time Governance System (RTGS)** is an agentic AI system designed to process government datasets from the Telangana Open Data Portal and generate actionable insights for policymakers. Built using CrewAI framework with intelligent LLM selection - TinyLlama for simple operations and Gemini for complex analysis.

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
- Ollama setup (local LLM for TinyLlama)
- Perplexity API key (for advanced analysis)
- Crew AI

## 🔧 Technical Details

- **Framework**: CrewAI 0.177.0
- **LLM Models**: 
  - TinyLlama (Ollama local) - Data ingestion and standardization
  - Perplexity (API) - Complex analysis and policy insights
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

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
# Install using UV
uv sync

# Or using pip
pip install -e .
```

### 2. Setup Ollama (TinyLlama)
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull TinyLlama model
ollama pull tinyllama

# Start Ollama service
ollama serve
```

### 3. Setup Perplexity API (Optional but Recommended)
1. **Get API Key**: Visit [Perplexity API](https://www.perplexity.ai/settings/api) and create an API key
2. **Set Environment Variable**:
   ```bash
   # Windows
   set PERPLEXITY_API_KEY=your_api_key_here
   
   # Linux/Mac
   export PERPLEXITY_API_KEY=your_api_key_here
   
   # Or add to .env file
   echo "PERPLEXITY_API_KEY=your_api_key_here" >> .env
   ```

### 4. Configure Dataset
1. Place your CSV file in the `data/` directory
2. Update `knowledge/user_preference.txt`:
   ```
   DATASET_FILENAME=your_dataset.csv
   ANALYSIS_YEAR=2024
   ANALYSIS_DISTRICT=all
   CHART_TOP_N=10
   REPORT_FORMAT=Markdown
   ```

### 5. Run Analysis
```bash
# Run the complete analysis pipeline
uv run agentic_ai

# Or using the installed script
agentic_ai
```

## 🤖 LLM Model Selection

The system uses Perplexity for all agents to ensure consistent quality and proper tool execution:

- **Perplexity (All Agents)**: Used for all tasks when API key is available
  - Advanced reasoning capabilities for all tasks
  - Better at schema documentation and transformation logging
  - Superior analysis and policy insights
  - Proper tool execution and data handling
  - Requires API key
  
- **TinyLlama (Fallback)**: Used when Perplexity API key is not available
  - Local model, no API costs
  - Basic functionality but may struggle with complex tasks
  - Works offline

**Note**: Perplexity is strongly recommended for optimal results and proper tool execution.

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
