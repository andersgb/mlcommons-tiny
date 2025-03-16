import argparse
import numpy as np
from pathlib import Path
import polars as pl
import serial
import time

from serial_device import SerialDevice

def parse_infer_results(res: list[str]):
    """
    res may look something like:
    [ 'm-ready', 'm-warmup-start-0', 'm-warmup-done', 'm-infer-start-3',
      'm-lap-us-2077028000', 'm-lap-us-2077237000', 'm-infer-done',
      'm-results-[0.000,0.000,0.000,0.000,0.000,0.089,0.000,0.000,0.000,0.000,0.000,0.910]'
    ]
    """
    n_inference = 0
    for i, line in enumerate(res):
        if "m-infer-start" in line:
            n_inference = int(line[len("m-infer-start-"):])
            break
    assert n_inference > 0
    assert "m-lap-us-" in res[i + 1]
    start_us = int(res[i + 1][len("m-lap-us-"):])
    assert "m-lap-us-" in res[i + 2]
    end_us = int(res[i + 2][len("m-lap-us-"):])
    assert "m-results-" in res[i + 4]
    results = res[i + 4][len("m-results-"):]
    results = results.strip('[]')  # Remove square brackets
    results = [float(x) for x in results.split(",")]
    print(f"infer {n_inference} took {(end_us - start_us)/1e3}ms, class {np.argmax(results)} ({np.max(results)})")
    return np.argmax(results)

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
        res = ser.send_command(command)
        print(f"RX> {res}")
        time.sleep(0.05)
        return res

    port = '/dev/ttyACM1'  # Replace with your serial port
    baudrate = 115200
    chunk_size = 72
    try:
        # Open the serial port with echo enabled
        with SerialDevice(port, baudrate, delimiter="%", end_of_response="<EOR>") as ser:
            ser._echo = False
            print(f"Connected to {port} at {baudrate} baud")
            send_command(ser, "help")
            wrong_predictions = set()
            for n_row, row in enumerate(y_labels.iter_rows(named=True)):
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
                    res = send_command(ser, chunk_command)
                assert "m-load-done" in res
                res = send_command(ser, "infer 1 0")
                assert "m-infer-done" in res
                pred = parse_infer_results(res)
                print(f"Sent: {args.dataset_path / row['file']}, ground truth {row["class"]}, pred {pred}")
                if pred != row["class"]:
                    wrong_predictions.add(n_row)
                    print(f"Wrong prediction: {args.dataset_path / row['file']}, ground truth {row["class"]}, pred {pred}")
                else:
                    print("Correct prediction")
                time.sleep(0.1)
                print("--------------------------------")
            print(f"Wrong predictions: {wrong_predictions}")
    except serial.SerialException as e:
        print(f"Error: Could not open serial port: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
