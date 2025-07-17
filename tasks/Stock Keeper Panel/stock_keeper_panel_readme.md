# Stock Keeper Panel - Atlas Fulfillment

## Overview
This document outlines the requirements for implementing a dedicated Stock Keeper Panel at `/stock-keeper/` within the Atlas Fulfillment CRM platform. The panel provides warehouse staff with streamlined inventory management tools, barcode scanning capabilities, and real-time stock tracking functionalities tailored for day-to-day warehouse operations.

## System Requirements

### Stock Keeper Authentication & Access
The Stock Keeper Panel operates as a separate interface accessible at `/stock-keeper/` with role-based authentication that restricts access to warehouse operations staff.

#### Access Control:
- **Stock Keeper Role:** Primary users with full operational access
- **Warehouse Manager Role:** Enhanced access with reporting capabilities  
- **Warehouse Supervisor Role:** Limited supervisory access for oversight
- **No Admin Panel Access:** Stock keepers cannot access the main admin inventory system

## Core Functionality

### 1. Warehouse-Specific Dashboard

The Stock Keeper Panel displays a focused dashboard for the assigned warehouse(s) with real-time inventory status and daily task overview.

#### Dashboard Components:
- **Assigned Warehouse Info:** Current warehouse name, location, and shift details
- **Today's Tasks:** Pending stock movements, transfers, and adjustments
- **Quick Stats:** Current stock levels, low stock alerts, and movement counts
- **Active Alerts:** Urgent notifications for immediate attention
- **Recent Activities:** Last 10 inventory movements performed by the user

