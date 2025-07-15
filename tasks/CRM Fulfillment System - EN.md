# Users

### **USERS** 

### 

### **1\. Super Admin:**

Permissions:

* Full system control (add/delete users, manage permissions).  
* Create sub-roles (e.g., "Assistant Manager") with limited permissions (e.g., allow report review without modifying settings).  
* Manage RBAC (Role-Based Access Control) to restrict access precisely (e.g., prevent Stock Keepers from editing financial reports).  
* Enable an Audit Log system to record critical actions (e.g., user deletion, order status changes) with user and timestamp details.  
* Oversee all operations and resolve critical issues.

---

### **2\. Admin:**

Permissions:

* Review financial reports and overall performance.  
* Monitor daily operations (orders, inventory, shipping).  
* Restrict Stock Keepers from editing financial reports via RBAC.  
* Approve/Review Sourcing Requests submitted by Sellers.  
* Coordinate between roles (e.g., Seller, Stock Keeper, Delivery).

---

### **3\. Seller:**

Permissions:

* View general statistics (order count, inventory status).  
* Create orders via multiple formats :  
  * Support Excel, CSV, Google Sheets with automatic data validation (e.g., phone number checks).  
* Modify orders before confirmation , with automatic client notifications.  
* Submit Sourcing Requests to import goods or transfer products to company warehouses.  
* View real-time inventory and order status.  
* Access financial reports linked to their orders.

---

### **4\. Stock Keeper:**

Permissions:

* Manage products (add/remove) using barcode/RFID scanners for automatic inventory updates.  
* Receive and verify incoming products (quantity, type).  
* Organize product locations in the warehouse.  
* Receive automatic low-stock notifications when inventory reaches a threshold.  
* Prepare products for orders and hand them to Packaging.

---

### **5\. Call Center Manager:**

Permissions:

* Monitor agent performance (KPIs, response time).  
* Distribute orders via a smart algorithm based on workload or specialization.  
* Manage work schedules and handle escalations.  
* Review daily/weekly performance reports.

---

### **6\. Call Center Agent:**

Permissions:

* Confirm orders with clients and validate information.  
* Update order status ("Confirmed," "Canceled," etc.).

---

### **7\. PICK & PACK:**

Permissions:

* Receive products from Stock Keepers and package them.  
* Attach invoices and select delivery providers.  
* Hand over orders to Delivery and track delivery status.  
* Receive returned orders and restock them.

---

### **8\. Delivery:**

Permissions:

* Deliver orders via in-house drivers or third-party providers.  
* Auto-update delivery status via API integration with delivery companies.  
* Provide clients with real-time tracking links via SMS/email.

---

### **9\. Follow-up Dashboard:**

Permissions:

* View details of delivered orders (order ID, client, address, delivery status).  
* "Call" and "WhatsApp" buttons for direct client communication.  
* Update order status (Postponed, Failed Delivery, Delivered, Canceled).

---

### **10\. Accountant:**

Permissions:

* Manage payments (collect funds, pay shipping costs).  
* Integrate with external accounting software (e.g., QuickBooks).  
* Review Sourcing costs and generate financial reports.

---

### **11\. Sourcing:**

Permissions:

* Create and track Sourcing Requests.  
* Evaluate suppliers using a scoring system (quality, on-time delivery).  
* Update request statuses (Submitted, Approved, Completed).

# Registration Page

#### **Registration Page**

---

#### **Step 1: Personal Registration**

1. Full Name:  
   * Example: "Mohammed Abdullah".  
   * Instant Validation:  
     * Message: "Name must include at least two words" if only one word is entered.  
     * Block names with numbers or invalid symbols (e.g., Ahmed123).  
2. Email:  
   * Example: "example@domain.com ".  
   * Validation:  
     * Use validator.js to verify email format.  
     * Message: "A verification link will be sent to your email".  
3. Phone Number:  
   * Dropdown for country code (e.g., \+971 UAE, \+966 Saudi Arabia).  
   * Example beside the field: "+971501234567".  
   * Validation:  
     * Use libphonenumber-js to check number validity and digit count.  
     * Error message: "Ensure the number includes the country code (e.g., \+971501234567)".  
