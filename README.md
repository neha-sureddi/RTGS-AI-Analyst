# RTGS-Style AI Analyst for Telangana Open Data

[Link to your demo video here] 🎥

This project is an AI-powered data analysis pipeline designed to extract policy-relevant insights from Telangana government data. It uses a multi-agent system built on CrewAI to automate the entire process, from data ingestion and cleaning to analysis and policy brief generation. The pipeline is designed to be highly reproducible and flexible, capable of handling various tabular datasets with minimal configuration.

-----

## High-Level Agentic Architecture

The system is composed of four specialized AI agents working sequentially to complete a single, complex task. Each agent has a distinct role and a set of tools to perform its duties.

1.  **Data Quality Inspector**: This agent loads the raw dataset, performs initial quality checks, and documents the dataset's schema. It provides a foundational report on the data's readiness for analysis.
2.  **Data Cleaning Specialist**: Building on the inspector's report, this agent executes a series of automated and manual cleaning procedures. Its primary goal is to produce a clean, standardized dataset, logging all transformations for transparency.
3.  **Governance Data Analyst**: This agent is the analytical core of the system. It reads the cleaned data, performs statistical analysis, identifies key trends and patterns, and generates visualizations to support its findings.
4.  **Policy Advisor**: The final agent synthesizes the analyst's findings into a clear, actionable executive policy brief. It translates data insights into tangible recommendations for policymakers, complete with action steps and success metrics.

-----

## Models and Tools

  * **LLM**: The system is powered by **Google Gemini 1.5 Flash**, a powerful and efficient model well-suited for reasoning and tool-use tasks.
  * **Core Framework**: **CrewAI** orchestrates the entire multi-agent workflow, managing task execution and agent collaboration.
  * **Dependencies**: The agents use various custom and open-source Python libraries for their tasks, including **pandas** for data manipulation, **matplotlib** and **seaborn** for visualization, and **rich** for enhanced console logging.

-----

## Installation and Setup

### Prerequisites

  * **Python**: Version 3.10 or higher.
  * **Git**: For cloning the repository.
  * **Google Gemini API Key**: You need an API key from [Google AI Studio](https://ai.google.dev/) to use the LLM.

### Steps

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/neha-sureddi/RTGS-AI-Analyst.git
    cd RTGS-AI-Analyst
    ```

2.  **Set up the environment**:
    Create a `.env` file in the root directory and add your API key:

    ```
    GEMINI_API_KEY=YOUR_API_KEY_HERE
    ```

3.  **Place your dataset**:
    Place the CSV file you wish to analyze inside the `data/` directory.

-----

## Reproducible Run Command

To ensure a seamless experience, a single Python script handles all setup and execution. This script will install dependencies, validate the environment, and run the entire pipeline from start to finish.

Simply run this command from the root directory:

```bash
python run.py
```

-----

## Config Samples

The pipeline is configured via a `user_preference.txt` file in the root directory. You can modify this file to change the input dataset and customize the analysis.

**Example `user_preference.txt`:**

```
# Telangana Governance Data Analysis Configuration
DATASET_FILENAME=birth_data.csv
REPORT_FORMAT=markdown
```

-----

## Final Run Artifacts and Expected Outputs

Upon successful completion, the `outputs/` directory will be populated with the following artifacts, providing a complete record of the analysis:

  * **`outputs/cleaned_data/`**:
      * `cleaned_data.csv`: The standardized dataset used for the analysis.
  * **`outputs/insights/`**:
      * `district_distribution.png`: A bar chart visualizing the data distribution by district.
      * `temporal_trend.png`: A line chart showing data trends over time.
  * **`outputs/logs/`**:
      * `ingestion_report.md`: A summary of the initial data quality assessment.
      * `cleaning_report.md`: A log of all data cleaning and transformation steps.
      * `schema_map.md`: A complete, documented schema of the dataset.
      * `transformation_log.md`: A log detailing transformations applied to the data.
  * **`outputs/reports/`**:
      * `analysis_report.md`: The raw analysis findings from the Governance Data Analyst.
      * `policy_brief.md`: The final executive summary and recommendations.

-----

## Dataset Manifest

  * **Dataset Name**: `birth_data.csv`
  * **Time Range**: The dataset contains records from 2023 to 2024.
  * **Key Fields**:
      * `DistrictName`: Categorical data on the district where a record originated.
      * `MandalName`: Categorical data on the mandal (sub-district) of the record.
      * `PanchayatId`, `PanchayatName`: Unique identifiers and names for panchayats (village-level administrative units).
      * `DateofRegister`: Date the record was registered, used for temporal analysis.
      * `Gender`: Coded integer values representing gender.
      * `year`, `month`: Extracted features for year-over-year and monthly analysis.

 Transforming government data into actionable insights for better governance.