#### Dashboard Layout:
```
┌─────────────────────────────────────────────────────────────────────┐
│ STOCK KEEPER DASHBOARD - Dubai Main Warehouse                      │
│ Welcome back, Ahmed | Shift: Morning (8:00 AM - 4:00 PM)          │
├─────────────────────────────────────────────────────────────────────┤
│ TODAY'S OVERVIEW                                                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ │Pending Tasks│ │Stock Alerts │ │Completed    │ │Total Items  │    │
│ │     12      │ │      5      │ │    28       │ │   1,245     │    │
│ │   items     │ │   urgent    │ │   today     │ │  in stock   │    │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │
│                                                                     │
│ URGENT ALERTS                                                       │
│ ⚠️ Samsung TV (SAM-001) - Stock critical (2 units remaining)        │
│ ⚠️ iPhone 13 (IPH-013) - Shipment overdue by 2 days               │
│ ℹ️ MacBook Pro (MAC-001) - Transfer requested from Abu Dhabi       │
│                                                                     │
│ QUICK ACTIONS                                                       │
│ [📦 Receive Stock] [📤 Ship Orders] [🔄 Transfer] [📱 Scan Item]    │
│                                                                     │
│ PENDING TASKS (12)                              [View All Tasks]    │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │□ Receive: ORD-12345 | Samsung TV × 5 units                     │ │
│ │□ Ship: ORD-12346 | iPhone 13 × 2 units                        │ │
│ │□ Count: Physical audit - Electronics section                    │ │
│ │□ Transfer: MacBook Pro × 3 to Abu Dhabi warehouse              │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. Barcode Scanning Interface

A dedicated scanning interface optimized for mobile devices and handheld scanners used in warehouse operations.

#### Scanning Capabilities:
- **Product Lookup:** Instant product information retrieval
- **Stock Updates:** Quick quantity adjustments via scanning
- **Location Verification:** Confirm product placement and location
- **Batch Processing:** Scan multiple items for bulk operations
- **Movement Tracking:** Record stock movements with scan confirmation

#### Mobile-Optimized Scan Interface:
```
┌─────────────────────────────────────────────────────────┐
│ BARCODE SCANNER                               [⚙️ Settings] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              [📷 Camera Viewfinder]                     │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │          Align barcode within frame                 │ │
│ │                                                     │ │
│ │              ┌─────────────┐                        │ │
│ │              │             │                        │ │
│ │              │   Scanning  │                        │ │
│ │              │             │                        │ │
│ │              └─────────────┘                        │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ LAST SCANNED: SAM-TV-001                               │
│ Samsung 55" Smart TV | Qty: 5 | Location: A-12        │
│                                                         │
│ QUICK ACTIONS:                                          │
│ [📦 Add Stock] [📤 Remove Stock] [🔄 Move] [ℹ️ Details] │
│                                                         │
│ OR MANUAL ENTRY:                                        │
│ [Product Code or Tracking#________] [🔍 Search]         │
└─────────────────────────────────────────────────────────┘
```

### 3. Stock Receiving Module

Streamlined interface for processing incoming stock from suppliers, returns, and inter-warehouse transfers.

#### Receiving Process:
1. **Scan/Select Incoming Shipment:** Choose from pending deliveries
2. **Item-by-Item Verification:** Scan each product to confirm receipt
3. **Quantity Confirmation:** Verify actual vs. expected quantities
4. **Condition Assessment:** Mark any damaged or defective items
5. **Location Assignment:** Assign storage locations for received items
6. **Documentation:** Generate receipt confirmation and update tracking

#### Stock Receiving Interface:
```
┌─────────────────────────────────────────────────────────┐
│ RECEIVE STOCK - Shipment #SHP-789123                   │
├─────────────────────────────────────────────────────────┤
│ From: Tech Supplier LLC | Expected: 15 items           │
│ Order Ref: ORD-12345 | Delivery Date: Today            │
│                                                         │
│ RECEIVING CHECKLIST                                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │✅ Samsung TV      │Expected: 5│Received: 5│Good✅   │ │
│ │⏳ iPhone 13       │Expected: 8│Received: -│Pending │ │
│ │❌ MacBook Pro     │Expected: 2│Received: 1│Short⚠️  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ CURRENT ITEM: iPhone 13 (IPH-013)                      │
│ [📱 Scan Next Item] OR Manual: [IPH-013____] [✓]       │
│                                                         │
│ Quantity Received: [8] Expected: 8                     │
│ Condition: ⚪ Good ⚪ Damaged ⚪ Defective               │
│ Storage Location: [A-15____] [📍 Assign]               │
│ Notes: [Item condition and remarks_____________]        │
│                                                         │
│ [⏭️ Next Item] [💾 Save Progress] [✅ Complete Receipt] │
└─────────────────────────────────────────────────────────┘
```

### 4. Stock Shipping Module

Efficient order fulfillment interface for picking, packing, and shipping customer orders.

#### Shipping Process:
1. **Order Selection:** Choose from ready-to-ship orders
2. **Pick List Generation:** Create optimized picking routes
3. **Item Picking:** Scan items to confirm picking accuracy
4. **Packing Verification:** Confirm all items packed correctly
5. **Shipping Label:** Generate and attach shipping labels
6. **Dispatch Confirmation:** Mark order as shipped and update tracking

#### Stock Shipping Interface:
```
┌─────────────────────────────────────────────────────────┐
│ SHIP ORDER - ORD-54321                                  │
├─────────────────────────────────────────────────────────┤
│ Customer: John Smith | Address: Dubai Marina           │
│ Courier: DHL Express | Priority: Next Day Delivery     │
│                                                         │
│ PICKING LIST                                            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │✅ Samsung TV      │Qty: 1│Location: A-12│Picked✅   │ │
│ │⏳ iPhone 13       │Qty: 2│Location: B-08│Picking    │ │
│ │⏸️ AirPods Pro     │Qty: 1│Location: C-03│Pending    │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ CURRENT ITEM: iPhone 13 (IPH-013)                      │
│ [📱 Scan Item] OR Manual: [IPH-013____] [✓]            │
│                                                         │
│ Pick Quantity: [2] Required: 2                         │
│ From Location: B-08 ✅ Confirmed                        │
│                                                         │
│ STATUS: Picking in Progress (2 of 4 items picked)      │
│                                                         │
│ [⏭️ Next Item] [📦 Complete Picking] [🚚 Generate Label]│
└─────────────────────────────────────────────────────────┘
```

### 5. Stock Transfer Module

Inter-warehouse transfer management for stock rebalancing and fulfillment optimization.

#### Transfer Process:
1. **Transfer Request Review:** View pending transfer requests
2. **Item Preparation:** Locate and prepare items for transfer
3. **Packaging:** Pack items securely for transport
4. **Documentation:** Generate transfer documentation
5. **Dispatch Confirmation:** Confirm items sent to destination
6. **Tracking Updates:** Update system with transfer status

#### Stock Transfer Interface:
```
┌─────────────────────────────────────────────────────────┐
│ STOCK TRANSFER - TRF-98765                              │
├─────────────────────────────────────────────────────────┤
│ From: Dubai Main → To: Abu Dhabi Branch                │
│ Requested by: Warehouse Manager | Reason: Rebalancing  │
│                                                         │
│ TRANSFER ITEMS                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │✅ MacBook Pro     │Qty: 3│From: A-05│Prepared✅     │ │
│ │⏳ iPad Air        │Qty: 5│From: B-12│Preparing      │ │
│ │⏸️ Apple Watch     │Qty: 2│From: C-01│Pending        │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ CURRENT ITEM: iPad Air (IPA-001)                       │
│ [📱 Scan Item] OR Manual: [IPA-001____] [✓]            │
│                                                         │
│ Transfer Quantity: [5] Available: 8                    │
│ Current Location: B-12 ✅ Verified                     │
│ Packaging: [Box Type____] [Protective Material____]    │
│                                                         │
│ [⏭️ Next Item] [📦 Complete Prep] [🚚 Dispatch Transfer]│
└─────────────────────────────────────────────────────────┘
```

### 6. Stock Adjustment & Cycle Counting

Tools for maintaining inventory accuracy through regular counts and adjustments.

#### Adjustment Features:
- **Cycle Counting:** Scheduled partial inventory counts
- **Spot Checks:** Random inventory verification
- **Discrepancy Resolution:** Handle count differences
- **Damage Recording:** Document damaged or defective items
- **Loss Reporting:** Report missing or stolen inventory

#### Cycle Count Interface:
```
┌─────────────────────────────────────────────────────────┐
│ CYCLE COUNT - Electronics Section A                     │
├─────────────────────────────────────────────────────────┤
│ Assigned: Ahmed K. | Started: 10:30 AM | Due: 12:00 PM │
│ Progress: 12 of 25 items counted (48% complete)         │
│                                                         │
│ CURRENT ITEM: Location A-15                            │
│ System Record: Samsung TV (SAM-001) | Expected: 5      │
│                                                         │
│ [📱 Scan Item] OR Manual: [SAM-001____] [✓]            │
│                                                         │
│ Physical Count: [____] Enter actual quantity found     │
│ Condition: ⚪ Good ⚪ Damaged ⚪ Missing                  │
│                                                         │
│ DISCREPANCIES FOUND:                                    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │iPhone 13 (IPH-013) | Expected: 12 | Found: 10 ❌   │ │
│ │Reason: [Damaged units removed_____________]         │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ [⏭️ Next Location] [💾 Save Count] [⚠️ Report Issue]    │
└─────────────────────────────────────────────────────────┘
```

### 7. Task Management System

Centralized task assignment and tracking system for warehouse operations.

#### Task Types:
- **Receiving Tasks:** Process incoming shipments
- **Shipping Tasks:** Fulfill customer orders  
- **Transfer Tasks:** Inter-warehouse movements
- **Count Tasks:** Inventory verification assignments
- **Maintenance Tasks:** Equipment and location upkeep
- **Special Tasks:** Custom assignments from management

#### Task Management Interface:
```
┌─────────────────────────────────────────────────────────┐
│ MY TASKS - Ahmed Khalil                                 │
├─────────────────────────────────────────────────────────┤
│ Filter: [All▼] [High Priority] [Due Today] [Overdue]   │
│                                                         │
│ HIGH PRIORITY TASKS (3)                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │🔴 URGENT | Ship ORD-12345 | Due: 2:00 PM | 30 min  │ │
│ │🟡 Process Return RET-789 | Due: 4:00 PM | 3 hours  │ │
│ │🟡 Count Section B | Due: Tomorrow | 1 day           │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ TODAY'S TASKS (8)                                       │
│ ┌─────────────────────────────────────────────────────┐ │
│ │✅ Receive SHP-123 | Completed: 9:30 AM             │ │
│ │⏳ Transfer TRF-456 | In Progress | 45% done         │ │
│ │⏸️ Ship ORD-12346 | Pending | Start time: 1:00 PM   │ │
│ │⏸️ Count Location A-20 | Scheduled: 3:00 PM         │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ COMPLETED TODAY: 5 tasks | PENDING: 3 tasks            │
│ [📋 Task Details] [▶️ Start Task] [✅ Mark Complete]     │
└─────────────────────────────────────────────────────────┘
```

## Database Schema Integration

### Stock Keeper Specific Tables

#### Stock Keeper Sessions
```sql
CREATE TABLE stock_keeper_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    shift_start TIMESTAMP,
    shift_end TIMESTAMP,
    tasks_completed INT DEFAULT 0,
    items_processed INT DEFAULT 0,
    scan_count INT DEFAULT 0,
    session_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    INDEX idx_user_session (user_id, shift_start)
);
```

#### Task Assignments
```sql
CREATE TABLE stock_keeper_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_type ENUM('receive', 'ship', 'transfer', 'count', 'adjustment', 'maintenance') NOT NULL,
    assigned_to INT NOT NULL,
    warehouse_id INT NOT NULL,
    priority ENUM('low', 'normal', 'high', 'urgent') DEFAULT 'normal',
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reference_id INT, -- Links to orders, transfers, etc.
    due_date TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration INT, -- in minutes
    actual_duration INT, -- in minutes
    completion_notes TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_assigned_tasks (assigned_to, status, due_date),
    INDEX idx_warehouse_tasks (warehouse_id, task_type)
);
```

#### Barcode Scan History
```sql
CREATE TABLE barcode_scan_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    scan_type ENUM('product_lookup', 'stock_update', 'receive', 'ship', 'transfer', 'count') NOT NULL,
    barcode_data VARCHAR(255) NOT NULL,
    product_id INT,
    task_id INT,
    scan_result ENUM('success', 'not_found', 'error') NOT NULL,
    quantity_change INT DEFAULT 0,
    location_code VARCHAR(50),
    notes TEXT,
    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (task_id) REFERENCES stock_keeper_tasks(id),
    INDEX idx_user_scans (user_id, scan_timestamp),
    INDEX idx_barcode_lookup (barcode_data)
);
```

#### Physical Count Records
```sql
CREATE TABLE physical_count_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    count_session_id VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    location_code VARCHAR(50),
    system_quantity INT NOT NULL,
    counted_quantity INT NOT NULL,
    variance INT GENERATED ALWAYS AS (counted_quantity - system_quantity) STORED,
    condition_status ENUM('good', 'damaged', 'defective', 'missing') DEFAULT 'good',
    count_notes TEXT,
    count_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_by INT,
    verification_timestamp TIMESTAMP,
    adjustment_applied BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (verified_by) REFERENCES users(id),
    INDEX idx_count_session (count_session_id),
    INDEX idx_variance_review (warehouse_id, variance, adjustment_applied)
);
```

## API Endpoints for Stock Keeper Panel

### Authentication & Session Management
```javascript
// Stock keeper login
POST /api/stock-keeper/auth/login
{
  "username": "ahmed.khalil",
  "password": "secure_password",
  "warehouse_id": 1
}
Response: {
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": 123,
    "name": "Ahmed Khalil",
    "role": "stock_keeper",
    "assigned_warehouse": {
      "id": 1,
      "name": "Dubai Main",
      "code": "DXB"
    }
  },
  "shift_info": {
    "shift_start": "2024-01-15T08:00:00Z",
    "shift_end": "2024-01-15T16:00:00Z"
  }
}

