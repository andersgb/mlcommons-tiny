Install zephyr and the required dependencies by following the instructions in the [official documentation](https://docs.zephyrproject.org/latest/getting_started/index.html).

```
west config manifest.project-filter -- +tflite-micro
west update
```

TODO:
-[ ] Find a good way to pin tflite-micro to a specific version without
modifying the manifest file.

## Building and running the application

Use `west` to build and flash the application to the board, see `Makefile` for an example
Open a serial terminal to the board to see the output (replace `/dev/ttyACM1` with the correct device name):
```
minicom -D /dev/ttyACM1 -b 115200
```

## Running the Python runner
Follow the instructions in the `py_runner` directory to run the Python runner.

## Notes
- TFLite Micro `invoke()` may overwrite the input data (residing in the `tensor_arena`), so after first `invoke()` we typically get different results. For timing this is unimportant, but for comparing results we need to know this.