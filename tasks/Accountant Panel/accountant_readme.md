### 3. Fee Management System

Comprehensive fee management interface for adjusting, tracking, and calculating all order-related fees.

#### Fee Management Process:
1. **Fee Overview:** View all fees associated with specific orders
2. **Individual Adjustments:** Modify specific fee amounts per order
3. **Bulk Fee Updates:** Apply fee changes across multiple orders
4. **Fee History Tracking:** Monitor all fee modifications and adjustments
5. **Default Override:** Override system defaults with custom fee amounts

#### Fee Management Interface:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ FEE MANAGEMENT - Order ORD-12345                        [💾 Save] [❌ Cancel] │
├─────────────────────────────────────────────────────────────────────────┤
│ Order Details: Samsung TV × 1 | Seller: TechCorp | Date: Jan 15, 2024  │
│ Base Price: $899.99 | Current Total Fees: $45.99                       │
│                                                                         │
│ FEE BREAKDOWN                                           Default | Custom │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Upsell Fees        │[$15.00] │✅ Applied │[Edit] │     $15.00 │$15.00│ │
│ │Confirmation Fees  │[$10.00] │✅ Applied │[Edit] │     $10.00 │$10.00│ │
│ │Cancellation Fees  │[ $0.00] │❌ N/A     │[Edit] │      $5.00 │ $0.00│ │
│ │Fulfillment Fees   │[ $8.99] │✅ Applied │[Edit] │      $8.99 │ $8.99│ │
│ │Shipping Fees      │[12.00] │✅ Applied │[Edit] │     $12.00 │$12.00│ │
│ │Return Fees        │[ $0.00] │❌ N/A     │[Edit] │      $3.00 │ $0.00│ │
│ │Warehouse Fees     │[ $0.00] │❌ N/A     │[Edit] │      $2.50 │ $0.00│ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ TOTAL FEES CALCULATION                                                  │
│ Applied Fees: $45.99 | Available Fees: $30.49 | Final Total: $945.98   │
│                                                                         │
│ FEE ADJUSTMENT HISTORY                                                  │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Jan 15, 10:30 AM │Sarah K. │Modified shipping fee from $15 to $12   │ │
│ │Jan 15, 09:15 AM │System   │Auto-applied default fees               │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ [💰 Recalculate Total] [📋 Apply to Similar Orders] [🔄 Reset to Default] │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4. Payment Processing Module

Streamlined payment processing interface for recording, modifying, and tracking all order payments.

#### Payment Processing Features:
- **Individual Payment Recording:** Process single order payments
- **Batch Payment Processing:** Handle multiple payments simultaneously
- **Payment Method Management:** Track various payment methods
- **Payment Status Updates:** Modify payment statuses in real-time
- **Payment Reconciliation:** Match payments with bank records

#### Add New Payment Interface:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ADD NEW PAYMENT - Step 1: Seller Selection              [📊 View All] │
├─────────────────────────────────────────────────────────────────────────┤
│ SELLER SEARCH & SELECTION                                               │
│ Search Seller: [TechCorp________________] [🔍 Search] [📋 Recent]       │
│                                                                         │
│ SELLER RESULTS                                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │✅ TechCorp Solutions Ltd.                                           │ │
│ │   📍 Dubai, UAE | 📞 +971-4-123-4567                               │ │
│ │   💰 Outstanding: $15,250 | 🛍️ Active Orders: 12                   │ │
│ │   [Select Seller] [View Details] [Payment History]                 │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ WAREHOUSE FILTER (Optional)                                             │
│ Filter by Warehouse: [All Warehouses ▼] [Dubai Main] [Abu Dhabi]       │
│                                                                         │
│ SELLER'S ORDERS (12 orders found)                      [Export List]   │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │☐│Order Code │Date   │Product     │Amount │Status  │Warehouse        │ │
│ │☐│ORD-12345  │Jan 15 │Samsung TV  │$945.98│Pending │Dubai Main       │ │
│ │☐│ORD-12346  │Jan 14 │iPhone 13   │$789.50│Pending │Dubai Main       │ │
│ │☐│ORD-12347  │Jan 14 │MacBook Pro │$1365.74│Overdue│Abu Dhabi        │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ Selected Orders: 0 | Total Amount: $0.00                               │
│ [☐ Select All] [☐ Select Pending] [☐ Select Overdue] [Continue ▶️]     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5. Invoice Generation & Management

