# Finance Page Update

## Overview
This document outlines the required updates to the "Finance" page (`/finance/`) of the application to manage order payments and associated fees.

## Required Changes

### Order List Table
The main section of the "Finance" page will display a table of orders with the following columns:
- **Order Code:** The unique identifier for the order
- **Date:** The date when the order was placed
- **Product:** The name of the product(s) in the order
- **Quantity:** The total quantity of the product(s) in the order
- **Price per Unit:** The selling price of a single unit of the product
- **Seller:** The name of the seller for this order
- **Status (Payment Status):** The current payment status of the order (e.g., Paid, Postponed, Pending Payment). This status should be editable by the administrator
- **Total Fees:** The sum of all applicable fees for this order
- **Total Price:** The final price of the order, calculated as `(Quantity × Price per Unit) + Total Fees`
- **Actions:** A column containing a "View Invoice" icon

### Invoice Generation
- Clicking the "View Invoice" icon in the "Actions" column should generate and display an invoice for the corresponding order
- The invoice should include all the information displayed in the order list table, plus the **Payment Method** used for that order

### Fees Details
- When the administrator clicks on the "Total Fees" value for a specific order, a detailed breakdown of the fees for that order should be displayed. This could be a modal or an expanded section
- The fee details should include:
  - Upsell Fees
  - Confirmation Fees
  - Cancellation Fees
  - Fulfillment Fees
  - Shipping Fees
  - Return Fees
  - Warehouse Fees
- **Crucially, the administrator should be able to edit these individual fee amounts for each specific order.** The default fee values will be pulled from the settings, but they can be overridden here

### Add New Payment Functionality
- An "Add New Payment" button should be available on the page
- Clicking this button will lead to a form with the following steps:

#### 1. Seller Selection
- A dropdown menu containing a list of all sellers on the platform
- An option to search for a seller by name, which then populates the dropdown or displays the matching seller(s)
- Once a seller is selected, an order list for that specific seller should be displayed below
- **Optional Filtering by Warehouse:** An additional dropdown to filter the seller's order list by selecting an existing warehouse

#### 2. Order Selection and Fee Input
- The order list for the selected seller (and optional warehouse filter) should allow the administrator to select the orders for which they want to record a payment. This could be through checkboxes next to each order
- For each selected order, fields should be available to:
  - Input or review the individual fee amounts (pre-populated with defaults but editable)
  - Set the **Payment Status** (dropdown: Paid, Postponed, Pending Payment)
  - Select the **Payment Method** (e.g., Bank Transfer, PayPal, etc.)

#### 3. Confirmation
- A "Confirm Payment" button to finalize the payment recording process for the selected orders with the specified fees, statuses, and payment methods. This action should update the order list table accordingly
