# Delivery Module

This module provides comprehensive delivery management functionality for the CRM Fulfillment system, including courier management, delivery tracking, and status updates.

## Features

- **Dashboard**: Real-time metrics and overview of delivery operations
- **Order List**: Filterable list of deliveries with export capabilities
- **Assign Orders**: Assign orders to couriers and delivery companies
- **Courier Management**: Manage delivery companies and couriers
- **Tracking**: Track deliveries by tracking number with status history
- **Barcode Scanning**: Scan barcodes to quickly find and update deliveries
- **Status Updates**: Update delivery status with history tracking
- **API Endpoints**: JSON API for integration with barcode scanners and mobile apps

## Models

- **DeliveryCompany**: Delivery service provider details
- **Courier**: Delivery agent/personnel information
- **DeliveryRecord**: Main delivery tracking record linked to an order
- **DeliveryStatusHistory**: History of all status changes for auditing

## Views

### Main Views
- `dashboard`: Overview with metrics and recent deliveries
- `order_list`: List of all deliveries with filters and export
- `assign_orders`: Interface for assigning orders to couriers
- `courier_management`: Manage delivery companies and couriers
- `courier_detail`: View and edit individual courier details
- `delivery_tracking`: Track deliveries by tracking number
- `update_delivery_status`: Update delivery status with notes and location
- `barcode_scan`: Interface for scanning barcodes

### API Views
- `barcode_scan_api`: JSON API for barcode scanning
- `get_couriers_by_company`: JSON API to get couriers filtered by company

## Template Tags

The module includes custom template tags in `delivery_tags.py`:

- `status_badge_class`: Returns CSS classes for status badges
- `priority_badge_class`: Returns CSS classes for priority badges
- `estimated_delivery_status`: Determines if delivery is on time, delayed, etc.
- `delivery_stats`: Returns common delivery statistics

## Signals

The module includes signal handlers that automatically:

- Create delivery records when new orders are created with relevant statuses
- Sync order status with delivery status when appropriate
- Update order status when delivery status changes

## Forms

- `DeliveryRecordForm`: Create/edit delivery records
- `StatusUpdateForm`: Update delivery status with notes
- `CourierForm`: Create/edit couriers
- `DeliveryCompanyForm`: Create/edit delivery companies
- `AssignmentForm`: Assign orders to couriers

## Usage

1. Access the delivery dashboard at `/delivery/`
2. Manage orders and deliveries at `/delivery/orders/`
3. Assign orders to couriers at `/delivery/assign/`
4. Track deliveries at `/delivery/track/` or `/delivery/track/<tracking_number>/`
5. Update delivery status at `/delivery/update-status/<delivery_id>/`
6. Scan barcodes at `/delivery/scan/`
7. Manage couriers at `/delivery/couriers/` 