Comprehensive invoice management system for creating, editing, and tracking all order invoices.

#### Invoice Management Features:
- **Automatic Invoice Generation:** Create invoices from order data
- **Custom Invoice Editing:** Modify invoice details as needed
- **Invoice Templates:** Multiple professional invoice formats
- **PDF Generation:** Export invoices in various formats
- **Invoice Tracking:** Monitor invoice status and delivery

#### Invoice Generation Interface:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ INVOICE PREVIEW - INV-ORD-12345                [💾 Save] [🖨️ Print] [📤 Send] │
├─────────────────────────────────────────────────────────────────────────┤
│ INVOICE DETAILS                                         [✏️ Edit Header] │
│ Invoice #: INV-ORD-12345        │ Order #: ORD-12345                   │
│ Date: January 15, 2024          │ Due Date: January 30, 2024          │
│ Customer: John Smith            │ Payment Method: Credit Card          │
│                                                                         │
│ BILLING INFORMATION                                                     │
│ ┌─────────────────────────────┐ ┌─────────────────────────────────────┐ │
│ │BILL TO:                     │ │SELLER:                              │ │
│ │John Smith                   │ │TechCorp Solutions Ltd.              │ │
│ │123 Dubai Marina             │ │456 Business Bay                     │ │
│ │Dubai, UAE                   │ │Dubai, UAE                           │ │
│ │+971-50-123-4567            │ │+971-4-123-4567                      │ │
│ └─────────────────────────────┘ └─────────────────────────────────────┘ │
│                                                                         │
│ ITEMS & CHARGES                                         [✏️ Edit Items] │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Description        │Qty│Unit Price│    Amount│Notes                   │ │
│ │Samsung 55" Smart TV│ 1 │  $899.99 │  $899.99│Model: UN55TU8000       │ │
│ │Upsell Fee         │ 1 │   $15.00 │   $15.00│Extended warranty       │ │
│ │Confirmation Fee   │ 1 │   $10.00 │   $10.00│Order processing       │ │
│ │Fulfillment Fee    │ 1 │    $8.99 │    $8.99│Warehouse handling      │ │
│ │Shipping Fee       │ 1 │   $12.00 │   $12.00│Express delivery        │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ PAYMENT SUMMARY                                                         │
│ Subtotal:     $899.99    │ Total Fees:     $45.99                      │
│ Tax (5%):      $47.30    │ TOTAL:         $993.28                      │
│                                                                         │
│ [📋 Copy Invoice] [📧 Email Customer] [💾 Save as Template] [🔄 Regenerate] │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6. Financial Reporting & Analytics

Comprehensive reporting system for financial analysis, revenue tracking, and business intelligence.

#### Reporting Features:
- **Revenue Reports:** Daily, weekly, monthly revenue analysis
- **Seller Payment Reports:** Outstanding and completed payments
- **Fee Analysis:** Breakdown of fee types and performance
- **Payment Method Analytics:** Analysis by payment method
- **Custom Report Builder:** Create tailored financial reports

