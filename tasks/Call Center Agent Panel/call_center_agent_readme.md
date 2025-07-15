# Call Center Agent Panel System - Customer Service Portal

## Overview
This document outlines the requirements and specifications for the Call Center Agent Panel - a dedicated web application for call center agents to manage customer interactions, track call performance, and handle day-to-day customer service operations. This system integrates with the main CRM system and provides a streamlined interface optimized for customer service personnel.

## System Purpose
The Call Center Agent Panel serves as the agent-facing interface that allows call center agents to:
- Access assigned customer orders and inquiries in real-time
- Update order statuses throughout the customer service process
- Track customer interaction history and communication logs
- Manage customer complaints and escalations
- Monitor their performance metrics and call statistics
- Access inventory information for customer inquiries
- Handle order modifications and cancellations

## User Roles and Access Levels

### 1. Call Center Agent
**Primary Users**: Individual customer service representatives
**Access Level**: Order-specific, customer interaction-based

**Capabilities:**
- View assigned orders and customer inquiries
- Update order status in real-time
- Access customer contact information and interaction history
- View inventory levels for product availability inquiries
- Track delivery status for customer inquiries
- Handle order modifications and cancellations
- Generate customer service reports
- Access product information and external URLs

### 2. Call Center Supervisor/Team Lead
**Secondary Users**: Customer service team supervisors
**Access Level**: Team-wide access

**Capabilities:**
- Monitor team performance and call metrics
- Handle escalated customer complaints
- Reassign orders and inquiries between team members
- Access team analytics and performance reports
- Manage team schedules and availability
- Review and approve order modifications

### 3. Call Center Manager
**Management Users**: Call center management
**Access Level**: Department-wide access

**Capabilities:**
- Manage all call center agents and supervisors
- View department performance metrics
- Handle executive-level customer escalations
- Configure system settings and call handling policies
- Access comprehensive analytics and business intelligence reports
- Manage customer service SLAs and KPIs

## Database Schema for Call Center Panel

### Enhanced Tables for Customer Service Operations

#### Agent Sessions Table
```sql
CREATE TABLE agent_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT,
    login_time TIMESTAMP,
    logout_time TIMESTAMP,
    status ENUM('available', 'busy', 'break', 'offline'),
    concurrent_orders INT DEFAULT 0,
    last_activity TIMESTAMP,
    workstation_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

#### Customer Interactions Table
```sql
CREATE TABLE customer_interactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    agent_id INT,
    customer_id INT,
    interaction_type ENUM('call', 'email', 'chat', 'follow_up'),
    interaction_time TIMESTAMP,
    duration_minutes INT,
    resolution_status ENUM('resolved', 'pending', 'escalated', 'follow_up_required'),
    interaction_notes TEXT,
    customer_satisfaction TINYINT,
    follow_up_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

#### Order Status History Table
```sql
CREATE TABLE order_status_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    agent_id INT,
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    status_change_reason TEXT,
    cancellation_reason TEXT,
    change_timestamp TIMESTAMP,
    customer_notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

#### Agent Performance Metrics Table
```sql
CREATE TABLE agent_performance_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    agent_id INT,
    date DATE,
    total_orders_handled INT DEFAULT 0,
    orders_confirmed INT DEFAULT 0,
    orders_cancelled INT DEFAULT 0,
    orders_postponed INT DEFAULT 0,
    average_call_duration DECIMAL(5,2),
    customer_satisfaction_avg DECIMAL(3,2),
    resolution_rate DECIMAL(5,2),
    first_call_resolution_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

## Call Center Agent Panel Interface Design

### 1. Login and Authentication

#### Login Page (`/call-center-panel/login`)
```
┌─────────────────────────────────────────────────────────┐
│                CALL CENTER AGENT LOGIN                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│        [COMPANY LOGO]                                   │
│                                                         │
│    Agent ID:    [________________________]              │
│    Password:    [________________________]              │
│                                                         │
│    □ Remember me    [Forgot Password?]                  │
│                                                         │
│              [LOGIN TO AGENT PANEL]                     │
│                                                         │
│    ─────────────── OR ──────────────────                │
│                                                         │
│         [LOGIN WITH BADGE SCANNER]                      │
│                                                         │
│    IT Support: ext. 2200 | Help Desk: ext. 2100       │
└─────────────────────────────────────────────────────────┘
```

