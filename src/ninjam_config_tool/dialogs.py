# src/ninjam_config_tool/dialogs.py
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any


class BaseEditDialog(tk.Toplevel):
    """
    A base class for modal dialog windows.
    """
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.title(title)
        
        self.result: Optional[Dict[str, Any]] = None
        self.data_fields: Dict[str, tk.Variable] = {}
        
        # --- Create main frames ---
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.form_frame = ttk.Frame(main_frame)
        self.form_frame.pack(fill=tk.X)
        self.form_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        # --- Create buttons ---
        ok_button = ttk.Button(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT)
        
        self.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Escape>", lambda e: self._on_cancel())

        # --- Modal setup ---
        self.transient(parent)
        self.grab_set()


    def _add_entry(self, key: str, label: str, value: str):
        """Helper to add a labeled text entry."""
        var = tk.StringVar(value=value)
        self.data_fields[key] = var
        
        row = self.form_frame.grid_size()[1]
        ttk.Label(self.form_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.form_frame, textvariable=var).grid(row=row, column=1, sticky=tk.EW, padx=5)


    def _add_combo(self, key: str, label: str, value: str, options: list):
        """Helper to add a labeled combobox."""
        var = tk.StringVar(value=value)
        self.data_fields[key] = var
        
        row = self.form_frame.grid_size()[1]
        ttk.Label(self.form_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
        combo = ttk.Combobox(self.form_frame, textvariable=var, values=options, state="readonly")
        combo.grid(row=row, column=1, sticky=tk.EW, padx=5)


    def _on_ok(self):
        """Stores the result and closes the dialog."""
        self.result = {key: var.get() for key, var in self.data_fields.items()}
        self.destroy()


    def _on_cancel(self):
        """Closes the dialog without storing a result."""
        self.destroy()


# --- Specific Dialog Implementations ---
class UserDialog(BaseEditDialog):
    """Dialog for adding or editing a User."""
    def __init__(self, parent, title="Edit User", data: Optional[Dict[str, str]] = None):
        data = data or {}
        super().__init__(parent, title)
        
        self._add_entry("username", "Username:", data.get("username", ""))
        self._add_entry("password", "Password:", data.get("password", ""))
        self._add_entry("permissions", "Permissions:", data.get("permissions", ""))

        self.wait_window(self)


class AclDialog(BaseEditDialog):
    """Dialog for adding or editing an ACL rule."""
    def __init__(self, parent, title="Edit ACL", data: Optional[Dict[str, str]] = None):
        data = data or {}
        super().__init__(parent, title)
        
        self._add_entry("mask", "IP Mask (e.g. 1.2.3.4/32):", data.get("mask", ""))
        self._add_combo("action", "Action:", data.get("action", "allow"), ["allow", "deny", "reserve"])

        self.wait_window(self)