#### Financial Reports Interface:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ FINANCIAL REPORTS & ANALYTICS                    [📊 New Report] [⚙️ Settings] │
├─────────────────────────────────────────────────────────────────────────┤
│ QUICK REPORTS                                                           │
│ [📊 Daily Revenue] [💰 Payment Summary] [📋 Fee Analysis] [🏪 Seller Report] │
│                                                                         │
│ CUSTOM REPORT BUILDER                                                   │
│ Report Type: [Revenue Analysis ▼]                                      │
│ Date Range: [Jan 1, 2024] to [Jan 15, 2024]                          │
│ Group By: [Daily ▼] [Weekly] [Monthly]                                 │
│ Filters: [All Sellers ▼] [All Payment Methods ▼] [All Warehouses ▼]   │
│                                                                         │
│ REVENUE ANALYSIS - January 1-15, 2024                  [📤 Export] [🖨️ Print] │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Date     │Orders│Revenue  │Fees     │Total    │Avg Order│Top Seller  │ │
│ │Jan 15   │  45  │$35,250  │$2,180   │$37,430  │  $831   │TechCorp    │ │
│ │Jan 14   │  38  │$28,900  │$1,890   │$30,790  │  $811   │MobileLtd   │ │
│ │Jan 13   │  52  │$42,100  │$2,650   │$44,750  │  $860   │TechCorp    │ │
│ │Jan 12   │  31  │$25,400  │$1,540   │$26,940  │  $869   │ElectroMax  │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ SUMMARY METRICS                                                         │
│ Total Revenue: $445,250 | Total Fees: $28,750 | Average Order: $847    │
│ Growth Rate: +12.5% vs previous period | Top Payment Method: Credit Card│
│                                                                         │
│ FEE BREAKDOWN CHART                                     [📊 View Details] │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Shipping (42%) ████████████████████                                 │ │
│ │Fulfillment (28%) ████████████                                      │ │
│ │Upsell (18%) ████████                                               │ │
│ │Confirmation (12%) █████                                            │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ [💾 Save Report] [📧 Schedule Email] [📋 Add to Dashboard] [🔄 Refresh]  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7. Payment Reconciliation System

Advanced reconciliation tools for matching payments with bank records and resolving discrepancies.

#### Reconciliation Features:
- **Bank Statement Import:** Upload and process bank statements
- **Automatic Matching:** AI-powered payment matching
- **Manual Reconciliation:** Handle complex matching scenarios
- **Discrepancy Resolution:** Tools for resolving payment differences
- **Reconciliation Reports:** Track reconciliation status and history

