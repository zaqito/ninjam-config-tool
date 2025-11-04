# src/ninjam_config_tool/config_parser.py
import os
from typing import Dict, Any, List
from importlib import resources


class ConfigParser:
    """Handles reading and writing the NINJAM server .cfg files."""

    def read(self, filepath: str) -> Dict[str, Any]:
        """
        Reads a .cfg file and returns a structured dictionary.
        """
        config_data = {
            "settings": {},
            "users": [],
            "acls": []
        }

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(None)
                if not parts:
                    continue
                
                keyword = parts[0]
                
                # Check for list-based items first
                if keyword == 'User' and len(parts) >= 3:
                    user_data = {
                        "username": parts[1],
                        "password": parts[2],
                        "permissions": parts[3] if len(parts) > 3 else ""
                    }
                    config_data["users"].append(user_data)
                
                elif keyword == 'ACL' and len(parts) == 3:
                    acl_data = {
                        "mask": parts[1],
                        "action": parts[2]
                    }
                    config_data["acls"].append(acl_data)
                
                # Fallback to key-value settings
                elif len(parts) >= 2:
                    key = parts[0]
                    value = " ".join(parts[1:]) # Re-join value if it has spaces
                    config_data["settings"][key] = value

        return config_data


    def write(self, filepath: str, 
              settings_data: Dict[str, Any], 
              user_list: List[Dict[str, str]],
              acl_list: List[Dict[str, str]],
              template: bool = False):
        """
        Writes all config data to the .cfg file.
        """
        if template or not os.path.exists(filepath):
            self._write_template(filepath, settings_data, user_list, acl_list)
        else:
            self._modify_existing(filepath, settings_data, user_list, acl_list)


    def _modify_existing(self, filepath: str, 
                         settings_data: Dict[str, Any],
                         user_list: List[Dict[str, str]],
                         acl_list: List[Dict[str, str]]):
        """
        Performs a read-modify-write on an existing config file,
        preserving comments and file structure.
        """
        keys_to_update = set(settings_data.keys())
        updated_lines = []

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            stripped_line = line.strip()
            
            # Preserve comments and empty lines
            if not stripped_line or stripped_line.startswith('#'):
                updated_lines.append(line)
                continue

            parts = stripped_line.split(None)
            if not parts:
                updated_lines.append(line)
                continue
            
            keyword = parts[0]

            # --- Skip old User and ACL lines; we'll add them fresh ---
            if keyword == 'User' or keyword == 'ACL':
                continue
            
            # Check if it's a setting we manage
            if keyword in keys_to_update:
                updated_lines.append(f"{keyword} {settings_data[keyword]}\n")
                keys_to_update.remove(keyword)
            else:
                # This is a key we don't manage. Preserve it.
                updated_lines.append(line)
        
        # Add any keys that were in new_data but not in the original file
        for key in keys_to_update:
             updated_lines.append(f"{key} {settings_data[key]}\n")

        # --- Add back the User and ACL lists from our app state ---
        if user_list:
            updated_lines.append("\n# --- User Accounts ---\n")
            for user in user_list:
                perms = user.get('permissions', '')
                line = f"User {user['username']} {user['password']} {perms}\n"
                updated_lines.append(line.strip() + "\n") # Clean up extra space if no perms

        if acl_list:
            updated_lines.append("\n# --- Access Control List ---\n")
            for acl in acl_list:
                updated_lines.append(f"ACL {acl['mask']} {acl['action']}\n")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)


    def _write_template(self, filepath: str, 
                        settings_data: Dict[str, Any],
                        user_list: List[Dict[str, str]],
                        acl_list: List[Dict[str, str]]):
        """
        Writes a new config file based on template.cfg,
        substituting values and appending lists.
        """
        try:
            template_text = resources.read_text("ninjam_config_tool", "template.cfg")
        except FileNotFoundError:
            template_text = "# Fallback: Could not find template.cfg\n"

        lines = template_text.splitlines()
        new_lines = []

        # Substitute simple settings
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('#'):
                new_lines.append(line)
                continue
            
            parts = stripped_line.split(None, 1)
            if len(parts) == 2:
                key = parts[0]
                if key in settings_data:
                    new_lines.append(f"{key} {settings_data[key]}")
                # Don't add User/ACL lines from template, we'll add them from state
                elif key not in ('User', 'ACL'):
                    new_lines.append(line)
            else:
                 new_lines.append(line)
        
        # Add lists from state
        if user_list:
            new_lines.append("\n# --- User Accounts ---\n")
            for user in user_list:
                perms = user.get('permissions', '')
                line = f"User {user['username']} {user['password']} {perms}\n"
                new_lines.append(line.strip()) # Clean up extra space if no perms

        if acl_list:
            new_lines.append("\n# --- Access Control List ---\n")
            for acl in acl_list:
                new_lines.append(f"ACL {acl['mask']} {acl['action']}")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(new_lines))