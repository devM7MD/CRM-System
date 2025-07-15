# Call Center Manager Panel System - Operations Management Portal

## Overview
This document outlines the requirements and specifications for the Call Center Manager Panel - a comprehensive web application designed for call center managers to oversee all call center operations, manage agent performance, assign tasks, and monitor key performance indicators. This system provides managerial oversight of the entire customer service operation and integrates with both the main CRM system and the Call Center Agent Panel.

## System Purpose
The Call Center Manager Panel serves as the management interface that allows call center managers to:
- Monitor real-time call center performance and operational statistics
- Oversee all orders across the entire call center operation
- Assign orders to specific call center agents and provide instructions
- Track individual and team performance metrics
- Generate comprehensive reports for operational analysis
- Manage agent workload distribution and task prioritization
- Access detailed analytics for decision-making and process optimization

## User Roles and Access Levels

### Call Center Manager
**Primary Users**: Call center management personnel
**Access Level**: Department-wide access across all operations

**Capabilities:**
- View and manage all orders in the system
- Assign orders to specific call center agents
- Leave notes and instructions for agents on specific orders
- Monitor real-time performance statistics and KPIs
- Access individual agent performance reports (daily/weekly)
- View team-wide analytics and operational trends
- Generate comprehensive performance and operational reports
- Monitor call center efficiency metrics and response times
- Oversee order confirmation rates and cancellation analysis

## Navigation
- **URL**: `/call-center-manager-panel/`
- **Access**: Dedicated login for Call Center Managers
- **Authentication**: Role-based access specific to call center manager permissions
- **Data Scope**: Access to all orders, comprehensive agent performance data, and operational statistics

## Database Schema for Call Center Manager Panel

### Enhanced Tables for Management Operations

