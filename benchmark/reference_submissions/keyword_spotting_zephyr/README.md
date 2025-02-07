Install zephyr and the required dependencies by following the instructions in the [official documentation](https://docs.zephyrproject.org/latest/getting_started/index.html).

```
west config manifest.project-filter -- +tflite-micro
west update
```
TODO:
-[ ] Find a good way to pin tflite-micro to a specific version without
modifying the manifest file.