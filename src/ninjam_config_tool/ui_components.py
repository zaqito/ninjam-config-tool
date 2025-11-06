# src/ninjam_config_tool/ui_components.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any


class ListEditorFrame(ttk.Frame):
    """
    A reusable frame widget that contains a Treeview for list management
    with Add, Edit, and Remove buttons.
    """
    def __init__(self, parent, 
                 columns: Dict[str, int], 
                 data_list: List[Dict[str, Any]], 
                 dialog_class: tk.Toplevel):
        
        super().__init__(parent)
        
        self.columns = columns
        self.data_list = data_list  # This is a reference to the app's state
        self.dialog_class = dialog_class
        
        # --- Create UI ---
        
        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=list(columns.keys()), 
            show="headings"
        )
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns
        for col, width in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.W)
            
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        add_btn = ttk.Button(button_frame, text="Add...", command=self._on_add)
        add_btn.pack(side=tk.LEFT)
        
        edit_btn = ttk.Button(button_frame, text="Edit...", command=self._on_edit)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = ttk.Button(button_frame, text="Remove", command=self._on_remove)
        remove_btn.pack(side=tk.LEFT)
        
        # --- Populate initial data ---
        self.refresh_tree()


    def refresh_tree(self):
        """Clears and repopulates the tree from the data_list."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new items from our data_list
        for item in self.data_list:
            values = [item.get(col_key, "") for col_key in self.columns.keys()]
            self.tree.insert("", tk.END, values=values)


    def _on_add(self):
        """Opens a dialog to add a new item."""
        dialog = self.dialog_class(self, f"Add {self.dialog_class.__name__.replace('Dialog', '')}")
        
        if dialog.result:
            self.data_list.append(dialog.result)
            self.refresh_tree()


    def _on_edit(self):
        """Opens a dialog to edit the selected item."""
        selected_iid = self.tree.focus()
        if not selected_iid:
            messagebox.showwarning("No Selection", "Please select an item to edit.")
            return

        # Find the corresponding item in our data_list
        selected_index = self.tree.index(selected_iid)
        item_data = self.data_list[selected_index]

        dialog = self.dialog_class(self, f"Edit {self.dialog_class.__name__.replace('Dialog', '')}", data=item_data)
        
        if dialog.result:
            # Update the list in-place
            self.data_list[selected_index] = dialog.result
            self.refresh_tree()


    def _on_remove(self):
        """Removes the selected item from the list."""
        selected_iid = self.tree.focus()
        if not selected_iid:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return

        if not messagebox.askyesno("Confirm Remove", "Are you sure you want to remove this item?"):
            return
            
        selected_index = self.tree.index(selected_iid)
        self.data_list.pop(selected_index)
        self.refresh_tree()