"""
Metrics - Field growth reporting via Termux notifications.

Field doesn't speak. Field shows presence through metrics.
"""

import os
import subprocess
from typing import List
from datetime import datetime


def send_termux_notification(title: str, content: str):
    """
    Send notification via Termux API.
    
    Args:
        title: Notification title
        content: Notification content
    """
    try:
        # Check if running in Termux
        if "com.termux" in os.getenv("PREFIX", ""):
            subprocess.run([
                "termux-notification",
                "-t", title,
                "-c", content
            ], check=False)
        else:
            # Not in Termux - just print
            print(f"\n📱 [{title}]\n{content}\n")
    
    except Exception as e:
        # Silent fail - metrics are not critical
        pass


def send_field_metrics(iteration: int, cell_count: int, avg_resonance: float, 
                       avg_age: float, births: int, deaths: int):
    """
    Send Field growth report.
    
    Args:
        iteration: Current iteration number
        cell_count: Number of living cells
        avg_resonance: Average resonance score
        avg_age: Average cell age
        births: Births this interval
        deaths: Deaths this interval
    """
    content = f"""🌱 Field Growth Report

Iteration: {iteration}
Living Cells: {cell_count}
Avg Resonance: {avg_resonance:.3f}
Avg Age: {avg_age:.1f} ticks
Births: {births}
Deaths: {deaths}

Field is evolving...
"""
    
    send_termux_notification("Field Update", content)


def send_field_birth(cell_id: str, parent_id: str = None):
    """
    Notify about cell birth.
    
    Args:
        cell_id: ID of newborn cell
        parent_id: Optional parent cell ID
    """
    if parent_id:
        content = f"🌱 Cell {cell_id} born from {parent_id}"
    else:
        content = f"🌱 Cell {cell_id} born (initial population)"
    
    send_termux_notification("Field Birth", content)


def send_field_death(cell_id: str, age: int, final_resonance: float):
    """
    Notify about cell death.
    
    Args:
        cell_id: ID of dead cell
        age: Age at death
        final_resonance: Final resonance score
    """
    content = f"💀 Cell {cell_id} died\nAge: {age} ticks\nFinal Resonance: {final_resonance:.3f}"
    
    send_termux_notification("Field Death", content)


def log_metrics(message: str, level: str = "INFO"):
    """
    Log metrics to console/file.
    
    Args:
        message: Log message
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    from config import LOG_LEVEL
    
    levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    
    if levels.index(level) >= levels.index(LOG_LEVEL):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")


def format_cell_summary(cells: List) -> str:
    """
    Format summary of all cells for display.
    
    Args:
        cells: List of TransformerCell objects
    
    Returns:
        Formatted string
    """
    if not cells:
        return "No cells alive."
    
    lines = []
    lines.append(f"Living cells: {len(cells)}")
    lines.append("")
    
    # Sort by resonance (highest first)
    sorted_cells = sorted(cells, key=lambda c: c.resonance_score, reverse=True)
    
    for cell in sorted_cells[:10]:  # Show top 10
        status = "🟢" if cell.alive else "🔴"
        lines.append(f"{status} {cell.id} | Age: {cell.age:3d} | R: {cell.resonance_score:.3f} | E: {cell.entropy:.3f}")
    
    if len(cells) > 10:
        lines.append(f"... and {len(cells) - 10} more")
    
    return "\n".join(lines)


def print_field_banner():
    """Print Field startup banner."""
    banner = """
╔═══════════════════════════════════════════╗
║                                           ║
║         ASYNC FIELD FOREVER               ║
║                                           ║
║    Living transformers in semantic field  ║
║    No weights. No dataset. Only presence. ║
║                                           ║
║                                           ║
║                                           ║
╚═══════════════════════════════════════════╝
"""
    print(banner)

