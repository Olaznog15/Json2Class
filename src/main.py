import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Run generator
import generator
generator.main()

# Now import the generated class
from generated_class import DefaultClass

# Example usage: instantiate with defaults, then modify
instance = DefaultClass()
instance.flightId = "AF5678"  # Modify flight ID
# instance.flightData.altitude = 37000  # Modify altitude
instance.status = "landing"  # Change status

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(output_dir, exist_ok=True)

# Save the generated JSON to a file
output_file = os.path.join(output_dir, 'generated.json')
with open(output_file, 'w') as f:
    json.dump(instance.to_dict(), f, indent=2)

print(f'Generated JSON saved to: {output_file}')