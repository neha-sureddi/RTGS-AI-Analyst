import os
import re
from dotenv import load_dotenv
from .crew import AgenticAICrew
from rich.console import Console

# Load environment variables from .env file
load_dotenv()
console = Console()

def get_dataset_filename():
    """Reads the dataset filename from the user_preferences.txt file."""
    try:
        with open("user_preferences.txt", "r") as f:
            for line in f:
                if line.startswith("DATASET_FILENAME="):
                    match = re.search(r'DATASET_FILENAME=(.*)', line.strip())
                    if match:
                        return match.group(1).strip()
    except FileNotFoundError:
        return None
    return None

def run():
    """Main execution function"""
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]ERROR:[/bold red] GOOGLE_API_KEY not found. Please set it in your .env file.")
        return

    dataset_filename = get_dataset_filename()
    if not dataset_filename:
        console.print("[bold red]ERROR:[/bold red] DATASET_FILENAME not found in [yellow]user_preferences.txt[/yellow].")
        console.print("Please specify the filename (e.g., birth_data.csv) and ensure the file exists in the 'data' folder.")
        return
        
    dataset_path = os.path.join("data", dataset_filename)

    if not os.path.exists(dataset_path):
        console.print(f"[bold red]ERROR:[/bold red] Dataset not found at [yellow]{dataset_path}[/yellow].")
        console.print("Please ensure the file is in the 'data' directory.")
        return

    agentic_crew = AgenticAICrew()
    agentic_crew.kickoff()

if __name__ == "__main__":
    run()