import sqlite3
import datetime
import os

class InventoryDatabase:
    def __init__(self, db_path="inventory.db"):
        """Sets up our store's inventory tracking - like a digital stock register."""
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        """Creates our inventory tracking system if it's a new store setup."""
        # Think of this as setting up fresh record books for the store
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # This is where we keep track of what items we sell
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,         -- Every product needs a name!
            code TEXT UNIQUE,           -- Optional product code/SKU
            category TEXT,              -- Helps group similar items (snacks, drinks, etc.)
            purchase_price REAL,        -- What we pay to our supplier
            selling_price REAL,         -- What customers pay us
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When we added this product
        )
        ''')
        
        # This records every time stock moves in or out - like a transaction diary
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            movement_type TEXT CHECK(movement_type IN ('stock_in', 'sale', 'adjustment')),
            quantity INTEGER NOT NULL,  -- How many items were added/removed
            unit_price REAL,            -- Price per item for this transaction
            notes TEXT,                 -- Any special notes about this movement
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When this happened
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # This gives us a quick way to see current stock for each product
        # It's like a summary page that's always up-to-date
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS current_stock AS
        SELECT 
            p.id,
            p.name,
            p.code,
            p.category,
            p.purchase_price,
            p.selling_price,
            COALESCE(SUM(CASE WHEN m.movement_type = 'stock_in' THEN m.quantity
                       WHEN m.movement_type = 'sale' THEN -m.quantity
                       WHEN m.movement_type = 'adjustment' THEN m.quantity
                       ELSE 0 END), 0) as current_quantity
        FROM products p
        LEFT JOIN stock_movements m ON p.id = m.product_id
        GROUP BY p.id
        ''')
        
        conn.commit()
        conn.close()
    
    def add_product(self, name, code=None, category=None, purchase_price=None, selling_price=None):
        """Adds a new item to our inventory - like stocking a new product type."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO products (name, code, category, purchase_price, selling_price)
            VALUES (?, ?, ?, ?, ?)
            ''', (name, code, category, purchase_price, selling_price))
            product_id = cursor.lastrowid
            conn.commit()
            return product_id, None
        except sqlite3.IntegrityError:
            # This happens if we try to use the same product code twice
            conn.rollback()
            return None, "This product code is already being used for another item!"
        finally:
            conn.close()
    
    def update_product(self, product_id, name=None, code=None, category=None, purchase_price=None, selling_price=None):
        """Updates product info - like when supplier prices change or we rename something."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First check if this product actually exists
        cursor.execute("SELECT name, code, category, purchase_price, selling_price FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return False, "Can't find this product in our inventory!"
        
        # Only update the fields that were actually changed
        current_name, current_code, current_category, current_purchase_price, current_selling_price = product
        name = name if name is not None else current_name
        code = code if code is not None else current_code
        category = category if category is not None else current_category
        purchase_price = purchase_price if purchase_price is not None else current_purchase_price
        selling_price = selling_price if selling_price is not None else current_selling_price
        
        try:
            cursor.execute('''
            UPDATE products 
            SET name = ?, code = ?, category = ?, purchase_price = ?, selling_price = ?
            WHERE id = ?
            ''', (name, code, category, purchase_price, selling_price, product_id))
            conn.commit()
            return True, None
        except sqlite3.IntegrityError:
            conn.rollback()
            return False, "This product code is already being used for another item!"
        finally:
            conn.close()
    
    def record_stock_movement(self, product_id, movement_type, quantity, unit_price=None, notes=None):
        """Records stock coming in, going out, or being adjusted - like writing in a sales log.
        
        This is the most important function - it tracks every time stock moves:
        - When we get new stock deliveries (stock_in)
        - When we sell items to customers (sale)
        - When we need to adjust stock due to damage, loss, etc. (adjustment)
        """
        if movement_type not in ('stock_in', 'sale', 'adjustment'):
            return False, "Please use a valid movement type (stock_in, sale, or adjustment)"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Make sure the product actually exists before recording movement
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return False, "Can't find this product in our inventory!"
        
        try:
            cursor.execute('''
            INSERT INTO stock_movements (product_id, movement_type, quantity, unit_price, notes)
            VALUES (?, ?, ?, ?, ?)
            ''', (product_id, movement_type, quantity, unit_price, notes))
            conn.commit()
            return True, None
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()
    
    def get_current_stock(self, low_stock_threshold=5):
        """Get the current stock levels for all products."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, code, category, current_quantity, purchase_price, selling_price
        FROM current_stock
        ORDER BY name
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def find_product(self, search_term):
        """Find products by name or code."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Search in both name and code fields
        cursor.execute('''
        SELECT id, name, code, category, purchase_price, selling_price
        FROM products
        WHERE name LIKE ? OR code LIKE ?
        ORDER BY name
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_product_by_id(self, product_id):
        """Get a product by its ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT p.id, p.name, p.code, p.category, p.purchase_price, p.selling_price, cs.current_quantity
        FROM products p
        LEFT JOIN current_stock cs ON p.id = cs.id
        WHERE p.id = ?
        ''', (product_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def get_product_movements(self, product_id, start_date=None, end_date=None):
        """Get stock movement history for a specific product."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return None, "Product not found!"
        
        product_name = product['name']
        
        # Build the query based on date filters
        query = '''
        SELECT 
            id, 
            movement_type, 
            quantity, 
            unit_price, 
            notes, 
            timestamp
        FROM stock_movements
        WHERE product_id = ?
        '''
        
        params = [product_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        movements = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return product_name, movements
    
    def get_daily_summary(self, date=None):
        """Get a daily summary of sales and stock-ins."""
        if not date:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        start_date = f"{date} 00:00:00"
        end_date = f"{date} 23:59:59"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total sales
        cursor.execute('''
        SELECT 
            COUNT(*) as num_sales,
            SUM(m.quantity) as total_items_sold,
            SUM(m.quantity * m.unit_price) as total_revenue
        FROM stock_movements m
        WHERE m.movement_type = 'sale'
        AND m.timestamp BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        sales_summary = cursor.fetchone()
        
        # Get total stock-ins
        cursor.execute('''
        SELECT 
            COUNT(*) as num_stock_ins,
            SUM(m.quantity) as total_items_received
        FROM stock_movements m
        WHERE m.movement_type = 'stock_in'
        AND m.timestamp BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        stock_in_summary = cursor.fetchone()
        
        # Get top sold products
        cursor.execute('''
        SELECT 
            p.name,
            SUM(m.quantity) as total_sold
        FROM stock_movements m
        JOIN products p ON m.product_id = p.id
        WHERE m.movement_type = 'sale'
        AND m.timestamp BETWEEN ? AND ?
        GROUP BY p.id
        ORDER BY total_sold DESC
        LIMIT 5
        ''', (start_date, end_date))
        
        top_sold = cursor.fetchall()
        
        conn.close()
        
        return {
            'date': date,
            'sales': sales_summary,
            'stock_ins': stock_in_summary,
            'top_sold': top_sold
        }
    
    def get_categories(self):
        """Get all unique product categories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''
        ''')
        
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return categories
    
    def get_low_stock_items(self, threshold=5):
        """Get items with stock at or below the specified threshold."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, code, category, current_quantity
        FROM current_stock
        WHERE current_quantity <= ?
        ORDER BY current_quantity ASC
        ''', (threshold,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def backup_database(self):
        """Create a backup of the database."""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"inventory_backup_{timestamp}.db"
        
        try:
            # Simple file copy for backup
            with open(self.db_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            
            return backup_path, None
        except Exception as e:
            return None, str(e)