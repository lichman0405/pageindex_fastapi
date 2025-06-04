# The code is to define logging utilities for the application using Rich.
# Author: Shibo Li
# Date: 2025-05-30
# Version: 0.1.0

import json
from datetime import datetime
import os
from app.utils.pdf_utils import get_pdf_name
from rich.console import Console
from rich.logging import RichHandler
from rich.json import JSON
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
import logging

class JsonLogger:
    def __init__(self, file_path):
        # Extract PDF name for logger name
        pdf_name = get_pdf_name(file_path)
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"{pdf_name}_{current_time}.json"
        self.pdf_name = pdf_name
        os.makedirs("./logs", exist_ok=True)
        
        # Initialize Rich console
        self.console = Console(record=True, width=120)
        
        # Initialize empty list to store all messages
        self.log_data = []
        
        # Setup Rich logger
        self._setup_rich_logger()
        
        # Welcome message
        self._print_welcome()

    def _setup_rich_logger(self):
        """Setup Rich logging handler"""
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(
                    console=self.console,
                    rich_tracebacks=True,
                    show_path=False,
                    markup=False
                )
            ]
        )
        self.logger = logging.getLogger(f"JsonLogger-{self.pdf_name}")

    def _print_welcome(self):
        """Print welcome panel"""
        welcome_text = Text()
        welcome_text.append("📄 PDF Logger Initialized\n", style="bold blue")
        welcome_text.append(f"File: {self.pdf_name}\n", style="cyan")
        welcome_text.append(f"Log: {self.filename}", style="dim")
        
        panel = Panel(
            welcome_text,
            title="[bold green] Logger Ready [/bold green]",
            border_style="green",
            expand=False
        )
        self.console.print(panel)

    def _create_log_entry(self, level, message, **kwargs):
        """Create log entry with timestamp"""
        timestamp = datetime.now().isoformat()
        
        if isinstance(message, dict):
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                **message,
                **kwargs
            }
        else:
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "message": str(message),
                **kwargs
            }
        
        return log_entry

    def _get_level_style(self, level):
        """Get Rich style for different log levels"""
        styles = {
            "INFO": "blue",
            "ERROR": "red",
            "DEBUG": "yellow",
            "SUCCESS": "green"
        }
        return styles.get(level, "white")

    def _print_log_message(self, level, message, **kwargs):
        """Print formatted log message using Rich"""
        level_style = self._get_level_style(level)
        
        # Create level badge
        level_text = Text(f" {level} ", style=f"bold white on {level_style}")
        
        # Create message content
        if isinstance(message, dict):
            # Pretty print JSON
            json_content = JSON.from_data(message)
            self.console.print(level_text, json_content)
        else:
            # Regular message
            message_text = Text(str(message))
            self.console.print(level_text, message_text)
        
        # Print additional kwargs if any
        if kwargs:
            kwargs_table = Table(show_header=False, box=None, padding=(0, 1))
            for key, value in kwargs.items():
                kwargs_table.add_row(
                    Text(f"{key}:", style="dim"),
                    Text(str(value), style="cyan")
                )
            self.console.print("  ", kwargs_table)

    def log(self, level, message, **kwargs):
        """Main logging method"""
        # Create log entry
        log_entry = self._create_log_entry(level, message, **kwargs)
        self.log_data.append(log_entry)
        
        # Print to console with Rich formatting
        self._print_log_message(level, message, **kwargs)
        
        # Write to JSON file
        self._write_to_file()

    def _write_to_file(self):
        """Write log data to JSON file"""
        try:
            with open(self._filepath(), "w", encoding='utf-8') as f:
                json.dump(self.log_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"[red]Failed to write log file: {e}[/red]")

    def info(self, message, **kwargs):
        """Log info message"""
        self.log("INFO", message, **kwargs)

    def error(self, message, **kwargs):
        """Log error message"""
        self.log("ERROR", message, **kwargs)

    def debug(self, message, **kwargs):
        """Log debug message"""
        self.log("DEBUG", message, **kwargs)

    def success(self, message, **kwargs):
        """Log success message"""
        self.log("SUCCESS", message, **kwargs)

    def exception(self, message, **kwargs):
        """Log exception with traceback"""
        kwargs["exception"] = True
        
        # Print exception with Rich traceback
        self.console.print_exception(show_locals=True)
        
        self.log("ERROR", message, **kwargs)

    def print_summary(self):
        """Print summary of logged messages"""
        if not self.log_data:
            self.console.print("[yellow]No log entries yet[/yellow]")
            return
        
        # Count messages by level
        level_counts = {}
        for entry in self.log_data:
            level = entry.get('level', 'UNKNOWN')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Create summary table
        table = Table(title=f"📊 Log Summary for {self.pdf_name}")
        table.add_column("Level", style="bold")
        table.add_column("Count", justify="right")
        
        for level, count in level_counts.items():
            style = self._get_level_style(level)
            table.add_row(level, str(count), style=style)
        
        self.console.print(table)

    def save_console_output(self, filename=None):
        """Save Rich console output to HTML file"""
        if filename is None:
            filename = f"{self.pdf_name}_console_output.html"
        
        output_path = os.path.join("logs", filename)
        self.console.save_html(output_path)
        self.console.print(f"[green]Console output saved to: {output_path}[/green]")

    def _filepath(self):
        """Get log file path"""
        return os.path.join("logs", self.filename)
    

if __name__ == "__main__":
    # Example usage
    logger = JsonLogger("example.pdf")
    logger.info("This is an info message.")
    logger.error("This is an error message.")
    logger.debug({"key": "value"}, additional_info="Debugging details")
    logger.success("Operation completed successfully!")
    
    # Print summary of logged messages
    logger.print_summary()