**Authentication Features:**
- Agent ID and password login
- Badge scanner integration for quick login
- Remember device functionality
- Password recovery via internal IT support
- Automatic session timeout for security
- Role-based access control

### 2. Dashboard Overview (`/call-center-panel/`)

#### Main Dashboard Layout
```
┌─────────────────────────────────────────────────────────┐
│ 👤 Sarah Al-Mansouri   🔔 5   📞 Available   ⚙️   🚪   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 📊 TODAY'S SUMMARY                    🕒 14:30, Nov 15 │
│ ┌─────────┬─────────┬─────────┬─────────┬─────────────┐ │
│ │ Total   │Confirmed│Postponed│Cancelled│     Calls   │ │
│ │Orders   │ Orders  │ Orders  │ Orders  │   Handled   │ │
│ │   24    │   18    │    3    │    3    │     47      │ │
│ │ 🟡      │ 🟢      │ 🟠      │ 🔴      │     📞      │ │
│ └─────────┴─────────┴─────────┴─────────┴─────────────┘ │
│                                                         │
│ 🎯 CURRENT PRIORITY ORDERS                              │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 📦 ORD-2024-001847    ⚠️ HIGH PRIORITY              │ │
│ │ 👤 Ahmed Al-Rashid    📞 +971-50-123-4567          │ │
│ │ 📍 Dubai Marina, Building 5, Apt 1203              │ │
│ │ 💰 AED 750.00        🕒 Expected: 16:00             │ │
│ │ Status: 🟠 No Response                              │ │
│ │                                                     │ │
│ │ [📞 CALL NOW] [✏️ UPDATE] [👁️ DETAILS] [📝 NOTES]  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 📋 RECENT ACTIVITY (Last 2 hours)                      │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 14:15 │ ORD-001846 │ Status → Confirmed │ Ahmed K.  │ │
│ │ 13:45 │ ORD-001845 │ Status → Cancelled │ Sara M.   │ │
│ │ 13:30 │ ORD-001844 │ Status → Postponed │ Ali H.    │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ [📋 ALL ORDERS] [📊 MY STATS] [📞 CALL LOG] [💬 MESSAGES] │
└─────────────────────────────────────────────────────────┘
```

#### Dashboard Statistics Cards

**Performance Metrics:**
- **Total Orders**: Overall count of orders assigned to the agent
- **Confirmed Orders**: Count of successfully confirmed orders
- **Postponed Orders**: Count of orders postponed by customers
- **Cancelled Orders**: Count of orders cancelled with reasons
- **Average Call Time**: Average duration of customer calls
- **Customer Satisfaction**: Average rating from customer feedback

**Quick Actions:**
- **Priority Orders**: High-priority orders requiring immediate attention
- **Pending Callbacks**: Customers requesting callbacks at specific times
- **Follow-ups**: Orders requiring follow-up communication
- **Escalations**: Issues requiring supervisor intervention

### 3. Orders Management Page (`/call-center-panel/orders`)

