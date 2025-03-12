import argparse
from pathlib import Path
import polars as pl
import serial
import time

from serial_device import SerialDevice

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=Path, required=True,
                        help="Path to the dataset, e.g. /data/energyrunner/datasets/kws01")
    args = parser.parse_args()
    y_labels = (pl
        .read_csv(args.dataset_path / "y_labels.csv", has_header=False)
        .rename({"column_1": "file", "column_2": "n_classes", "column_3": "class"})
    )

    def send_command(ser, command):
        ser.send_command(command)
        time.sleep(0.05)

    port = '/dev/ttyACM1'  # Replace with your serial port
    baudrate = 115200
    chunk_size = 72
    try:
        # Open the serial port with echo enabled
        with SerialDevice(port, baudrate, delimiter="%") as ser:
            ser._echo = True
            print(f"Connected to {port} at {baudrate} baud")
            send_command(ser, "help")
            for row in y_labels.head(1).iter_rows(named=True):
                with open(args.dataset_path / row["file"], "rb") as file:
                    binary_data = file.read()
                n_bytes = len(binary_data)

                # Send the "db load" command
                command = f"db load {n_bytes}"
                send_command(ser, command)

                # Convert binary data to hex representation
                hex_data = ''.join([f'{byte:02x}' for byte in binary_data])

                # Send the hex data in chunks
                for i in range(0, len(hex_data), chunk_size):
                    chunk = hex_data[i:i + chunk_size]
                    chunk_command = f"db {chunk}"
                    send_command(ser, chunk_command)
                send_command(ser, "infer 1 0")
                print(f"Sent: {args.dataset_path / row['file']}, ground truth {row["class"]}")
                time.sleep(0.2)
                print("--------------------------------")
    except serial.SerialException as e:
        print(f"Error: Could not open serial port: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
