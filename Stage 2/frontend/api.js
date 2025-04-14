/**
 * API Client for Kiryana Inventory System
 */

const API = {
    baseUrl: 'http://localhost:8000',
    
    // Get API key from input field
    getApiKey() {
        return document.getElementById('apiKeyInput').value;
    },
    
    // Get selected store ID
    getStoreId() {
        return Number(document.getElementById('storeSelector').value);
    },
    
    // Helper method for API requests
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            'X-API-Key': this.getApiKey()
        };
        
        const requestOptions = {
            headers,
            credentials: 'include',  // Add this line
            ...options
        };

        
        try {
            const response = await fetch(url, requestOptions);
            
                    // Handle 401 Unauthorized
        if (response.status === 401) {
            localStorage.removeItem('apiKey');
            // window.location.reload();
            throw new Error('Session expired. Please reload the page.');
        }


            // Handle rate limiting
            if (response.status === 429) {
                const resetTime = response.headers.get('X-RateLimit-Reset');
                throw new Error(`Rate limit exceeded. Try again in ${resetTime} seconds.`);
            }
            
            // Handle authentication errors
            if (response.status === 401) {
                throw new Error('Invalid API key. Please check your credentials.');
            }
            
            // Handle other errors
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'An error occurred');
            }
            
            // Parse JSON response
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // Products API
    products: {
        getAll(params = {}) {
            console.log("Store ID:", API.getStoreId(), "Type:", typeof API.getStoreId());

            const queryParams = new URLSearchParams(params).toString();
            return API.request(`/products/?${queryParams}`);
        },
        
        getById(id) {
            console.log("Store ID:", API.getStoreId(), "Type:", typeof API.getStoreId());

            return API.request(`/products/${id}`);
        },
        
        create(productData) {
            console.log("Store ID:", API.getStoreId(), "Type:", typeof API.getStoreId());

            return API.request('/products/', {
                method: 'POST',
                body: JSON.stringify(productData)
            });
        },
        
        update(id, productData) {
            return API.request(`/products/${id}`, {
                method: 'PUT',
                body: JSON.stringify(productData)
            });
        }
    },
    
    // Stores API
    stores: {
        getAll() {
            return API.request('/stores/');
        },
        
        getById(id) {
            return API.request(`/stores/${id}`);
        },
        
        create(storeData) {
            return API.request('/stores/', {
                method: 'POST',
                body: JSON.stringify(storeData)
            });
        }
    },
    
    // Inventory API
    inventory: {
        getAll(params = {}) {
            // Default to current store
            if (!params.store_id) {
                params.store_id = API.getStoreId();
            }
            
            const queryParams = new URLSearchParams(params).toString();
            return API.request(`/inventory/?${queryParams}`);
        },
        
        getLowStock(threshold = 5) {
            return API.request(`/inventory/?store_id=${API.getStoreId()}&low_stock=true&threshold=${threshold}`);
        },
        
        updateQuantity(productId, quantity) {
            return API.request('/inventory/', {
                method: 'POST',
                body: JSON.stringify({
                    store_id: Number(API.getStoreId()),
                    product_id: Number(productId),
                    current_quantity: Number(quantity)
                })
            });
        }
        
    },
    
    // Stock Movements API
    movements: {
        getAll(params = {}) {
            // Default to current store
            if (!params.store_id) {
                params.store_id = API.getStoreId();
            }
            
            const queryParams = new URLSearchParams(params).toString();
            return API.request(`/movements/?${queryParams}`);
        },
        
        create(movementData) {
            // Ensure store_id is set and is a number
            if (!movementData.store_id) {
                movementData.store_id = Number(API.getStoreId());
            }
            
            // Ensure all numeric fields are numbers
            if (typeof movementData.store_id === 'string') {
                movementData.store_id = Number(movementData.store_id);
            }
            if (typeof movementData.product_id === 'string') {
                movementData.product_id = Number(movementData.product_id);
            }
            if (typeof movementData.quantity === 'string') {
                movementData.quantity = Number(movementData.quantity);
            }
            if (movementData.unit_price && typeof movementData.unit_price === 'string') {
                movementData.unit_price = Number(movementData.unit_price);
            }
            
            return API.request('/movements/', {
                method: 'POST',
                body: JSON.stringify(movementData)
            });
        },
        
        
        
        // Convenience methods for different movement types
        stockIn(productId, quantity, unitPrice, notes = '') {
            return this.create({
                product_id: Number(productId),
                movement_type: 'stock_in',
                quantity: Number(quantity),
                unit_price: unitPrice ? Number(unitPrice) : null,
                notes
            });
        },
        
        recordSale(productId, quantity, unitPrice, notes = '') {
            return this.create({
                product_id: Number(productId),
                movement_type: 'sale',
                quantity: Number(quantity),
                unit_price: unitPrice ? Number(unitPrice) : null,
                notes
            });
        },
        
        makeAdjustment(productId, quantity, notes = '') {
            return this.create({
                product_id: Number(productId),
                movement_type: 'adjustment',
                quantity: Number(quantity),
                unit_price: null,
                notes
            });
        }
    },
    
    // Reports API
    reports: {
        getInventorySummary(storeId = null) {
            const id = storeId || API.getStoreId();
            return API.request(`/reports/inventory-summary?store_id=${id}`);
        },
        
        getDailySales(params = {}) {
            // Default to current store
            if (!params.store_id) {
                params.store_id = API.getStoreId();
            }
            
            const queryParams = new URLSearchParams(params).toString();
            return API.request(`/reports/daily-sales?${queryParams}`);
        }
    }
};