#### Orders List Interface
```
┌─────────────────────────────────────────────────────────┐
│ ORDERS MANAGEMENT                         🔄 Auto-refresh│
├─────────────────────────────────────────────────────────┤
│ Filter: [All ▼] [Today ▼] [Priority ▼] 🔍 Search Order  │
│                                                         │
│ 🔴 HIGH PRIORITY ORDERS (3)                            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 📦 ORD-001847 │ 👤 Ahmed Al-Rashid │ 📞 050-123-4567│ │
│ │ 🛍️ Samsung Galaxy S24 │ 📍 Dubai Marina            │ │
│ │ 💰 AED 750.00 │ Status: 🟠 No Response │ ⏰ 2h ago   │ │
│ │ [📞 CALL] [✏️ UPDATE] [👁️ DETAILS] [📝 ADD NOTE]    │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ 📦 ORD-001848 │ 👤 Fatima Hassan │ 📞 052-987-6543  │ │
│ │ 🛍️ iPhone 15 Pro │ 📍 Sharjah Al Nahda            │ │
│ │ 💰 AED 1,200.00 │ Status: ⏰ Postponed │ 📅 Tomorrow │ │
│ │ [📞 CALL] [✏️ UPDATE] [👁️ DETAILS] [📝 ADD NOTE]    │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 📋 ALL ASSIGNED ORDERS                                  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Order Code│Seller Name│Customer│Product│Address│Price│Status│
│ ├─────────┼───────────┼────────┼───────┼───────┼─────┼──────┤
│ │001847   │TechStore  │Ahmed R.│Galaxy │Dubai  │750  │No Res│
│ │001848   │MobileHub  │Fatima H│iPhone │Sharjah│1200 │Postpn│
│ │001849   │ElectroMax │Sara K. │iPad   │Abu Dh │800  │Confir│
│ │001850   │GadgetPro  │Omar M. │Watch  │Dubai  │400  │Review│
│ └─────────┴───────────┴────────┴───────┴───────┴─────┴──────┘ │
│                                                         │
│ [➕ BULK UPDATE] [📊 EXPORT DATA] [🔄 REFRESH]          │
└─────────────────────────────────────────────────────────┘
```

#### Order Status Update Modal
```
┌─────────────────────────────────────────────────────────┐
│ UPDATE ORDER STATUS - ORD-001847                    ✖️  │
├─────────────────────────────────────────────────────────┤
│ 📊 CURRENT STATUS: 🟠 No Response                       │
│ 👤 Customer: Ahmed Al-Rashid (+971-50-123-4567)       │
│ 🛍️ Product: Samsung Galaxy S24 - AED 750.00           │
│                                                         │
│ 📋 NEW STATUS (Required)                                │
│ ○ ✅ Confirmed                                          │
│ ○ 📞 No Response                                        │
│ ○ 🔒 Closed                                             │
│ ○ ⏰ Postponed                                          │
│ ○ 🔍 Under Review                                       │
│ ○ ❌ Cancelled                                          │
│                                                         │
│ 📝 UPDATE NOTES                                         │
│ [_____________________________________________]         │
│ [_____________________________________________]         │
│                                                         │
│ ⚠️ CANCELLATION REASON (Required if Cancelled)         │
│ ○ Customer changed mind                                 │
│ ○ Price concerns                                        │
│ ○ Found better offer elsewhere                          │
│ ○ Financial constraints                                 │
│ ○ Product not as described                              │
│ ○ Delivery issues                                       │
│ ○ Other (specify below)                                 │
│                                                         │
│ Additional Details:                                     │
│ [_____________________________________________]         │
│                                                         │
│ ☑️ Notify customer via SMS                              │
│ ☑️ Schedule follow-up if needed                         │
│                                                         │
│ [CANCEL]                           [UPDATE STATUS]      │
└─────────────────────────────────────────────────────────┘
```