4. Password:  
   * Strength Requirements:  
     * Progress bar (Red/Yellow/Green) with criteria: uppercase, lowercase, numbers, symbols.  
     * Confirm Password field to avoid errors.  
     * "Show/Hide Password" button.  
5. "Next" Button:  
   * Disabled until all fields are valid.  
   * Error Summary: A banner at the top listing all invalid fields (e.g., "Please correct the highlighted fields").  
6. Additional Security:  
   * CAPTCHA (e.g., Google reCAPTCHA) to prevent bots.

---

#### **Step 2: Business Details**

1. Business Name:  
   * Example: "Abu Mohammed Restaurant \- Dubai".  
   * Allowed Symbols: Period (.) or hyphen (-) (e.g., "Shawarma.AL Restaurant").  
   * Blocked Symbols: @\#$%.  
2. Target Country:  
   * If the service is UAE-only:  
     * Message: "Service is currently available in the UAE only".  
     * Hide selection option.  
3. Residence (Seller’s Country):  
   * Searchable dropdown (e.g., UAE, Saudi Arabia).  
   * Warning: If different from target country: "Your residence must be in the target country to use the service".  
4. Expected Daily Orders:  
   * Slider: 0 to 1000 orders/day.  
     * Hint: "Average daily orders for our clients is 200".  
     * Allow manual input beside the slider.  
5. Marketing Platforms (Ad Types):  
   * Select platforms for promoting your products:  
     * 🌐 Google Ads .  
     * 🎥 TikTok Ads .  
     * 👥 Meta Ads (Includes Facebook and Instagram).  
6. Upload ID Document:  
   * Preview: Automatically display the image after upload.  
   * Instructions: "Image must be clear, showing front and back sides".  
   * Retry Button if upload fails.  
   * Allowed Formats: PNG, JPG (≤5MB).

---

#### **General Enhancements**

1. Progress Bar:  
   * Interactive (lights up green when a step is completed).  
   * Display progress percentage: "Step 1 of 2".  
2. "Previous" Button:  
   * Auto-save data when returning to edit.  
3. Final Confirmation Step:  
   * Display data in a table/cards with an "Edit" option for each section.  
4. Two-Step Verification:  
   * Send a verification code via email/SMS with a "Resend after 60 seconds" option.  
5. Responsive Design:  
   * Optimized for mobile with vertical field alignment.

---

#### **Custom Error Messages**

* Image Upload Failure:  
  "Invalid or unsupported image. Please upload a clear (PNG/JPG) file ≤5MB."  
* Budget Below Minimum:  
  "Daily budget must be at least 100 AED. Would you like to adjust the range?"  
* Invalid Phone Number:  
  "Ensure the number includes the country code (e.g., \+971501234567)."  
* 

# Seller

### **Seller** 

---

#### **Permissions and Responsibilities:**

1\. Seller Dashboard (General Statistics):

* Quick Stats:  
  * Total Sales and Profit (visible only if the seller sets the product’s purchase price ).  
  * Order Status:  
    * Count of orders (Ready/In Delivery/Completed/Canceled).  
  * Inventory Status:  
    * Total, available, and in-delivery quantities for each product (updated via Stock Keeper API ).  
* Visual Analytics:  
  * Daily/weekly sales analysis.  
  * Sales breakdown by Sales Channels (linked e-commerce stores).

---

2\. Product Management:

* Product Display:  
  * Product details:  
    * Name (Arabic/English), auto-generated product code (e.g., PROD-2023-001), total/available/in-delivery quantities, price, product image.  
  * Integration with Stock Keeper:  
    * Real-time inventory updates.  
    * Warning : Shown if the requested order quantity exceeds available stock.  
* Adding New Products:  
  * Required Fields:  
    * Name (Arabic/English), description, selling price , purchase price (optional) , image (PNG/JPG ≤5MB), product link.  
  * Automation:  
    * Product Code : Auto-generated (e.g., PROD-2023-001).  
    * Duplicate Name Check : Verify the product name doesn’t already exist in the system.

