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
from .tools.data_tools import (
    ReadCSVTool, InspectDataTool, ViewColumnTool, SafeExecuteTool,
    CalculateStatsTool, SaveSchemaTool, LogTransformationTool, SaveReportTool
)
from .tools.custom_tool import MyCustomTool
from .tools.save_chart_tool import SaveChartTool
from .tools.detect_outliers_tool import DetectOutliersTool
from .tools.trend_analysis_tool import TrendAnalysisTool

console = Console()

class AgenticAICrew:
    def __init__(self):
        # Load configurations
        base_dir = Path(__file__).parent
        
        with open(base_dir / "config" / "agents.yaml", 'r') as f:
            self.agents_config = yaml.safe_load(f)
        
        with open(base_dir / "config" / "tasks.yaml", 'r') as f:
            self.tasks_config = yaml.safe_load(f)

        # Initialize agents with all relevant tools
        self.data_ingestion_agent = Agent(
            role=self.agents_config['data_ingestion_agent']['role'],
            goal=self.agents_config['data_ingestion_agent']['goal'], 
            backstory=self.agents_config['data_ingestion_agent']['backstory'],
            tools=[ReadCSVTool(), InspectDataTool(), ViewColumnTool(), SaveSchemaTool()],
            verbose=True,
            llm="gemini/gemini-1.5-flash"
        )
        
        self.data_standardization_agent = Agent(
            role=self.agents_config['data_standardization_agent']['role'],
            goal=self.agents_config['data_standardization_agent']['goal'],
            backstory=self.agents_config['data_standardization_agent']['backstory'], 
            tools=[ViewColumnTool(), SafeExecuteTool(), CalculateStatsTool(), LogTransformationTool(), DetectOutliersTool()],
            verbose=True,
            llm="gemini/gemini-1.5-flash"
        )
        
        self.analysis_agent = Agent(
            role=self.agents_config['analysis_agent']['role'],
            goal=self.agents_config['analysis_agent']['goal'],
            backstory=self.agents_config['analysis_agent']['backstory'],
            tools=[CalculateStatsTool(), SaveChartTool(), TrendAnalysisTool()],
            verbose=True,
            llm="gemini/gemini-1.5-flash"
        )
        
        self.policy_insights_agent = Agent(
            role=self.agents_config['policy_insights_agent']['role'],
            goal=self.agents_config['policy_insights_agent']['goal'],
            backstory=self.agents_config['policy_insights_agent']['backstory'],
            tools=[SaveReportTool()],
            verbose=True,
            llm="gemini/gemini-1.5-flash"
        )

        # Initialize tasks with human_input and output_json
        self.data_ingestion_task = Task(
            description=self.tasks_config['data_ingestion_task']['description'],
            expected_output=self.tasks_config['data_ingestion_task']['expected_output'],
            agent=self.data_ingestion_agent,
            human_input=True,
            output_json=True,
            output_file='outputs/logs/ingestion_report.json'
        )
        
        self.data_standardization_task = Task(
            description=self.tasks_config['data_standardization_task']['description'],
            expected_output=self.tasks_config['data_standardization_task']['expected_output'],
            agent=self.data_standardization_agent,
            context=[self.data_ingestion_task],
            output_file='outputs/logs/standardization_report.md'
        )
        
        self.analysis_task = Task(
            description=self.tasks_config['analysis_task']['description'],
            expected_output=self.tasks_config['analysis_task']['expected_output'],
            agent=self.analysis_agent,
            context=[self.data_standardization_task],
            output_file='outputs/reports/analysis_report.md'
        )
        
        self.policy_insights_task = Task(
            description=self.tasks_config['policy_insights_task']['description'],
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

    def kickoff(self):
        """Execute the AI Agent pipeline with enhanced CLI output"""
        console.print(Panel.fit(
            "[bold blue]🏛️  AGENTIC AI SYSTEM[/bold blue]\n"
            "[yellow]AI-Powered Policy Analysis for Telangana[/yellow]",
            border_style="blue"
        ))
        
        console.print("[green]🚀 Starting AI Agent Pipeline...[/green]")
        results = self.crew.kickoff()
        
        self._display_results_summary()
        
        return results

    def _display_results_summary(self):
        """Display a rich summary of generated outputs"""
        console.rule("[bold green]📋 Analysis Results Summary[/bold green]")
        
        file_checks = [
            ("📥 Ingestion Report", "outputs/logs/ingestion_report.json"),
            ("🧹 Standardization Report", "outputs/logs/standardization_report.md"),
            ("📊 Analysis Report", "outputs/reports/analysis_report.md"),
            ("🎯 Policy Brief", "outputs/reports/policy_brief.md"),
            ("🗺️  Schema Map (JSON)", "outputs/logs/schema_map.json"),
            ("📝 Transformation Log", "outputs/logs/transformation_log.md"),
        ]
        
        # Add insights folder check
        insights_folder = "outputs/insights"
        if os.path.exists(insights_folder) and os.listdir(insights_folder):
            for file in os.listdir(insights_folder):
                file_checks.append((f"📈 Insight: {file}", os.path.join(insights_folder, file)))
        
        table = Table(title="Generated Reports")
        table.add_column("Report Type", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Location", style="yellow")
        table.add_column("Size", style="magenta")
        
        for name, path in file_checks:
            if os.path.exists(path):
                size = f"{os.path.getsize(path) / 1024:.1f} KB"
                table.add_row(name, "[bold green]Generated[/bold green]", path, size)
            else:
                table.add_row(name, "[bold red]Missing[/bold red]", path, "N/A")
        
        console.print(table)
        console.rule("[bold green]✅ Pipeline Complete[/bold green]")
