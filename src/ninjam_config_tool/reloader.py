# src/ninjam_config_tool/reloader.py
import platform
import subprocess
import os
from typing import Tuple, Optional

import psutil


class ProcessNotFoundError(Exception):
    """Raised when the NINJAM server process cannot be found."""
    pass


class Reloader:
    """
    Handles the platform-specific logic for reloading the ninjamsrv.
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.server_process_names = ["cninjamsrv", "ninjamsrv", "ninjamsrv.exe"]


    def _find_server_pid(self) -> Optional[int]:
        """
        Finds the NINJAM server PID by iterating over running processes.
        Uses psutil for cross-platform compatibility.
        """
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.name() in self.server_process_names:
                    # Found it!
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process might have died, or we don't have permission
                continue
        
        # If we get here, we didn't find it
        raise ProcessNotFoundError(
            "Could not find a running NINJAM server process "
            f"(looked for: {', '.join(self.server_process_names)})."
        )
    

    def reload(self) -> Tuple[str, str]:
        """
        Attempts to reload the server.
        
        Returns a (title, message) tuple for the UI.
        """
        if self.platform == "windows":
            return self.reload_windows()
        elif self.platform == "linux":
            return self.reload_linux()
        elif self.platform == "darwin": # macOS
            return self.reload_linux() # SIGHUP works on macOS too
        else:
            return ("Config Saved", 
                    f"Config was saved, but reload is not supported on '{self.platform}'.")


    def reload_windows(self) -> Tuple[str, str]:
        """Windows-specific 'reload' (which is just a message)."""
        return ("Config Saved (Windows)",
                "Configuration file was saved.\n\n"
                "To apply changes, please go to your running server "
                "console and press the 'R' key.")


    def reload_linux(self) -> Tuple[str, str]:
        """Linux/Unix-specific reload using SIGHUP."""
        try:
            pid = self._find_server_pid()
            
            # Use pkexec for privileged signal sending.
            cmd = ["pkexec", "kill", "-HUP", str(pid)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                return ("Reload Successful",
                        f"Config saved and reload signal (SIGHUP) sent to PID {pid}.")
            else:
                # User cancel (126/127) or other auth error
                return ("Reload Failed",
                        "Config saved, but reload signal failed (user cancel?).\n\n"
                        f"Error: {result.stderr}")

        except ProcessNotFoundError as e:
            return ("Error: Process Not Found", f"Config saved, but reload failed.\n\Type {e}")
        except FileNotFoundError:
            return ("Error: pkexec",
                    "Config saved, but `pkexec` was not found. "
                    "Is PolicyKit installed on your system?")
        except Exception as e:
            return ("Error: Unknown Reload", f"Config saved, but reload failed.\n\n{e}")