#### Order Details View
```
┌─────────────────────────────────────────────────────────┐
│ ORDER DETAILS - ORD-001847                          ✖️  │
├─────────────────────────────────────────────────────────┤
│ 📊 ORDER STATUS: 🟠 No Response                         │
│ 📅 Created: Nov 15, 2024 at 09:30                     │
│ 👤 Assigned Agent: Sarah Al-Mansouri                   │
│                                                         │
│ 👤 CUSTOMER INFORMATION                                 │
│ Name: Ahmed Al-Rashid                                  │
│ Phone: +971-50-123-4567 [📞 CALL] [💬 SMS]            │
│ Email: ahmed.rashid@email.com                          │
│ Previous Orders: 3 (2 completed, 1 cancelled)         │
│                                                         │
│ 🛍️ PRODUCT INFORMATION                                 │
│ Product: Samsung Galaxy S24 Ultra                     │
│ Seller: TechStore Electronics                          │
│ Price: AED 750.00                                      │
│ [🔗 VIEW PRODUCT PAGE]                                 │
│                                                         │
│ 📍 DELIVERY INFORMATION                                 │
│ Address: Dubai Marina, Building 5, Apt 1203           │
│ Area: Dubai Marina                                     │
│ Landmark: Near Marina Mall                             │
│ Expected Delivery: Nov 16, 2024                       │
│                                                         │
│ 📞 COMMUNICATION HISTORY                                │
│ • Nov 15, 14:30 - Call attempt (No answer)            │
│ • Nov 15, 13:15 - SMS sent (Order confirmation)       │
│ • Nov 15, 09:45 - Initial contact attempt             │
│                                                         │
│ 📝 AGENT NOTES                                          │
│ • Customer didn't answer first call attempt            │
│ • SMS sent with order details                          │
│ • Need to follow up before 5 PM                        │
│                                                         │
│ ⚡ QUICK ACTIONS                                        │
│ [📞 CALL CUSTOMER] [💬 SEND SMS] [✏️ UPDATE STATUS]     │
│ [📝 ADD NOTE] [⏰ SCHEDULE CALLBACK] [🔄 REASSIGN]      │
│                                                         │
│                               [CLOSE]                   │
└─────────────────────────────────────────────────────────┘
```

### 4. Inventory Page (`/call-center-panel/inventory`)

#### Inventory View Interface
```
┌─────────────────────────────────────────────────────────┐
│ INVENTORY - MY ASSIGNED ORDERS                          │
├─────────────────────────────────────────────────────────┤
│ 🔍 Search Products: [_________________________] [SEARCH] │
│ Filter: [All Categories ▼] [In Stock ▼] [Location ▼]   │
│                                                         │
│ 📦 PRODUCTS IN MY CURRENT ORDERS                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Product Name    │Code    │Stock│Status │Location     │ │
│ ├────────────────┼────────┼─────┼───────┼─────────────┤ │
│ │Samsung Galaxy  │SG-S24U │ 15  │In Stock│WH-A-R3-S12 │ │
│ │S24 Ultra       │        │     │       │             │ │
│ ├────────────────┼────────┼─────┼───────┼─────────────┤ │
│ │iPhone 15 Pro   │IP-15P  │  3  │Low    │WH-A-R2-S08 │ │ 
│ │               │        │     │Stock  │             │ │
│ ├────────────────┼────────┼─────┼───────┼─────────────┤ │
│ │iPad Air 5th Gen│IP-AIR5 │  0  │Out of │WH-B-R1-S15 │ │
│ │               │        │     │Stock  │             │ │
│ ├────────────────┼────────┼─────┼───────┼─────────────┤ │
│ │Apple Watch S9  │AW-S9   │ 25  │In Stock│WH-A-R4-S03 │ │
│ └────────────────┴────────┴─────┴───────┴─────────────┘ │
│                                                         │
│ 📊 STOCK SUMMARY                                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🟢 In Stock: 12 products                            │ │
│ │ 🟠 Low Stock: 3 products                            │ │
│ │ 🔴 Out of Stock: 1 product                          │ │
│ │ 📦 Total Products: 16                               │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ⚠️ STOCK ALERTS FOR MY ORDERS                           │
│ • ORD-001850: iPad Air requested but out of stock      │
│ • ORD-001852: iPhone 15 Pro low stock (only 3 left)    │
│                                                         │
│ [📋 FULL INVENTORY] [📊 STOCK REPORT] [🔄 REFRESH]      │
└─────────────────────────────────────────────────────────┘
```

**Read-Only Access Features:**
- View stock levels for products in assigned orders
- Check product availability for customer inquiries
- Access warehouse location information
- Stock alerts for products in current orders
- Search functionality for quick product lookup