// Start shift session
POST /api/stock-keeper/session/start
{
  "warehouse_id": 1,
  "shift_notes": "Regular morning shift"
}

// End shift session
POST /api/stock-keeper/session/end
{
  "session_id": "session_uuid",
  "end_notes": "Completed all assigned tasks"
}
```

### Dashboard & Overview
```javascript
// Get stock keeper dashboard data
GET /api/stock-keeper/dashboard/{warehouse_id}
Response: {
  "overview": {
    "pending_tasks": 12,
    "stock_alerts": 5,
    "completed_today": 28,
    "total_inventory": 1245
  },
  "urgent_alerts": [
    {
      "type": "low_stock",
      "product": "Samsung TV",
      "current_stock": 2,
      "minimum_threshold": 5
    }
  ],
  "pending_tasks": [
    {
      "id": 1,
      "type": "receive",
      "title": "Receive Shipment SHP-123",
      "priority": "high",
      "due_date": "2024-01-15T14:00:00Z"
    }
  ],
  "recent_activities": []
}

// Get assigned tasks
GET /api/stock-keeper/tasks?status=pending&priority=high
```

### Barcode Scanning Operations
```javascript
// Process barcode scan
POST /api/stock-keeper/scan
{
  "barcode_data": "SAM-TV-001",
  "scan_type": "product_lookup",
  "warehouse_id": 1,
  "task_id": 123
}
Response: {
  "success": true,
  "product": {
    "id": 456,
    "name": "Samsung 55\" Smart TV",
    "code": "SAM-TV-001",
    "current_stock": 5,
    "location": "A-12",
    "tracking_number": "TRK-DXB-123456-A4"
  },
  "available_actions": ["add_stock", "remove_stock", "move_location", "view_details"]
}