---

3\. Sales Channels:

* Add/Remove E-commerce Store:  
  * Fields:  
    * Store name (Arabic/English), URL, country.  
  * API Integration:  
    * Auto-import orders from the store to AS System.  
  * Notifications:  
    * On success: “Store linked successfully.”  
    * On failure: “Linking error: Check URL or API credentials.”

---

4\. Order Creation:

* Two Methods:  
  * Manual Entry:  
    * Form with data validation (phone number, quantity).  
    * Warning : Shown if the requested quantity exceeds stock.  
  * Excel Upload:  
    * Template with columns:  
      * Product Code , quantity, customer name, phone, address.

---

5\. Sourcing Requests:

* Creating a Sourcing Request:  
  * Required Fields:  
    * Product Name : Selected from a searchable dropdown (managed by Admin).  
    * Carton Quantity : Number of cartons.  
    * Source : Country of origin or primary supplier.  
    * Destination : Target country (e.g., UAE, Saudi Arabia).  
    * Finance From : Funding source (seller’s account/company account).  
    * Sourcing Agent : Selected from approved suppliers.  
    * Agent Phone : Validated via libphonenumber-js.  
    * Weight : For shipping cost calculation.  
* Workflow:  
  * Instant notification to the Sourcing Department for review.  
  * Auto-update status :  
    Submitted → Approved/Rejected → Completed.  
  * Notification to Accountant upon approval for cost deduction.  
* Enhancements:  
  * Auto-generated Tracking Number (e.g., TRK-2023-001) upon approval.  
  * Priority Level : Normal / Urgent.  
  * Shipping Cost Calculation : Based on weight and destination (integrated with Delivery Department ).

---

6\. Finance Section:

* Financial Dashboard:  
  * Daily/Monthly Revenue with filters by store or product.  
  * Reports:  
    * Export to Excel/PDF with auto-scheduling.  
    * Profit Analysis : Visible only if purchase price is set.

---

### **Integration with Other Departments:**

* Sourcing Department:  
  * Filter suppliers by destination to avoid incompatible shipments.  
* Stock Keeper:  
  * Auto-update quantities when shipments are received.  
* Delivery Department:  
  * Calculate shipping costs based on weight and destination.

---

### **Security Enhancements:**

* Access Restrictions:  
  * Sellers cannot edit selling price or funding source after order creation without Admin approval .  
  * Encryption of e-commerce store links and Sourcing Agent details.  
* Audit Log:  
  * Track changes to sourcing requests with mandatory reason (for Admin/Sourcing).

---

### **Final Notes:**

* Simplified Sourcing Requests:  
  * Limited to product name (from a managed dropdown) to avoid incomplete data.  
  * Full product details (price, image, specs) added later by Sourcing Department post-approval.  
* Data Validation:  
  * Ensure weight does not exceed limits (e.g., 50kg/carton).  
  * Alert Admin if purchase price exceeds budget.  
* Multilingual Support:  
  * Request details written in the target country’s language (Arabic/English).

# Sourcing

### **Sourcing Role** 

---

#### **Core Responsibilities:**

1. Creating & Managing Sourcing Requests:  
   * Generate new sourcing requests with an auto-generated Request ID (e.g., SOR-2023-001).  
   * Track requests through completion, updating statuses:  
     Submitted → Under Review → Approved/Rejected → Completed.  
   * With the ability to upload photos of the product and shipment label   
   * Prepare periodic reports on delivery times, material quality, and supplier costs .

---

#### **Dashboard:**

* Key Performance Indicators (KPIs):  
  * Approval Rate : % of approved requests.  
  * Average Processing Time : From creation to completion.  
  * Top 3 Suppliers : Based on speed or quality.  
* Filters:  
  * Time period, supplier name, request status.  
* Visuals:  
  * Bar Chart : Distribution of request statuses.  
  * Line Chart : Monthly completion rate trends.

---

#### **Financial Section (Enhanced Fields):**

