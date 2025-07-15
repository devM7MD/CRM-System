# Inventory Management System - Atlas Fulfillment

## Overview
This document outlines the requirements for implementing a comprehensive Inventory Management System at `/inventory/` within the Atlas Fulfillment CRM platform. The system will provide warehouse-specific inventory tracking, product management, and real-time stock monitoring capabilities.

## System Requirements

### Sidebar Navigation Update
A new "Inventory" page should be added to the main sidebar navigation menu with the URL `/inventory/`. This page will allow administrators to manage and track products within the various warehouses.

## Core Functionality

### 1. Warehouse-Specific Inventory Tables

The "Inventory" page will display a separate table for *each existing warehouse* (as defined in the "Warehouse" section). Each table will list the products currently held in that specific warehouse's inventory.

#### Table Columns for Each Warehouse:
- **Product Name:** The name of the product
- **Product Image:** A thumbnail or preview of the product image
- **Product Code:** The unique identifier for the product (e.g., SKU)
- **Quantity:** The current stock quantity of the product within that specific warehouse
- **Tracking Number:** Auto-generated unique identifier for inventory tracking
- **Actions:** A column containing options to:
  - **Edit:** Button to edit quantity or other details of the product entry
  - **Delete:** Button to remove the product entry from warehouse inventory

### 2. Adding Products to Inventory (Warehouse Specific)

#### Process Flow:
1. Each warehouse inventory table includes an "Add Product" button
2. Clicking the button displays:
   - List of existing **orders** from the main order system
   - Filtering options by seller (if relevant to warehouse setup)
3. Administrator selects specific orders from the list
4. "Add to Stock" button becomes available
5. Selected order products are added to the specific warehouse inventory

#### Interface Design:
```
┌─────────────────────────────────────────────────────────┐
│ ADD PRODUCTS TO WAREHOUSE: Dubai Main                   │
├─────────────────────────────────────────────────────────┤
│ Available Orders:                                       │
│ Filters: [Seller▼] [Date Range] [Status▼] [Search]     │
│                                                         │
│ ☑ Select All  Available Orders (15)                    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │☑ ORD-001 │ Samsung TV    │ Seller A │ 2 units     │ │
│ │☑ ORD-002 │ iPhone 13     │ Seller B │ 5 units     │ │
│ │☐ ORD-003 │ MacBook Pro   │ Seller A │ 1 unit      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Selected: 2 orders (7 total units)                     │
│ Notes: [Received from supplier shipment]               │
│                                                         │
│ [Cancel]                           [Add to Stock]      │
└─────────────────────────────────────────────────────────┘
```

### 3. Dynamic Inventory Updates

The system automatically updates stock levels based on actions from other departments:

#### Automatic Stock Adjustments:
- **Deliveries:** Products marked as delivered or shipped reduce stock quantities
- **Returns:** Returned products increase stock quantities
- **Internal Transfers:** Products moved between warehouses update both locations
- **Damaged Goods:** Quality control issues adjust inventory counts
- **Manual Adjustments:** Administrative corrections with audit trail

#### Real-time Synchronization:
- WebSocket integration for live inventory updates
- Cross-department notifications for stock changes
- Audit logging for all inventory movements

### 4. Order Tracking and Location Search

#### Search Functionality:
- Prominent search bar on the main inventory page
- Search capabilities:
  - **Order ID lookup:** Find current warehouse location
  - **Product Code search:** Locate products across all warehouses
  - **Tracking Number search:** Find specific inventory items
  - **Barcode scanning:** Hardware scanner integration

#### Search Interface:
```
┌─────────────────────────────────────────────────────────┐
│ INVENTORY SEARCH                                        │
├─────────────────────────────────────────────────────────┤
│ Search: [Order ID, Product Code, or Tracking#] [🔍]     │
│ Or: [Scan Barcode] 📷                                   │
│                                                         │
│ Search Results for: "ORD-12345"                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Found in: Dubai Main Warehouse                      │ │
│ │ Product: Samsung 55" Smart TV                       │ │
│ │ Code: SAM-TV-001                                    │ │
│ │ Quantity: 3 units                                   │ │
│ │ Tracking: TRK-789123                                │ │
│ │ Status: In Stock                                    │ │
│ │ [View Details] [Edit] [Move to Another Warehouse]  │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 5. Automatic Tracking Number Generation

#### Tracking System:
- Unique tracking numbers generated when orders are added to inventory
- Format: `TRK-{WAREHOUSE_CODE}-{SEQUENTIAL_NUMBER}-{CHECKSUM}`
- Example: `TRK-DXB-123456-A4`
- Visible in all inventory views and searchable
- Links to complete product history and movement logs

#### Tracking Number Features:
- **Sequential numbering** per warehouse
- **Checksum validation** for data integrity
- **QR code generation** for mobile scanning
- **Integration with barcode system** for hardware scanners

### 6. Barcode Scanning Integration

#### Hardware Scanner Support:
- USB-connected barcode scanners
- Bluetooth scanner connectivity
- Mobile device camera scanning
- Network-attached scanner devices

#### Scanning Capabilities:
- **Product Identification:** Quick retrieval of product details
- **Inventory Updates:** Efficient stock quantity modifications
- **Location Verification:** Confirm product warehouse location
- **Batch Operations:** Scan multiple items for bulk updates

#### Scanner Configuration:
```javascript
// Barcode scanner integration
window.addEventListener('inventoryBarcodeScan', function(event) {
  const scannedData = event.detail.barcode;
  const scannerLocation = event.detail.warehouse_id;
  processInventoryBarcode(scannedData, scannerLocation);
});