#### Bank Reconciliation Interface:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ BANK RECONCILIATION - January 15, 2024              [📁 Import] [💾 Save] │
├─────────────────────────────────────────────────────────────────────────┤
│ RECONCILIATION STATUS                                                   │
│ Bank Statement: ADCB-Jan15.csv | Total Transactions: 45                │
│ Matched: 38 (84%) | Unmatched: 7 (16%) | Discrepancies: 2             │
│                                                                         │
│ UNMATCHED TRANSACTIONS                              [🔄 Auto-Match] [⚙️ Rules] │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Bank Transaction          │Amount │System Record        │Status      │ │
│ │REF-789456 | John Smith   │$945.98│ORD-12345           │✅ Matched  │ │
│ │REF-789457 | Sarah Johnson│$1250.50│No Match Found      │❌ Unmatched│ │
│ │REF-789458 | TechCorp Ltd │$2100.00│ORD-12350          │⚠️ Partial  │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ MANUAL MATCHING                                                         │
│ Selected Bank Transaction: REF-789457 | Sarah Johnson | $1,250.50      │
│                                                                         │
│ Search System Records: [Sarah Johnson_______] [🔍 Search]              │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Order Code │Customer      │Amount   │Date   │Status  │Actions         │ │
│ │ORD-12351  │Sarah Johnson │$1,250.50│Jan 15 │Pending │[🔗 Match]      │ │
│ │ORD-12298  │S. Johnson    │$1,249.99│Jan 14 │Pending │[🔗 Maybe]      │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ DISCREPANCY RESOLUTION                                                  │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Issue: Amount mismatch | Bank: $2,100.00 | System: $2,099.50        │ │
│ │Difference: $0.50 | Likely Cause: Bank processing fee               │ │
│ │Resolution: [Adjust System ▼] [Add Fee Entry] [Mark as Resolved]     │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ [📊 Reconciliation Report] [✅ Complete Reconciliation] [🔄 Refresh]     │
└─────────────────────────────────────────────────────────────────────────┘
```

## Database Schema Integration

### Accountant Specific Tables

#### Accountant Sessions
```sql
CREATE TABLE accountant_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP NULL,
    orders_processed INT DEFAULT 0,
    payments_processed INT DEFAULT 0,
    total_amount_processed DECIMAL(15,2) DEFAULT 0.00,
    session_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_sessions (user_id, session_start)
);
```

#### Payment Processing History
```sql
CREATE TABLE payment_processing_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    processed_by INT NOT NULL,
    action_type ENUM('create', 'update', 'delete', 'status_change') NOT NULL,
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    previous_amount DECIMAL(15,2),
    new_amount DECIMAL(15,2),
    payment_method VARCHAR(100),
    processing_notes TEXT,
    batch_id VARCHAR(50), -- For bulk operations
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (processed_by) REFERENCES users(id),
    INDEX idx_order_history (order_id, processed_at),
    INDEX idx_processor_history (processed_by, processed_at),
    INDEX idx_batch_operations (batch_id)
);
```

#### Fee Adjustment History
```sql
CREATE TABLE fee_adjustment_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    adjusted_by INT NOT NULL,
    fee_type ENUM('upsell', 'confirmation', 'cancellation', 'fulfillment', 'shipping', 'return', 'warehouse') NOT NULL,
    previous_amount DECIMAL(10,2),
    new_amount DECIMAL(10,2),
    adjustment_reason TEXT,
    adjustment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (adjusted_by) REFERENCES users(id),
    INDEX idx_order_fee_history (order_id, adjustment_date),
    INDEX idx_fee_type_history (fee_type, adjustment_date)
);
```

#### Invoice Generation Log
```sql
CREATE TABLE invoice_generation_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number VARCHAR(100) NOT NULL UNIQUE,
    order_id INT NOT NULL,
    generated_by INT NOT NULL,
    invoice_data JSON, -- Store complete invoice details
    generation_method ENUM('auto', 'manual', 'batch') DEFAULT 'manual',
    invoice_status ENUM('draft', 'sent', 'paid', 'cancelled') DEFAULT 'draft',
    pdf_path VARCHAR(255),
    sent_to_customer BOOLEAN DEFAULT FALSE,
    customer_email VARCHAR(255),
    sent_at TIMESTAMP NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (generated_by) REFERENCES users(id),
    INDEX idx_order_invoices (order_id),
    INDEX idx_invoice_status (invoice_status, generated_at)
);
```

#### Bank Reconciliation Records
```sql
CREATE TABLE bank_reconciliation_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    reconciliation_date DATE NOT NULL,
    bank_statement_file VARCHAR(255),
    processed_by INT NOT NULL,
    total_bank_transactions INT DEFAULT 0,
    matched_transactions INT DEFAULT 0,
    unmatched_transactions INT DEFAULT 0,
    total_bank_amount DECIMAL(15,2) DEFAULT 0.00,
    total_system_amount DECIMAL(15,2) DEFAULT 0.00,
    discrepancy_amount DECIMAL(15,2) DEFAULT 0.00,
    reconciliation_status ENUM('in_progress', 'completed', 'needs_review') DEFAULT 'in_progress',
    reconciliation_notes TEXT,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (processed_by) REFERENCES users(id),
    INDEX idx_reconciliation_date (reconciliation_date),
    INDEX idx_reconciliation_status (reconciliation_status)
);
```

#### Financial Report Templates
```sql
CREATE TABLE financial_report_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_name VARCHAR(255) NOT NULL,
    created_by INT NOT NULL,
    report_type ENUM('revenue', 'payments', 'fees', 'sellers', 'custom') NOT NULL,
    template_config JSON, -- Store report configuration
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INT DEFAULT 0,
    last_used TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_template_type (report_type, created_at),
    INDEX idx_public_templates (is_public, usage_count)
);
```

## API Endpoints for Accountant Panel

### Authentication & Session Management
```javascript
// Accountant login
POST /api/accountant/auth/login
{
  "username": "sarah.finance",
  "password": "secure_password"
}
Response: {
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": 456,
    "name": "Sarah Finance",
    "role": "accountant",
    "permissions": ["financial_full_access"]
  },
  "session_info": {
    "session_start": "2024-01-15T08:00:00Z",
    "last_activity": "2024-01-15T10:30:00Z"
  }
}

