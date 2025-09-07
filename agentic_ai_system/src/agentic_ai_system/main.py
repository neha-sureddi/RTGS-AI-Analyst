import os
import re
from dotenv import load_dotenv
from .crew import AgenticAICrew
from rich.console import Console

# Load environment variables from .env file
load_dotenv()
console = Console()

def get_user_preferences():
    """
    Reads all user preferences from the user_preferences.txt file.
    It parses key=value pairs, ignoring comments and empty lines.
    """
    preferences = {}
    try:
        pref_path = os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge', 'user_preference.txt')
        pref_path = os.path.abspath(pref_path)
        with open(pref_path, "r") as f:
            for line in f:
                line = line.strip()
                # Ignore comments and empty lines
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        preferences[key.strip()] = value.strip()
    except FileNotFoundError:
        console.print("[bold red]ERROR:[/bold red] The file [yellow]user_preference.txt[/yellow] was not found in the knowledge directory.")
        return None
    return preferences

def run():
    """
    Main execution function that orchestrates the AI agent crew.
    It loads user preferences and kicks off the workflow.
    """
    # Check for API key in the environment
    if not os.getenv("GEMINI_API_KEY"):
        console.print("[bold red]ERROR:[/bold red] GEMINI_API_KEY not found. Please set it in your .env file.")
        return

    # Get all user preferences from the configuration file
    user_prefs = get_user_preferences()
    if not user_prefs:
        return # Exit if the preferences file is missing or invalid

    # Safely get the dataset filename from the preferences
    dataset_filename = user_prefs.get('DATASET_FILENAME')
    if not dataset_filename:
        console.print("[bold red]ERROR:[/bold red] DATASET_FILENAME is not specified in [yellow]user_preferences.txt[/yellow].")
        console.print("Please specify the filename (e.g., birth_data.csv) and ensure the file exists in the 'data' folder.")
        return
        
    dataset_path = os.path.join("data", dataset_filename)

    # Validate that the dataset file exists
    if not os.path.exists(dataset_path):
        console.print(f"[bold red]ERROR:[/bold red] Dataset not found at [yellow]{dataset_path}[/yellow].")
        console.print("Please ensure the file is in the 'data' directory.")
        return

    # Initialize the crew and pass the user preferences for use in tasks
    agentic_crew = AgenticAICrew(user_prefs)
    
    # Kick off the agentic workflow
    agentic_crew.kickoff()

if __name__ == "__main__":
    run()