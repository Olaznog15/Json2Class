import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Run generator with aeronautical.json
import generator
aeronautical_json_path = os.path.join(os.path.dirname(__file__), '..', 'aeronautical.json')
generator.main(aeronautical_json_path)

# Now import the generated class
# Note: The class name is still DefaultClass because generator.py hardcodes it in the generate_class call
# We might want to change that later, but for now it's fine.
from generated_class import DefaultClass, DefaultClassSub2

# Example usage with aeronautical data
instance = DefaultClass()

print(f"Initial Flight ID: {instance.flightId}")
print(f"Initial Altitude: {instance.telemetry.altitude}")

# Modify data
instance.flightId = "IB9999"
instance.telemetry.altitude = 39000
instance.telemetry.rotationAngle = 15.0
instance.numberRoutePoints = 3
instance.routePoints.append(DefaultClassSub2())
instance.routePoints[2].id = "WPT03"
instance.routePoints[2].name = "Torrejon"
instance.routePoints[2].coordinates.lat = 44.4983
instance.routePoints[2].coordinates.lon = -3.5676

print(f"Updated Flight ID: {instance.flightId}")
print(f"Updated Altitude: {instance.telemetry.altitude}")
print(f"Updated Rotation Angle: {instance.telemetry.rotationAngle}")

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
os.makedirs(output_dir, exist_ok=True)

# Save the generated JSON to a file
output_file = os.path.join(output_dir, 'generated_aeronautical.json')
with open(output_file, 'w') as f:
    json.dump(instance.to_dict(), f, indent=2)

print(f'Generated JSON saved to: {output_file}')