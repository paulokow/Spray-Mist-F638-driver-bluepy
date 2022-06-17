# Python Library for controlling of Spray-Mist-F638

![test](https://github.com/paulokow/Spray-Mist-F638-driver-bluepy/workflows/test/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/paulokow/Spray-Mist-F638-driver-bluepy/branch/master/graph/badge.svg)](https://codecov.io/gh/paulokow/Spray-Mist-F638-driver-bluepy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Usage example

```python
from spraymistf638.driver import (
  SprayMistF638,
  WorkingMode,
  RunningMode,
  SprayMistF638Exception
)

device = SprayMistF638("11:11:11:11:11:11")
if device.connect():
  work_mode = device.working_mode
  run_mode = device.running_mode
  device.disconnect()
```