#### Manager Dashboard Metrics Table
```sql
CREATE TABLE manager_dashboard_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE,
    total_orders INT DEFAULT 0,
    orders_confirmed INT DEFAULT 0,
    orders_cancelled INT DEFAULT 0,
    orders_postponed INT DEFAULT 0,
    orders_pending INT DEFAULT 0,
    confirmation_rate DECIMAL(5,2),
    cancellation_rate DECIMAL(5,2),
    average_response_time_minutes DECIMAL(5,2),
    total_agents_active INT DEFAULT 0,
    total_calls_handled INT DEFAULT 0,
    customer_satisfaction_avg DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Order Assignment History Table
```sql
CREATE TABLE order_assignment_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    manager_id INT,
    agent_id INT,
    assignment_date TIMESTAMP,
    manager_notes TEXT,
    priority_level ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    expected_completion TIMESTAMP,
    assignment_reason TEXT,
    previous_agent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (manager_id) REFERENCES managers(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (previous_agent_id) REFERENCES agents(id)
);
```

#### Manager Notes Table
```sql
CREATE TABLE manager_notes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    manager_id INT,
    agent_id INT,
    note_text TEXT,
    note_type ENUM('instruction', 'reminder', 'priority', 'escalation') DEFAULT 'instruction',
    is_urgent BOOLEAN DEFAULT FALSE,
    is_read_by_agent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (manager_id) REFERENCES managers(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

#### Team Performance Summary Table
```sql
CREATE TABLE team_performance_summary (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE,
    team_id INT,
    total_agents INT DEFAULT 0,
    orders_handled INT DEFAULT 0,
    orders_confirmed INT DEFAULT 0,
    orders_cancelled INT DEFAULT 0,
    average_handle_time DECIMAL(5,2),
    team_confirmation_rate DECIMAL(5,2),
    team_satisfaction_avg DECIMAL(3,2),
    top_performer_agent_id INT,
    lowest_performer_agent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (top_performer_agent_id) REFERENCES agents(id),
    FOREIGN KEY (lowest_performer_agent_id) REFERENCES agents(id)
);
```

## Page Structure

### Call Center Manager Sidebar Navigation
The Call Center Manager Panel features a persistent sidebar navigation bar with the following menu items:
- **Dashboard** (Default landing page containing statistics and KPIs)
- **Order Management** (Page for viewing all orders and assigning to agents)
- **Agent Reports** (Page for daily/weekly individual agent performance reports)

## Call Center Manager Panel Interface Design

### 1. Login and Authentication

#### Login Page (`/call-center-manager-panel/login`)
```
┌─────────────────────────────────────────────────────────┐
│            CALL CENTER MANAGER LOGIN                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│        [COMPANY LOGO]                                   │
│                                                         │
│    Manager ID:  [________________________]              │
│    Password:    [________________________]              │
│                                                         │
│    □ Remember me    [Forgot Password?]                  │
│                                                         │
│            [LOGIN TO MANAGER PANEL]                     │
│                                                         │
│    ─────────────── OR ──────────────────                │
│                                                         │
│         [LOGIN WITH MANAGER BADGE]                      │
│                                                         │
│    IT Support: ext. 2200 | Help Desk: ext. 2100       │
└─────────────────────────────────────────────────────────┘
```

### 2. Dashboard (Default Landing Page) (`/call-center-manager-panel/`)

#### Main Dashboard Layout
```
┌─────────────────────────────────────────────────────────┐
│ 👤 Manager: Ahmad Al-Khalil  📊 Call Center Overview    │
├─────────────────────────────────────────────────────────┤
│ 📋 SIDEBAR NAVIGATION                                   │
│ ┌─────────────┐ ┌─────────────────────────────────────┐ │
│ │ 📊 Dashboard│ │ 📈 OPERATIONAL PERFORMANCE          │ │
│ │ 📦 Orders   │ │ 🕒 Real-time: Nov 15, 2024 - 14:30 │ │
│ │ 👥 Agents   │ │                                     │ │
│ │ 📋 Reports  │ │ ┌─────────┬─────────┬─────────────┐ │ │
│ │             │ │ │ Total   │ Active  │   Orders    │ │ │
│ │             │ │ │ Orders  │ Agents  │  Processed  │ │ │
│ │             │ │ │   156   │   12    │    Today     │ │ │
│ │             │ │ │         │         │     89      │ │ │
│ │             │ │ └─────────┴─────────┴─────────────┘ │ │
│ │             │ │                                     │ │
│ │             │ │ 📊 KEY PERFORMANCE INDICATORS       │ │
│ │             │ │ ┌─────────────────────────────────┐ │ │
│ │             │ │ │ ✅ Confirmation Rate: 78.5%    │ │ │
│ │             │ │ │ ⏱️ Avg Response Time: 3.2 min   │ │ │
│ │             │ │ │ ❌ Cancellation Rate: 15.2%    │ │ │
│ │             │ │ │ ⭐ Customer Satisfaction: 4.3   │ │ │
│ │             │ │ └─────────────────────────────────┘ │ │
│ │             │ │                                     │ │
│ │             │ │ 📈 CONFIRMATION RATE TREND         │ │
│ │             │ │ ┌─────────────────────────────────┐ │ │
│ │             │ │ │Rate                             │ │ │
│ │             │ │ │85% ╭─╮     ╭─╮                  │ │ │
│ │             │ │ │80%╱   ╲   ╱   ╲                 │ │ │
│ │             │ │ │75%     ╲ ╱     ╲╱               │ │ │
│ │             │ │ │70%      ╲╱                      │ │ │
│ │             │ │ │    Mon Tue Wed Thu Fri          │ │ │
│ │             │ │ └─────────────────────────────────┘ │ │
│ │             │ │                                     │ │
│ │             │ │ 📊 RESPONSE TIME ANALYSIS          │ │
│ │             │ │ ┌─────────────────────────────────┐ │ │
│ │             │ │ │Min                              │ │ │
│ │             │ │ │5.0╭─╮                           │ │ │
│ │             │ │ │4.0│ │╲   ╭─╮                    │ │ │
│ │             │ │ │3.0│ │ ╲ ╱│ │╲                   │ │ │
│ │             │ │ │2.0└─┘  ╲╱ │ │ ╲╱                │ │ │
│ │             │ │ │    Mon Tue Wed Thu Fri          │ │ │
│ │             │ │ └─────────────────────────────────┘ │ │
│ │             │ │                                     │ │
│ │             │ │ 📉 CANCELLATION ANALYSIS           │ │
│ │             │ │ ┌─────────────────────────────────┐ │ │
│ │             │ │ │Rate                             │ │ │
│ │             │ │ │20% ╭─╮                          │ │ │
│ │             │ │ │15%╱   ╲     ╭─╮                 │ │ │
│ │             │ │ │10%     ╲   ╱   ╲╱               │ │ │
│ │             │ │ │ 5%      ╲ ╱                     │ │ │
│ │             │ │ │    Mon Tue Wed Thu Fri          │ │ │
│ │             │ │ └─────────────────────────────────┘ │ │
│ │             │ │                                     │ │
│ │             │ │ ⏰ TIME RANGE SELECTOR             │ │ │
│ │             │ │ [Daily] [Weekly] [Monthly]          │ │ │
│ └─────────────┘ └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### Statistical Charts Section
```
┌─────────────────────────────────────────────────────────┐
│ 📊 DETAILED PERFORMANCE ANALYTICS                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 🎯 TOP PERFORMING AGENTS TODAY                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Agent Name    │Orders│Confirmed│Rate │Avg Time│Rating│ │
│ ├─────────────┼──────┼─────────┼─────┼────────┼──────┤ │
│ │Sarah Al-Mansouri│ 24   │   21    │87.5%│  3.2min│ 4.7⭐│ │
│ │Omar Al-Rashid   │ 19   │   16    │84.2%│  2.9min│ 4.6⭐│ │
│ │Fatima Hassan    │ 22   │   18    │81.8%│  3.5min│ 4.5⭐│ │
│ │Ahmed Al-Zahra   │ 18   │   14    │77.8%│  4.1min│ 4.4⭐│ │
│ └─────────────────┴──────┴─────────┴─────┴────────┴──────┘ │
│                                                         │
│ ⚠️ ALERTS & NOTIFICATIONS                              │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🔴 High Priority: 15 orders pending >2 hours       │ │
│ │ 🟠 Agent Overload: Sarah Al-Mansouri (30+ orders)  │ │
│ │ 🟡 Low Stock Alert: iPhone 15 Pro (3 units left)   │ │
│ │ 🔵 System Update: New CRM features available        │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🚀 QUICK ACTIONS                                        │
│ [📦 VIEW ALL ORDERS] [👥 ASSIGN ORDERS] [📊 REPORTS]    │
│ [⚙️ SYSTEM SETTINGS] [📢 SEND BROADCAST]               │
└─────────────────────────────────────────────────────────┘
```

### 3. Order Management Page (`/call-center-manager-panel/orders`)

#### Order Management Interface
```
┌─────────────────────────────────────────────────────────┐
│ 📦 ORDER MANAGEMENT - ALL ORDERS                        │
├─────────────────────────────────────────────────────────┤
│ Filter: [All Status ▼] [All Agents ▼] [Today ▼]        │
│ 🔍 Search: [_________________________] [SEARCH]         │
│                                                         │
│ 📊 ORDER SUMMARY                                        │
│ Total: 156 | Assigned: 134 | Unassigned: 22           │
│ Confirmed: 89 | Pending: 45 | Cancelled: 22           │
│                                                         │
│ 🔴 UNASSIGNED HIGH PRIORITY ORDERS (5)                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Order Code│Customer   │Product  │Price │Status│Agent │ │
│ ├──────────┼───────────┼─────────┼──────┼──────┼──────┤ │
│ │ORD-001860│Ahmed K.   │Galaxy   │750   │Pending│[▼]  │ │
│ │ORD-001861│Sara M.    │iPhone   │1200  │Pending│[▼]  │ │
│ │ORD-001862│Omar H.    │iPad     │800   │Pending│[▼]  │ │
│ │          │           │         │      │      │[📝] │ │
│ └──────────┴───────────┴─────────┴──────┴──────┴──────┘ │
│                                                         │
│ 📋 ALL ORDERS                                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Order │Customer│Seller   │Product│Price │Status│Agent│ │
│ ├──────┼────────┼─────────┼───────┼──────┼──────┼─────┤ │
│ │001847│Ahmed R.│TechStore│Galaxy │750   │Confirm│Sarah│ │
│ │001848│Fatima H│MobileHub│iPhone │1200  │Postpn │Omar │ │
│ │001849│Sara K. │ElectMax │iPad   │800   │Confirm│Fatima│ │
│ │001850│Omar M. │GadgetPro│Watch  │400   │Review │Ahmed│ │
│ │      │        │         │       │      │      │[📝] │ │
│ └──────┴────────┴─────────┴───────┴──────┴──────┴─────┘ │
│                                                         │
│ 📝 QUICK ACTIONS                                        │
│ [🎯 ASSIGN ORDERS] [📊 BULK UPDATE] [📋 EXPORT DATA]    │
│ [📢 SEND ALERT] [⚙️ SETTINGS]                          │
└─────────────────────────────────────────────────────────┘
```

#### Order Assignment Modal
```
┌─────────────────────────────────────────────────────────┐
│ ASSIGN ORDER TO AGENT - ORD-001860                  ✖️  │
├─────────────────────────────────────────────────────────┤
│ 📦 ORDER DETAILS                                        │
│ Customer: Ahmed Al-Khalil (+971-50-555-1234)          │
│ Product: Samsung Galaxy S24 Ultra - AED 750.00        │
│ Address: Dubai Marina, Building 12, Apt 504           │
│ Created: Nov 15, 2024 at 11:30                       │
│                                                         │
│ 👥 SELECT AGENT (Required)                              │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Agent Name      │Current Load│Availability│Perf Rate│ │
│ ├────────────────┼────────────┼────────────┼─────────┤ │
│ │○ Sarah Al-Mansouri│    25    │ Available  │  87.5%  │ │
│ │○ Omar Al-Rashid   │    19    │ Available  │  84.2%  │ │
│ │○ Fatima Hassan    │    22    │ Busy       │  81.8%  │ │
│ │○ Ahmed Al-Zahra   │    18    │ Available  │  77.8%  │ │
│ └────────────────┴────────────┴────────────┴─────────┘ │
│                                                         │
│ 🎯 PRIORITY LEVEL                                       │
│ ○ Low      ○ Medium      ● High      ○ Urgent          │
│                                                         │
│ 📝 MANAGER NOTES FOR AGENT                              │
│ [___________________________________________________]   │
│ [___________________________________________________]   │
│ [___________________________________________________]   │
│                                                         │
│ ⏰ EXPECTED COMPLETION                                   │
│ Date: [Nov 16, 2024 ▼] Time: [16:00 ▼]                │
│                                                         │
│ 📢 NOTIFICATION OPTIONS                                 │
│ ☑️ Send immediate notification to agent                 │
│ ☑️ Add to agent's priority queue                       │
│ ☐ Schedule reminder for completion time                 │
│                                                         │
│ [CANCEL]                        [ASSIGN ORDER]          │
└─────────────────────────────────────────────────────────┘
```

#### Manager Notes Interface
```
┌─────────────────────────────────────────────────────────┐
│ ADD MANAGER NOTE - ORD-001847                       ✖️  │
├─────────────────────────────────────────────────────────┤
│ 📦 Order: ORD-001847 - Ahmed Al-Rashid                 │
│ 👤 Assigned Agent: Sarah Al-Mansouri                    │
│ 📅 Current Status: No Response                         │
│                                                         │
│ 📝 NOTE TYPE                                            │
│ ○ General Instruction                                   │
│ ○ Priority Reminder                                     │
│ ● Customer Service Tip                                  │
│ ○ Escalation Notice                                     │
│                                                         │
│ 📋 NOTE CONTENT                                         │
│ [___________________________________________________]   │
│ [Customer mentioned preference for evening delivery ]   │
│ [Please confirm delivery time before 6 PM         ]   │
│ [___________________________________________________]   │
│                                                         │
│ ⚠️ URGENCY LEVEL                                        │
│ ○ Normal      ● Important      ○ Urgent                │
│                                                         │
│ 📢 NOTIFICATION                                         │
│ ☑️ Send immediate notification to agent                 │
│ ☑️ Show as priority note in agent panel                │
│                                                         │
│ [CANCEL]                           [SAVE NOTE]          │
└─────────────────────────────────────────────────────────┘
```

### 4. Agent Reports Page (`/call-center-manager-panel/reports`)

#### Agent Performance Reports Interface
```
┌─────────────────────────────────────────────────────────┐
│ 👥 AGENT PERFORMANCE REPORTS                            │
├─────────────────────────────────────────────────────────┤
│ 👤 SELECT AGENT                                         │
│ [Sarah Al-Mansouri ▼] [🔄 Load Report]                  │
│                                                         │
│ 📅 TIME PERIOD                                          │
│ ● Daily Report    ○ Weekly Report    ○ Monthly Report  │
│ Date Range: [Nov 15, 2024 ▼] to [Nov 15, 2024 ▼]      │
│                                                         │
│ 📊 SARAH AL-MANSOURI - PERFORMANCE REPORT              │
│ Report Period: November 15, 2024 (Today)              │
│                                                         │
│ 📈 KEY METRICS                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Orders Handled:         24      Target: 20 ✅       │ │
│ │ Successful Confirmations: 21    Rate: 87.5% ✅      │ │
│ │ Orders Postponed:        2      Rate: 8.3%          │ │
│ │ Orders Cancelled:        1      Rate: 4.2% ✅       │ │
│ │ Average Call Time:    3.2 min   Target: <5 min ✅   │ │
│ │ Customer Satisfaction: 4.7⭐     Target: >4.0 ✅     │ │
│ │ First Call Resolution: 89.2%    Target: 85% ✅      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 📊 PERFORMANCE TREND (Last 7 Days)                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Orders                                               │ │
│ │ 30 ╭─╮                                              │ │
│ │ 25 │ │╲  ╭─╮                                        │ │
│ │ 20 │ │ ╲╱│ │╲   ╭─╮                                 │ │
│ │ 15 │ │   │ │ ╲ ╱│ │                                 │ │
│ │ 10─┴─┴───┴─┴──╲╱─┴─┴─                               │ │
│ │   Mon Tue Wed Thu Fri Sat Sun                      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🎯 CANCELLATION BREAKDOWN                              │ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Customer Changed Mind:        0 orders              │ │
│ │ Price Concerns:              0 orders              │ │
│ │ Found Better Offer:          1 order               │ │
│ │ Financial Constraints:       0 orders              │ │
│ │ Product Issues:              0 orders              │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 💬 RECENT CUSTOMER FEEDBACK                            │
│ • "Excellent service, very professional" - 5⭐         │
│ • "Quick response and helpful" - 5⭐                   │
│ • "Resolved my issue efficiently" - 4⭐                │
│                                                         │
│ [📊 DETAILED REPORT] [📧 EMAIL REPORT] [📁 EXPORT]     │
└─────────────────────────────────────────────────────────┘
```

#### Weekly Performance Comparison
```
┌─────────────────────────────────────────────────────────┐
│ 📊 WEEKLY TEAM PERFORMANCE COMPARISON                   │
├─────────────────────────────────────────────────────────┤
│ 📅 Week of: November 11-17, 2024                       │
│                                                         │
│ 👥 AGENT PERFORMANCE RANKING                            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │Rank│Agent Name      │Orders│Confirm│Rate │Avg Time│ │
│ ├────┼────────────────┼──────┼───────┼─────┼────────┤ │
│ │ 1  │Sarah Al-Mansouri│ 156  │  136  │87.2%│ 3.1min │ │
│ │ 2  │Omar Al-Rashid   │ 142  │  118  │83.1%│ 3.4min │ │
│ │ 3  │Fatima Hassan    │ 138  │  112  │81.2%│ 3.6min │ │
│ │ 4  │Ahmed Al-Zahra   │ 124  │   96  │77.4%│ 4.2min │ │
│ │ 5  │Layla Al-Amiri   │ 118  │   88  │74.6%│ 4.5min │ │
│ └────┴────────────────┴──────┴───────┴─────┴────────┘ │
│                                                         │
│ 📈 TEAM PERFORMANCE METRICS                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Team Average Confirmation Rate: 80.7%               │ │
│ │ Team Average Response Time: 3.8 minutes             │ │
│ │ Team Customer Satisfaction: 4.5⭐                    │ │
│ │ Total Orders Processed: 678                         │ │
│ │ Team Efficiency Score: 85.2%                        │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ 🏆 ACHIEVEMENTS THIS WEEK                              │ │
│ • Sarah Al-Mansouri: Highest confirmation rate        │
│ • Omar Al-Rashid: Fastest average response time       │
│ • Team exceeded weekly targets by 12%                  │
│                                                         │
│ ⚠️ AREAS FOR IMPROVEMENT                               │
│ • Focus on reducing cancellation rates                 │
│ • Improve first-call resolution metrics                │
│ • Balance workload distribution                        │
│                                                         │
│ [📧 EMAIL TEAM REPORT] [📋 INDIVIDUAL FEEDBACK] [📊 EXPORT] │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints for Call Center Manager Panel

### Authentication APIs
```javascript
// Manager login
POST /api/manager/auth/login
{
  "manager_id": "MGR001",
  "password": "manager_password",
  "workstation_id": "WS-MGR-001"
}

// Get manager permissions
GET /api/manager/auth/permissions

// Update manager session
PUT /api/manager/auth/session
{
  "status": "active" | "away" | "offline"
}
```

### Dashboard Analytics APIs
```javascript
// Get dashboard metrics
GET /api/manager/dashboard/metrics?period=today

// Get performance trends
GET /api/manager/dashboard/trends?metric=confirmation_rate&period=week

// Get real-time statistics
GET /api/manager/dashboard/realtime

// Get team performance summary
GET /api/manager/dashboard/team-summary?date=2024-11-15
```

### Order Management APIs
```javascript
// Get all orders (manager view)
GET /api/manager/orders?status=all&agent=all&date=today

// Assign order to agent
POST /api/manager/orders/{order_id}/assign
{
  "agent_id": 5,
  "priority_level": "high",
  "manager_notes": "Customer prefers evening delivery",
  "expected_completion": "2024-11-16T18:00:00Z",
  "notify_agent": true
}

// Add manager note to order
POST /api/manager/orders/{order_id}/notes
{
  "note_text": "Customer mentioned specific delivery requirements",
  "note_type": "instruction",
  "is_urgent": false,
  "agent_id": 5
}

// Reassign order
PUT /api/manager/orders/{order_id}/reassign
{
  "from_agent_id": 3,
  "to_agent_id": 5,
  "reassignment_reason": "Workload balancing",
  "manager_notes": "Handle with priority"
}

// Bulk assign orders
POST /api/manager/orders/bulk-assign
{
  "orders": [
    {
      "order_id": 123,
      "agent_id": 5,
      "priority": "medium"
    },
    {
      "order_id": 124,
      "agent_id": 3,
      "priority": "high"
    }
  ]
}
```

### Agent Management APIs
```javascript
// Get all agents with current status
GET /api/manager/agents?status=all

// Get