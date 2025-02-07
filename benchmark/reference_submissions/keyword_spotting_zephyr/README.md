Install zephyr and the required dependencies by following the instructions in the [official documentation](https://docs.zephyrproject.org/latest/getting_started/index.html).

```
west config manifest.project-filter -- +tflite-micro
west update
```
TODO:
-[ ] Find a good way to pin tflite-micro to a specific version without
modifying the manifest file.

## Notes
- TFLite Micro `invoke()` may overwrite the input data (residing in the `tensor_arena`), so after first `invoke()` we typically get different results. For timing this is unimportant, but for comparing results we need to know this.