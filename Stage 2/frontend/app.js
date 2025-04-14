/**
 * Main Application JavaScript for Kiryana Inventory System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    const navLinks = document.querySelectorAll('.nav-link[data-page]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetPage = this.getAttribute('data-page');
            showPage(targetPage);
        });
    });
    
    // Initialize components
    initDashboard();
    initProducts();
    initInventory();
    initMovements();
    initReports();
    
    // Initialize store selector
    const storeSelector = document.getElementById('storeSelector');
    const apiKeyInput = document.getElementById('apiKeyInput');
    // Set initial values
    const savedStoreId = localStorage.getItem('selectedStoreId') || '1';
    const apiKey = localStorage.getItem('apiKey') || (savedStoreId === '1' ? 'store1_api_key' : 'store2_api_key');
    
    storeSelector.value = savedStoreId;
    apiKeyInput.value = apiKey;
    // Store selector change handler
    storeSelector.addEventListener('change', function() {
        const newApiKey = this.value === '1' ? 'store1_api_key' : 'store2_api_key';
        apiKeyInput.value = newApiKey;
        localStorage.setItem('selectedStoreId', this.value);
        localStorage.setItem('apiKey', newApiKey);
        refreshCurrentPage();
    });
    
    // Show initial page (dashboard)
    showPage('dashboard');
});

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page-section').forEach(page => {
        page.classList.add('d-none');
    });
    
    // Show selected page
    const selectedPage = document.getElementById(`${pageName}-page`);
    if (selectedPage) {
        selectedPage.classList.remove('d-none');
    }
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`.nav-link[data-page="${pageName}"]`).classList.add('active');
    
    // Refresh page data
    refreshPage(pageName);
}

function getCurrentPage() {
    const visiblePage = document.querySelector('.page-section:not(.d-none)');
    if (visiblePage) {
        return visiblePage.id.replace('-page', '');
    }
    return 'dashboard';
}

function refreshCurrentPage() {
    refreshPage(getCurrentPage());
}

function refreshPage(pageName) {
    switch(pageName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'products':
            loadProducts();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'movements':
            loadMovements();
            break;
        case 'reports':
            loadReport('daily-sales');
            break;
    }
}

// Error handling
function showError(message) {
    alert(message);
}

// Date formatting
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function formatMovementType(type) {
    switch(type) {
        case 'stock_in':
            return 'Stock In';
        case 'sale':
            return 'Sale';
        case 'adjustment':
            return 'Adjustment';
        default:
            return type;
    }
}

// Dashboard functionality
function initDashboard() {
    loadDashboardData();
}

function loadDashboardData() {
    loadInventorySummary();
    loadLowStockItems();
    loadRecentTransactions();
}

function loadInventorySummary() {
    const summaryElement = document.getElementById('inventorySummary');
    summaryElement.innerHTML = '<div class="loading-placeholder">Loading inventory summary...</div>';
    
    API.reports.getInventorySummary()
        .then(data => {
            if (data && data.length > 0) {
                const summary = data[0]; // Current store summary
                
                let html = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="stat-card primary">
                            <h5>Total Products</h5>
                            <p>${summary.product_count}</p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="stat-card danger">
                            <h5>Low Stock Items</h5>
                            <p>${summary.low_stock_count}</p>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-12">
                        <div class="stat-card success">
                            <h5>Total Inventory Value</h5>
                            <p>₹${summary.total_value.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
                `;
                
                summaryElement.innerHTML = html;
            } else {
                summaryElement.innerHTML = '<div class="alert alert-info">No inventory data available.</div>';
            }
        })
        .catch(error => {
            summaryElement.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}

function loadLowStockItems() {
    const lowStockElement = document.getElementById('lowStockAlert');
    lowStockElement.innerHTML = '<div class="loading-placeholder">Loading low stock items...</div>';
    
    API.inventory.getLowStock()
        .then(data => {
            if (data && data.length > 0) {
                let html = `
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
                `;
                
                data.forEach(item => {
                    html += `
                    <tr>
                        <td>${item.product.name}</td>
                        <td class="status-low">${item.current_quantity}</td>
                    </tr>
                    `;
                });
                
                html += `
                    </tbody>
                </table>
                `;
                
                if (data.length >= 5) {
                    html += `<a href="#" onclick="showPage('inventory'); return false;" class="btn btn-sm btn-outline-danger">View All Low Stock Items</a>`;
                }
                
                lowStockElement.innerHTML = html;
            } else {
                lowStockElement.innerHTML = '<div class="alert alert-success">No low stock items!</div>';
            }
        })
        .catch(error => {
            lowStockElement.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}

function loadRecentTransactions() {
    const transactionsElement = document.getElementById('recentTransactions');
    transactionsElement.innerHTML = '<div class="loading-placeholder">Loading recent transactions...</div>';
    
    API.movements.getAll({ limit: 10 })
        .then(data => {
            if (data && data.length > 0) {
                let html = `
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Product</th>
                                <th>Type</th>
                                <th>Quantity</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                data.forEach(movement => {
                    const movementClass = `movement-${movement.movement_type}`;
                    const valueText = movement.unit_price 
                        ? `₹${(movement.quantity * movement.unit_price).toFixed(2)}` 
                        : '-';
                    
                    html += `
                    <tr>
                        <td>${formatDate(movement.timestamp)}</td>
                        <td>${movement.product.name}</td>
                        <td class="${movementClass}">${formatMovementType(movement.movement_type)}</td>
                        <td>${movement.quantity}</td>
                        <td>${valueText}</td>
                    </tr>
                    `;
                });
                
                html += `
                    </tbody>
                </table>
                </div>
                <a href="#" onclick="showPage('movements'); return false;" class="btn btn-sm btn-outline-primary">View All Transactions</a>
                `;
                
                transactionsElement.innerHTML = html;
            } else {
                transactionsElement.innerHTML = '<div class="alert alert-info">No recent transactions.</div>';
            }
        })
        .catch(error => {
            transactionsElement.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}

// Complete Products Functionality
function loadProducts() {
    const productList = document.getElementById('productList');
    productList.innerHTML = '<div class="loading-placeholder">Loading products...</div>';
    
    API.products.getAll()
        .then(products => {
            if (products && products.length > 0) {
                // Populate category filter
                const categories = new Set();
                products.forEach(product => {
                    if (product.category) {
                        categories.add(product.category);
                    }
                });
                
                const categoryFilter = document.getElementById('categoryFilter');
                categoryFilter.innerHTML = '<option value="">All Categories</option>';
                categories.forEach(category => {
                    categoryFilter.innerHTML += `<option value="${category}">${category}</option>`;
                });
                
                // Render product table
                let html = `
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Name</th>
                                <th>Category</th>
                                <th>Purchase Price</th>
                                <th>Selling Price</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                products.forEach(product => {
                    html += `
                    <tr>
                        <td>${product.code || '-'}</td>
                        <td>${product.name}</td>
                        <td>${product.category || '-'}</td>
                        <td>₹${product.purchase_price?.toFixed(2) || '-'}</td>
                        <td>₹${product.selling_price?.toFixed(2) || '-'}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="editProduct(${product.id})">Edit</button>
                            <button class="btn btn-sm btn-outline-success" onclick="showStockInModal(${product.id})">Stock In</button>
                        </td>
                    </tr>
                    `;
                });
                
                html += `
                        </tbody>
                    </table>
                </div>
                `;
                
                productList.innerHTML = html;
            } else {
                productList.innerHTML = '<div class="alert alert-info">No products found. Add your first product to get started.</div>';
            }
        })
        .catch(error => {
            productList.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}

function initProducts() {
    // Setup product search
    const productSearch = document.getElementById('productSearch');
    productSearch.addEventListener('input', function() {
        const searchTerm = this.value.trim();
        if (searchTerm.length >= 2) {
            API.products.getAll({ search: searchTerm })
                .then(updateProductTable)
                .catch(error => showError(error.message));
        } else if (searchTerm.length === 0) {
            loadProducts();
        }
    });
    
    // Setup category filter
    const categoryFilter = document.getElementById('categoryFilter');
    categoryFilter.addEventListener('change', function() {
        const category = this.value;
        if (category) {
            API.products.getAll({ category })
                .then(updateProductTable)
                .catch(error => showError(error.message));
        } else {
            loadProducts();
        }
    });
    
    // Setup add product button
    const addProductBtn = document.getElementById('addProductBtn');
    addProductBtn.addEventListener('click', function() {
        // Reset form
        document.getElementById('productForm').reset();
        document.getElementById('productId').value = '';
        
        // Update modal title
        document.getElementById('productModalTitle').textContent = 'Add Product';
        
        // Show modal
        const productModal = new bootstrap.Modal(document.getElementById('productModal'));
        productModal.show();
    });
    
    // Setup save product button
    const saveProductBtn = document.getElementById('saveProductBtn');
    saveProductBtn.addEventListener('click', saveProduct);
    
    // Initial load
    loadProducts();
}

function updateProductTable(products) {
    const productList = document.getElementById('productList');
    
    if (products && products.length > 0) {
        let html = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Purchase Price</th>
                        <th>Selling Price</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        products.forEach(product => {
            html += `
            <tr>
                <td>${product.code || '-'}</td>
                <td>${product.name}</td>
                <td>${product.category || '-'}</td>
                <td>₹${product.purchase_price?.toFixed(2) || '-'}</td>
                <td>₹${product.selling_price?.toFixed(2) || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editProduct(${product.id})">Edit</button>
                    <button class="btn btn-sm btn-outline-success" onclick="showStockInModal(${product.id})">Stock In</button>
                </td>
            </tr>
            `;
        });
        
        html += `
                </tbody>
            </table>
        </div>
        `;
        
        productList.innerHTML = html;
    } else {
        productList.innerHTML = '<div class="alert alert-info">No products match your search criteria.</div>';
    }
}

function handleEditProduct(productId) {
    // Fetch product details
    API.products.getById(productId)
        .then(product => {
            // Populate form
            document.getElementById('productId').value = product.id;
            document.getElementById('productName').value = product.name;
            document.getElementById('productCode').value = product.code || '';
            document.getElementById('productCategory').value = product.category || '';
            document.getElementById('purchasePrice').value = product.purchase_price || '';
            document.getElementById('sellingPrice').value = product.selling_price || '';
            
            // Update modal title
            document.getElementById('productModalTitle').textContent = 'Edit Product';
            
            // Show modal
            const productModal = new bootstrap.Modal(document.getElementById('productModal'));
            productModal.show();
        })
        .catch(error => {
            showError(error.message);
        });
}

function saveProduct() {
    // Get form data
    const productId = document.getElementById('productId').value;
    const productData = {
        name: document.getElementById('productName').value,
        code: document.getElementById('productCode').value || null,
        category: document.getElementById('productCategory').value || null,
        purchase_price: parseFloat(document.getElementById('purchasePrice').value) || null,
        selling_price: parseFloat(document.getElementById('sellingPrice').value) || null
    };
    
    // Validate required fields
    if (!productData.name) {
        showError('Product name is required');
        return;
    }
    
    // For editing existing products, we need to use a different code
    // to avoid the unique constraint violation
    if (productId) {
        // If we're editing, modify the code slightly to make it unique
        if (productData.code) {
            // Append current timestamp to ensure uniqueness
            productData.code = productData.code + '_' + Date.now();
        }
    }
    
    // Always use create since the backend doesn't have an update endpoint
    API.products.create(productData)
        .then(response => {
            // Close modal
            const productModal = bootstrap.Modal.getInstance(document.getElementById('productModal'));
            productModal.hide();
            
            // Refresh product list
            loadProducts();
        })
        .catch(error => {
            showError(error.message);
        });
}

// Complete Inventory Functionality
function loadInventory() {
    const inventoryList = document.getElementById('inventoryList');
    inventoryList.innerHTML = '<div class="loading-placeholder">Loading inventory...</div>';
    
    const filter = document.getElementById('inventoryFilter').value;
    const params = { store_id: API.getStoreId() };
    
    if (filter === 'low') {
        params.low_stock = true;
        params.threshold = 5;
    }
    
    API.inventory.getAll(params)
        .then(items => {
            if (items && items.length > 0) {
                let html = `
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Category</th>
                                <th>Current Stock</th>
                                <th>Value</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                items.forEach(item => {
                    const stockClass = item.current_quantity <= 5 ? 'status-low' : 'status-ok';
                    const stockValue = item.product.selling_price ? (item.current_quantity * item.product.selling_price).toFixed(2) : '-';
                    
                    html += `
                    <tr>
                        <td>${item.product.name}</td>
                        <td>${item.product.category || '-'}</td>
                        <td class="${stockClass}">${item.current_quantity}</td>
                        <td>₹${stockValue}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="updateInventoryItem(${item.product.id}, ${item.current_quantity})">Update</button>
                            <button class="btn btn-sm btn-outline-success me-1" onclick="showStockInModal(${item.product.id})">Stock In</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="showSaleModal(${item.product.id})">Sell</button>
                        </td>
                    </tr>
                    `;
                });
                
                html += `
                        </tbody>
                    </table>
                </div>
                `;
                
                inventoryList.innerHTML = html;
            } else {
                inventoryList.innerHTML = '<div class="alert alert-info">No inventory items found.</div>';
            }
        })
        .catch(error => {
            inventoryList.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}

function initInventory() {
    // Setup inventory filter
    const inventoryFilter = document.getElementById('inventoryFilter');
    inventoryFilter.addEventListener('change', loadInventory);
    
    // Setup inventory search
    const inventorySearch = document.getElementById('inventorySearch');
    inventorySearch.addEventListener('input', function() {
        const searchTerm = this.value.trim();
        if (searchTerm.length >= 2) {
            // Search inventory by product name (client-side filtering for now)
            const rows = document.querySelectorAll('#inventoryList table tbody tr');
            rows.forEach(row => {
                const productName = row.querySelector('td:first-child').textContent.toLowerCase();
                if (productName.includes(searchTerm.toLowerCase())) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        } else if (searchTerm.length === 0) {
            const rows = document.querySelectorAll('#inventoryList table tbody tr');
            rows.forEach(row => row.style.display = '');
        }
    });
    
    // Initial load
    loadInventory();
}

function handleUpdateInventoryItem(productId, currentQuantity) {
    const newQuantity = prompt("Enter new quantity:", currentQuantity);
    if (newQuantity !== null) {
        const quantity = parseInt(newQuantity);
        if (!isNaN(quantity) && quantity >= 0) {
            API.inventory.updateQuantity(productId, quantity)
                .then(() => {
                    loadInventory();
                })
                .catch(error => {
                    showError(error.message);
                });
        } else {
            showError("Please enter a valid non-negative number");
        }
    }
}

// Complete Stock Movements Functionality
function loadMovements() {
    const movementsList = document.getElementById('movementsList');
    movementsList.innerHTML = '<div class="loading-placeholder">Loading stock movements...</div>';
    
    // Collect filter values
    const movementType = document.getElementById('movementTypeFilter').value;
    const startDate = document.getElementById('startDateFilter').value;
    const endDate = document.getElementById('endDateFilter').value;
    
    // Build params object
    const params = { store_id: API.getStoreId() };
    if (movementType) params.movement_type = movementType;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    API.movements.getAll(params)
        .then(movements => {
            if (movements && movements.length > 0) {
                let html = `
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Date & Time</th>
                                <th>Product</th>
                                <th>Type</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Total</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                movements.forEach(movement => {
                    const movementClass = `movement-${movement.movement_type}`;
                    const timestamp = new Date(movement.timestamp);
                    const dateStr = formatDate(timestamp);
                    const timeStr = timestamp.toLocaleTimeString();
                    const unitPrice = movement.unit_price ? `₹${movement.unit_price.toFixed(2)}` : '-';
                    const total = movement.unit_price ? `₹${(movement.quantity * movement.unit_price).toFixed(2)}` : '-';
                    
                    html += `
                    <tr>
                        <td>${dateStr} ${timeStr}</td>
                        <td>${movement.product.name}</td>
                        <td class="${movementClass}">${formatMovementType(movement.movement_type)}</td>
                        <td>${movement.quantity}</td>
                        <td>${unitPrice}</td>
                        <td>${total}</td>
                        <td>${movement.notes || '-'}</td>
                    </tr>
                    `;
                });
                
                html += `
                        </tbody>
                    </table>
                </div>
                `;
                
                movementsList.innerHTML = html;
            } else {
                movementsList.innerHTML = '<div class="alert alert-info">No stock movements found.</div>';
            }
        })
        .catch(error => {
            movementsList.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}

function initMovements() {
    // Apply filters button
    document.getElementById('applyMovementFilters').addEventListener('click', loadMovements);
    
    // Stock In button
    document.getElementById('stockInBtn').addEventListener('click', function() {
        document.getElementById('movementType').value = 'stock_in';
        document.getElementById('movementModalTitle').textContent = 'Record Stock In';
        document.getElementById('unitPrice').disabled = false;
        
        // Load products
        loadProductsForSelect().then(() => {
            const movementModal = new bootstrap.Modal(document.getElementById('movementModal'));
            movementModal.show();
        });
    });
    
    // Sale button
    document.getElementById('saleBtn').addEventListener('click', function() {
        document.getElementById('movementType').value = 'sale';
        document.getElementById('movementModalTitle').textContent = 'Record Sale';
        document.getElementById('unitPrice').disabled = false;
        
        // Load products
        loadProductsForSelect().then(() => {
            const movementModal = new bootstrap.Modal(document.getElementById('movementModal'));
            movementModal.show();
        });
    });
    
    // Adjustment button
    document.getElementById('adjustmentBtn').addEventListener('click', function() {
        document.getElementById('movementType').value = 'adjustment';
        document.getElementById('movementModalTitle').textContent = 'Record Adjustment';
        document.getElementById('unitPrice').disabled = true;
        document.getElementById('unitPrice').value = '';
        
        // Load products
        loadProductsForSelect().then(() => {
            const movementModal = new bootstrap.Modal(document.getElementById('movementModal'));
            movementModal.show();
        });
    });
    
    // Save movement button
    document.getElementById('saveMovementBtn').addEventListener('click', saveMovement);
    
    // Initial load
    loadMovements();
}

function loadProductsForSelect() {
    const productSelect = document.getElementById('productSelect');
    productSelect.innerHTML = '<option value="">Select a product</option>';
    
    return API.products.getAll()
        .then(products => {
            products.forEach(product => {
                productSelect.innerHTML += `<option value="${product.id}">${product.name}</option>`;
            });
        })
        .catch(error => {
            showError(error.message);
        });
}

function handleShowStockInModal(productId) {
    document.getElementById('movementType').value = 'stock_in';
    document.getElementById('movementModalTitle').textContent = 'Record Stock In';
    document.getElementById('unitPrice').disabled = false;
    
    loadProductsForSelect().then(() => {
        document.getElementById('productSelect').value = productId;
        const movementModal = new bootstrap.Modal(document.getElementById('movementModal'));
        movementModal.show();
    });
}

function handleShowSaleModal(productId) {
    document.getElementById('movementType').value = 'sale';
    document.getElementById('movementModalTitle').textContent = 'Record Sale';
    document.getElementById('unitPrice').disabled = false;
    
    loadProductsForSelect().then(() => {
        document.getElementById('productSelect').value = productId;
        const movementModal = new bootstrap.Modal(document.getElementById('movementModal'));
        movementModal.show();
    });
}

function saveMovement() {
    const movementType = document.getElementById('movementType').value;
    const productId = document.getElementById('productSelect').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const unitPrice = document.getElementById('unitPrice').value ? parseFloat(document.getElementById('unitPrice').value) : null;
    const notes = document.getElementById('notes').value;
    
    // Validate required fields
    if (!productId) {
        showError('Please select a product');
        return;
    }
    
    if (!quantity || quantity <= 0) {
        showError('Please enter a valid quantity');
        return;
    }
    
    // Validate unit price for stock_in and sale
    if ((movementType === 'stock_in' || movementType === 'sale') && !unitPrice) {
        showError('Please enter a unit price');
        return;
    }
    
    // Handle different movement types
    let saveOperation;
    
    switch (movementType) {
        case 'stock_in':
            saveOperation = API.movements.stockIn(productId, quantity, unitPrice, notes);
            break;
        case 'sale':
            saveOperation = API.movements.recordSale(productId, quantity, unitPrice, notes);
            break;
        case 'adjustment':
            saveOperation = API.movements.makeAdjustment(productId, quantity, notes);
            break;
    }
    
    saveOperation
        .then(response => {
            // Close modal
            const movementModal = bootstrap.Modal.getInstance(document.getElementById('movementModal'));
            movementModal.hide();
            
            // Reset form
            document.getElementById('movementForm').reset();
            
            // Refresh movements list
            loadMovements();
            
            // Refresh inventory if on inventory page
            if (getCurrentPage() === 'inventory') {
                loadInventory();
            }
        })
        .catch(error => {
            showError(error.message);
        });
}

// Complete Reports Functionality
function initReports() {
    // Set up report tab clicks
    document.getElementById('daily-sales-tab').addEventListener('click', function(e) {
        e.preventDefault();
        loadReport('daily-sales');
        
        // Update active tab
        document.querySelectorAll('.nav-link').forEach(tab => tab.classList.remove('active'));
        this.classList.add('active');
    });
    
    document.getElementById('inventory-value-tab').addEventListener('click', function(e) {
        e.preventDefault();
        loadReport('inventory-value');
        
        // Update active tab
        document.querySelectorAll('.nav-link').forEach(tab => tab.classList.remove('active'));
        this.classList.add('active');
    });
    
    // Initial load
    loadReport('daily-sales');
}

function loadReport(reportType) {
    const reportContent = document.getElementById('reportContent');
    reportContent.innerHTML = '<div class="loading-placeholder">Loading report data...</div>';
    
    if (reportType === 'daily-sales') {
        // Create date inputs for filtering
        const today = new Date();
        const oneWeekAgo = new Date();
        oneWeekAgo.setDate(today.getDate() - 7);
        
        const startDate = oneWeekAgo.toISOString().split('T')[0];
        const endDate = today.toISOString().split('T')[0];
        
        reportContent.innerHTML = `
        <div class="mb-3">
            <div class="row">
                <div class="col-md-4">
                    <label for="salesStartDate">Start Date:</label>
                    <input type="date" id="salesStartDate" class="form-control" value="${startDate}">
                </div>
                <div class="col-md-4">
                    <label for="salesEndDate">End Date:</label>
                    <input type="date" id="salesEndDate" class="form-control" value="${endDate}">
                </div>
                <div class="col-md-4">
                    <label>&nbsp;</label>
                    <button id="applySalesDateFilter" class="form-control btn btn-primary">Apply</button>
                </div>
            </div>
        </div>
        <div id="salesReportData"></div>
        `;
        
        // Add event listener to the apply button
        document.getElementById('applySalesDateFilter').addEventListener('click', function() {
            loadDailySalesReport();
        });
        
        // Load report data
        loadDailySalesReport();
    } else if (reportType === 'inventory-value') {
        loadInventoryValueReport();
    }
}

function loadDailySalesReport() {
    const salesReportData = document.getElementById('salesReportData');
    salesReportData.innerHTML = '<div class="loading-placeholder">Loading sales data...</div>';
    
    const startDate = document.getElementById('salesStartDate').value;
    const endDate = document.getElementById('salesEndDate').value;
    
    API.reports.getDailySales({
        store_id: API.getStoreId(),
        start_date: startDate,
        end_date: endDate
    })
    .then(data => {
        if (data && data.length > 0) {
            let totalRevenue = 0;
            let totalItems = 0;
            let totalTransactions = 0;
            
            let html = `
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Transactions</th>
                            <th>Items Sold</th>
                            <th>Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            data.forEach(day => {
                totalRevenue += day.total_revenue;
                totalItems += day.total_items;
                totalTransactions += day.transaction_count;
                
                html += `
                <tr>
                    <td>${day.date}</td>
                    <td>${day.transaction_count}</td>
                    <td>${day.total_items}</td>
                    <td>₹${day.total_revenue.toFixed(2)}</td>
                </tr>
                `;
            });
            
            html += `
                    </tbody>
                    <tfoot>
                        <tr class="table-active">
                            <th>Total</th>
                            <th>${totalTransactions}</th>
                            <th>${totalItems}</th>
                            <th>₹${totalRevenue.toFixed(2)}</th>
                        </tr>
                    </tfoot>
                </table>
            </div>
            `;
            
            salesReportData.innerHTML = html;
        } else {
            salesReportData.innerHTML = '<div class="alert alert-info">No sales data found for the selected period.</div>';
        }
    })
    .catch(error => {
        salesReportData.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    });
}

function loadInventoryValueReport() {
    const reportContent = document.getElementById('reportContent');
    reportContent.innerHTML = '<div class="loading-placeholder">Loading inventory value data...</div>';
    
    API.reports.getInventorySummary()
        .then(data => {
            if (data && data.length > 0) {
                const summary = data[0]; // Current store
                
                let html = `
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Inventory Summary</h5>
                                <div class="stat-card success">
                                    <h5>Total Inventory Value</h5>
                                    <p>₹${summary.total_value.toFixed(2)}</p>
                                </div>
                                <div class="stat-card primary">
                                    <h5>Total Products</h5>
                                    <p>${summary.product_count}</p>
                                </div>
                                <div class="stat-card danger">
                                    <h5>Low Stock Items</h5>
                                    <p>${summary.low_stock_count}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                `;
                
                // Now load top products by value
                html += `<h5>Top Products by Value</h5>`;
                html += `<div id="topProductsData" class="loading-placeholder">Loading top products...</div>`;
                
                reportContent.innerHTML = html;
                
                // Load top products by value
                loadTopProductsByValue();
            } else {
                reportContent.innerHTML = '<div class="alert alert-info">No inventory data available.</div>';
            }
        })
        .catch(error => {
            reportContent.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}

function loadTopProductsByValue() {
    const topProductsData = document.getElementById('topProductsData');
    
    API.inventory.getAll()
        .then(items => {
            if (items && items.length > 0) {
                // Calculate value for each item
                const itemsWithValue = items.map(item => {
                    return {
                        ...item,
                        value: item.current_quantity * (item.product.selling_price || 0)
                    };
                });
                
                // Sort by value descending
                itemsWithValue.sort((a, b) => b.value - a.value);
                
                // Take top 10
                const topItems = itemsWithValue.slice(0, 10);
                
                let html = `
                <div class="table-responsive">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Category</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Total Value</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                
                topItems.forEach(item => {
                    html += `
                    <tr>
                        <td>${item.product.name}</td>
                        <td>${item.product.category || '-'}</td>
                        <td>${item.current_quantity}</td>
                        <td>₹${item.product.selling_price?.toFixed(2) || '-'}</td>
                        <td>₹${item.value.toFixed(2)}</td>
                    </tr>
                    `;
                });
                
                html += `
                        </tbody>
                    </table>
                </div>
                `;
                
                topProductsData.innerHTML = html;
            } else {
                topProductsData.innerHTML = '<div class="alert alert-info">No inventory items found.</div>';
            }
        })
        .catch(error => {
            topProductsData.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}


// Global functions that need to be accessible from HTML onclick handlers
window.editProduct = function(productId) {
    handleEditProduct(productId);
};

window.updateInventoryItem = function(productId, currentQuantity) {
    handleUpdateInventoryItem(productId, currentQuantity);
};

window.showStockInModal = function(productId) {
    handleShowStockInModal(productId);
};

window.showSaleModal = function(productId) {
    handleShowSaleModal(productId);
};