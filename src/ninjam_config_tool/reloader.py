# src/ninjam_config_tool/reloader.py
import platform
import subprocess
import os
from typing import Tuple

class Reloader:
    """
    Handles the platform-specific logic for reloading the ninjamsrv.
    """
    
    def __init__(self):
        self.platform = platform.system().lower()


    def reload(self, pid_filepath: str) -> Tuple[str, str]:
        """
        Attempts to reload the server.
        
        Returns a (title, message) tuple for the UI.
        """
        if self.platform == "windows":
            return self.reload_windows()
        elif self.platform == "linux":
            return self.reload_linux(pid_filepath)
        elif self.platform == "darwin": # macOS
            return self.reload_linux(pid_filepath) # SIGHUP works on macOS too
        else:
            return ("Config Saved", 
                    f"Config was saved, but reload is not supported on '{self.platform}'.")


    def reload_windows(self) -> Tuple[str, str]:
        """Windows-specific 'reload' (which is just a message)."""
        return ("Config Saved (Windows)",
                "Configuration file was saved.\n\n"
                "To apply changes, please go to your running server "
                "console and press the 'R' key.")


    def reload_linux(self, pid_filepath: str) -> Tuple[str, str]:
        """Linux/Unix-specific reload using SIGHUP."""
        if not pid_filepath or not pid_filepath.strip():
            return ("Error: PID File",
                    "Configuration was saved, but cannot reload.\n\n"
                    "Please specify the path to your server's .pid file "
                    "(set with 'SetPID' in your config).")

        if not os.path.exists(pid_filepath):
            return ("Error: PID File Not Found",
                    f"Config saved, but PID file not found at:\n{pid_filepath}")

        try:
            with open(pid_filepath, 'r') as f:
                pid = f.read().strip()
            
            if not pid.isdigit():
                return ("Error: Invalid PID", f"The file '{pid_filepath}' did not contain a valid PID.")
            
            # Check if process exists first
            # os.kill(pid, 0) will raise an exception if the process doesn't exist
            os.kill(int(pid), 0)

        except (IOError, OSError) as e:
            return ("Error: Process Not Found",
                    f"Config saved, but could not read PID or find process.\n\n{e}")
        
        # Use pkexec for privileged signal sending.
        # This will trigger a native password prompt.
        cmd = ["pkexec", "kill", "-HUP", pid]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                return ("Reload Successful",
                        f"Config saved and reload signal (SIGHUP) sent to PID {pid}.")
            else:
                # User cancel (126/127) or other auth error
                return ("Reload Failed",
                        "Config saved, but reload signal failed (user cancel?).\n\n"
                        f"Error: {result.stderr}")
                
        except FileNotFoundError:
            return ("Error: pkexec",
                    "Config saved, but `pkexec` was not found. "
                    "Is PolicyKit installed on your system?")
        except Exception as e:
            return ("Error: Unknown Reload", f"Config saved, but reload failed.\n\n{e}")