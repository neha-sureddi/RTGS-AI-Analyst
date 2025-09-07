import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .crew import AnalystCrew
from rich.console import Console
from rich.panel import Panel
import pandas as pd

# Load environment variables
load_dotenv()

console = Console()

def get_user_preferences():
    """Read user preferences from user_preference.txt"""
    preferences = {}
    
    # Look for user_preference.txt in expected locations
    possible_paths = [
        Path(__file__).parent.parent / 'knowledge' / 'user_preference.txt',
        Path(__file__).parent.parent / 'user_preference.txt',
        Path('knowledge') / 'user_preference.txt',
        Path('user_preference.txt')
    ]
    
    pref_file = None
    for path in possible_paths:
        if path.exists():
            pref_file = path
            break
    
    if not pref_file:
        console.print("[red]ERROR: user_preference.txt not found[/red]")
        console.print("Expected locations:")
        for path in possible_paths:
            console.print(f"  - {path}")
        console.print("\nCreate user_preference.txt with:")
        console.print("DATASET_FILENAME=birth_data.csv")
        console.print("ANALYSIS_YEAR=all")
        console.print("ANALYSIS_DISTRICT=all")
        console.print("CHART_TOP_N=10")
        console.print("REPORT_FORMAT=markdown")
        return None
    
    try:
        with open(pref_file, "r", encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        preferences[key.strip()] = value.strip()
                    else:
                        console.print(f"[yellow]Invalid format line {line_num}: {line}[/yellow]")
        
        console.print(f"[green]Preferences loaded from {pref_file.name}[/green]")
        return preferences
        
    except Exception as e:
        console.print(f"[red]Error reading preferences: {str(e)}[/red]")
        return None

def validate_environment():
    """Validate environment setup"""
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 10):
        issues.append(f"Python 3.10+ required, found {sys.version}")
    
    # Check/create directories
    for dir_name in ["data", "outputs"]:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                console.print(f"[yellow]Created directory: {dir_name}[/yellow]")
            except Exception as e:
                issues.append(f"Cannot create {dir_name}: {str(e)}")
    
    # Check API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        console.print("[green]GEMINI_API_KEY found[/green]")
    else:
        issues.append("GEMINI_API_KEY not set in environment")
        console.print("[red]GEMINI_API_KEY missing - add to .env file[/red]")
    
    return issues

def display_startup_info(user_prefs):
    """Display configuration summary"""
    console.print(Panel.fit(
        "[bold blue]TELANGANA GOVERNANCE DATA ANALYST[/bold blue]\n"
        "[cyan]AI-Powered Multi-Agent Analysis[/cyan]",
        border_style="blue"
    ))
    
    if user_prefs:
        console.print("\n[bold]Configuration:[/bold]")
        console.print(f"Dataset: {user_prefs.get('DATASET_FILENAME', 'Not set')}")
        console.print(f"Year Filter: {user_prefs.get('ANALYSIS_YEAR', 'All')}")
        console.print(f"District Filter: {user_prefs.get('ANALYSIS_DISTRICT', 'All')}")
        console.print(f"Chart Limit: {user_prefs.get('CHART_TOP_N', '10')}")

def run():
    """Main execution function"""
    try:
        # Validate environment
        env_issues = validate_environment()
        if env_issues:
            console.print("[red]Environment issues:[/red]")
            for issue in env_issues:
                console.print(f"  - {issue}")
            console.print("\n[yellow]Please fix these issues before running[/yellow]")
            return
        
        # Load preferences
        user_prefs = get_user_preferences()
        if not user_prefs:
            console.print("[red]Cannot proceed without valid preferences[/red]")
            return
        
        # Step 3: Show configuration
        display_startup_info(user_prefs)
        
        # Validate dataset
        dataset_filename = user_prefs.get('DATASET_FILENAME')
        if not dataset_filename:
            console.print("[red]DATASET_FILENAME not in preferences[/red]")
            return
        
        dataset_path = Path("data") / dataset_filename
        if not dataset_path.exists():
            console.print(f"[red]Dataset not found: {dataset_path}[/red]")
            
            # Show available files
            data_dir = Path("data")
            if data_dir.exists():
                csv_files = list(data_dir.glob("*.csv"))
                if csv_files:
                    console.print("\nAvailable CSV files:")
                    for csv_file in csv_files:
                        console.print(f"  - {csv_file.name}")
            return
        
        # Quick dataset validation
        try:
            import pandas as pd
            sample = pd.read_csv(dataset_path, nrows=3)
            console.print(f"[green]Dataset validated: {sample.shape[1]} columns[/green]")
        except Exception as e:
            console.print(f"[red]Cannot read dataset: {str(e)}[/red]")
            return
        
        # Initialize and run analysis
        console.print("\n[cyan]Initializing AI agents...[/cyan]")
        analyst_crew = AnalystCrew(user_prefs)
        
        results = analyst_crew.kickoff()
        
        if results:
            console.print(Panel(
                "[bold green]Analysis completed successfully![/bold green]\n"
                "Check outputs folder for reports and insights.",
                title="Success",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "[bold red]Analysis failed or incomplete.[/bold red]",
                title="Error",
                border_style="red"
            ))
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        console.print("[yellow]Please check your setup and try again[/yellow]")

def train():
    """Placeholder for training functionality"""
    console.print("[yellow]Training not implemented[/yellow]")

def replay():
    """Placeholder for replay functionality"""
    console.print("[yellow]Replay not implemented[/yellow]")

def test():
    """Test system setup"""
    console.print("[cyan]Testing system...[/cyan]")
    
    # Test environment
    env_issues = validate_environment()
    if env_issues:
        console.print("[red]Environment test failed[/red]")
        return
    
    # Test preferences
    user_prefs = get_user_preferences()
    if not user_prefs:
        console.print("[red]Preferences test failed[/red]")
        return
    
    console.print("[green]All tests passed[/green]")

if __name__ == "__main__":
    run()