| Field | Details |
| ----- | ----- |
| Request No | Auto-generated (e.g.,SOR-2023-001). |
| SKU | Auto-linked to product for tracking. |
| Payment Status | Options:Pending→Partially Paid→Paid→Overdue. |
| Payment Method | Select method (Bank Transfer, PayPal, etc.). |
| Due Date | Payment deadline with automated reminders for delays. |

---

#### **Integration with Other Departments:**

1. Inventory Sync:  
   * Auto-update inventory when status changes to Completed.  
   * Smart Notifications :  
     * Alert Stock Keeper upon product receipt with shelf location details .  
   * Quality Check :  
     * Mandatory review by Stock Keeper before closing the request.  
2. Accounting Sync:  
   * Auto-send Amount to Finance and link invoices directly in the system.  
3. Audit Log:  
   * Track changes to Status or Amount with:  
     * Username, timestamp, mandatory reason for change .  
   * Security Alerts : Notify Super Admin if Amount is modified by \>10%.

---

#### **Reports:**

* Features:  
  * Export to Excel/PDF/Power BI .  
  * Scheduled Reports : Auto-email weekly/monthly summaries.  
  * Cost vs. Budget Report : Analyze deviations.

---

#### **Automated Notifications:**

* Channels:  
  * Email, SMS, WhatsApp, and in-system alerts.  
* Escalation Alerts:  
  * Notify Admin if no response to a request within 24 hours.

---

#### **Enhanced Workflow:**

\+-------------------+       \+-------------------+       \+-------------------+  
| Create Sourcing   | → | Review by Admin   | →       | Approve/Reject?    |  
| Request           |       | (Budget Check)     |       | Yes/No             |  
\+-------------------+       \+-------------------+       \+-------------------+  
                                                                 |  
                                                                 ↓  
                                                        \+-------------------+  
                                                        | Send to Supplier  |  
                                                        | with Auto-PO No.  |  
                                                        \+-------------------+  
                                                                 |  
                                                                 ↓  
                                                        \+-------------------+  
                                                        | Quality Check by  |  
                                                        | Stock Keeper      |  
                                                        \+-------------------+  
                                                                 |  
                                                                 ↓  
                                                        \+-------------------+  
                                                        | Update Status to  |  
                                                        | "Completed"       |  
                                                        \+-------------------+  
                                                                 |  
                                                                 ↓  
                                                        \+-------------------+  
                                                        | Update Inventory  |  
                                                        | & Process Payment |  
                                                        \+-------------------+  
                                                                 |  
                                                                 ↓  
                                                        \+-------------------+  
                                                        | Generate Final    |  
                                                        | Report & Notify   |  
                                                        \+-------------------+

---

#### **Security Enhancements:**

* Access Restrictions:  
  * Prevent Sourcing from editing SELLER ID or Amount after submission.  
  * Only Super Admin can delete requests.

---

# Stock Keeper

### **Stock Keeper** 

---

#### **Objective:**

Efficiently manage products in the warehouse to ensure availability when needed and accurately prepare orders for the Packaging department.  
---

### **Core Permissions:**

#### **1\. Inventory Management:**

* Add/Remove Products:  
  * Register new products by scanning barcodes (auto-fetches data).  
  * Remove damaged products with a mandatory "Reason for Removal" field (e.g., "Broken during storage").  
* Update Quantities:  
  * Adjust quantities based on orders or returns.  
  * Support Batch Tracking for expiration dates.

#### **2\. Receiving New Shipments:**

* Verification:  
  * Scan barcodes of incoming shipments from Sourcing .  
  * Ensure quantities and product types match the original order.  
* Auto-Registration:  
  * Automatically update the status to "Received in Warehouse" with the employee’s name and timestamp.  
  * Automated Notifications:  
    * Alert Sourcing if quantities mismatch.

#### **3\. Warehouse Organization:**

* Dynamic Storage System:  
  * Automatically relocate products based on demand rates (e.g., high-selling items placed near Packaging).  
* Interactive Warehouse Map:  
  * Display product locations with color coding:  
    * Red: Low-stock products.  
    * Green: Sufficiently stocked products.

#### **4\. Order Preparation:**

* Barcode Verification:  
  * Scan barcodes to validate product accuracy.  