// Bulk barcode processing
POST /api/stock-keeper/scan/batch
{
  "scans": [
    {"barcode": "SAM-TV-001", "action": "receive", "quantity": 2},
    {"barcode": "IPH-013", "action": "receive", "quantity": 5}
  ],
  "task_id": 123,
  "warehouse_id": 1
}
```

### Stock Receiving Operations
```javascript
// Get pending shipments
GET /api/stock-keeper/shipments/pending?warehouse_id=1
Response: {
  "shipments": [
    {
      "id": "SHP-789123",
      "supplier": "Tech Supplier LLC",
      "expected_items": 15,
      "expected_date": "2024-01-15",
      "status": "in_transit",
      "items": [
        {
          "product_id": 456,
          "product_name": "Samsung TV",
          "expected_quantity": 5,
          "received_quantity": 0
        }
      ]
    }
  ]
}

// Process item receipt
POST /api/stock-keeper/receive/item
{
  "shipment_id": "SHP-789123",
  "product_id": 456,
  "received_quantity": 5,
  "condition": "good",
  "location": "A-15",
  "notes": "All items in perfect condition"
}

// Complete shipment receipt
POST /api/stock-keeper/receive/complete
{
  "shipment_id": "SHP-789123",
  "completion_notes": "All items received and processed"
}
```

### Stock Shipping Operations
```javascript
// Get ready-to-ship orders
GET /api/stock-keeper/orders/ready-to-ship?warehouse_id=1
Response: {
  "orders": [
    {
      "id": "ORD-54321",
      "customer": "John Smith",
      "priority": "next_day",
      "courier": "DHL Express",
      "items": [
        {
          "product_id": 456,
          "product_name": "Samsung TV",
          "quantity": 1,
          "location": "A-12"
        }
      ]
    }
  ]
}