### 5. Delivery Tracking Page (`/call-center-panel/delivery`)

#### Delivery Tracking Interface
```
┌─────────────────────────────────────────────────────────┐
│ DELIVERY TRACKING - MY ORDERS                           │
├─────────────────────────────────────────────────────────┤
│ 🔍 Track Order: [________________] [TRACK] 🔄 Refresh   │
│ Filter: [All Status ▼] [This Week ▼] [Courier ▼]       │
│                                                         │
│ 🚚 ACTIVE DELIVERIES (8)                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Order│Customer   │Product  │Courier   │Track#│Status │ │
│ ├─────┼───────────┼─────────┼──────────┼──────┼───────┤ │
│ │001847│Ahmed R.  │Galaxy   │FastDel   │FD789 │Transit│ │
│ │001848│Fatima H. │iPhone   │QuickShip │QS456 │Shipped│ │
│ │001849│Sara K.   │iPad     │FastDel   │FD790 │Deliver│ │
│ │001850│Omar M.   │Watch    │SpeedPost │SP123 │Transit│ │
│ └─────┴───────────┴─────────┴──────────┴──────┴───────┘ │
│                                                         │
│ 📋 DELIVERY DETAILS - ORD-001847                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 📦 Order: ORD-001847                                │ │
│ │ 👤 Customer: Ahmed Al-Rashid (+971-50-123-4567)    │ │
│ │ 🛍️ Product: Samsung Galaxy S24 Ultra               │ │
│ │ 🚚 Courier: FastDelivery LLC                        │ │
│ │ 📝 Tracking: FD789456123                            │ │
│ │ 📅 Ship Date: Nov 15, 2024 at 10:30               │ │
│ │ 📅 Est. Delivery: Nov 16, 2024 by 18:00           │ │
│ │ 📍 Status: 🟠 In Transit                            │ │
│ │                                                     │ │
│ │ 📍 TRACKING HISTORY                                 │ │
│ │ • 15:30 - Package in transit to delivery location  │ │
│ │ • 12:45 - Package departed from distribution center│ │
│ │ • 10:30 - Package picked up from warehouse         │ │
│ │                                                     │ │
│ │ [📞 CALL CUSTOMER] [💬 SMS UPDATE] [📋 FULL TRACK]  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ ✅ COMPLETED DELIVERIES TODAY (12)                     │
│ [👁️ VIEW COMPLETED] [📊 DELIVERY REPORT]               │
└─────────────────────────────────────────────────────────┘
```

**Delivery Tracking Features:**
- Real-time tracking of orders assigned to the agent
- Quick order lookup by tracking number
- Customer communication tools for delivery updates
- Delivery history and status changes
- Integration with multiple courier services
- Estimated delivery time tracking

### 6. Performance Dashboard (`/call-center-panel/performance`)

