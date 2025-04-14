/**
 * Main Application JavaScript for Kiryana Inventory System
 */

// DOM elements and initialization
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
    
    // Store and API key changes
    const storeSelector = document.getElementById('storeSelector');
    storeSelector.addEventListener('change', function() {
        // Save selected store to localStorage
        localStorage.setItem('selectedStoreId', this.value);
        refreshCurrentPage();
    });
    
    const apiKeyInput = document.getElementById('apiKeyInput');
    apiKeyInput.addEventListener('change', function() {
        // Save API key to localStorage
        localStorage.setItem('apiKey', this.value);
        refreshCurrentPage();
    });
    
    // Load saved values from localStorage
    const savedStoreId = localStorage.getItem('selectedStoreId');
    if (savedStoreId) {
        storeSelector.value = savedStoreId;
    }
    
    const savedApiKey = localStorage.getItem('apiKey');
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    } else {
        // Set default API key if none is saved
        apiKeyInput.value = 'store1_api_key';
        localStorage.setItem('apiKey', 'store1_api_key');
    }
    
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