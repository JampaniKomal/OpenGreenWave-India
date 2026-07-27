import json
import math
import sys

def calculate_greenwave():
    print("=== OpenGreenWave-India Offset Calculator ===")
    print("This tool calculates the precise time offset required to synchronize")
    print("an offline traffic light for a continuous Green Wave.\n")

    try:
        # Prompt for inputs
        distance_m = float(input("Enter distance to the next intersection (in meters): "))
        speed_kmh = float(input("Enter target speed limit (in km/h): "))
        base_cycle_s = int(input("Enter base cycle time (in seconds, e.g., 60): "))
        
        # Convert speed from km/h to m/s
        speed_ms = speed_kmh * (1000 / 3600)
        
        # Calculate ideal offset in seconds
        if speed_ms <= 0:
            print("Error: Speed must be greater than 0.")
            return

        ideal_offset_s = distance_m / speed_ms
        
        # In a real traffic system, offset is modulo the base cycle time
        # so we don't have offsets larger than a single signal cycle.
        practical_offset_s = round(ideal_offset_s) % base_cycle_s
        
        print("\n--- Calculation Results ---")
        print(f"Target Speed: {speed_ms:.2f} m/s")
        print(f"Ideal Travel Time: {ideal_offset_s:.2f} seconds")
        print(f"Practical Offset (modulo base cycle): {practical_offset_s} seconds")
        
        # Generate JSON configuration
        config = {
            "green_wave_config": {
                "distance_m": distance_m,
                "target_speed_kmh": speed_kmh,
                "base_cycle_s": base_cycle_s,
                "calculated_offset_s": practical_offset_s
            }
        }
        
        json_output = json.dumps(config, indent=4)
        print("\n--- JSON Configuration Snippet (for ESP32) ---")
        print(json_output)
        
        # Optionally save to file
        save = input("\nSave this configuration to 'config.json'? (y/n): ").strip().lower()
        if save == 'y':
            with open("config.json", "w") as f:
                f.write(json_output)
            print("Saved to config.json. You can now transfer this to your ESP32.")

    except ValueError:
        print("\nError: Invalid input. Please enter numerical values.")
        sys.exit(1)

if __name__ == "__main__":
    calculate_greenwave()