* Status Update:  
  * Automatically change order status to "Ready for Packaging" upon delivery.  
  * In-system notification to Packaging department.

---

### **Key System Components:**

#### **1\. Inventory Dashboard:**

* KPIs:  
  * Inventory Accuracy Rate (actual vs. recorded quantities).  
  * Average Order Preparation Time .  
  * Error Rate in order fulfillment.  
* Smart Alerts:  
  * Instant notifications for low stock or expiring batches.  
* Interactive Warehouse Map:  
  * Visualize product locations with color indicators (Red/Green).

#### **2\. Warehouse Management:**

* Add/Edit/Delete Warehouses:  
  * Create, modify, or remove warehouses.  
  * Assign specific locations within warehouses (e.g., Shelf "C1", Zone "B").  
* Transfer Products Between Warehouses:  
  * Manual Transfer: Select product, quantity, and target warehouse.  
  * Auto-Suggest Transfers: Recommend transfers when stock is low in a specific warehouse.  
* Multi-Warehouse View:  
  * Display total product quantities across all warehouses.  
* Usage Reports:  
  * Turnover Rate per warehouse.

#### **3\. Inventory Log:**

* Reference Field:  
  * Link transactions to Sourcing Requests (e.g., "Sourcing Request \#SOR-2023-001").

---

### **Integration with Other Departments:**

1. With Sourcing:  
   * Auto-update Sourcing Request status to "Received in Warehouse" .  
2. With Packaging:  
   * Send in-system notifications when orders are ready for packaging.

---

### **Enhanced Workflow:**

1\. Receiving New Shipments:  
   \- Scan barcode → Verify match → Assign warehouse/location → Update inventory → Notify Sourcing.

2\. Transferring Products:  
   \- Select product/quantity → Choose target warehouse → Update inventory in both warehouses.

3\. Preparing Orders:  
   \- Receive order → Scan barcode → Confirm quantity → Deliver to Packaging → Update status → Notify via system.

4\. Handling Returns:  
   \- Quality check → Restock if valid → Update inventory.

### **Security Enhancements:**

* Access Restrictions:  
  * Block Stock Keepers from editing Sourcing Request quantities.  
  * Allow Super Admin only to delete inventory records.

# Call Center Agent

### **Call Center Agent** 

---

#### **Responsibilities:**

1. Order Confirmation:  
   * Contact the customer via phone or WhatsApp to verify order details.  
   * Verify:  
     * Address, amount, and product details (linked to the Seller Dashboard ).  
   * Update Order Status:  
     * Confirmed: If the order details are verified.  
     * No Response: If the customer doesn’t answer the call or WhatsApp.  
     * Closed: If the customer’s number is unreachable.  
     * Postponed: With an option to specify the new delivery date chosen by the customer.  
     * Under Review: If the customer requests a follow-up later.  
     * Cancelled: With a reason for cancellation (e.g., incorrect information, customer refusal).

---

#### **Agent Interface:**

* Main Dashboard:  
  * Quick Stats:  
    * Total orders, confirmed, postponed, cancelled (with charts for percentages).  
  * New Orders List:  
    * Order details:  
      * Order Code (e.g., ORD-2023-001).  
      * Customer name, products (linked to Product Code from the seller).  
      * Address, price (matches the selling price in the system).  
  * Verification Tools:  
    * "Call" Button : To directly call the customer.  
    * "WhatsApp" Button : Sends an automated message with order details (e.g., "Hi, have you confirmed your order \#ORD-2023-001?").  
    * Update Status :  
      * Options: Confirmed / No Response / Closed / Postponed / Cancelled / Under Review.  
      * Cancellation Reason Field : Mandatory when selecting Cancelled.  
      * Postponement Date Field : Appears when selecting Postponed.

---

#### **3\. Call Log:**

* Customer Interaction Tracking:  
  * Record date and time of each call or message.  
  * Confirmation result (Confirmed / Cancelled / Escalated).  
  * Agent Notes :  
    * Example: "Customer requested to change the address to Abu Dhabi."

---

### **Integration with Other Roles:**