function processInventoryBarcode(barcode, warehouse_id) {
  // Look up product in current warehouse
  // Display product information
  // Enable quick actions (add stock, update quantity, move)
}
```

## Database Schema

### Core Tables

#### Warehouse Inventory Table
```sql
CREATE TABLE warehouse_inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_code VARCHAR(100) NOT NULL,
    product_image TEXT,
    quantity INT NOT NULL DEFAULT 0,
    tracking_number VARCHAR(50) UNIQUE,
    added_from_order_id INT,
    last_movement_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (added_from_order_id) REFERENCES orders(id),
    UNIQUE KEY unique_product_warehouse (warehouse_id, product_id),
    INDEX idx_tracking_number (tracking_number),
    INDEX idx_product_code (product_code)
);
```

#### Inventory Movement History
```sql
CREATE TABLE inventory_movements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    movement_type ENUM('in', 'out', 'transfer', 'adjustment', 'return', 'damage') NOT NULL,
    quantity_change INT NOT NULL,
    previous_quantity INT NOT NULL,
    new_quantity INT NOT NULL,
    reason VARCHAR(255),
    reference_order_id INT,
    destination_warehouse_id INT,
    created_by INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (destination_warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (reference_order_id) REFERENCES orders(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_product_movement (product_id, created_at),
    INDEX idx_warehouse_movement (warehouse_id, created_at)
);
```

#### Tracking Numbers Registry
```sql
CREATE TABLE tracking_numbers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tracking_number VARCHAR(50) UNIQUE NOT NULL,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT,
    qr_code TEXT,
    barcode_data TEXT,
    status ENUM('active', 'shipped', 'delivered', 'returned') DEFAULT 'active',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_tracking_lookup (tracking_number)
);
```

## API Endpoints

### Inventory Management APIs

#### Get Warehouse Inventory
```javascript
// Get all inventory for specific warehouse
GET /api/inventory/warehouse/{warehouse_id}
Response: {
  "warehouse": {
    "id": 1,
    "name": "Dubai Main",
    "code": "DXB"
  },
  "inventory": [
    {
      "id": 1,
      "product_name": "Samsung TV",
      "product_code": "SAM-001",
      "quantity": 5,
      "tracking_number": "TRK-DXB-123456-A4",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ],
  "total_items": 1,
  "total_quantity": 5
}

// Get inventory across all warehouses
GET /api/inventory/all
```

#### Add Products from Orders
```javascript
// Add products from specific orders to warehouse
POST /api/inventory/warehouse/{warehouse_id}/add-from-orders
{
  "order_ids": [1, 2, 3, 4],
  "notes": "Stock received from supplier",
  "received_by": "admin_user_id"
}
Response: {
  "success": true,
  "added_products": 12,
  "tracking_numbers": ["TRK-DXB-123457-B2", "TRK-DXB-123458-C1"],
  "message": "Successfully added 12 items to Dubai Main warehouse"
}
```

#### Update Inventory Quantities
```javascript
// Update product quantity in warehouse
PUT /api/inventory/warehouse/{warehouse_id}/product/{product_id}
{
  "quantity": 50,
  "movement_type": "adjustment",
  "reason": "Physical count correction",
  "notes": "Annual audit adjustment"
}

// Bulk quantity update
PUT /api/inventory/warehouse/{warehouse_id}/bulk-update
{
  "updates": [
    {"product_id": 1, "quantity": 25, "reason": "Recount"},
    {"product_id": 2, "quantity": 15, "reason": "Damaged items removed"}
  ]
}
```

#### Search and Tracking
```javascript
// Search for order location across all warehouses
GET /api/inventory/search/order/{order_id}
Response: {
  "order_id": "ORD-12345",
  "found": true,
  "locations": [
    {
      "warehouse_id": 1,
      "warehouse_name": "Dubai Main",
      "products": [
        {
          "product_name": "Samsung TV",
          "quantity": 2,
          "tracking_number": "TRK-DXB-123456-A4"
        }
      ]
    }
  ]
}

// Search by tracking number
GET /api/inventory/search/tracking/{tracking_number}

// Search by product code
GET /api/inventory/search/product/{product_code}

// General search endpoint
GET /api/inventory/search?q={search_term}&type={order|product|tracking}
```

#### Tracking Number Management
```javascript
// Generate tracking number for inventory item
POST /api/inventory/tracking/generate
{
  "warehouse_id": 1,
  "product_id": 123,
  "order_id": 456
}
Response: {
  "tracking_number": "TRK-DXB-123459-D3",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "barcode_data": "123459"
}

// Get tracking history
GET /api/inventory/tracking/{tracking_number}/history
```

#### Inventory Movements
```javascript
// Record inventory movement
POST /api/inventory/movement
{
  "warehouse_id": 1,
  "product_id": 123,
  "movement_type": "out",
  "quantity": 2,
  "reason": "Order shipped",
  "reference_order_id": 789,
  "notes": "Shipped via courier ABC"
}

// Transfer between warehouses
POST /api/inventory/transfer
{
  "from_warehouse_id": 1,
  "to_warehouse_id": 2,
  "product_id": 123,
  "quantity": 5,
  "reason": "Stock rebalancing",
  "notes": "Moving excess inventory"
}

// Get movement history
GET /api/inventory/movements?warehouse_id={id}&date_from={date}&date_to={date}
```

#### Barcode Integration
```javascript
// Process scanned barcode
POST /api/inventory/barcode/scan
{
  "barcode_data": "scanned_barcode_string",
  "warehouse_id": 1,
  "scanner_id": "device_001",
  "action": "lookup" | "add_stock" | "update_quantity"
}

// Generate barcode for product
POST /api/inventory/barcode/generate
{
  "product_id": 123,
  "format": "CODE128" | "QR" | "CODE39"
}
```

## User Interface Layout

### Main Inventory Page Layout
```
┌─────────────────────────────────────────────────────────────────────┐
│ INVENTORY MANAGEMENT                                                │
├─────────────────────────────────────────────────────────────────────┤
│ Search: [Order ID, Product Code, Tracking#] [🔍] [📷 Scan]         │
│                                                                     │
│ OVERVIEW CARDS                                                      │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ │Total Products│ │Low Stock    │ │Movements    │ │Warehouses   │    │
│ │    1,245     │ │     23      │ │Today: 45    │ │      4      │    │
│ │    items     │ │   alerts    │ │   actions   │ │   active    │    │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │
│                                                                     │
│ WAREHOUSE: Dubai Main (ID: 1)                        [Add Product]  │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │Image│Product Name  │Code    │Qty│Tracking#    │Actions        │ │
│ │[📦] │Samsung TV    │SAM-001 │ 5 │TRK-12345   │[Edit][Delete] │ │
│ │[📱] │iPhone 13     │IPH-013 │12 │TRK-12346   │[Edit][Delete] │ │
│ │[💻] │MacBook Pro   │MAC-001 │ 0 │-           │[Edit][Delete] │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ Showing 3 of 25 items                              [View All][▼▲]  │
│                                                                     │
│ WAREHOUSE: Abu Dhabi Branch (ID: 2)                  [Add Product]  │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │Image│Product Name  │Code    │Qty│Tracking#    │Actions        │ │
│ │[🎧] │AirPods Pro   │AIR-001 │25 │TRK-12347   │[Edit][Delete] │ │
│ │[⌚] │Apple Watch   │APW-001 │ 8 │TRK-12348   │[Edit][Delete] │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ Showing 2 of 18 items                              [View All][▼▲]  │
│                                                                     │
│ RECENT INVENTORY MOVEMENTS                          [View All]      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │Time     │Warehouse │Product   │Type│Qty│Reason        │By      │ │
│ │10:30 AM │Dubai     │Samsung TV│Out │ 2 │Order shipped │Admin   │ │
│ │09:15 AM │Abu Dhabi │AirPods   │In  │ 5 │Return        │Agent   │ │
│ │08:45 AM │Dubai     │MacBook   │Transfer│ 3 │Rebalance │Manager │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Role-Based Access Control

### Admin Role
- Full access to all inventory functions
- Warehouse management and configuration
- System settings and barcode scanner setup
- Advanced reporting and analytics
- User permission management

### Warehouse Manager Role
- Manage inventory for assigned warehouses
- Add/remove products from inventory
- Process stock movements and transfers
- Generate reports for their warehouses
- Configure warehouse-specific settings

### Stock Keeper Role
- Update product quantities
- Process incoming and outgoing stock
- Use barcode scanning interface
- Record inventory movements
- Basic reporting access

### Call Center Agent Role (Limited)
- Search inventory for customer inquiries
- View product availability across warehouses
- Read-only access to stock levels
- Cannot modify inventory quantities

## Integration Requirements

### CRM Platform Integration
- Seamless navigation from main CRM sidebar
- Single sign-on (SSO) authentication
- Shared user management system
- Consistent UI/UX design language

### Order Management Integration
- Real-time synchronization with order status
- Automatic inventory adjustments on order completion
- Link between orders and inventory additions
- Delivery status impact on stock levels

### Warehouse System Integration
- Dynamic warehouse list from existing warehouse module
- Warehouse-specific inventory segregation
- Location-based access controls
- Inter-warehouse transfer capabilities

### Delivery System Integration
- Stock reduction on delivery confirmation
- Return processing and stock restoration
- Courier pickup confirmation updates
- Failed delivery stock restoration