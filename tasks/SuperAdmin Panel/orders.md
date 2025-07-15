# Orders Page Update

## Overview
This document outlines the required updates to the existing "Orders" page (`/orders/`) of the application.

## Required Changes

### Orders Table Columns
The main orders table should display the following columns:
- **Order Code:** A unique identifier for the order
- **Customer:** The name of the customer who placed the order
- **Date:** The date when the order was placed
- **Product:** The name of the product(s) ordered (if multiple, consider displaying the first few or indicating the number of items)
- **Quantity:** The total quantity of the product(s) in the order
- **Price Per Unit:** The price of a single unit of the product
- **Seller:** The name of the seller who is selling the product(s) in the order
- **Status:** The current status of the order (e.g., Pending, Processing, Shipped, Delivered, Cancelled)

### Order Details View
- Clicking on any order row in the table should expand or navigate to a detailed view of that specific order
- This detailed view should display all the information visible in the table, plus the following additional details:
  - **Customer Details:**
    - Customer Name
    - Customer Phone Number
  - **Seller Details:**
    - Seller Name
    - Seller Phone Number
    - Seller Email
    - Link to the Store (of the seller for this order)
  - **Total Price:** Calculated as "Price Per Unit" multiplied by "Quantity"

### Add New Order Functionality
- An "Add New Order" button should be present on the page
- Clicking this button should lead to a form where administrators can manually input all the information required for a new order, mirroring the columns in the orders table:
  - Order Code
  - Customer
  - Date
  - Product
  - Quantity
  - Price Per Unit
  - Seller
  - Status

### Import Orders Functionality
- An "Import Orders" button should also be available on the page
- Clicking this button should allow administrators to import order data in a supported format (e.g., CSV, Excel)

### Search and Filter
- A search bar should be implemented above the orders table to allow users to search for orders based on any of the displayed columns (e.g., order code, customer name, product name)
- Filtering options should also be provided above the table, allowing users to filter orders based on specific criteria, such as:
  - Status (dropdown with different order statuses)
  - Date Range (date picker to select a period)
  - Seller (dropdown to filter by seller)
