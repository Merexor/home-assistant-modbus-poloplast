# home-assistant-modbus-poloplast
Modbus Intergation for Poloplast ventilation systems (POLO-AIR-Serie) over Modbus RTU/TCP

# `poloplast-modbus` Python library

`poloplast-modbus` is an asynchronous, backend-neutral, and transport-independent Python library for communicating with Poloplast ventilation units over Modbus.

The library was developed primarily as the backend for the corresponding Home Assistant integration. It is independent of Home Assistant and can be used in any async Python project.

## Features

- Fully typed data model using `modbus-connection`.
- Grouped poll capabilities to retrieve ventilation status, sensor readings, and energy analytics in minimized Modbus reads.
- Supports any `modbus-connection` backend (`pymodbus`, `tmodbus`, or the mock framework).

## Installation

```bash
pip install poloplast-modbus
