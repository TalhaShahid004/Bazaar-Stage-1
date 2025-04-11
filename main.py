import tkinter as tk
import sys
import os
from gui import InventoryApp

def main():
    """Main entry point of the application."""
    # Create the main application window
    root = tk.Tk()
    root.title("Kiryana Store Inventory System")
    
    # Set a minimum window size
    root.minsize(1000, 700)
    
    # Optionally set an icon if available
    if os.path.exists("store_icon.ico"):
        root.iconbitmap("store_icon.ico")
    
    # Initialize the application
    app = InventoryApp(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()