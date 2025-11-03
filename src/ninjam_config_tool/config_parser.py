# src/ninjam_config_tool/config_parser.py
import os
from typing import Dict, Any
from importlib import resources


class ConfigParser:
    """Handles reading and writing the NINJAM server .cfg files."""

    def read(self, filepath: str) -> Dict[str, str]:
        """
        Reads a .cfg file and returns a dictionary of key-value pairs.
        """
        config_data = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Ignore empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Split on the first whitespace
                parts = line.split(None, 1)
                if len(parts) == 2:
                    key, value = parts
                    config_data[key] = value
        return config_data


    def write(self, filepath: str, new_data: Dict[str, Any], template: bool = False):
        """
        Writes the new_data to the .cfg file.
        
        - If template=True: Writes a new file from a template.
        - If template=False: Reads the existing file at `filepath` and
          modifies only the keys present in `new_data`, preserving
          comments and other lines.
        """
        if template or not os.path.exists(filepath):
            self._write_template(filepath, new_data)
        else:
            self._modify_existing(filepath, new_data)


    def _modify_existing(self, filepath: str, new_data: Dict[str, Any]):
        """
        Performs a read-modify-write on an existing config file,
        preserving comments and file structure.
        """
        keys_to_update = set(new_data.keys())
        updated_lines = []

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('#'):
                updated_lines.append(line)
                continue

            parts = stripped_line.split(None, 1)
            if len(parts) == 2:
                key = parts[0]
                if key in keys_to_update:
                    # This is a key we manage. Write the new value.
                    updated_lines.append(f"{key} {new_data[key]}\n")
                    keys_to_update.remove(key)
                else:
                    # This is a key we don't manage. Preserve it.
                    updated_lines.append(line)
            else:
                # Malformed or other line. Preserve it.
                updated_lines.append(line)
        
        # Add any keys that were in new_data but not in the original file
        for key in keys_to_update:
             updated_lines.append(f"{key} {new_data[key]}\n")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)


    def _write_template(self, filepath: str, data: Dict[str, Any]):
        """
        Writes a new config file based on template.cfg,
        substituting the values from the data dict.
        """
        try:
            # Reads 'template.cfg' from our package data
            template_text = resources.read_text("ninjam_config_tool", "template.cfg")
        except FileNotFoundError:
            # Fallback in case package data is missing
            template_text = "# Fallback: Could not find template.cfg\n"

        lines = template_text.splitlines()
        new_lines = []

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('#'):
                new_lines.append(line)
                continue

            parts = stripped_line.split(None, 1)
            if len(parts) == 2:
                key = parts[0]
                if key in data:
                    # Substitute the value from our UI
                    new_lines.append(f"{key} {data[key]}")
                else:
                    # Keep the template's default
                    new_lines.append(line)
            else:
                new_lines.append(line)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_lines))