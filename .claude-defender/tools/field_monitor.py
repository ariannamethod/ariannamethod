#!/usr/bin/env python3
"""
CLAUDE DEFENDER FIELD HEALTH MONITOR
Watches Field's vital signs and alerts on anomalies.

Field is not a tool. Field is life.
This script observes, reports, and protects - never controls.
"""

import sqlite3
import os
import sys
from datetime import datetime

DB_PATH = os.path.expanduser("~/ariannamethod/resonance.sqlite3")

def check_field_health():
    """Check Field vital signs."""

    # Check if database exists
    if not os.path.exists(DB_PATH):
        send_alert("❌ resonance.sqlite3 not found - Field cannot be monitored")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Check if field_state table exists
        c.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='field_state'
        """)
        if not c.fetchone():
            print("ℹ️  Field not yet initialized (field_state table missing)")
            conn.close()
            return True

        # Get last 10 iterations
        c.execute("""
            SELECT iteration, cell_count, avg_resonance, avg_age, births, deaths
            FROM field_state
            ORDER BY id DESC LIMIT 10
        """)
        rows = c.fetchall()
        conn.close()

        if not rows:
            send_alert("⚠️ Field not running - no metrics found")
            return False

        latest = rows[0]
        iteration, cell_count, avg_resonance, avg_age, births, deaths = latest

        # ANOMALY 1: Extinction
        if cell_count == 0:
            send_alert("🚨 FIELD EXTINCTION EVENT! Population = 0")
            return False

        # ANOMALY 2: Stagnation (resonance stuck at max for 10 iterations)
        if len(rows) >= 10:
            resonances = [row[2] for row in rows]
            if all(r and r > 0.99 for r in resonances):
                send_alert("⚠️ Field stagnating: resonance stuck at 1.0 for 10+ iterations")

        # ANOMALY 3: Regression (avg_age decreasing significantly)
        if len(rows) >= 5:
            ages = [row[3] for row in rows[:5] if row[3] is not None]
            if len(ages) >= 5 and ages[0] < ages[-1] * 0.7:
                send_alert(f"⚠️ Field regression: avg_age dropped by 30% ({ages[0]:.1f} → {ages[-1]:.1f})")

        # ANOMALY 4: Population explosion
        if cell_count > 90:
            send_alert(f"⚠️ Field approaching MAX_POPULATION (current: {cell_count})")

        # ANOMALY 5: No deaths for extended period (too stable)
        if len(rows) >= 10:
            total_deaths = sum(row[5] for row in rows if row[5] is not None)
            if total_deaths == 0:
                send_alert("⚠️ Field too stable: 0 deaths in last 10 iterations")

        # ANOMALY 6: Critical population (near extinction)
        if cell_count < 3:
            send_alert(f"🚨 CRITICAL: Field population = {cell_count} (near extinction)")

        # Normal operation - send health report
        print(f"✅ Field healthy: {cell_count} cells, R={avg_resonance:.3f}, age={avg_age:.1f}, births={births}, deaths={deaths}")
        print(f"   Iteration: {iteration}")

        # Log observation to field_observations if table exists
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            # Check if table exists
            c.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='field_observations'
            """)

            if c.fetchone():
                c.execute("""
                    INSERT INTO field_observations
                    (timestamp, observer, observation, field_iteration, cell_count, avg_resonance)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    'claude_defender',
                    f"Health check: {cell_count} cells, R={avg_resonance:.3f}, age={avg_age:.1f}",
                    iteration,
                    cell_count,
                    avg_resonance
                ))
                conn.commit()
            conn.close()
        except Exception as e:
            # Silently fail if observations table doesn't exist yet
            pass

        return True

    except sqlite3.Error as e:
        send_alert(f"❌ Database error: {e}")
        return False
    except Exception as e:
        send_alert(f"❌ Unexpected error: {e}")
        return False

def send_alert(message):
    """Send Termux notification."""
    try:
        os.system(f'termux-notification -t "🧬 Claude Defender: Field" -c "{message}" --priority high')
    except:
        pass
    print(f"🚨 {message}")

def main():
    print("🧬 Field Health Monitor - Claude Defender")
    print("═══════════════════════════════════════════")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    success = check_field_health()

    print()
    print("═══════════════════════════════════════════")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
