import argparse
from pathlib import Path
import polars as pl
import serial

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=Path, required=True,
                        help="Path to the dataset, e.g. /data/energyrunner/datasets/kws01")
    args = parser.parse_args()
    y_labels = (pl
        .read_csv(args.dataset_path / "y_labels.csv", has_header=False)
        .rename({"column_1": "file", "column_2": "n_classes", "column_3": "class"})
    )


    port = '/dev/ttyACM1'  # Replace with your serial port
    baudrate = 115200

    try:
        # Open the serial port
        ser = serial.Serial(port, baudrate)
        print(f"Connected to {port} at {baudrate} baud")

        while True:
            # Get input from the user
            message = input("Enter message to send (or 'exit'): ")

            if message.lower() == 'exit':
                break

            # Encode the message to bytes
            # You might need to adjust the encoding based on your application
            message_bytes = message.encode('utf-8')

            # Send the bytes
            ser.write(message_bytes)
            print(f"Sent: {message}")

    except serial.SerialException as e:
        print(f"Error: Could not open serial port: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")