// Start work session
POST /api/accountant/session/start
{
  "session_notes": "Beginning daily financial review"
}

// End work session
POST /api/accountant/session/end
{
  "session_id": "session_uuid",
  "orders_processed": 25,
  "payments_processed": 18,
  "session_summary": "Completed batch payment processing"
}
```

### Dashboard & Financial Overview
```javascript
// Get accountant dashboard data
GET /api/accountant/dashboard
Response: {
  "financial_overview": {
    "daily_revenue": 45230.50,
    "payments_processed": 28,
    "outstanding_amount": 12450.75,
    "orders_processed": 156
  },
  "urgent_alerts": [
    {
      "type": "overdue_payment",
      "order_id": "ORD-12345",
      "days_overdue": 15,
      "amount": 2450.00
    }
  ],
  "pending_tasks": [
    {
      "id": 1,
      "type": "payment_batch",
      "description": "Process payment batch for Seller XYZ",
      "priority": "high",
      "due_date": "2024-01-15T16:00:00Z"
    }
  ],
  "recent_activities": []
}

// Get financial quick stats
GET /api/accountant/stats/quick
```

### Order Financial Management
```javascript
// Get orders with financial details
GET /api/accountant/orders?status=pending&seller_id=123&page=1&limit=50
Response: {
  "orders": [
    {
      "id": "ORD-12345",
      "date": "2024-01-15",
      "product_name": "Samsung TV",
      "quantity": 1,
      "unit_price": 899.99,
      "seller_name": "TechCorp",
      "payment_status": "pending",
      "total_fees": 45.99,
      "total_price": 945.98,
      "payment_method": null,
      "fees_breakdown": {
        "upsell": 15.00,
        "confirmation": 10.00,
        "fulfillment": 8.99,
        "shipping": 12.00
      }
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 52,
    "total_records": 156
  }
}

// Update payment status
PUT /api/accountant/orders/{order_id}/payment-status
{
  "status": "paid",
  "payment_method": "credit_card",
  "payment_reference": "TXN-789456",
  "notes": "Payment confirmed via bank statement"
}

// Bulk update payment status
POST /api/accountant/orders/bulk-update
{
  "order_ids": ["ORD-12345", "ORD-12346", "ORD-12347"],
  "update_data": {
    "payment_status": "paid",
    "payment_method": "bank_transfer",
    "batch_reference": "BATCH-20240115-001"
  }
}
```

### Fee Management
```javascript
// Get fee details for order
GET /api/accountant/orders/{order_id}/fees
Response: {
  "order_id": "ORD-12345",
  "fees": {
    "upsell": {"default": 15.00, "current": 15.00, "applied": true},
    "confirmation": {"default": 10.00, "current": 10.00, "applied": true},
    "cancellation": {"default": 5.00, "current": 0.00, "applied":# Accountant Panel - Atlas Fulfillment

## Overview
This document outlines the requirements for implementing a dedicated Accountant Panel at `/accountant/` within the Atlas Fulfillment CRM platform. The panel provides accounting staff with comprehensive financial management tools, payment processing capabilities, and real-time financial tracking functionalities tailored for day-to-day accounting operations.

## System Requirements

### Accountant Authentication & Access
The Accountant Panel operates as a separate interface accessible at `/accountant/` with role-based authentication that restricts access to financial operations staff.

#### Access Control:
- **Accountant Role:** Primary users with full financial management access
- **No Admin Panel Access:** Accountants operate exclusively within the dedicated accountant panel
- **Complete Financial Authority:** Full read, write, edit, and delete permissions for all financial data

## Core Functionality

### 1. Financial Dashboard

The Accountant Panel displays a comprehensive financial dashboard with real-time payment status, revenue tracking, and daily financial overview.

#### Dashboard Components:
- **Daily Financial Summary:** Today's revenue, payments processed, and outstanding amounts
- **Payment Status Overview:** Paid, pending, and overdue payment counts
- **Quick Financial Stats:** Total revenue, fees collected, and order values
- **Priority Alerts:** Urgent payment issues and financial discrepancies
- **Recent Activities:** Last 10 financial transactions processed by the user

#### Dashboard Layout:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ACCOUNTANT DASHBOARD - Atlas Fulfillment Finance                       │
│ Welcome back, Sarah | Today: Monday, Jan 15, 2024                      │
├─────────────────────────────────────────────────────────────────────────┤
│ TODAY'S FINANCIAL OVERVIEW                                              │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │Total Revenue│ │Payments     │ │Outstanding  │ │Orders       │        │
│ │  $45,230    │ │ Processed   │ │  $12,450    │ │ Processed   │        │
│ │   today     │ │     28      │ │   overdue   │ │    156      │        │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘        │
│                                                                         │
│ URGENT FINANCIAL ALERTS                                                 │
│ ⚠️ ORD-12345 - Payment overdue by 15 days ($2,450)                     │
│ ⚠️ Seller ABC Corp - Outstanding balance exceeds credit limit          │
│ ℹ️ Bank reconciliation required for yesterday's transactions           │
│                                                                         │
│ QUICK ACTIONS                                                           │
│ [💰 Process Payment] [📊 Generate Report] [🔄 Reconcile] [📱 Add Entry]│
│                                                                         │
│ PENDING FINANCIAL TASKS (8)                     [View All Tasks]       │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │□ Process: Payment batch for Seller XYZ (15 orders)                 │ │
│ │□ Review: Fee adjustments for damaged goods returns                  │ │
│ │□ Reconcile: Bank statement for Jan 14, 2024                        │ │
│ │□ Generate: Monthly seller payment report                            │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2. Order Financial Management Interface

A comprehensive order management interface optimized for financial operations and payment processing.

#### Financial Management Capabilities:
- **Payment Status Updates:** Quick status changes for order payments
- **Fee Adjustments:** Real-time fee modification and calculation
- **Bulk Operations:** Process multiple orders simultaneously
- **Payment Method Tracking:** Monitor payment methods and reconciliation
- **Financial Documentation:** Generate invoices and payment confirmations

#### Order Management Interface:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ ORDER FINANCIAL MANAGEMENT                      [🔍 Search] [⚙️ Filter] │
├─────────────────────────────────────────────────────────────────────────┤
│ Filters: [All Orders▼] [Payment Status▼] [Date Range▼] [Seller▼]       │
│                                                                         │
│ BULK ACTIONS: [☐ Select All] [💰 Batch Payment] [📊 Export] [🗑️ Delete] │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │☐│Order Code │Date    │Product      │Qty│Unit Price│Seller   │Status│ │
│ │☐│ORD-12345  │Jan 15  │Samsung TV   │ 1 │  $899.99 │TechCorp │ Paid │ │
│ │☐│ORD-12346  │Jan 15  │iPhone 13    │ 2 │  $699.99 │MobileLtd│Pending│ │
│ │☐│ORD-12347  │Jan 14  │MacBook Pro  │ 1 │ $1299.99 │TechCorp │Overdue│ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │Total Fees │Total Price│Payment Method│Actions                      │ │
│ │   $45.99  │  $945.98  │ Credit Card  │[👁️ Invoice][✏️ Edit][🗑️ Del]│ │
│ │   $89.50  │ $1489.48  │   Pending    │[👁️ Invoice][✏️ Edit][🗑️ Del]│ │
│ │   $65.75  │ $1365.74  │ Bank Transfer│[👁️ Invoice][✏️ Edit][🗑️ Del]│ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ Showing 1-3 of 156 orders | [◀️ Previous] [1][2][3]...[52] [Next ▶️]   │
└─────────────────────────────────────────────────────────────────────────┘
```