#### Agent Performance Interface
```
┌─────────────────────────────────────────────────────────┐
│ MY PERFORMANCE DASHBOARD                                │
├─────────────────────────────────────────────────────────┤
│ 📊 TODAY'S PERFORMANCE                                  │
│ ┌─────────┬─────────┬─────────┬─────────┬─────────────┐ │
│ │ Orders  │Success  │Avg Call │Customer │ Resolution  │ │
│ │Handled  │ Rate    │Duration │ Rating  │    Rate     │ │
│ │   24    │ 87.5%   │ 4.2 min │  4.6⭐  │    92.3%    │ │
│ │ 📈 +3   │ 📈 +2%  │ 📉 -30s │📈 +0.1  │   📈 +5%   │ │
│ └─────────┴─────────┴─────────┴─────────┴─────────────┘ │
│                                                         │
│ 📈 WEEKLY PERFORMANCE TREND                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Orders╭─╮                                            │ │
│ │ 30  ╱│ │╲    ╭─╮                                     │ │
│ │ 25 ╱ │ │ ╲  ╱│ │╲                                    │ │
│ │ 20   │ │  ╲╱ │ │ ╲╱╲                                 │ │
│ │ 15   │ │     │ │    ╲                                │ │
│ │ 10───┴─┴─────┴─┴─────╲───                            │ │
│ │    Mon Tue Wed Thu Fri Sat Sun                      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🎯 KEY PERFORMANCE INDICATORS                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ First Call Resolution: 89.2% (Target: 85%)         │ │
│ │ Average Handle Time: 4.2 min (Target: <5 min)      │ │
│ │ Customer Satisfaction: 4.6/5 (Target: >4.0)        │ │
│ │ Order Confirmation Rate: 75% (Target: 70%)         │ │
│ │ Cancellation Rate: 12.5% (Target: <15%)           │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🏆 ACHIEVEMENTS & RECOGNITION                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🌟 Customer Champion - High satisfaction ratings    │ │
│ │ ⚡ Quick Resolver - Fast problem resolution         │ │
│ │ 📞 Communication Expert - Clear customer calls     │ │
│ │ 🎯 Target Achiever - Met monthly KPIs              │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 📋 IMPROVEMENT OPPORTUNITIES                            │
│ • Reduce average call duration by 30 seconds           │
│ • Increase first call resolution rate to 90%           │
│ • Focus on high-value order confirmations              │
│                                                         │
│ [📊 DETAILED REPORT] [📅 MONTHLY VIEW] [🎯 SET GOALS]   │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints for Call Center Panel

### Authentication APIs
```javascript
// Agent login
POST /api/agent/auth/login
{
  "agent_id": "AG001",
  "password": "agent_password",
  "workstation_id": "WS-001"
}

// Update agent availability status
PUT /api/agent/auth/status
{
  "status": "available" | "busy" | "break" | "offline",
  "concurrent_orders": 5
}

// Refresh authentication token
POST /api/agent/auth/refresh
{
  "refresh_token": "existing_refresh_token"
}
```

### Order Management APIs
```javascript
// Get agent's assigned orders
GET /api/agent/orders?status=all&date=today

// Get specific order details
GET /api/agent/orders/{order_id}

// Update order status
PUT /api/agent/orders/{order_id}/status
{
  "status": "confirmed" | "no_response" | "closed" | "postponed" | "under_review" | "cancelled",
  "notes": "Customer confirmed order via phone call",
  "cancellation_reason": "customer_changed_mind", // Required if status is cancelled
  "cancellation_details": "Found better price elsewhere",
  "notify_customer": true,
  "follow_up_required": false
}

// Log customer interaction
POST /api/agent/orders/{order_id}/interaction
{
  "interaction_type": "call" | "email" | "chat",
  "duration_minutes": 5,
  "resolution_status": "resolved" | "pending" | "escalated",
  "notes": "Customer inquired about delivery time",
  "customer_satisfaction": 5,
  "follow_up_date": "2024-11-16T10:00:00Z"
}
```

### Inventory APIs
```javascript
// Get inventory for agent's assigned orders
GET /api/agent/inventory?orders=assigned

// Search products in agent's orders
GET /api/agent/inventory/search?query=samsung&order_filter=true

// Get stock alerts for agent's orders
GET /api/agent/inventory/alerts
```

### Delivery Tracking APIs
```javascript
// Get delivery status for agent's orders
GET /api/agent/delivery?orders=assigned&status=active

// Track specific order delivery
GET /api/agent/delivery/track/{order_id}

// Search delivery by tracking number
GET /api/agent/delivery/search?tracking_number=FD789456123
```

### Performance APIs
```javascript
// Get agent performance metrics
GET /api/agent/performance?period=today

// Get detailed performance report
GET /api/agent/performance/detailed?date_from=2024-11-01&date_to=2024-11-15

// Get team comparison
GET /api/agent/performance/team-comparison?period=week
```

### Communication APIs
```javascript
// Send SMS to customer
POST /api/agent/communication/sms
{
  "order_id": 123,
  "message": "Your order has been confirmed and will be delivered tomorrow",
  "template": "order_confirmation"
}

// Log phone call
POST /api/agent