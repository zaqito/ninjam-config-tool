# src/ninjam_config_tool/app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict

from .config_parser import ConfigParser
from .reloader import Reloader

class Application(tk.Tk):
    """
    Main application class for the NINJAM Config Tool.
    
    This class inherits from tk.Tk and acts as the main controller,
    managing UI state and coordinating the ConfigParser and Reloader.
    """
    
    def __init__(self):
        super().__init__()
        self.title("NINJAM Server Config Tool")
        self.geometry("450x350")

        # --- Application State ---
        self.current_file_path: Optional[str] = None
        
        # We use Tkinter's variable classes to auto-update the UI.
        # This is the core of the state management.
        self.config_vars: Dict[str, tk.Variable] = {
            "MaxUsers": tk.IntVar(value=10),
            "DefaultTopic": tk.StringVar(value=""),
            "DefaultBPM": tk.DoubleVar(value=120.0),
            "DefaultBPI": tk.IntVar(value=16),
            "Port": tk.IntVar(value=2049)
            # Add other parameters you want to manage here
        }
        
        self.pid_file_path = tk.StringVar(value="")

        # --- Component Initialization ---
        self.config_parser = ConfigParser()
        self.reloader = Reloader()

        # --- UI Construction ---
        self._create_menu()
        self._create_widgets()
        

    def _create_menu(self):
        """Creates the main application menu bar."""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="Open Config...", command=self._on_open)
        file_menu.add_command(label="Save", command=self._on_save)
        file_menu.add_command(label="Save As...", command=self._on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)


    def _create_widgets(self):
        """Creates and lays out the main UI widgets."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Server Settings Frame ---
        settings_frame = ttk.LabelFrame(main_frame, text="Server Settings", padding=10)
        settings_frame.pack(fill=tk.X)
        
        # Using a grid for clean label-entry alignment
        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(settings_frame, text="Max Users:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(settings_frame, from_=1, to=100,
                    textvariable=self.config_vars["MaxUsers"]).grid(row=0, column=1, sticky=tk.EW, padx=5)

        ttk.Label(settings_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(settings_frame, from_=1024, to=65535,
                    textvariable=self.config_vars["Port"]).grid(row=1, column=1, sticky=tk.EW, padx=5)

        ttk.Label(settings_frame, text="Default BPM:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(settings_frame, from_=20, to=400,
                    textvariable=self.config_vars["DefaultBPM"]).grid(row=2, column=1, sticky=tk.EW, padx=5)
        
        ttk.Label(settings_frame, text="Default Topic:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame,
                  textvariable=self.config_vars["DefaultTopic"]).grid(row=3, column=1, sticky=tk.EW, padx=5)

        # --- Reload/Action Frame ---
        action_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        action_frame.pack(fill=tk.X, pady=10)
        action_frame.columnconfigure(1, weight=1)
        
        ttk.Label(action_frame, text="PID File Path (Linux):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(action_frame, 
                  textvariable=self.pid_file_path).grid(row=0, column=1, sticky=tk.EW, padx=5)

        # --- Main Action Button ---
        apply_button = ttk.Button(main_frame, text="Save and Apply", command=self._on_save_and_apply)
        apply_button.pack(fill=tk.X, side=tk.BOTTOM, pady=(5,0))


    def _on_open(self):
        """Handles the 'File > Open' menu command."""
        filepath = filedialog.askopenfilename(
            title="Open NINJAM Config File",
            filetypes=[("Config Files", "*.cfg"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            config_data = self.config_parser.read(filepath)
            
            # Populate the UI from the file
            for key, var in self.config_vars.items():
                if key in config_data:
                    try:
                        var.set(config_data[key])
                    except tk.TclError as e:
                        print(f"Warning: Could not set '{key}' to '{config_data[key]}'. Error: {e}")
            
            self.current_file_path = filepath
            self.title(f"NINJAM Config Tool - {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not read config file.\n\n{e}")


    def _on_save(self) -> bool:
        """Handles the 'File > Save' menu command. Returns True on success."""
        if not self.current_file_path:
            return self._on_save_as()
        else:
            return self._save_to_path(self.current_file_path, template=False)


    def _on_save_as(self) -> bool:
        """Handles the 'File > Save As...' menu command. Returns True on success."""
        filepath = filedialog.asksaveasfilename(
            title="Save NINJAM Config File",
            filetypes=[("Config Files", "*.cfg"), ("All Files", "*.*")],
            defaultextension=".cfg"
        )
        if not filepath:
            return False
        
        # We assume a new file should be written from our template
        return self._save_to_path(filepath, template=True)


    def _save_to_path(self, filepath: str, template: bool) -> bool:
        """
        Gathers data from UI and writes it to the specified file path.
        Returns True on success.
        """
        try:
            # Get current values from all tk.Variables
            data_from_ui = {key: var.get() for key, var in self.config_vars.items()}
            
            self.config_parser.write(filepath, data_from_ui, template=template)
            
            self.current_file_path = filepath
            self.title(f"NINJAM Config Tool - {filepath}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error Saving File", f"Could not save config file.\n\n{e}")
            return False


    def _on_save_and_apply(self):
        """Handles the 'Save and Apply' button click."""
        # Step 1: Save the file
        if not self._on_save():
            messagebox.showwarning("Save Failed", "Configuration was not saved. Aborting apply.")
            return

        # Step 2: Trigger the reloader
        try:
            pid_path = self.pid_file_path.get()
            title, message = self.reloader.reload(pid_path)
            
            if "Error" in title:
                messagebox.showerror(title, message)
            else:
                messagebox.showinfo(title, message)
                
        except Exception as e:
            messagebox.showerror("Reload Error", f"An unexpected error occurred during reload.\n\n{e}")


    def start(self):
        """Starts the Tkinter main event loop."""
        self.mainloop()