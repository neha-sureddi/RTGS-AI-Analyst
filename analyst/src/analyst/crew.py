import os
import yaml
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

# Import tools
from analyst.tools.data_tools import (
    ReadCSVTool, InspectDataTool, ViewColumnTool, SafeExecuteTool,
    CalculateStatsTool, SaveSchemaTool, LogTransformationTool, SaveReportTool,
    QuickCleanTool
)
from analyst.tools.save_chart_tool import SaveChartTool
from analyst.tools.detect_outliers_tool import DetectOutliersTool
from analyst.tools.trend_analysis_tool import TrendAnalysisTool

console = Console()

class AnalystCrew:
    def __init__(self, user_prefs=None):
        self.user_prefs = user_prefs or {}
        
        # Configure LLM with error handling
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                console.print("[red]ERROR: GEMINI_API_KEY not found in environment[/red]")
                raise ValueError("GEMINI_API_KEY not found")
            
            # Set for CrewAI compatibility
            os.environ["GOOGLE_API_KEY"] = gemini_api_key
            
            self.llm = LLM(
                model="gemini/gemini-1.5-flash",
                temperature=0.1,
                max_tokens=2500
            )
            console.print("[green]LLM configured successfully[/green]")
            
        except Exception as e:
            console.print(f"[red]LLM setup error: {str(e)}[/red]")
            raise

        # Create agents with simplified, focused roles
        self.data_ingestion_agent = Agent(
            role="Data Quality Inspector",
            goal=f"Load and assess the quality of {self.user_prefs.get('DATASET_FILENAME', 'dataset')} for governance analysis",
            backstory="Expert at quickly evaluating government datasets and identifying data quality issues",
            tools=[ReadCSVTool(), InspectDataTool(), ViewColumnTool(), SaveSchemaTool()],
            verbose=True,
            llm=self.llm,
            max_iter=4,
            memory=False
        )
        
        self.data_cleaning_agent = Agent(
            role="Data Cleaning Specialist", 
            goal="Clean the dataset and save it to outputs/cleaned_data/ for analysis",
            backstory="Specialist in preparing government data with comprehensive cleaning procedures",
            tools=[ViewColumnTool(), SafeExecuteTool(), QuickCleanTool(), 
                   LogTransformationTool(), DetectOutliersTool()],
            verbose=True,
            llm=self.llm,
            max_iter=5,
            memory=False
        )
        
        # Add SafeExecuteTool to the analysis agent's toolset
        self.analysis_agent = Agent(
            role="Governance Data Analyst",
            goal="Analyze the cleaned dataset to find patterns relevant to Telangana governance, applying user-specified filters.",
            backstory="Expert in extracting policy-relevant insights from government data",
            tools=[ReadCSVTool(), CalculateStatsTool(), SaveChartTool(), TrendAnalysisTool(), SafeExecuteTool()],
            verbose=True,
            llm=self.llm,
            max_iter=5,
            memory=False
        )
        
        self.policy_agent = Agent(
            role="Policy Advisor",
            goal="Create actionable policy recommendations based on data analysis findings",
            backstory="Senior policy advisor who transforms data insights into government action plans",
            tools=[SaveReportTool()],
            verbose=True,
            llm=self.llm,
            max_iter=3,
            memory=False
        )

        # Create tasks with clear, actionable descriptions
        self.data_ingestion_task = Task(
            description=self._get_ingestion_description(),
            expected_output="Dataset loaded with quality assessment and schema documentation saved",
            agent=self.data_ingestion_agent,
            output_file='outputs/logs/ingestion_report.md'
        )
        
        self.data_cleaning_task = Task(
            description=self._get_cleaning_description(),
            expected_output="Cleaned dataset saved as outputs/cleaned_data/cleaned_data.csv with transformation log",
            agent=self.data_cleaning_agent,
            context=[self.data_ingestion_task],
            output_file='outputs/logs/cleaning_report.md'
        )
        
        self.analysis_task = Task(
            description=self._get_analysis_description(),
            expected_output="Analysis report with insights and visualizations saved to outputs/",
            agent=self.analysis_agent,
            context=[self.data_cleaning_task],
            output_file='outputs/reports/analysis_report.md'
        )
        
        self.policy_task = Task(
            description=self._get_policy_description(),
            expected_output="Executive policy brief with specific recommendations saved to outputs/reports/",
            agent=self.policy_agent,
            context=[self.analysis_task],
            output_file='outputs/reports/policy_brief.md'
        )

        # Initialize crew
        self.crew = Crew(
            agents=[
                self.data_ingestion_agent,
                self.data_cleaning_agent, 
                self.analysis_agent,
                self.policy_agent
            ],
            tasks=[
                self.data_ingestion_task,
                self.data_cleaning_task,
                self.analysis_task,
                self.policy_task
            ],
            process=Process.sequential,
            verbose=True,
            memory=False
        )

    def _get_ingestion_description(self) -> str:
        dataset = self.user_prefs.get('DATASET_FILENAME', 'birth_data.csv')
        
        return f"""TASK: Load and inspect Telangana government dataset for quality assessment.

STEPS TO EXECUTE:
1. Load the dataset using `ReadCSVTool` with file_path="data/{dataset}".
2. Inspect the data's structure and types using `InspectDataTool` with aspect="overview".
3. Check for any missing data patterns using `InspectDataTool` with aspect="missing".
4. Finally, document the complete schema of the dataset using `SaveSchemaTool` with a descriptive file_name like "initial_schema". This will save the schema to outputs/logs/schema_map.md.

Provide a professional assessment of the dataset's quality and its readiness for detailed governance analysis."""

    def _get_cleaning_description(self) -> str:
        return """TASK: Clean the dataset thoroughly and save it for analysis.

CRITICAL REQUIREMENT: You MUST save a cleaned dataset to outputs/cleaned_data/cleaned_data.csv

EXECUTE THESE STEPS:
1. LogTransformationTool with message="Starting comprehensive data cleaning"
2. QuickCleanTool - performs automatic comprehensive cleaning and saves the dataset
3. ViewColumnTool - verify cleaning results on key columns
4. LogTransformationTool with message="Data cleaning completed successfully"

The QuickCleanTool will:
- Remove duplicate rows
- Clean text columns (strip spaces, standardize)
- Handle missing values intelligently
- Save cleaned dataset to outputs/cleaned_data/cleaned_data.csv

VERIFY: Ensure the cleaned dataset file exists and is properly saved."""

    def _get_analysis_description(self) -> str:
        analysis_year = self.user_prefs.get('ANALYSIS_YEAR', 'all')
        analysis_district = self.user_prefs.get('ANALYSIS_DISTRICT', 'all')
        
        task_description = """TASK: Analyze the cleaned dataset for governance insights.

STEPS TO EXECUTE:
1. Use `ReadCSVTool` with file_path="outputs/cleaned_data/cleaned_data.csv" to load the cleaned data.
"""
        # Dynamic filtering steps
        if analysis_year != 'all' and analysis_year:
            task_description += f"2. Use `SafeExecuteTool` with a pandas query to filter the DataFrame for the year {analysis_year}. For example, query=\"df = df[df['year'] == {analysis_year}]\".\n"
        if analysis_district != 'all' and analysis_district:
            task_description += f"3. Use `SafeExecuteTool` with a pandas query to filter the DataFrame for the district {analysis_district}. For example, query=\"df = df[df['DistrictName'] == '{analysis_district}']\".\n"

        # Core analysis and visualization steps
        task_description += """
4. Generate descriptive statistics using `CalculateStatsTool` with stat_type="describe".
5. Calculate value counts for the 'DistrictName' column using `CalculateStatsTool` with stat_type="value_counts".
6. Create a bar chart of the district distribution using `SaveChartTool` with plot_type="bar", x_column="DistrictName", and title="Data Distribution by District".
7. Analyze temporal trends using `TrendAnalysisTool` on the 'DateofRegister' column.
8. Create a line chart of the temporal trend using `SaveChartTool` with plot_type="line", x_column="DateofRegister", and title="Data Trends Over Time".

Provide a final report summarizing all key findings.
"""
        return task_description

    def _get_policy_description(self) -> str:
        return """TASK: Create executive policy brief for Telangana government.

BRIEF STRUCTURE (use SaveReportTool):

## Executive Summary
Top 3 critical findings that require immediate policy attention

## Priority Recommendations
4-5 specific, actionable interventions with:
- Problem statement with data evidence
- Specific action steps
- Responsible department
- Implementation timeline
- Success metrics

## Implementation Roadmap
- Phase 1 (0-6 months): Immediate actions
- Phase 2 (6-18 months): Medium-term reforms
- Phase 3 (18+ months): Long-term improvements

## Expected Outcomes
Quantifiable benefits for Telangana citizens

TARGET: Busy executives who need clear, actionable recommendations

Use SaveReportTool with content as the complete policy brief and file_name="telangana_policy_brief"."""

    def kickoff(self):
        """Execute the complete analysis pipeline"""
        
        console.print(Panel.fit(
            "[bold blue]TELANGANA GOVERNANCE ANALYST[/bold blue]\n"
            "[cyan]Multi-Agent Data Analysis System[/cyan]\n"
            f"[white]Processing: {self.user_prefs.get('DATASET_FILENAME', 'Unknown')}[/white]",
            border_style="blue"
        ))
        
        # Validate setup
        if not self._validate_setup():
            return None
        
        try:
            # Create output directories
            self._create_directories()
            
            console.print("[cyan]Starting analysis pipeline...[/cyan]")
            
            # Execute crew
            results = self.crew.kickoff()
            
            # Display results
            self._show_results()
            
            return results
            
        except Exception as e:
            console.print(f"[red]Pipeline error: {str(e)}[/red]")
            return None

    def _validate_setup(self) -> bool:
        """Validate all prerequisites"""
        
        # Check dataset
        dataset = self.user_prefs.get('DATASET_FILENAME')
        if not dataset:
            console.print("[red]ERROR: DATASET_FILENAME not specified[/red]")
            return False
        
        dataset_path = f"data/{dataset}"
        if not os.path.exists(dataset_path):
            console.print(f"[red]ERROR: {dataset_path} not found[/red]")
            
            # Show available files
            data_dir = Path("data")
            if data_dir.exists():
                csv_files = list(data_dir.glob("*.csv"))
                if csv_files:
                    console.print("[yellow]Available datasets:[/yellow]")
                    for file in csv_files:
                        console.print(f"  - {file.name}")
            return False
        
        # Test dataset readability
        try:
            test_df = pd.read_csv(dataset_path, nrows=3)
            console.print(f"[green]Dataset validated: {dataset} ({test_df.shape[1]} columns)[/green]")
        except Exception as e:
            console.print(f"[red]Cannot read dataset: {str(e)}[/red]")
            return False
        
        return True

    def _create_directories(self):
        """Create all output directories"""
        dirs = [
            "outputs/logs",
            "outputs/reports", 
            "outputs/insights",
            "outputs/cleaned_data"
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        console.print("[green]Output directories ready[/green]")

    def _show_results(self):
        """Display comprehensive results summary"""
        console.rule("[bold green]Analysis Complete[/bold green]")
        
        # Check all expected outputs
        expected_files = [
            ("Data Ingestion Report", "outputs/logs/ingestion_report.md"),
            ("Data Cleaning Report", "outputs/logs/cleaning_report.md"),
            ("Analysis Report", "outputs/reports/analysis_report.md"), 
            ("Policy Brief", "outputs/reports/policy_brief.md"),
            ("Cleaned Dataset", "outputs/cleaned_data/cleaned_data.csv"),
            ("Schema Documentation", "outputs/logs/schema_map.md"),
            ("Transformation Log", "outputs/logs/transformation_log.md")
        ]
        
        table = Table(title="Generated Outputs")
        table.add_column("Output Type", style="cyan")
        table.add_column("Status", style="green") 
        table.add_column("File Path", style="yellow")
        table.add_column("Size", style="white")
        
        for name, path in expected_files:
            if os.path.exists(path):
                size = os.path.getsize(path)
                if path.endswith('.csv'):
                    # Show row count for CSV
                    try:
                        df = pd.read_csv(path)
                        size_str = f"{len(df):,} rows"
                    except:
                        size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/1024:.1f} KB"
                
                table.add_row(name, "✅ Generated", path, size_str)
            else:
                table.add_row(name, "❌ Missing", path, "N/A")
        
        console.print(table)
        
        # Check visualizations
        insights_dir = Path("outputs/insights")
        if insights_dir.exists():
            charts = list(insights_dir.glob("*.png"))
            if charts:
                console.print(f"\n[bold blue]Visualizations Generated:[/bold blue]")
                for chart in charts:
                    console.print(f"  📊 {chart.name}")
        
        # Success message
        console.print(Panel(
            "[bold]Next Steps:[/bold]\n"
            "1. 📋 Review policy brief: outputs/reports/policy_brief.md\n"
            "2. 📊 Check cleaned data: outputs/cleaned_data/cleaned_data.csv\n"
            "3. 📈 View charts: outputs/insights/\n"
            "4. 📝 Read detailed logs: outputs/logs/",
            title="Analysis Pipeline Complete",
            border_style="green"
        ))
