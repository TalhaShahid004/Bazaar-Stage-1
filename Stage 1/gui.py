import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.font import Font
import datetime
from tkcalendar import DateEntry  # Need to install: pip install tkcalendar

from database import InventoryDatabase

class ProductSelector:
    """Dialog for selecting a product."""
    def __init__(self, parent, inventory_db, search_term=None):
        self.parent = parent
        self.inventory_db = inventory_db
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Product")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Search frame
        search_frame = tk.Frame(self.dialog, padx=10, pady=10)
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar(value=search_term or "")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Search", command=self.search).pack(side=tk.LEFT)
        
        # Results frame
        results_frame = tk.Frame(self.dialog)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for results
        columns = ("id", "name", "code", "category", "price")
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        # Define column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("code", text="Code")
        self.tree.heading("category", text="Category")
        self.tree.heading("price", text="Price (₹)")
        
        # Define column widths
        self.tree.column("id", width=50)
        self.tree.column("name", width=200)
        self.tree.column("code", width=100)
        self.tree.column("category", width=100)
        self.tree.column("price", width=80)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.on_select)
        
        # Button frame
        button_frame = tk.Frame(self.dialog, padx=10, pady=10)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Select", command=self.select_item).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Perform initial search
        if search_term:
            self.search()
        else:
            # Show all products if no search term
            self.load_all_products()
        
        # Focus search entry
        search_entry.focus_set()
        search_entry.bind('<Return>', lambda event: self.search())
        
        # Wait for the dialog to close
        self.dialog.wait_window()
    
    def load_all_products(self):
        """Load all products into the treeview."""
        # Clear previous results
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Get all products
        products = self.inventory_db.get_current_stock()
        
        # Add to treeview
        for product in products:
            values = (
                product['id'],
                product['name'],
                product['code'] or '',
                product['category'] or '',
                f"{product['selling_price']:.2f}" if product['selling_price'] else ''
            )
            self.tree.insert('', tk.END, values=values)
    
    def search(self):
        """Search for products and display results."""
        search_term = self.search_var.get().strip()
        
        # Clear previous results
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if not search_term:
            self.load_all_products()
            return
        
        # Get search results
        products = self.inventory_db.find_product(search_term)
        
        # Add to treeview
        for product in products:
            values = (
                product['id'],
                product['name'],
                product['code'] or '',
                product['category'] or '',
                f"{product['selling_price']:.2f}" if product.get('selling_price') else ''
            )
            self.tree.insert('', tk.END, values=values)
    
    def on_select(self, event):
        """Handle double-click on a product."""
        self.select_item()
    
    def select_item(self):
        """Get the selected product."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Get values
        values = self.tree.item(selected_items[0], 'values')
        product_id = int(values[0])
        
        # Get full product details
        product = self.inventory_db.get_product_by_id(product_id)
        
        if product:
            self.result = product
            self.dialog.destroy()


class InventoryApp:
    def __init__(self, root, db_path="inventory.db"):
        """Creates our store management app with a friendly, simple interface.
        
        We've designed this to be as straightforward as possible - big buttons,
        clear sections, and helpful visuals that make sense for kiryana stores.
        """
        self.root = root
        self.root.title("Kiryana Store Inventory")
        self.root.geometry("1024x768")  # Good size for most screens
        self.root.config(bg="#f0f0f0")  # Light gray background is easy on the eyes
        
        # Connect to our inventory tracking system
        self.inventory_db = InventoryDatabase(db_path)
        
        # Make text clear and readable - especially important in busy shops
        self.title_font = Font(family="Arial", size=16, weight="bold")  # Big headings
        self.button_font = Font(family="Arial", size=12)  # Easy-to-see buttons
        self.label_font = Font(family="Arial", size=10)   # Regular text
        self.heading_font = Font(family="Arial", size=12, weight="bold") # Section titles
        
        # Make the app look nice and consistent
        self.style = ttk.Style()
        self.style.configure("TButton", font=self.button_font, padding=10)  # Big, clickable buttons
        self.style.configure("TLabel", font=self.label_font, background="#f0f0f0")
        self.style.configure("Header.TLabel", font=self.heading_font, background="#f0f0f0")
        self.style.configure("Low.TLabel", foreground="red")  # Red for attention-grabbing alerts
        
        # Main container for everything
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add the search bar at the top for quick product lookup
        self.create_search_bar()
        
        # Add the main navigation buttons - like a simple dashboard
        self.create_main_menu()
        
        # This is where different screens will appear (inventory, sales, etc.)
        self.content_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status bar to show helpful messages at the bottom
        self.status_var = tk.StringVar()
        self.status_var.set("System Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Start by showing the current inventory - most commonly needed view
        self.show_inventory()
    
    def create_search_bar(self):
        search_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Store name and date
        store_label = ttk.Label(search_frame, text="KIRYANA STORE INVENTORY", font=self.title_font, background="#f0f0f0")
        store_label.pack(side=tk.LEFT, padx=5)
        
        # Current date
        date_label = ttk.Label(search_frame, text=datetime.datetime.now().strftime("%d-%b-%Y"), font=self.button_font, background="#f0f0f0")
        date_label.pack(side=tk.RIGHT, padx=5)
        
        # Search box
        search_container = tk.Frame(search_frame, bg="#f0f0f0")
        search_container.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(search_container, text="Quick Search:", background="#f0f0f0").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_container, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_button = ttk.Button(search_container, text="Search", command=self.search_products)
        search_button.pack(side=tk.LEFT)
        
        # Bind Enter key to search
        search_entry.bind('<Return>', lambda event: self.search_products())
    
    def create_main_menu(self):
        """Creates big, clear buttons for all the main tasks a shop owner needs.
        
        We've organized the buttons in order of common usage:
        - Inventory check (most frequent)
        - Adding new products
        - Recording stock deliveries
        - Recording sales
        - Checking daily performance
        - Managing low stock items
        - Backup (safely tucked on the right)
        """
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main actions arranged left-to-right by frequency of use
        self.inventory_button = ttk.Button(button_frame, text="Inventory", command=self.show_inventory)
        self.inventory_button.pack(side=tk.LEFT, padx=5)
        
        self.add_product_button = ttk.Button(button_frame, text="Add Product", command=self.show_add_product)
        self.add_product_button.pack(side=tk.LEFT, padx=5)
        
        self.stock_in_button = ttk.Button(button_frame, text="Stock In", command=self.show_stock_in)
        self.stock_in_button.pack(side=tk.LEFT, padx=5)
        
        self.sales_button = ttk.Button(button_frame, text="Record Sale", command=self.show_sales)
        self.sales_button.pack(side=tk.LEFT, padx=5)
        
        self.reports_button = ttk.Button(button_frame, text="Daily Report", command=self.show_daily_report)
        self.reports_button.pack(side=tk.LEFT, padx=5)
        
        self.low_stock_button = ttk.Button(button_frame, text="Low Stock Alert", command=self.show_low_stock)
        self.low_stock_button.pack(side=tk.LEFT, padx=5)
        
        # Keep backup on the right side - important but used less frequently
        self.backup_button = ttk.Button(button_frame, text="Backup", command=self.backup_database)
        self.backup_button.pack(side=tk.RIGHT, padx=5)
    
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_inventory(self):
        """Shows what's currently in stock - the main screen shopkeepers need most.
        
        This screen is designed to answer the most common questions at a glance:
        - What products do we have?
        - How many of each item do we have?
        - What items are running low? (shown in red)
        - What are our buying and selling prices?
        
        Double-clicking any item lets you edit it or record a sale/restock.
        """
        self.clear_content_frame()
        
        # Page title
        title_label = ttk.Label(self.content_frame, text="Current Inventory", font=self.title_font, background="#f0f0f0")
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Create a table-like view for all products
        columns = ("id", "name", "code", "category", "quantity", "cost", "price")
        tree = ttk.Treeview(self.content_frame, columns=columns, show='headings')
        
        # Set up the column headings
        tree.heading("id", text="ID")
        tree.heading("name", text="Product Name")
        tree.heading("code", text="Code")
        tree.heading("category", text="Category")
        tree.heading("quantity", text="In Stock")
        tree.heading("cost", text="Cost (₹)")
        tree.heading("price", text="Price (₹)")
        
        # Adjust column widths to make the most important info easy to see
        tree.column("id", width=50)
        tree.column("name", width=200)  # Names get more space - they're important
        tree.column("code", width=100)
        tree.column("category", width=100)
        tree.column("quantity", width=80)
        tree.column("cost", width=80)
        tree.column("price", width=80)
        
        # Add a scrollbar for when inventory gets large
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        # Put the inventory view in the main area
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Get the current inventory from our database
        stock_items = self.inventory_db.get_current_stock()
        low_stock_threshold = 5  # Items with 5 or fewer in stock get highlighted
        
        # Add each product to the view
        for item in stock_items:
            values = (
                item['id'],
                item['name'],
                item['code'] or '',
                item['category'] or '',
                item['current_quantity'],
                f"{item['purchase_price']:.2f}" if item['purchase_price'] else '',
                f"{item['selling_price']:.2f}" if item['selling_price'] else ''
            )
            
            # Make low stock items RED so they stand out - important for reordering!
            if item['current_quantity'] <= low_stock_threshold:
                tree.insert('', tk.END, values=values, tags=('low_stock',))
            else:
                tree.insert('', tk.END, values=values)
        
        # Set up the red color for low stock items
        tree.tag_configure('low_stock', foreground='red')
        
        # Double-click an item to edit it, restock it, or record a sale
        tree.bind('<Double-1>', self.on_product_double_click)
        
        # Show summary info in the status bar
        low_stock_count = sum(1 for item in stock_items if item['current_quantity'] <= low_stock_threshold)
        self.status_var.set(f"Total Products: {len(stock_items)} | Low Stock Alert: {low_stock_count} items")
    
    def show_add_product(self):
        self.clear_content_frame()
        
        # Title
        title_label = ttk.Label(self.content_frame, text="Add New Product", font=self.title_font, background="#f0f0f0")
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Create form
        form_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # Product name
        ttk.Label(form_frame, text="Product Name:", width=15, background="#f0f0f0").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Product code
        ttk.Label(form_frame, text="Product Code:", width=15, background="#f0f0f0").grid(row=1, column=0, sticky=tk.W, pady=5)
        code_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=code_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Category
        ttk.Label(form_frame, text="Category:", width=15, background="#f0f0f0").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Get existing categories for dropdown
        categories = self.inventory_db.get_categories()
        category_var = tk.StringVar()
        
        if categories:
            category_dropdown = ttk.Combobox(form_frame, textvariable=category_var, width=20)
            category_dropdown['values'] = categories
            category_dropdown.grid(row=2, column=1, sticky=tk.W, pady=5)
        else:
            ttk.Entry(form_frame, textvariable=category_var, width=20).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Purchase price
        ttk.Label(form_frame, text="Purchase Price:", width=15, background="#f0f0f0").grid(row=3, column=0, sticky=tk.W, pady=5)
        purchase_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=purchase_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Selling price
        ttk.Label(form_frame, text="Selling Price:", width=15, background="#f0f0f0").grid(row=4, column=0, sticky=tk.W, pady=5)
        selling_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=selling_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_product():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Product name is required!")
                return
            
            try:
                purchase_price = float(purchase_var.get()) if purchase_var.get() else None
                selling_price = float(selling_var.get()) if selling_var.get() else None
            except ValueError:
                messagebox.showerror("Error", "Prices must be numbers!")
                return
            
            code = code_var.get().strip() or None
            category = category_var.get().strip() or None
            
            product_id, error = self.inventory_db.add_product(
                name, code, category, purchase_price, selling_price
            )
            
            if product_id:
                messagebox.showinfo("Success", f"Product '{name}' added successfully!")
                
                # Ask if they want to add initial stock
                if messagebox.askyesno("Initial Stock", "Do you want to add initial stock for this product?"):
                    self.show_stock_in(product_id)
                else:
                    # Clear form
                    name_var.set("")
                    code_var.set("")
                    category_var.set("")
                    purchase_var.set("")
                    selling_var.set("")
            else:
                messagebox.showerror("Error", error)
        
        ttk.Button(button_frame, text="Save Product", command=save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.show_inventory).pack(side=tk.LEFT, padx=5)
    
   
    def show_stock_in(self, product_id=None):
        self.clear_content_frame()
        
        # Title
        title_label = ttk.Label(self.content_frame, text="Record Stock In", font=self.title_font, background="#f0f0f0")
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Create form
        form_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # Product selection
        product_frame = tk.Frame(form_frame, bg="#f0f0f0")
        product_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(product_frame, text="Select Product:", background="#f0f0f0").pack(side=tk.LEFT)
        
        self.selected_product_id = tk.StringVar(value=str(product_id) if product_id else "")
        self.product_name_display = tk.StringVar()
        
        product_display = ttk.Entry(product_frame, textvariable=self.product_name_display, width=30, state='readonly')
        product_display.pack(side=tk.LEFT, padx=5)
        
        # Define price_var here, BEFORE it might be used
        price_var = tk.StringVar()
        
        def select_product():
            product_selector = ProductSelector(self.root, self.inventory_db)
            if product_selector.result:
                self.selected_product_id.set(str(product_selector.result['id']))
                self.product_name_display.set(product_selector.result['name'])
                
                # Update price field if available
                if product_selector.result['purchase_price']:
                    price_var.set(str(product_selector.result['purchase_price']))
        
        # If product_id was provided, populate the product name
        if product_id:
            product = self.inventory_db.get_product_by_id(product_id)
            if product:
                self.product_name_display.set(product['name'])
                if product['purchase_price']:
                    price_var.set(str(product['purchase_price']))
        
        ttk.Button(product_frame, text="Browse...", command=select_product).pack(side=tk.LEFT)
        
        # Quantity
        quantity_frame = tk.Frame(form_frame, bg="#f0f0f0")
        quantity_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(quantity_frame, text="Quantity:", background="#f0f0f0").pack(side=tk.LEFT)
        quantity_var = tk.StringVar(value="1")
        ttk.Entry(quantity_frame, textvariable=quantity_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Price per unit
        price_frame = tk.Frame(form_frame, bg="#f0f0f0")
        price_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(price_frame, text="Purchase Price:", background="#f0f0f0").pack(side=tk.LEFT)
        # price_var was moved up before it's first used
        ttk.Entry(price_frame, textvariable=price_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Notes
        notes_frame = tk.Frame(form_frame, bg="#f0f0f0")
        notes_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(notes_frame, text="Notes:", background="#f0f0f0").pack(side=tk.LEFT)
        notes_var = tk.StringVar()
        ttk.Entry(notes_frame, textvariable=notes_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        def save_stock_in():
            if not self.selected_product_id.get():
                messagebox.showerror("Error", "Please select a product!")
                return
            
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be positive!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a number!")
                return
            
            try:
                price = float(price_var.get()) if price_var.get() else None
            except ValueError:
                messagebox.showerror("Error", "Price must be a number!")
                return
            
            notes = notes_var.get()
            
            success, error = self.inventory_db.record_stock_movement(
                int(self.selected_product_id.get()), 'stock_in', quantity, price, notes
            )
            
            if success:
                messagebox.showinfo("Success", f"Stock recorded successfully!")
                # Reset form for another entry
                if not product_id:  # If we came here from "Add Product", don't reset product
                    self.selected_product_id.set("")
                    self.product_name_display.set("")
                quantity_var.set("1")
                price_var.set("")
                notes_var.set("")
            else:
                messagebox.showerror("Error", error)
        
        ttk.Button(button_frame, text="Record Stock", command=save_stock_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.show_inventory).pack(side=tk.LEFT, padx=5)
        
    def show_sales(self, product_id=None):
        self.clear_content_frame()
        
        # Title
        title_label = ttk.Label(self.content_frame, text="Record Sale", font=self.title_font, background="#f0f0f0")
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Create form
        form_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # Product selection
        product_frame = tk.Frame(form_frame, bg="#f0f0f0")
        product_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(product_frame, text="Select Product:", background="#f0f0f0").pack(side=tk.LEFT)
        
        self.selected_product_id = tk.StringVar(value=str(product_id) if product_id else "")
        self.product_name_display = tk.StringVar()
        
        product_display = ttk.Entry(product_frame, textvariable=self.product_name_display, width=30, state='readonly')
        product_display.pack(side=tk.LEFT, padx=5)
        
        def select_product():
            product_selector = ProductSelector(self.root, self.inventory_db)
            if product_selector.result:
                self.selected_product_id.set(str(product_selector.result['id']))
                self.product_name_display.set(product_selector.result['name'])
                
                # Update price field if available
                if product_selector.result['selling_price']:
                    price_var.set(str(product_selector.result['selling_price']))
                
                # Update max quantity
                if 'current_quantity' in product_selector.result:
                    max_qty = product_selector.result['current_quantity']
                    quantity_var.set("1" if max_qty > 0 else "0")
        
        # If product_id was provided, populate the product name
        if product_id:
            product = self.inventory_db.get_product_by_id(product_id)
            if product:
                self.product_name_display.set(product['name'])
                if product['selling_price']:
                    price_var.set(str(product['selling_price']))
        
        ttk.Button(product_frame, text="Browse...", command=select_product).pack(side=tk.LEFT)
        
        # Quantity
        quantity_frame = tk.Frame(form_frame, bg="#f0f0f0")
        quantity_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(quantity_frame, text="Quantity:", background="#f0f0f0").pack(side=tk.LEFT)
        quantity_var = tk.StringVar(value="1")
        ttk.Entry(quantity_frame, textvariable=quantity_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Price per unit
        price_frame = tk.Frame(form_frame, bg="#f0f0f0")
        price_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(price_frame, text="Selling Price:", background="#f0f0f0").pack(side=tk.LEFT)
        price_var = tk.StringVar()
        ttk.Entry(price_frame, textvariable=price_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Notes
        notes_frame = tk.Frame(form_frame, bg="#f0f0f0")
        notes_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(notes_frame, text="Notes:", background="#f0f0f0").pack(side=tk.LEFT)
        notes_var = tk.StringVar()
        ttk.Entry(notes_frame, textvariable=notes_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        def save_sale():
            if not self.selected_product_id.get():
                messagebox.showerror("Error", "Please select a product!")
                return
            
            try:
                quantity = int(quantity_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be positive!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a number!")
                return
            
            try:
                price = float(price_var.get()) if price_var.get() else None
            except ValueError:
                messagebox.showerror("Error", "Price must be a number!")
                return
            
            notes = notes_var.get()
            
            # Check if we have enough stock
            product = self.inventory_db.get_product_by_id(int(self.selected_product_id.get()))
            if product and product['current_quantity'] < quantity:
                if not messagebox.askyesno("Warning", 
                                       f"Only {product['current_quantity']} units in stock. Do you want to continue anyway?"):
                    return
            
            success, error = self.inventory_db.record_stock_movement(
                int(self.selected_product_id.get()), 'sale', quantity, price, notes
            )
            
            if success:
                messagebox.showinfo("Success", f"Sale recorded successfully!")
                # Reset form for another entry
                self.selected_product_id.set("")
                self.product_name_display.set("")
                quantity_var.set("1")
                price_var.set("")
                notes_var.set("")
            else:
                messagebox.showerror("Error", error)
        
        ttk.Button(button_frame, text="Record Sale", command=save_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.show_inventory).pack(side=tk.LEFT, padx=5)
    
    def show_daily_report(self):
        self.clear_content_frame()
        
        # Title frame with date selector
        title_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Daily Sales Report", font=self.title_font, background="#f0f0f0")
        title_label.pack(side=tk.LEFT)
        
        date_frame = tk.Frame(title_frame, bg="#f0f0f0")
        date_frame.pack(side=tk.RIGHT)
        
        ttk.Label(date_frame, text="Select Date:", background="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        today = datetime.datetime.now()
        cal = DateEntry(date_frame, width=12, background='darkblue',
                        foreground='white', borderwidth=2, year=today.year,
                        month=today.month, day=today.day)
        cal.pack(side=tk.LEFT, padx=5)
        
        # Report container
        report_frame = tk.Frame(self.content_frame, bg="white", bd=1, relief=tk.SOLID)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Function to load report data
        def load_report():
            # Clear previous report
            for widget in report_frame.winfo_children():
                widget.destroy()
            
            selected_date = cal.get_date().strftime('%Y-%m-%d')
            summary = self.inventory_db.get_daily_summary(selected_date)
            
            # Format date nicely
            formatted_date = datetime.datetime.strptime(summary['date'], '%Y-%m-%d').strftime('%d %B, %Y')
            
            # Header
            header_label = ttk.Label(report_frame, text=f"Summary for {formatted_date}", 
                                     font=self.heading_font, background="white")
            header_label.pack(pady=10)
            
            # Main content
            content_frame = tk.Frame(report_frame, bg="white")
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Sales summary
            sales_frame = tk.LabelFrame(content_frame, text="Sales Summary", bg="white", font=self.label_font)
            sales_frame.pack(fill=tk.X, pady=5)
            
            num_sales, items_sold, revenue = summary['sales']
            items_sold = items_sold or 0
            revenue = revenue or 0
            
            ttk.Label(sales_frame, text=f"Number of sales: {num_sales}", background="white").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(sales_frame, text=f"Total items sold: {items_sold}", background="white").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(sales_frame, text=f"Total revenue: ₹{revenue:.2f}", background="white").pack(anchor=tk.W, padx=10, pady=2)
            
            # Stock-ins summary
            stock_frame = tk.LabelFrame(content_frame, text="Stock Received", bg="white", font=self.label_font)
            stock_frame.pack(fill=tk.X, pady=5)
            
            num_stock_ins, items_received = summary['stock_ins']
            items_received = items_received or 0
            
            ttk.Label(stock_frame, text=f"Number of deliveries: {num_stock_ins}", background="white").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(stock_frame, text=f"Total items received: {items_received}", background="white").pack(anchor=tk.W, padx=10, pady=2)
            
            # Top sold products
            top_frame = tk.LabelFrame(content_frame, text="Top Selling Products", bg="white", font=self.label_font)
            top_frame.pack(fill=tk.X, pady=5)
            
            if summary['top_sold']:
                for i, (product, quantity) in enumerate(summary['top_sold'], 1):
                    ttk.Label(top_frame, text=f"{i}. {product}: {quantity} units", background="white").pack(anchor=tk.W, padx=10, pady=2)
            else:
                ttk.Label(top_frame, text="No sales recorded for this day", background="white").pack(anchor=tk.W, padx=10, pady=2)
        
        # Load initial report
        load_report()
        
        # Refresh button
        refresh_button = ttk.Button(title_frame, text="Refresh", command=load_report)
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind date change to refresh
        cal.bind("<<DateEntrySelected>>", lambda e: load_report())
    
    def show_low_stock(self):
        self.clear_content_frame()
        
        # Title
        title_label = ttk.Label(self.content_frame, text="Low Stock Alert", font=self.title_font, background="#f0f0f0")
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Set threshold
        threshold_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        threshold_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(threshold_frame, text="Low Stock Threshold:", background="#f0f0f0").pack(side=tk.LEFT)
        
        threshold_var = tk.StringVar(value="5")
        threshold_entry = ttk.Entry(threshold_frame, textvariable=threshold_var, width=5)
        threshold_entry.pack(side=tk.LEFT, padx=5)
        
        # Container for low stock items
        items_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        items_frame.pack(fill=tk.BOTH, expand=True)
        
        def load_low_stock():
            # Clear previous list
            for widget in items_frame.winfo_children():
                widget.destroy()
            
            try:
                threshold = int(threshold_var.get())
                if threshold <= 0:
                    messagebox.showerror("Error", "Threshold must be positive!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Threshold must be a number!")
                return
            
            # Get low stock items
            low_stock_items = self.inventory_db.get_low_stock_items(threshold)
            
            if not low_stock_items:
                message_label = ttk.Label(items_frame, text=f"No items below threshold ({threshold} units)", 
                                         font=self.label_font, background="#f0f0f0")
                message_label.pack(pady=20)
                return
            
            # Create a treeview for displaying items
            columns = ("id", "name", "code", "category", "quantity")
            tree = ttk.Treeview(items_frame, columns=columns, show='headings')
            
            # Define column headings
            tree.heading("id", text="ID")
            tree.heading("name", text="Product Name")
            tree.heading("code", text="Code")
            tree.heading("category", text="Category")
            tree.heading("quantity", text="In Stock")
            
            # Define column widths
            tree.column("id", width=50)
            tree.column("name", width=200)
            tree.column("code", width=100)
            tree.column("category", width=100)
            tree.column("quantity", width=80)
            
            # Add a scrollbar
            scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            
            # Pack the treeview and scrollbar
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Add items to the treeview
            for item in low_stock_items:
                values = (
                    item['id'],
                    item['name'],
                    item['code'] or '',
                    item['category'] or '',
                    item['current_quantity']
                )
                tree.insert('', tk.END, values=values)
            
            # Add double-click event to stock-in
            tree.bind('<Double-1>', lambda event: self.on_low_stock_double_click(event, tree))
            
            # Update status
            self.status_var.set(f"Low Stock Alert: {len(low_stock_items)} items below threshold ({threshold} units)")
        
        # Load button
        ttk.Button(threshold_frame, text="Update", command=load_low_stock).pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        load_low_stock()
    
    def backup_database(self):
        """Create a backup of the database."""
        backup_path, error = self.inventory_db.backup_database()
        
        if backup_path:
            messagebox.showinfo("Backup Created", f"Database backup created successfully at:\n{backup_path}")
        else:
            messagebox.showerror("Backup Failed", f"Failed to create backup: {error}")
    
    def on_product_double_click(self, event):
        """Handle double-click on a product in the inventory view."""
        # Get the treeview
        tree = event.widget
        
        # Get the selected item
        selected_item = tree.selection()
        if not selected_item:
            return
        
        # Get the product ID
        values = tree.item(selected_item[0], 'values')
        product_id = int(values[0])
        
        # Show product edit dialog
        self.edit_product(product_id)
    
    def on_low_stock_double_click(self, event, tree):
        """Handle double-click on an item in the low stock view."""
        # Get the selected item
        selected_item = tree.selection()
        if not selected_item:
            return
        
        # Get the product ID
        values = tree.item(selected_item[0], 'values')
        product_id = int(values[0])
        
        # Ask if they want to stock this item
        if messagebox.askyesno("Stock In", f"Do you want to add stock for '{values[1]}'?"):
            self.show_stock_in(product_id)
    
    def edit_product(self, product_id):
        """Display a dialog to edit a product."""
        product = self.inventory_db.get_product_by_id(product_id)
        if not product:
            messagebox.showerror("Error", f"Product ID {product_id} not found!")
            return
        
        # Create top level dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Product: {product['name']}")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Add form fields
        form_frame = tk.Frame(dialog, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product name
        ttk.Label(form_frame, text="Product Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=product['name'])
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Product code
        ttk.Label(form_frame, text="Product Code:").grid(row=1, column=0, sticky=tk.W, pady=5)
        code_var = tk.StringVar(value=product['code'] or "")
        ttk.Entry(form_frame, textvariable=code_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Category
        ttk.Label(form_frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value=product['category'] or "")
        
        # Get existing categories for dropdown
        categories = self.inventory_db.get_categories()
        
        if categories:
            category_dropdown = ttk.Combobox(form_frame, textvariable=category_var, width=20)
            category_dropdown['values'] = categories
            category_dropdown.grid(row=2, column=1, sticky=tk.W, pady=5)
        else:
            ttk.Entry(form_frame, textvariable=category_var, width=20).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Purchase price
        ttk.Label(form_frame, text="Purchase Price:").grid(row=3, column=0, sticky=tk.W, pady=5)
        purchase_var = tk.StringVar(value=str(product['purchase_price']) if product['purchase_price'] else "")
        ttk.Entry(form_frame, textvariable=purchase_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Selling price
        ttk.Label(form_frame, text="Selling Price:").grid(row=4, column=0, sticky=tk.W, pady=5)
        selling_var = tk.StringVar(value=str(product['selling_price']) if product['selling_price'] else "")
        ttk.Entry(form_frame, textvariable=selling_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Current stock (display only)
        ttk.Label(form_frame, text="Current Stock:").grid(row=5, column=0, sticky=tk.W, pady=5)
        stock_var = tk.StringVar(value=str(product['current_quantity']))
        stock_display = ttk.Entry(form_frame, textvariable=stock_var, width=10, state='readonly')
        stock_display.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        def save_changes():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Product name is required!")
                return
            
            try:
                purchase_price = float(purchase_var.get()) if purchase_var.get() else None
                selling_price = float(selling_var.get()) if selling_var.get() else None
            except ValueError:
                messagebox.showerror("Error", "Prices must be numbers!")
                return
            
            code = code_var.get().strip() or None
            category = category_var.get().strip() or None
            
            success, error = self.inventory_db.update_product(
                product_id, name, code, category, purchase_price, selling_price
            )
            
            if success:
                messagebox.showinfo("Success", f"Product updated successfully!")
                dialog.destroy()
                self.show_inventory()  # Refresh inventory view
            else:
                messagebox.showerror("Error", error)
        
        ttk.Button(button_frame, text="Save Changes", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Additional action buttons
        action_frame = tk.Frame(form_frame)
        action_frame.grid(row=7, column=0, columnspan=2, pady=5)
        
        ttk.Button(action_frame, text="Stock In", 
                  command=lambda: [dialog.destroy(), self.show_stock_in(product_id)]).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="Record Sale", 
                  command=lambda: [dialog.destroy(), self.show_sales(product_id)]).pack(side=tk.LEFT, padx=5)
    
    def search_products(self):
        """Search for products and display results."""
        search_term = self.search_var.get().strip()
        if not search_term:
            return
        
        products = self.inventory_db.find_product(search_term)
        
        if not products:
            messagebox.showinfo("Search Results", f"No products found matching '{search_term}'.")
            return
        
        # If only one product found, open it directly
        if len(products) == 1:
            self.edit_product(products[0]['id'])
            return
        
        # Create a product selector to show multiple results
        selector = ProductSelector(self.root, self.inventory_db, search_term)
        if selector.result:
            self.edit_product(selector.result['id'])