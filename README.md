# STM32 Nucleo-64 GPS & Pressure Tracker

A data logging project using the STM32 Nucleo-L452RE board with GNSS and environmental sensors to track position and altitude via GPS and barometric pressure.

## Hardware

- [Nucleo-L452RE](https://www.st.com/en/evaluation-tools/nucleo-l452re.html)
- [X-NUCLEO-GNSS1A1](https://www.st.com/en/ecosystems/x-nucleo-gnss1a1.html#overview) – GNSS expansion board with Teseo-LIV3F module
- [X-NUCLEO-IKS01A3](https://www.st.com/en/ecosystems/x-nucleo-iks01a3.html#overview) – Environmental sensor board (pressure, temperature, humidity)
- Optional: USB-UART bridge or Flipper Zero for live UART data debugging

## Features

- Logs GPS coordinates and timestamps using NMEA sentences via UART
- Measures atmospheric pressure using the LPS22HH sensor
- Calculates barometric altitude using the barometric height formula:  
  [Barometric Formula](https://www.apt-huerth.de/apt_eng/barometric-height-formula.html)
- Exports data to `.gpx` format for visualization (e.g., with [gpx.studio](https://gpx.studio/))
- Compares GPS-based vs pressure-based elevation

## Software

- STM32CubeIDE (HAL-based)
- Optionally: MicroPython custom firmware for STM32L4
- Python scripts for data post-processing and GPX generation

## Wiring Notes

If not using the stacked configuration:
- Connect GNSS1A1 `D2` (TX) → Nucleo `PA10` (RX)
- Connect `GND`, `3.3V`, and `IOREF`
- Connect I2C pins from IKS01A3 to Nucleo (`D14` → `PB9`, `D15` → `PB8`)
- Remove J11/J12 if necessary to avoid I2C conflicts

## License

MIT