// Process order picking
POST /api/stock-keeper/pick/item
{
  "order_id": "ORD-54321",
  "product_id": 456,
  "picked_quantity": 1,
  "location_confirmed": "A-12",
  "condition": "good"
}

// Complete order fulfillment
POST /api/stock-keeper/ship/complete
{
  "order_id": "ORD-54321",
  "packed_by": "Ahmed Khalil",
  "packaging_notes": "Securely packed with bubble wrap",
  "shipping_label_generated": true
}
```

### Stock Transfer Operations
```javascript
// Get pending transfers
GET /api/stock-keeper/transfers/pending?warehouse_id=1
{
  "outbound_transfers": [
    {
      "id": "TRF-98765",
      "destination_warehouse": "Abu Dhabi Branch",
      "status": "preparing",
      "items": [
        {
          "product_id": 789,
          "product_name": "MacBook Pro",
          "quantity": 3,
          "current_location": "A-05"
        }
      ]
    }
  ],
  "inbound_transfers": []
}

// Process transfer preparation
POST /api/stock-keeper/transfer/prepare
{
  "transfer_id": "TRF-98765",
  "product_id": 789,
  "prepared_quantity": 3,
  "packaging_type": "Original boxes",
  "condition_verified": true
}

// Dispatch transfer
POST /api/stock-keeper/transfer/dispatch
{
  "transfer_id": "TRF-98765",
  "dispatch_notes": "Items securely packed and ready for transport",
  "transport_method": "Company vehicle"
}
```

### Cycle Counting & Adjustments
```javascript
// Get assigned count tasks
GET /api/stock-keeper/counts/assigned?user_id=123
Response: {
  "count_sessions": [
    {
      "session_id": "COUNT-20240115-001",
      "section": "Electronics Section A",
      "total_locations": 25,
      "completed_locations": 12,
      "due_date": "2024-01-15T12:00:00Z"
    }
  ]
}

