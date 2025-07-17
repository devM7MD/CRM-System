# Seller Panel: Sourcing Page

## Overview
The Sourcing page enables sellers to submit product sourcing requests directly to CRM administrators through a streamlined interface. This page serves as the primary gateway for sellers to request new products, specify sourcing requirements, and initiate the procurement workflow that integrates seamlessly with the admin order management system.

## Navigation
- **URL**: `/seller/sourcing/`
- **Access**: Seller Panel sidebar navigation
- **Authentication**: Seller-only access with session validation
- **Data Scope**: Sourcing requests filtered to current logged-in seller only

---

## Page Structure

### Page Header
A clear header section providing context and guidance to sellers about the sourcing process, including current request statistics and helpful information about the sourcing workflow.

### Sourcing Request Form
The primary interface component allowing sellers to submit detailed sourcing requests to CRM administrators.

#### Required Form Fields

**Product Name**
- **Type**: Text input (required)
- **Max Length**: 255 characters
- **Placeholder**: "Enter product name (e.g., iPhone 15 Pro Max)"
- **Validation**: Required field with proper character limits
- **Help Text**: Provide clear, specific product name including model numbers if applicable

**Carton Quantity**
- **Type**: Number input (required)
- **Range**: 1 to 10,000 cartons
- **Display**: Input with "cartons" suffix
- **Validation**: Must be positive integer
- **Help Text**: Specify quantity in cartons/boxes. Standard carton sizes vary by product.

**Source Country (Country of Origin)**
- **Type**: Dropdown select (required)
- **Options**: China, India, Thailand, Vietnam, Malaysia, South Korea, Japan, Other
- **Default**: No selection
- **Validation**: Must select valid country
- **Help Text**: Select the country where you want the product to be sourced from

**Destination Country (Target Country)**
- **Type**: Dropdown select (required)
- **Options**: UAE, Saudi Arabia, Kuwait, Qatar, Bahrain, Oman, Egypt, Jordan, Other
- **Default**: No selection
- **Validation**: Must select valid destination
- **Help Text**: Select the country where the product should be delivered

**Funding Source**
- **Type**: Radio button group (required)
- **Options**: 
  - "Seller's Funds" - I will finance this sourcing request
  - "CRM Funding Request" - Request CRM to finance this sourcing
- **Validation**: Must select one option
- **Help Text**: Choose how this sourcing request will be financed

#### Optional Form Fields

**Supplier Name (Optional)**
- **Type**: Text input
- **Max Length**: 255 characters
- **Purpose**: Allow sellers to specify preferred suppliers
- **Help Text**: If you have a preferred supplier, provide their company name

**Supplier Phone Number (Optional)**
- **Type**: Phone input with international format support
- **Validation**: Valid phone number format with country code
- **Help Text**: Include country code for international numbers

**Product Description**
- **Type**: Textarea
- **Max Length**: 1000 characters
- **Rows**: 4
- **Character Counter**: Real-time character count display
- **Purpose**: Detailed product specifications and requirements

**Target Unit Price (Optional)**
- **Type**: Number input with currency selector
- **Currency Options**: USD, AED, SAR
- **Step**: 0.01 for decimal precision
- **Purpose**: Help administrators understand pricing expectations

**Quality Requirements**
- **Type**: Checkbox group
- **Options**: Brand New Only, Original Packaging Required, Warranty Required, Certified Products Only
- **Purpose**: Specify quality standards and requirements

**Special Instructions/Notes**
- **Type**: Textarea
- **Max Length**: 500 characters
- **Purpose**: Additional requirements or special handling instructions

---

## Request Submission and Workflow

### Form Submission Process

#### Client-Side Validation
- **Required Fields**: All mandatory fields must be completed
- **Format Validation**: Phone numbers, prices, and text lengths validated
- **Business Rules**: Quantity limits, valid country combinations
- **Real-time Feedback**: Immediate validation messages for user guidance

#### Submit Request Button
- **Location**: Prominent placement at bottom of form
- **States**: Default, Loading, Success, Error
- **Action**: Triggers form validation and submission process
- **Confirmation**: Success message with request reference number

#### Draft Functionality
- **Save as Draft**: Allow sellers to save incomplete requests
- **Auto-save**: Periodic automatic saving of form data
- **Draft Management**: List and resume saved drafts

### Admin Notification System

#### Immediate Notification
- **Email Alert**: Instant email notification to CRM administrators
- **Dashboard Notification**: Real-time notification in admin panel
- **Request Details**: Complete request summary in notification
- **Urgency Indicators**: Priority flags based on request characteristics

#### Admin Review Process
- **Review Queue**: Centralized queue for pending sourcing requests
- **Request Details**: Complete view of all submitted information
- **Approval Actions**: Approve, Reject, or Request More Information
- **Communication**: Built-in messaging system for clarifications

### Post-Approval Workflow

#### Automatic Order Creation
- **Order Generation**: Approved requests automatically create entries in Admin Orders list
- **Data Transfer**: All relevant request data transferred to order record
- **Status Tracking**: Request status updates to "Approved - Order Created"
- **Reference Linking**: Maintain connection between original request and generated order

#### Order Integration
- **Order Details**: Product name, quantities, sourcing specifications
- **Supplier Information**: Preferred supplier data if provided
- **Funding Source**: Payment responsibility clearly indicated
- **Delivery Requirements**: Source and destination country information

---

## Request Management and Tracking

### Seller Request History

#### Request List Table
Display all submitted requests with key information in a sortable, filterable table:

| Column | Description | Width | Sortable |
|--------|-------------|--------|----------|
| Request ID | Unique identifier | 120px | Yes |
| Product Name | Requested product | 200px | Yes |
| Quantity | Carton quantity | 100px | Yes |
| Source Country | Origin country | 120px | Yes |
| Destination | Target country | 120px | Yes |
| Status | Current status | 130px | Yes |
| Submitted Date | Request date | 120px | Yes |
| Actions | View/Edit options | 100px | No |

#### Status Categories
- **Draft**: Saved but not submitted
- **Submitted**: Pending admin review
- **Under Review**: Being evaluated by administrators
- **Approved**: Approved and converted to order
- **Rejected**: Not approved with reasons
- **More Info Needed**: Requires additional information

#### Request Details View
- **Complete Information**: All submitted form data
- **Status History**: Timeline of status changes
- **Admin Comments**: Feedback or questions from administrators
- **Related Order**: Link to generated order if approved

### Communication System

#### Request Messages
- **Admin Questions**: Built-in messaging for clarifications
- **Status Updates**: Automated notifications for status changes
- **Approval Notifications**: Confirmation when request is approved
- **Rejection Reasons**: Clear explanation when request is declined

---

## Technical Implementation

### Frontend Architecture

#### Component Structure
```
SourcingPage/
├── SourcingHeader/
├── SourcingRequestForm/
│   ├── ProductInfoSection/
│   ├── SourcingDetailsSection/
│   ├── SupplierInfoSection/
│   └── FormActions/
├── RequestHistoryTable/
│   ├── RequestRow/
│   ├── StatusBadge/
│   └── ActionButtons/
└── RequestDetailsModal/
```

#### State Management
Centralized state management for form data, request history, validation states, and submission status.

#### Form Validation
- **Client-side**: Immediate validation feedback
- **Server-side**: Backend validation for security and data integrity
- **Progressive Enhancement**: Form works without JavaScript

### Backend Requirements

#### API Endpoints
- `POST /api/seller/sourcing/requests` - Submit new request
- `GET /api/seller/sourcing/requests` - List seller's requests
- `GET /api/seller/sourcing/requests/{id}` - Get request details
- `PUT /api/seller/sourcing/requests/{id}` - Update draft request
- `DELETE /api/seller/sourcing/requests/{id}` - Delete draft request

#### Database Schema

**Sourcing Requests Table**
- Primary keys, foreign keys to sellers and orders
- All form fields as appropriate data types
- Status tracking and timestamps
- Admin review fields and comments

**Request Status History Table**
- Track all status changes with timestamps
- Admin actions and comments
- Audit trail for compliance

#### Integration Points
- **Order Management**: Automatic order creation upon approval
- **User Management**: Seller authentication and authorization
- **Notification System**: Email and in-app notifications
- **File Storage**: Support for product images or documents

### Security and Access Control

#### Authentication Requirements
- **Seller Authentication**: Valid seller session required
- **Data Isolation**: Sellers only see their own requests
- **Role-based Access**: Different permissions for sellers vs admins

#### Data Validation
- **Input Sanitization**: Prevent XSS and injection attacks
- **Business Rules**: Validate quantity limits, country combinations
- **Rate Limiting**: Prevent spam requests

---

## User Experience Features

### Form Usability
- **Progressive Disclosure**: Show relevant fields based on selections
- **Auto-complete**: Smart suggestions for product names and suppliers
- **Real-time Validation**: Immediate feedback on field completion
- **Mobile Optimization**: Responsive design for mobile devices

### Loading States and Feedback
- **Form Submission**: Clear loading indicators during submission
- **Success Messages**: Confirmation with request reference number
- **Error Handling**: Clear error messages with resolution guidance
- **Auto-save Indicators**: Visual feedback for draft saving

### Accessibility Features
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **High Contrast**: Accessible color schemes
- **Focus Management**: Clear visual focus indicators

---

## Performance and Scalability

### Optimization Strategies
- **Form Caching**: Cache dropdown options and country lists
- **Lazy Loading**: Load request history on demand
- **Image Optimization**: Compress uploaded product images
- **API Response Caching**: Cache static reference data

### Scalability Considerations
- **Database Indexing**: Proper indexes for seller queries
- **File Storage**: Scalable storage for attachments
- **Background Processing**: Queue-based request processing
- **Load Balancing**: Support for high-volume request submissions

---

## Monitoring and Analytics

### Key Metrics
- **Request Volume**: Daily/monthly request submissions
- **Approval Rates**: Percentage of requests approved
- **Processing Time**: Average time from submission to approval
- **Popular Products**: Most requested product categories
- **Geographic Patterns**: Source and destination trends

### Business Intelligence
- **Request Analytics**: Insights into seller sourcing patterns
- **Supplier Analysis**: Performance of preferred suppliers
- **Market Trends**: Popular products and regions
- **Conversion Tracking**: Request to order conversion rates

---

## Future Enhancements

### Advanced Features
- **Bulk Requests**: Submit multiple product requests simultaneously
- **Template System**: Save and reuse common request patterns
- **Price Comparison**: Integration with supplier pricing APIs
- **Automated Sourcing**: AI-powered supplier matching
- **Real-time Chat**: Live communication with administrators

### Integration Expansions
- **Supplier Portal**: Direct integration with supplier systems
- **Logistics Integration**: Shipping and customs integration
- **Payment Gateway**: Direct payment processing for approved requests
- **Market Intelligence**: Real-time market pricing and availability

### Business Process Improvements
- **Workflow Automation**: Automated approval for standard requests
- **Smart Routing**: Route requests to specialized procurement teams
- **Predictive Analytics**: Forecast demand and optimize sourcing
- **Quality Scoring**: Rate and track supplier performance