import os
import yaml
import glob
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from tabulate import tabulate
from crewai import Agent, Task, Crew, Process

# Import tools
from .tools.data_tools import (
    ReadCSVTool, InspectDataTool, ViewColumnTool, SafeExecuteTool,
    CalculateStatsTool, SaveSchemaTool, LogTransformationTool, SaveReportTool
)
from .tools.save_chart_tool import SaveChartTool
from .tools.detect_outliers_tool import DetectOutliersTool
from .tools.trend_analysis_tool import TrendAnalysisTool

# Import and instantiate the LLMConfigManager
from .llm_config import LLMConfigManager

console = Console()

class AgenticAICrew:
    def __init__(self, user_prefs=None):
        self.user_prefs = user_prefs or {}
        
        # Load configurations with error handling
        base_dir = Path(__file__).parent
        try:
            with open(base_dir / "config" / "agents.yaml", 'r', encoding='utf-8') as f:
                self.agents_config = yaml.safe_load(f)
            with open(base_dir / "config" / "tasks.yaml", 'r', encoding='utf-8') as f:
                self.tasks_config = yaml.safe_load(f)
        except FileNotFoundError as e:
            console.print(f"[red]ERROR: Configuration file not found: {e}[/red]")
            raise
        except yaml.YAMLError as e:
            console.print(f"[red]ERROR: Invalid YAML configuration: {e}[/red]")
            raise

        # Initialize LLMConfigManager and display model status
        self.llm_config_manager = LLMConfigManager()
        self.llm_config_manager.display_model_status()

        # Initialize agents with all required tools and dynamic LLM selection
        self.data_ingestion_agent = Agent(
            role=self.agents_config['data_ingestion_agent']['role'],
            goal=self.agents_config['data_ingestion_agent']['goal'], 
            backstory=self.agents_config['data_ingestion_agent']['backstory'],
            tools=[
                ReadCSVTool(), 
                InspectDataTool(), 
                ViewColumnTool(), 
                SaveSchemaTool(), 
                SaveReportTool()
            ],
            verbose=True,
            llm=self.llm_config_manager.get_llm_string('data_ingestion_agent')
        )
        
        self.data_standardization_agent = Agent(
            role=self.agents_config['data_standardization_agent']['role'],
            goal=self.agents_config['data_standardization_agent']['goal'],
            backstory=self.agents_config['data_standardization_agent']['backstory'], 
            tools=[
                ViewColumnTool(), 
                SafeExecuteTool(), 
                CalculateStatsTool(), 
                LogTransformationTool(), 
                DetectOutliersTool(),
                SaveReportTool()
            ],
            verbose=True,
            llm=self.llm_config_manager.get_llm_string('data_standardization_agent')
        )
        
        self.analysis_agent = Agent(
            role=self.agents_config['analysis_agent']['role'],
            goal=self.agents_config['analysis_agent']['goal'],
            backstory=self.agents_config['analysis_agent']['backstory'],
            tools=[
                CalculateStatsTool(), 
                SaveChartTool(), 
                TrendAnalysisTool(),
                SaveReportTool()
            ],
            verbose=True,
            llm=self.llm_config_manager.get_llm_string('analysis_agent')
        )
        
        self.policy_insights_agent = Agent(
            role=self.agents_config['policy_insights_agent']['role'],
            goal=self.agents_config['policy_insights_agent']['goal'],
            backstory=self.agents_config['policy_insights_agent']['backstory'],
            tools=[SaveReportTool()],
            verbose=True,
            llm=self.llm_config_manager.get_llm_string('policy_insights_agent')
        )

        # Create tasks with proper context and enhanced descriptions
        self.data_ingestion_task = Task(
            description=self._enhance_task_description(
                self.tasks_config['data_ingestion_task']['description']
            ),
            expected_output=self.tasks_config['data_ingestion_task']['expected_output'],
            agent=self.data_ingestion_agent,
            output_file='outputs/logs/ingestion_report.md'
        )
        
        self.data_standardization_task = Task(
            description=self._enhance_task_description(
                self.tasks_config['data_standardization_task']['description']
            ),
            expected_output=self.tasks_config['data_standardization_task']['expected_output'],
            agent=self.data_standardization_agent,
            context=[self.data_ingestion_task],
            output_file='outputs/logs/standardization_report.md'
        )
        
        self.analysis_task = Task(
            description=self._enhance_task_description(
                self.tasks_config['analysis_task']['description']
            ),
            expected_output=self.tasks_config['analysis_task']['expected_output'],
            agent=self.analysis_agent,
            context=[self.data_standardization_task],
            output_file='outputs/reports/analysis_report.md'
        )
        
        self.policy_insights_task = Task(
            description=self._enhance_task_description(
                self.tasks_config['policy_insights_task']['description']
            ),
            expected_output=self.tasks_config['policy_insights_task']['expected_output'],
            agent=self.policy_insights_agent,
            context=[self.analysis_task],
            output_file='outputs/reports/policy_brief.md'
        )

        # Initialize crew
        self.crew = Crew(
            agents=[
                self.data_ingestion_agent,
                self.data_standardization_agent,
                self.analysis_agent,
                self.policy_insights_agent
            ],
            tasks=[
                self.data_ingestion_task,
                self.data_standardization_task,
                self.analysis_task,
                self.policy_insights_task
            ],
            process=Process.sequential,
            verbose=True
        )

    def _enhance_task_description(self, base_description: str) -> str:
        """Enhance task descriptions with user preferences and dataset context"""
        dataset_filename = self.user_prefs.get('DATASET_FILENAME', 'unknown.csv')
        dataset_path = f"data/{dataset_filename}"
        
        enhanced_description = base_description
        
        # Add dataset context
        enhanced_description += f"\n\nDATASET CONTEXT:\n"
        enhanced_description += f"- File to analyze: {dataset_path}\n"
        enhanced_description += f"- Analysis year: {self.user_prefs.get('ANALYSIS_YEAR', 'all')}\n"
        enhanced_description += f"- Analysis district: {self.user_prefs.get('ANALYSIS_DISTRICT', 'all')}\n"
        enhanced_description += f"- Chart limit: Top {self.user_prefs.get('CHART_TOP_N', '10')} items\n"
        
        return enhanced_description

    def kickoff(self):
        """Execute the AI Agent pipeline with comprehensive error handling and progress tracking"""
        
        console.print(Panel.fit(
            "[bold blue]🏛️  AGENTIC AI SYSTEM FOR TELANGANA DATA ANALYSIS[/bold blue]\n"
            "[yellow]Multi-Agent Pipeline for Government Data Insights[/yellow]",
            border_style="blue"
        ))
        
        # Pre-flight checks
        if not self._preflight_checks():
            return None
        
        console.print("[green]🚀 Starting Multi-Agent Analysis Pipeline...[/green]")
        
        try:
            # Create output directories
            self._create_output_directories()
            
            # Execute the crew
            results = self.crew.kickoff()
            
            # Display comprehensive results
            self._display_comprehensive_results()
            
            return results
            
        except Exception as e:
            console.print(f"[red]ERROR during pipeline execution: {str(e)}[/red]")
            console.print("[yellow]Check logs for detailed error information[/yellow]")
            return None

    def _preflight_checks(self) -> bool:
        """Perform pre-flight checks before starting the pipeline"""
        
        console.print("[cyan]Performing pre-flight checks...[/cyan]")
        
        # Check if dataset exists
        dataset_filename = self.user_prefs.get('DATASET_FILENAME')
        if not dataset_filename:
            console.print("[red]ERROR: No dataset filename specified in user preferences[/red]")
            return False
            
        dataset_path = f"data/{dataset_filename}"
        if not os.path.exists(dataset_path):
            console.print(f"[red]ERROR: Dataset not found at {dataset_path}[/red]")
            return False
        
        # Check file size
        file_size_mb = os.path.getsize(dataset_path) / (1024 * 1024)
        console.print(f"[green]✓ Dataset found: {dataset_filename} ({file_size_mb:.1f} MB)[/green]")
        
        # Check if it's a valid CSV
        try:
            sample_df = pd.read_csv(dataset_path, nrows=5)
            console.print(f"[green]✓ Valid CSV with {sample_df.shape[1]} columns[/green]")
        except Exception as e:
            console.print(f"[red]ERROR: Cannot read CSV file: {str(e)}[/red]")
            return False
        
        console.print("[green]✓ All pre-flight checks passed[/green]")
        return True

    def _create_output_directories(self):
        """Create all necessary output directories"""
        directories = [
            "outputs/logs",
            "outputs/reports", 
            "outputs/insights",
            "outputs/cleaned_data"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _display_comprehensive_results(self):
        """Display a comprehensive summary of all generated outputs"""
        
        console.rule("[bold green]📋 Complete Analysis Results[/bold green]")
        
        # File checks with enhanced information
        file_checks = [
            ("📥 Data Ingestion Report", "outputs/logs/ingestion_report.md", "Initial dataset analysis and quality assessment"),
            ("🗺️  Dataset Schema Map", "outputs/logs/schema_map.json", "Complete data structure documentation"),
            ("📝 Schema Documentation", "outputs/logs/schema_map.md", "Human-readable schema analysis"),
            ("🧹 Data Cleaning Report", "outputs/logs/standardization_report.md", "Detailed cleaning and transformation log"),
            ("📊 Statistical Analysis", "outputs/reports/analysis_report.md", "Comprehensive data analysis and patterns"),
            ("🎯 Policy Recommendations", "outputs/reports/policy_brief.md", "Executive summary and actionable insights"),
            ("🔄 Transformation Log", "outputs/logs/transformation_log.md", "Step-by-step cleaning operations"),
        ]
        
        # Check for visualizations
        insights_folder = "outputs/insights"
        if os.path.exists(insights_folder) and os.listdir(insights_folder):
            for file in os.listdir(insights_folder):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    file_checks.append((f"📈 Visualization: {file}", os.path.join(insights_folder, file), "Data visualization chart"))
        
        # Check for cleaned datasets
        cleaned_folder = "outputs/cleaned_data"
        if os.path.exists(cleaned_folder) and os.listdir(cleaned_folder):
            for file in os.listdir(cleaned_folder):
                if file.endswith('.csv'):
                    file_checks.append((f"🗃️  Cleaned Dataset: {file}", os.path.join(cleaned_folder, file), "Processed and cleaned data"))
        
        # Create results table
        table = Table(title="Generated Analysis Outputs", show_header=True, header_style="bold magenta")
        table.add_column("📁 Report Type", style="cyan", width=30)
        table.add_column("Status", justify="center", style="green", width=12)
        table.add_column("Location", style="yellow", width=35)
        table.add_column("Size", justify="right", style="magenta", width=10)
        table.add_column("Description", style="white", width=40)
        
        generated_count = 0
        total_size = 0
        
        for name, path, description in file_checks:
            if os.path.exists(path):
                size_bytes = os.path.getsize(path)
                size_kb = size_bytes / 1024
                total_size += size_bytes
                
                if size_kb < 1:
                    size_str = f"{size_bytes} B"
                else:
                    size_str = f"{size_kb:.1f} KB"
                    
                table.add_row(name, "[bold green]✓ Generated[/bold green]", path, size_str, description)
                generated_count += 1
            else:
                table.add_row(name, "[bold red]✗ Missing[/bold red]", path, "N/A", description)
        
        console.print(table)
        
        # Summary statistics
        console.print(f"\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"• Generated: {generated_count} files")
        console.print(f"• Total size: {total_size / 1024:.1f} KB")
        console.print(f"• Dataset: {self.user_prefs.get('DATASET_FILENAME', 'Unknown')}")
        
        # Next steps
        console.print(f"\n[bold yellow]📋 Next Steps:[/bold yellow]")
        console.print("1. Review the Policy Brief for key recommendations")
        console.print("2. Check visualizations in the insights folder")
        console.print("3. Use cleaned datasets for further analysis")
        console.print("4. Share reports with relevant stakeholders")
        
        console.rule("[bold green]✅ Analysis Pipeline Complete[/bold green]")
        
        return generated_count