// Record count for location
POST /api/stock-keeper/count/record
{
  "session_id": "COUNT-20240115-001",
  "product_id": 456,
  "location_code": "A-15",
  "system_quantity": 5,
  "counted_quantity": 4,
  "condition": "good",
  "notes": "One unit missing from shelf"
}

// Submit count discrepancies
POST /api/stock-keeper/count/submit-variance
{
  "session_id": "COUNT-20240115-001",
  "variances": [
    {
      "product_id": 456,
      "variance": -1,
      "reason": "Item not found on designated shelf"
    }
  ]
}
```

### Task Management
```javascript
// Update task status
PUT /api/stock-keeper/tasks/{task_id}/status
{
  "status": "in_progress",
  "notes": "Started processing shipment"
}

// Complete task
POST /api/stock-keeper/tasks/{task_id}/complete
{
  "completion_notes": "All items processed successfully",
  "actual_duration": 45,
  "items_processed": 15
}

// Request task assistance
POST /api/stock-keeper/tasks/{task_id}/request-help
{
  "issue_type": "equipment_malfunction",
  "description": "Barcode scanner not working properly"
}
```

## Mobile Optimization

### Responsive Design
The Stock Keeper Panel is optimized for mobile devices and tablets commonly used in warehouse environments:

- **Touch-Friendly Interface:** Large buttons and touch targets
- **Barcode Scanner Integration:** Camera-based scanning capabilities
- **Offline Functionality:** Essential features work without internet connection
- **Voice Commands:** Hands-free operation for specific tasks
- **Dark Mode:** Reduced eye strain in warehouse lighting conditions

### PWA Features
- **Installable App:** Can be installed on mobile devices as a native app
- **Push Notifications:** Real-time alerts for urgent tasks and updates
- **Background Sync:** Sync data when connection is restored
- **Offline Storage:** Cache critical data for offline access

## Hardware Integration

### Barcode Scanner Support
- **USB Handheld Scanners:** Zebra, Honeywell, and other industrial scanners
- **Bluetooth Scanners:** Wireless scanning capability
- **Ring Scanners:** Hands-free scanning for continuous operations
- **Mobile Device Cameras:** Backup scanning method

### Printer Integration
- **Label Printers:** For shipping labels and location tags
- **Receipt Printers:** For transaction confirmations
- **Mobile Printers:** Portable printing solutions

### Warehouse Hardware
- **Rugged Tablets:** Industrial-grade devices for harsh environments
- **Smartphone Mounts:** Hands-free device positioning
- **Charging Stations:** Device power management throughout shifts

## Reporting & Analytics

### Performance Metrics
- **Task Completion Rates:** Track individual and team productivity
- **Accuracy Metrics:** Monitor