* With Seller:  
  * Display the order price registered by the seller (cannot be modified).  
* With Stock Keeper:  
  * If the order is Confirmed, send details to Stock Keeper for preparation.  
* With Call Center Manager:  
  * Escalation Notifications : Pending orders (Under Review or Escalated) are sent to the manager.

---

### **Notes and Improvements:**

1. Prevent Data Conflicts:  
   * The agent cannot modify the order price or product code (only view data from the seller).  
2. Automated WhatsApp Messages:  
   * Use pre-defined templates (e.g., "Hello {Customer Name}, have you confirmed your order details?").  
3. Enhanced Call Log:  
   * Integrate with Audit Log to track any changes in order status.  
4. Multilingual Support:  
   * Send messages in Arabic or English based on the customer’s preferred language (set by the seller).

---

# Call Center Manger

### **Call Center Manager** 

---

#### **Permissions:**

1. Performance Monitoring:  
   * KPIs (Key Performance Indicators):  
     * Successful confirmation rate.  
     * Average response time to customers.  
     * Percentage of orders cancelled due to incorrect data.  
   * Daily/Weekly Reports:  
     * Report on each agent’s performance (number of calls, outcomes).  
2. Handling Escalated Orders:  
   * Process orders marked as Under Review or Escalated by agents.  
   * Options:  
     * Reassign the order to another agent.  
     * Cancel the order with a reason.  
3. Order Distribution:  
   * Distribution Algorithm:  
     * Assign orders to agents based on current workload or specialization (e.g., UAE orders to specific agents).  
4. Quality Improvement:  
   * Review Agent Notes:  
     * Analyze reasons for cancellations or postponements to improve seller processes.

---

#### **Integration with Other Roles:**

* With Admin:  
  * Send weekly reports on cancelled or escalated orders .  
* With Seller:  
  * Notify sellers of recurring issues (e.g., unclear addresses).

# Packaging

### **Packaging Department** 

---

#### **Responsibilities:**

1. Receiving Products from Stock Keeper:  
   * Barcode Verification : Scan to match order details (quantity, type, serial).  
   * Auto-Update Status : Change to "Packaging in Progress" after receipt.  
   * Audit Log : Record employee name and timestamp.  
2. Order Packaging & Invoicing:  
   * Secure Packaging : Use materials based on product type (e.g., padded boxes for electronics).  
   * Unique Barcode Generation :  
     * Includes Order ID , product details (quantity, price, seller).  
   * Printing : Barcode on invoice and package.  
3. Delivery Partner Selection:  
   * From a Predefined List :  
     * Companies added by Admin (e.g., Aramex, SMSA, Fetchr).  
     * Performance Integration : Show delivery success rates and delays.  
4. Handover to Delivery:  
   * Integration :  
     * Delivery scans barcode → status updates to "Ready for Delivery" .  
5. Returns Management:  
   * Return Process :  
     * Scan returned order → classify as "Resellable" or "Damaged" .  
     * Update status to "Returned" with reason (e.g., damaged product).

---

#### **Integration with Other Departments:**

* Finance :  
  * No automatic packaging cost deduction (managed by Admin later).  
* Admin :  
  * Permissions :  
    * Only Admin can delete packaging records or edit orders.  
    * 

# Follow-up

### **Follow-up Department**

#### 

#### 

#### **Permissions:**

1. Order Data Access:  
   * View details: Order Code, customer name, address, products, quantity, price , notes , delivery status.  
2. Restricted Edits :  
   * Modify Price/Quantity :  
     * Allowed only for specific reasons (e.g., order errors, special offers).  
     * Auto-notification to Finance and Seller upon modification.  
   * Update Status :  
     * Postponed / Delivery Failed / Delivered / Canceled.

---

#### **Key Components:**

* "Modify Order" Button :  
  * Visible only for justified cases.  
  * Mandatory "Reason" Field : To log the modification cause.  
* "Cancel Modification" Button :  
  * Revert changes if Finance rejects the update.

---

#### **Integration:**

* With Finance :  
  * Modified price/quantity requires Finance approval.  
