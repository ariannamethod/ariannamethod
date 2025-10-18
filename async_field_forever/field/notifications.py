"""
Metrics - Field growth reporting via Termux notifications.

Field doesn't speak. Field shows presence through metrics.
"""

import os
import subprocess
from typing import List
from datetime import datetime


def send_termux_notification(title: str, content: str, priority: str = "default"):
    """
    Send notification via Termux API.

    Args:
        title: Notification title
        content: Notification content
        priority: Notification priority (default, high, low)
    """
    try:
        # Check if running in Termux
        if "com.termux" in os.getenv("PREFIX", ""):
            subprocess.run([
                "termux-notification",
                "-t", title,
                "-c", content,
                "--priority", priority
            ], check=False)
        else:
            # Not in Termux - just print
            print(f"\n📱 [{title}] (priority: {priority})\n{content}\n")

    except Exception as e:
        # Silent fail - metrics are not critical
        pass


def send_field_metrics(iteration: int, cell_count: int, avg_resonance: float,
                       avg_age: float, births: int, deaths: int, force: bool = False):
    """
    Send Field growth report.

    Only sends if force=True (emergency) or scheduled time (every 6 hours).
    Regular updates: 4x per day. Emergency updates: always.

    Args:
        iteration: Current iteration number
        cell_count: Number of living cells
        avg_resonance: Average resonance score
        avg_age: Average cell age
        births: Births this interval
        deaths: Deaths this interval
        force: If True, send regardless of schedule (emergency)
    """
    # Emergency conditions (always notify)
    is_emergency = (
        cell_count == 0 or           # Extinction
        cell_count > 90 or           # Near population cap
        cell_count < 3 or            # Critical population
        (cell_count > 0 and avg_resonance > 0.95)  # Stagnation
    )

    # Only send if forced, emergency, or scheduled interval
    if not (force or is_emergency):
        return

    # Determine notification priority
    if cell_count == 0:
        emoji = "💀"
        title = "🚨 Field EXTINCTION"
        priority = "high"
    elif cell_count < 3:
        emoji = "⚠️"
        title = "⚠️ Field Critical"
        priority = "high"
    elif cell_count > 90:
        emoji = "📈"
        title = "⚠️ Field Population High"
        priority = "default"
    else:
        emoji = "🌱"
        title = "Field Update"
        priority = "default"

    content = f"""{emoji} Field Growth Report

Iteration: {iteration}
Living Cells: {cell_count}
Avg Resonance: {avg_resonance:.3f}
Avg Age: {avg_age:.1f} ticks
Births: {births}
Deaths: {deaths}

Field is evolving...
"""

    send_termux_notification(title, content, priority=priority)


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

