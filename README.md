# NINJAM Config Tool

A cross-platform GUI tool to easily manage `ninjamsrv` configuration files.

## Installation

### From Source (via Pip)

1.  Clone this repository.
2.  Install in editable mode:
    ```bash
    pip install -e .
    ```
3.  Run the application:
    ```bash
    ninjam-config-tool
    ```

### As a Standalone Executable

Run PyInstaller to build the app:
```bash
pyinstaller --onefile --windowed --name=ninjam-config-tool src/ninjam_config_tool/main.py

```