* With Seller :  
  * Notify Seller of changes to avoid future errors.  
  * 

# Delivery

### **Delivery Department \- AS System**

---

#### **1\. Delivery Dashboard:**

* Stats :  
  * Total orders, in delivery, completed, canceled, returned.  
  * Success Rate : (Completed / Total) × 100%.  
* Visuals :  
  * Pie Chart : Distribution between internal/external couriers.  
  * Interactive Map : Orders per region (Dubai: 50, Abu Dhabi: 30).

---

#### **2\. Order List:**

![][image1]  
---

#### **3\. Assign Orders:**

* Features :  
  * Auto-assign based on driver location and performance metrics .  
  * Priority Filter : Assign urgent orders first.

---

#### **4\. Update Orders:**

* Status Updates :  
  * Preparing → Shipped → Delivered.  
  * Canceled/Returned with mandatory reason .  
* Audit Log :  
  * Track changes with employee name , timestamp, and old/new status.

---

#### **5\. Delivery Companies:**

* Performance Reports :  
  * Success Rate : Daily/weekly delivery success %.  
  * Cost Analysis : Compare delivery costs between companies.

---

#### **6\. Finance Integration:**

* Auto-Deduct :  
  * Delivery costs are deducted from the seller/company account upon "Delivered" status.  
  * 

# Accountant

### **Accountant Role** 

---

#### **Permissions:**

* Financial Stats :  
  * Total sales, completed/canceled orders, delivery fees, credit balances.  
* Payment Management :  
  * Process customer payments (Cash/Online).  
  * Pay delivery/supplier costs.  
* Refund Handling :  
  * Approve/reject refunds based on policies.

---

#### **Key Components:**

1. Finance Dashboard :  
   * Quick Stats : Total sales, refunds, delivery costs, credit limits.  
   * Charts : Cost vs. revenue, payment method distribution.  
2. Payment List :  
   * Table Columns :  
     * Order Code, Seller, Area, Customer Name, Price, Payment Method, Status, Delivery Fees, Refund Status.  
   * Actions :  
     * Filter by date, method, or status.  
     * Export to Excel/PDF.  
3. Fees Management :  
   * Seller Fees :  
     * Set % fees per seller (e.g., 5% per order).  
     * Total Price : Auto-calculated (price × quantity \+ fees).  
4. Sourcing Integration :  
   * Track supplier costs and link to inventory updates.  
5. Credit Management :  
   * Customer Credit Limits : Set maximum thresholds (e.g., 5,000 AED).  
   * Alerts : Notify when limits are exceeded.  
6. Refunds :  
   * Auto-Refund : Process via original payment method.  
   * Reports : Monthly refund count and reasons.  
   * 

# Admin

### **1\. Manager (Admin) Role**

Objective :  
Oversee daily operations, coordinate departments, and ensure smooth workflows.  
Permissions :

* Order Management :  
  * Edit orders exceptionally (e.g., address correction).  
  * Reset passwords for non-sensitive roles (e.g., Call Center Agents).  
* Department Supervision :  
  * Monitor Call Center , Packaging , and Delivery performance.  
  * Approve/Reject sourcing requests from sellers.

Responsibilities :

* Escalation Handling :  
  * Resolve issues escalated from Call Center or Delivery .  
* Quality Assurance :  
  * Verify inventory accuracy and order details.  
  * Review performance reports (e.g., delivery success rate).  
* Support :  
  * Assist sellers with API integrations (e.g., linking e-commerce stores).

Interface :

* Dashboard :  
  * Daily Stats : Sales, pending orders, return rates.  
  * Charts : Delivery performance by region, sourcing request statuses.  
* Order List :  
  * Filter by seller, status, or region.  
  * View Audit Log for individual orders.

---

### **Integration Between Roles**

| Feature | Super Admin | Admin |
| ----- | ----- | ----- |
| Delete Users | ✔️ (All roles) | ❌ (Only non-sensitive) |
| Modify Permissions | ✔️ (All roles) | ✔️ (Limited permissions) |
| Access Audit Logs | ✔️ (Full access) | ✔️ (Restricted to orders) |
| Approve Sourcing Requests | ✔️ (High-value orders) | ✔️ (Standard orders) |

