import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .crew import AgenticAICrew
from rich.console import Console
from rich.panel import Panel

# Load environment variables from .env file
load_dotenv()
console = Console()

def get_user_preferences():
    """
    Reads all user preferences from the user_preferences.txt file with robust error handling.
    """
    preferences = {}
    
    # Try multiple possible locations for the preferences file
    possible_paths = [
        Path(__file__).parent.parent.parent / 'knowledge' / 'user_preference.txt',
        Path(__file__).parent.parent / 'knowledge' / 'user_preference.txt',
        Path('knowledge') / 'user_preference.txt',
        Path('user_preference.txt')
    ]
    
    pref_file = None
    for path in possible_paths:
        if path.exists():
            pref_file = path
            break
    
    if not pref_file:
        console.print("[bold red]ERROR:[/bold red] user_preference.txt not found in any expected location")
        console.print("Expected locations:")
        for path in possible_paths:
            console.print(f"  - {path}")
        return None
    
    try:
        with open(pref_file, "r", encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Ignore comments and empty lines
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        preferences[key.strip()] = value.strip()
                    else:
                        console.print(f"[yellow]WARNING:[/yellow] Invalid format on line {line_num}: {line}")
        
        console.print(f"[green]✓ Loaded preferences from {pref_file}[/green]")
        return preferences
        
    except Exception as e:
        console.print(f"[bold red]ERROR:[/bold red] Failed to read preferences file: {str(e)}")
        return None

def validate_environment():
    """
    Validate that all required environment variables and dependencies are available.
    """
    issues = []
    
    if not os.getenv("API_BASE"):
        issues.append("API_BASE not found in environment variables")
    
    # Check Python version
    if sys.version_info < (3, 10):
        issues.append(f"Python 3.10+ required, found {sys.version}")
    
    # Check for required directories
    required_dirs = ["data", "outputs"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                console.print(f"[yellow]Created missing directory: {dir_name}[/yellow]")
            except Exception as e:
                issues.append(f"Cannot create directory {dir_name}: {str(e)}")
    
    return issues

def display_startup_info(user_prefs):
    """Display startup information and configuration summary"""
    
    console.print(Panel.fit(
        "[bold blue]TELANGANA GOVERNANCE DATA ANALYST[/bold blue]\n"
        "[cyan]AI-Powered Multi-Agent Analysis System[/cyan]\n\n"
        "[yellow]Hackathon Version - Optimized for Government Data[/yellow]",
        border_style="blue",
        title="🏛️ System Startup"
    ))
    
    if user_prefs:
        console.print("\n[bold]Configuration Summary:[/bold]")
        console.print(f"📊 Dataset: {user_prefs.get('DATASET_FILENAME', 'Not specified')}")
        console.print(f"📅 Analysis Year: {user_prefs.get('ANALYSIS_YEAR', 'All')}")
        console.print(f"🗺️ Analysis District: {user_prefs.get('ANALYSIS_DISTRICT', 'All')}")
        console.print(f"📈 Chart Limit: Top {user_prefs.get('CHART_TOP_N', '10')} items")
        console.print(f"📝 Report Format: {user_prefs.get('REPORT_FORMAT', 'Markdown')}")

def run():
    """
    Main execution function that orchestrates the AI agent crew with comprehensive error handling.
    """
    try:
        # Environment validation
        env_issues = validate_environment()
        if env_issues:
            console.print("[bold red]Environment Issues Detected:[/bold red]")
            for issue in env_issues:
                console.print(f"  ❌ {issue}")
            
            if any("API_BASE" in issue for issue in env_issues):
                console.print("\n[yellow]Please set your API_BASE in the .env file:[/yellow]")
                console.print("API_BASE=your_api_key_here")
                return
        
        # Load user preferences
        user_prefs = get_user_preferences()
        if not user_prefs:
            return
        
        # Display startup information
        display_startup_info(user_prefs)
        
        # Validate dataset
        dataset_filename = user_prefs.get('DATASET_FILENAME')
        if not dataset_filename:
            console.print("[bold red]ERROR:[/bold red] DATASET_FILENAME not specified in user_preferences.txt")
            console.print("Please add: DATASET_FILENAME=your_file.csv")
            return
        
        # Construct absolute dataset path
        dataset_path = Path("data") / dataset_filename
        if not dataset_path.exists():
            console.print(f"[bold red]ERROR:[/bold red] Dataset not found at {dataset_path}")
            console.print(f"Please ensure {dataset_filename} is in the 'data' directory")
            
            # Show available datasets
            data_dir = Path("data")
            if data_dir.exists():
                csv_files = list(data_dir.glob("*.csv"))
                if csv_files:
                    console.print("\n[yellow]Available CSV files in data directory:[/yellow]")
                    for csv_file in csv_files:
                        console.print(f"  - {csv_file.name}")
            return
        
        # Final validation - try to read a sample of the dataset
        try:
            import pandas as pd
            sample_df = pd.read_csv(dataset_path, nrows=3)
            console.print(f"[green]✓ Dataset validation successful: {sample_df.shape[1]} columns, sample loaded[/green]")
        except Exception as e:
            console.print(f"[bold red]ERROR:[/bold red] Cannot read dataset: {str(e)}")
            console.print("Please check that the file is a valid CSV format")
            return
        
        # Initialize and run the crew
        console.print("\n[cyan]Initializing AI Agent Crew...[/cyan]")
        agentic_crew = AgenticAICrew(user_prefs)
        
        # Execute the analysis pipeline
        results = agentic_crew.kickoff()
        
        if results:
            console.print(Panel(
                "[bold green]Analysis completed successfully![/bold green]\n"
                "Check the outputs folder for detailed reports and insights.",
                title="✅ Success",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "[bold red]Analysis failed or incomplete.[/bold red]\n"
                "Check error messages above for details.",
                title="❌ Failure",
                border_style="red"
            ))
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        console.print("[yellow]Please check your configuration and try again[/yellow]")

def train():
    """
    Placeholder for training functionality - could be used for fine-tuning agents
    """
    console.print("[yellow]Training functionality not implemented in this version[/yellow]")

def replay():
    """
    Placeholder for replay functionality - could replay previous analysis
    """
    console.print("[yellow]Replay functionality not implemented in this version[/yellow]")

def test():
    """
    Test function to validate the system setup
    """
    console.print("[cyan]Running system tests...[/cyan]")
    
    # Test environment
    env_issues = validate_environment()
    if env_issues:
        console.print("[red]Environment test failed[/red]")
        return
    
    # Test preferences loading
    user_prefs = get_user_preferences()
    if not user_prefs:
        console.print("[red]Preferences test failed[/red]")
        return
    
    console.print("[green]✅ All tests passed - system ready[/green]")

if __name__ == "__main__":
    run()
