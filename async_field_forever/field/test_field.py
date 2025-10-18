"""Quick test to see Field in action."""

import time
from field_core import Field

# Create field
field = Field()

# Initialize population
field.initialize_population()

print(f"\n🧬 Field initialized with {len(field.cells)} cells\n")

# Run 5 iterations manually
for i in range(5):
    print(f"\n{'='*60}")
    print(f"ITERATION {i+1}")
    print(f"{'='*60}\n")
    
    field.tick()
    
    # Print summary
    print(f"\nLiving cells: {len(field.cells)}")
    print(f"Total births: {field.total_births}")
    print(f"Total deaths: {field.total_deaths}")
    
    if field.cells:
        avg_res = sum(c.resonance_score for c in field.cells) / len(field.cells)
        print(f"Avg resonance: {avg_res:.3f}")
        
        # Show top 3 cells
        sorted_cells = sorted(field.cells, key=lambda c: c.resonance_score, reverse=True)
        print(f"\nTop 3 cells:")
        for cell in sorted_cells[:3]:
            status = "🟢" if cell.alive else "🔴"
            print(f"  {status} {cell.id} | Age: {cell.age:2d} | R: {cell.resonance_score:.3f} | E: {cell.entropy:.3f}")
    
    time.sleep(2)

print("\n\n🧬 Field test complete. Check field_test.sqlite3 for full history.\n")

