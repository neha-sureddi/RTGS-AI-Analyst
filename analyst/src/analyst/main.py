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
    """Read user preferences with better error handling"""
    preferences = {}
    
    # Look for user_preference.txt in multiple locations
    possible_paths = [
        Path('user_preference.txt'),
        Path('knowledge/user_preference.txt'),
        Path(__file__).parent.parent / 'user_preference.txt',
        Path(__file__).parent.parent / 'knowledge' / 'user_preference.txt'
    ]
    
    pref_file = None
    for path in possible_paths:
        if path.exists():
            pref_file = path
            break
    
    if not pref_file:
        console.print("[red]ERROR: user_preference.txt not found[/red]")
        console.print("\nExpected locations:")
        for path in possible_paths:
            console.print(f"  - {path}")
        
        console.print("\n[yellow]Creating default user_preference.txt...[/yellow]")
        # Create default preferences file
        default_content = """# Telangana Governance Data Analysis Configuration
DATASET_FILENAME=birth_data.csv
ANALYSIS_YEAR=all
ANALYSIS_DISTRICT=all
CHART_TOP_N=10
REPORT_FORMAT=markdown"""
        
        try:
            with open('user_preference.txt', 'w') as f:
                f.write(default_content)
            console.print("[green]Created user_preference.txt with default settings[/green]")
            pref_file = Path('user_preference.txt')
        except Exception as e:
            console.print(f"[red]Could not create user_preference.txt: {str(e)}[/red]")
            return None
    
    try:
        with open(pref_file, "r", encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    try:
                        key, value = line.split('=', 1)
                        preferences[key.strip()] = value.strip()
                    except ValueError:
                        console.print(f"[yellow]Skipping invalid line {line_num}: {line}[/yellow]")
        
        console.print(f"[green]Loaded preferences from {pref_file.name}[/green]")
        return preferences
        
    except Exception as e:
        console.print(f"[red]Error reading preferences: {str(e)}[/red]")
        return None

def validate_environment():
    """Enhanced environment validation"""
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 10):
        issues.append(f"Python 3.10+ required (found {sys.version})")
    
    # Check/create required directories
    required_dirs = ["data", "outputs", "outputs/logs", "outputs/reports", "outputs/insights", "outputs/cleaned_data"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                console.print(f"[yellow]Created directory: {dir_name}[/yellow]")
            except Exception as e:
                issues.append(f"Cannot create {dir_name}: {str(e)}")
    
    # Check API key with better error messaging
    gemini_key = os.getenv("GEMINI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if gemini_key or google_key:
        console.print("[green]API key found[/green]")
    else:
        issues.append("No API key found (GEMINI_API_KEY or GOOGLE_API_KEY)")
        console.print("[red]Missing API key![/red]")
        console.print("[yellow]Create .env file with:[/yellow]")
        console.print("GEMINI_API_KEY=your_api_key_here")
    
    # Check for required packages
    try:
        import crewai
        import pandas
        import matplotlib
        import seaborn
        import rich
        console.print("[green]All required packages available[/green]")
    except ImportError as e:
        issues.append(f"Missing package: {str(e)}")
    
    return issues

def display_startup_info(user_prefs):
    """Show system configuration"""
    console.print(Panel.fit(
        "[bold blue]TELANGANA GOVERNANCE DATA ANALYST[/bold blue]\n"
        "[cyan]AI-Powered Multi-Agent Analysis Pipeline[/cyan]\n"
        "[white]Version 1.0 - Production Ready[/white]",
        border_style="blue"
    ))
    
    if user_prefs:
        console.print("\n[bold]Configuration Summary:[/bold]")
        for key, value in user_prefs.items():
            console.print(f"  {key}: {value}")

def validate_dataset(dataset_filename):
    """Enhanced dataset validation"""
    if not dataset_filename:
        console.print("[red]No dataset specified in preferences[/red]")
        return False
    
    dataset_path = Path("data") / dataset_filename
    
    if not dataset_path.exists():
        console.print(f"[red]Dataset not found: {dataset_path}[/red]")
        
        # Show available datasets
        data_dir = Path("data")
        if data_dir.exists():
            csv_files = list(data_dir.glob("*.csv"))
            if csv_files:
                console.print("\n[yellow]Available datasets in data/ folder:[/yellow]")
                for i, csv_file in enumerate(csv_files, 1):
                    try:
                        df = pd.read_csv(csv_file, nrows=1)
                        console.print(f"  {i}. {csv_file.name} ({df.shape[1]} columns)")
                    except:
                        console.print(f"  {i}. {csv_file.name} (read error)")
            else:
                console.print("\n[red]No CSV files found in data/ folder[/red]")
                console.print("[yellow]Please add your dataset to the data/ folder[/yellow]")
        else:
            console.print("\n[red]data/ folder does not exist[/red]")
        
        return False
    
    # Test dataset readability
    try:
        sample_df = pd.read_csv(dataset_path, nrows=5)
        console.print(f"[green]Dataset validated: {dataset_filename}[/green]")
        console.print(f"  - Rows: {len(pd.read_csv(dataset_path)):,}")
        console.print(f"  - Columns: {sample_df.shape[1]}")
        console.print(f"  - Size: {dataset_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    except Exception as e:
        console.print(f"[red]Cannot read dataset: {str(e)}[/red]")
        console.print("[yellow]Check file format and encoding[/yellow]")
        return False

def run():
    """Main execution function with comprehensive error handling"""
    try:
        console.print("[cyan]Initializing Telangana Governance Analyst...[/cyan]")
        
        # Step 1: Validate environment
        env_issues = validate_environment()
        if env_issues:
            console.print("[red]Environment Setup Issues:[/red]")
            for issue in env_issues:
                console.print(f"  - {issue}")
            console.print("\n[yellow]Please fix these issues before running[/yellow]")
            return
        
        # Step 2: Load preferences
        user_prefs = get_user_preferences()
        if not user_prefs:
            console.print("[red]Cannot proceed without valid preferences[/red]")
            return
        
        # Step 3: Show configuration
        display_startup_info(user_prefs)
        
        # Step 4: Validate dataset
        dataset_filename = user_prefs.get('DATASET_FILENAME')
        if not validate_dataset(dataset_filename):
            console.print("[red]Dataset validation failed[/red]")
            return
        
        # Step 5: Initialize and run analysis
        console.print("\n[cyan]Starting AI analysis pipeline...[/cyan]")
        
        try:
            analyst_crew = AnalystCrew(user_prefs)
            console.print("[green]Crew initialized successfully[/green]")
            
            results = analyst_crew.kickoff()
            
            if results:
                console.print(Panel(
                    "[bold green]🎉 Analysis Completed Successfully![/bold green]\n\n"
                    "[white]Your Telangana governance analysis is ready.[/white]\n"
                    "[cyan]Check the outputs folder for all reports and insights.[/cyan]",
                    title="Success",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    "[bold red]❌ Analysis Failed[/bold red]\n\n"
                    "[white]The analysis did not complete successfully.[/white]\n"
                    "[yellow]Check the error messages above for details.[/yellow]",
                    title="Error", 
                    border_style="red"
                ))
                
        except Exception as crew_error:
            console.print(f"[red]Crew execution error: {str(crew_error)}[/red]")
            console.print("[yellow]This might be an API key issue or network problem[/yellow]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Analysis interrupted by user[/yellow]")
        console.print("[white]You can restart the analysis anytime by running the script again[/white]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        console.print("[yellow]Please check your setup and try again[/yellow]")

def train():
    """Training functionality placeholder"""
    console.print(Panel(
        "[bold yellow]Training Mode[/bold yellow]\n\n"
        "[white]Training functionality not implemented in this version.[/white]\n"
        "[cyan]The system uses pre-configured AI agents.[/cyan]",
        border_style="yellow"
    ))

def replay():
    """Replay functionality placeholder"""
    console.print(Panel(
        "[bold yellow]Replay Mode[/bold yellow]\n\n"
        "[white]Replay functionality not implemented in this version.[/white]\n"
        "[cyan]Re-run the analysis with: python -m analyst.main[/cyan]",
        border_style="yellow"
    ))

def test():
    """Comprehensive system test"""
    console.print("[cyan]🧪 Testing Telangana Governance Analyst System...[/cyan]\n")
    
    all_passed = True
    
    # Test 1: Environment
    console.print("[bold]Test 1: Environment Setup[/bold]")
    env_issues = validate_environment()
    if env_issues:
        console.print("[red]❌ Environment test failed[/red]")
        for issue in env_issues:
            console.print(f"   - {issue}")
        all_passed = False
    else:
        console.print("[green]✅ Environment test passed[/green]")
    
    # Test 2: Preferences
    console.print("\n[bold]Test 2: Configuration[/bold]")
    prefs = get_user_preferences()
    if not prefs:
        console.print("[red]❌ Configuration test failed[/red]")
        all_passed = False
    else:
        console.print("[green]✅ Configuration test passed[/green]")
        console.print(f"   - Found {len(prefs)} settings")
    
    # Test 3: Dataset
    if prefs:
        console.print("\n[bold]Test 3: Dataset Validation[/bold]")
        dataset = prefs.get('DATASET_FILENAME')
        if validate_dataset(dataset):
            console.print("[green]✅ Dataset test passed[/green]")
        else:
            console.print("[red]❌ Dataset test failed[/red]")
            all_passed = False
    
    # Test 4: Import test
    console.print("\n[bold]Test 4: Module Imports[/bold]")
    try:
        from analyst.tools.data_tools import ReadCSVTool
        from analyst.crew import AnalystCrew
        console.print("[green]✅ Import test passed[/green]")
    except Exception as e:
        console.print(f"[red]❌ Import test failed: {str(e)}[/red]")
        all_passed = False
    
    # Final result
    if all_passed:
        console.print(Panel(
            "[bold green]🎉 All Tests Passed![/bold green]\n\n"
            "[white]Your system is ready for analysis.[/white]\n"
            "[cyan]Run: python -m analyst.main[/cyan]",
            title="Test Results",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[bold red]❌ Some Tests Failed[/bold red]\n\n"
            "[white]Please fix the issues above before running analysis.[/white]",
            title="Test Results",
            border_style="red"
        ))

if __name__ == "__main__":
    run()