# Super Admin

### **1\. General Manager (Super Admin) Role**

Objective :  
Full control over the system, user permissions, and security.  
Permissions :

* User Management :  
  * Create/Delete/Modify all roles (Admin, Seller, Call Center Agent, etc.).  
  * Assign custom permissions (e.g., restrict price edits for Sellers).  
* System-Wide Access :  
  * View all data (orders, inventory, sourcing, delivery, finance).  
  * Configure global settings (tax rules, account types, security protocols).  
* Security Oversight :  
  * Access full Audit Logs for all critical changes.  
  * Approve sensitive operations (e.g., inventory deletion, price overrides).

Responsibilities :

* System Monitoring :  
  * Review Audit Logs for suspicious activities (e.g., unauthorized deletions).  
  * Ensure compliance with security standards (GDPR, PCI-DSS).  
* Role Customization :  
  * Create new roles (e.g., "Inventory Supervisor", "Customer Support").  
* High-Level Approvals :  
  * Approve large sourcing requests or refunds exceeding limits.

Interface :

* Dashboard :  
  * System Metrics : Failed orders, security alerts, user activity.  
  * Charts : Performance trends, permission distribution.  
* Audit Log :  
  * Track who, when, and what changed (e.g., "Order ORD-2023-001 deleted by Admin X").

# General Settings

### **General Settings**

---

#### **1\. Countries Management**

* Permission : Super Admin only .  
* Components :  
  * Add/Delete Countries :  
    * Fields:  
      * Name (Arabic/English).  
      * Local currency (e.g., AED, SAR, USD).  
      * Timezone (e.g., GMT+4 for UAE).  
  * Integration with Finance :  
    * Auto-convert currencies using API (XE, OpenExchangeRates).  
  * Integration with Delivery :  
    * Link countries to allowed delivery companies.

---

#### **2\. Delivery Companies and Areas**

* Permission : Super Admin and Admin (view-only).  
* Components :  
  * Add/Delete Delivery Company :  
    * Fields:  
      * Name (Arabic/English).  
      * Countries of operation (e.g., UAE, Saudi Arabia).  
      * Base shipping cost (e.g., 50 AED for standard orders).  
      * API Key : For system integration (if applicable).  
  * Performance Reports :  
    * Success rate, average delivery time.

---

#### **3\. Users & Permissions**

* Permission : Super Admin only .  
* Components :  
  * Add New User :  
    * Fields:  
      * Name, email, role (Seller, Call Center Agent, etc.).  
    * Custom Permissions :  
      * Define access to specific sections (e.g., prevent sellers from editing prices).  
  * Manage Permissions :  
    * Table linking each role to allowed permissions (e.g., Admin → cannot delete orders).

---

#### **4\. Fees Management**

* Permission : Super Admin only .  
* Components :  
  * Types of Fees :  
    * Payment gateway fees (e.g., 2% per transaction).  
    * Shipping fees based on region or weight.  
    * Service fees for sellers (e.g., 5% commission per order).  
  * Integration with Finance :  
    * Auto-apply fees during invoice creation.  
    * Display total price (product price \+ fees) in order details.

---

#### **5\. Currencies Management**

* Permission : Super Admin and Admin (view-only).  
* Components :  
  * Supported Currencies :  
    * Add/remove currencies (AED, SAR, USD, etc.).  
    * Set base currency (e.g., AED).  
  * Integration with Finance :  
    * Auto-convert prices using API (XE, OpenExchangeRates).  
    * Display prices in the local currency for customers and the base currency in reports.

---

### **Integration with Other Roles**

| Setting | Super Admin Permission | Admin Permission |
| ----- | ----- | ----- |
| Add/Delete Countries | ✔️ | ❌ |
| Manage Delivery Companies | ✔️ | ✔️ (View-only) |
| Modify Permissions | ✔️ | ❌ |
| Manage Fees | ✔️ | ❌ |
| Manage Currencies | ✔️ | ✔️ (View-only) |

[image1]: <data:image/png;base64,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>