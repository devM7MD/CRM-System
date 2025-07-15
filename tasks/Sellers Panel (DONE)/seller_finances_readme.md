# Seller Panel: Finances Page

## Overview
The Finances page provides sellers with comprehensive oversight of their payment transactions and financial activities. This page serves as a centralized hub for payment monitoring, status tracking, and proof of payment management, enabling sellers to maintain accurate financial records and handle payment-related inquiries effectively.

## Navigation
- **URL**: `/seller/finances/`
- **Access**: Seller Panel sidebar navigation
- **Authentication**: Seller-only access with session validation
- **Data Scope**: Payments filtered to current logged-in seller's transactions only

---

## Page Structure

### Payments Overview Dashboard
A summary section at the top of the page displaying key financial metrics and quick insights.

#### Financial Summary Cards
- **Total Received**: Sum of all successfully received payments
- **Pending Payments**: Amount currently being processed or pending
- **Processing Payments**: Payments in active processing state
- **Monthly Revenue**: Current month's total received payments
- **Payment Count**: Total number of transactions

#### Dashboard Interface Design
```html
<div class="finances-overview-container">
  <div class="summary-cards">
    <div class="summary-card received">
      <h3>Total Received</h3>
      <span class="amount">$12,450.00</span>
      <span class="change">+8.2% from last month</span>
    </div>
    <div class="summary-card pending">
      <h3>Pending</h3>
      <span class="amount">$1,250.00</span>
      <span class="count">5 transactions</span>
    </div>
    <div class="summary-card processing">
      <h3>Processing</h3>
      <span class="amount">$650.00</span>
      <span class="count">2 transactions</span>
    </div>
  </div>
</div>
```

---

## Payments List Table

### Table Structure
The main interface displays all payments in a comprehensive table format with the following columns:

| Column | Type | Width | Description | Example | Sortable |
|--------|------|-------|-------------|---------|----------|
| **Payment ID** | String | 120px | Unique payment identifier | P001, P002 | Yes |
| **Date** | DateTime | 140px | Payment recorded date | 2024-01-15 14:30 | Yes |
| **Amount** | Currency | 120px | Payment amount | $150.00 | Yes |
| **Related Order(s)** | Link | 180px | Associated order references | Order #123, #124 | No |
| **Status** | Enum | 120px | Current payment status | Received, Pending | Yes |
| **Actions** | Button | 80px | View button/icon | View Details | No |

### Column Details

#### Payment ID
- **Format**: Alphanumeric identifier (P001, P002, etc.)
- **Generation**: Auto-generated unique identifier
- **Display**: Consistent formatting across the system
- **Search**: Searchable field for quick lookup

#### Date
- **Format**: YYYY-MM-DD HH:MM format or localized display
- **Timezone**: Display in seller's configured timezone
- **Sorting**: Chronological sorting (newest first by default)
- **Filtering**: Date range filtering capabilities

#### Amount
- **Display**: Currency symbol with proper formatting ($1,234.56)
- **Precision**: Two decimal places for currency accuracy
- **Multi-currency**: Support for different currencies if applicable
- **Sorting**: Numerical sorting from highest to lowest

#### Related Order(s)
**Single Order Display:**
```
Order #123
```

**Multiple Orders Display:**
```
Order #123, Order #124
Order #123, Order #124, +2 more
```

**Advanced Display Options:**
- **Links**: Clickable links to order details pages
- **Tooltip**: Show complete order list on hover for multiple orders
- **Optional Field**: May be empty if payment not linked to specific orders
- **Formatting**: Consistent order reference formatting

#### Status Categories
```javascript
const PAYMENT_STATUSES = {
  RECEIVED: "Received",           // Payment successfully processed
  PROCESSING: "Processing",       // Payment being processed by gateway
  PENDING: "Pending",            // Payment awaiting processing/verification
  FAILED: "Failed",              // Payment transaction failed
  REFUNDED: "Refunded"           // Payment has been refunded
};
```

**Status Display:**
- **Color Coding**: 
  - Received: Green (#28a745)
  - Processing: Blue (#007bff)
  - Pending: Orange (#ffc107)
  - Failed: Red (#dc3545)
  - Refunded: Purple (#6f42c1)
- **Icons**: Visual status indicators
- **Badges**: Rounded badge design for clear visibility

#### Actions Column
- **View Button**: Primary action for each payment row
- **Icon Design**: Eye icon or "View" text button
- **Hover States**: Clear hover indication
- **Accessibility**: Proper ARIA labels for screen readers

### Table Features

#### Sorting and Filtering
```javascript
// Filter and sort options
const tableOptions = {
  sorting: {
    default: { field: 'date', direction: 'desc' },
    options: ['payment_id', 'date', 'amount', 'status']
  },
  filtering: {
    status: ["All", "Received", "Processing", "Pending", "Failed", "Refunded"],
    dateRange: {
      start: null,
      end: null,
      presets: ["Today", "This Week", "This Month", "Last Month"]
    },
    amountRange: {
      min: null,
      max: null
    }
  },
  search: {
    fields: ['payment_id', 'related_orders'],
    placeholder: "Search by Payment ID or Order..."
  }
};
```

#### Pagination and Performance
- **Page Sizes**: 25, 50, 100 payments per page
- **Default**: 25 payments per page
- **Navigation**: Previous/Next with page numbers
- **Total Count**: Display total number of payments
- **Jump to Page**: Direct page navigation input

#### Interactive Features
- **Row Click**: Navigate to payment details view
- **Bulk Actions**: Select multiple payments for bulk operations
- **Export Function**: Export filtered results to CSV/Excel
- **Refresh**: Manual refresh button with loading indicator
- **Auto-refresh**: Optional periodic updates every 5 minutes

---

## Payment Details View

### Access Methods
- **Row Click**: Click any table row to view details
- **View Button**: Click the view action in the Actions column
- **Direct URL**: `/seller/finances/payments/{payment_id}`
- **Search Results**: Direct access from search functionality

### Detail View Options
- **Modal Dialog**: Overlay modal for quick viewing
- **Dedicated Page**: Full page view for comprehensive details
- **Side Panel**: Sliding panel from the right side

### Detailed Information Display

#### Payment Summary Section
```html
<div class="payment-details-container">
  <header class="payment-header">
    <h2>Payment Details</h2>
    <div class="payment-meta">
      <span class="payment-id">Payment ID: P001</span>
      <span class="status-badge received">Received</span>
    </div>
  </header>
  
  <section class="payment-summary">
    <div class="amount-display">
      <span class="currency">$</span>
      <span class="amount">150.00</span>
    </div>
    <div class="payment-date">
      Received on January 15, 2024 at 2:30 PM
    </div>
  </section>
</div>
```

#### Transaction Information
- **Payment Method**: How the payment was made (Bank Transfer, Credit Card, etc.)
- **Transaction Reference**: External transaction ID from payment processor
- **Processing Time**: Duration from initiation to completion
- **Fees**: Any processing fees deducted (if applicable)
- **Currency**: Payment currency and exchange rate (if different from base currency)

#### Related Orders Section
**Single Order Display:**
```html
<div class="related-orders">
  <h3>Related Order</h3>
  <div class="order-item">
    <a href="/seller/orders/ORD123" class="order-link">
      Order #ORD123
    </a>
    <span class="order-amount">$150.00</span>
    <span class="order-date">January 10, 2024</span>
  </div>
</div>
```

**Multiple Orders Display:**
```html
<div class="related-orders">
  <h3>Related Orders (2)</h3>
  <div class="orders-list">
    <div class="order-item">
      <a href="/seller/orders/ORD123">Order #ORD123</a>
      <span class="amount">$100.00</span>
    </div>
    <div class="order-item">
      <a href="/seller/orders/ORD124">Order #ORD124</a>
      <span class="amount">$50.00</span>
    </div>
  </div>
</div>
```

#### Payment Timeline
**Status History Display:**
```
● Received                    Jan 15, 2024 - 2:30 PM
  └─ Payment successfully processed and funds received

● Processing                  Jan 15, 2024 - 2:25 PM  
  └─ Payment submitted to processing gateway

● Pending                     Jan 15, 2024 - 2:20 PM
  └─ Payment initiated by customer
```

#### Notes and Comments
- **System Notes**: Automatically generated transaction notes
- **Seller Notes**: Custom notes added by the seller
- **Edit Functionality**: Ability to add or modify seller notes
- **Timestamp**: When notes were added or modified

---

## Proof of Payment Upload

### Upload Interface Location
The proof of payment upload functionality is prominently displayed within the payment details view.

#### Upload Section Design
```html
<div class="proof-of-payment-section">
  <header class="section-header">
    <h3>Proof of Payment</h3>
    <p class="section-description">
      Upload supporting documents for this payment transaction
    </p>
  </header>
  
  <div class="upload-area">
    <div class="dropzone" id="proof-upload-zone">
      <div class="dropzone-content">
        <icon class="upload-icon">cloud_upload</icon>
        <p class="upload-text">
          Drag and drop files here, or 
          <button class="browse-button">browse files</button>
        </p>
        <p class="upload-help">
          Supported: JPG, PNG, PDF, DOC (Max 5MB per file)
        </p>
      </div>
    </div>
    
    <button class="upload-button" disabled>
      Upload Proof of Payment
    </button>
  </div>
</div>
```

### File Upload Specifications

#### Supported File Types
- **Images**: JPEG (.jpg, .jpeg), PNG (.png), GIF (.gif), WebP (.webp)
- **Documents**: PDF (.pdf), Microsoft Word (.doc, .docx)
- **Maximum File Size**: 5MB per individual file
- **Maximum Files**: 10 files per payment transaction
- **Total Storage**: 50MB combined per payment

#### Upload Interface Features
- **Drag and Drop**: Intuitive drag-and-drop upload area
- **File Browser**: Traditional file selection dialog
- **Progress Indicators**: Upload progress bars for each file
- **Preview**: Thumbnail previews for images
- **File Validation**: Real-time validation before upload

#### Upload Process Flow
```javascript
// Upload workflow
const uploadProcess = {
  1: "File Selection (drag/drop or browse)",
  2: "Client-side Validation (type, size)",
  3: "Preview Display",
  4: "Upload Initiation",
  5: "Progress Tracking",
  6: "Server Processing",
  7: "Success Confirmation",
  8: "File List Update"
};
```

### Uploaded Files Management

#### Files List Display
```html
<div class="uploaded-files-section">
  <h4>Uploaded Files (3)</h4>
  <div class="files-list">
    <div class="file-item">
      <div class="file-info">
        <icon class="file-icon">picture_as_pdf</icon>
        <div class="file-details">
          <span class="file-name">bank_statement.pdf</span>
          <span class="file-size">2.4 MB</span>
          <span class="upload-date">Uploaded Jan 15, 2024</span>
        </div>
      </div>
      <div class="file-actions">
        <button class="view-button">View</button>
        <button class="download-button">Download</button>
        <button class="delete-button">Delete</button>
      </div>
    </div>
  </div>
</div>
```

#### File Actions
- **View**: Open file in browser or modal viewer
- **Download**: Download original file
- **Delete**: Remove file with confirmation dialog
- **Replace**: Option to replace existing files

#### File Security
- **Access Control**: Only the payment owner can view/manage files
- **Secure Storage**: Files stored outside web root directory
- **Virus Scanning**: Automatic malware detection
- **Audit Trail**: Log all file operations

---

## Technical Implementation

### Frontend Requirements

#### Framework and Libraries
```javascript
// Required dependencies
{
  "react": "^18.0.0",
  "react-table": "^8.0.0",
  "react-dropzone": "^14.0.0",
  "date-fns": "^2.29.0",
  "axios": "^1.3.0",
  "react-router-dom": "^6.8.0",
  "react-query": "^4.24.0",
  "recharts": "^2.5.0"
}
```

#### Component Structure
```javascript
// Component hierarchy
FinancesPage/
├── FinancesOverview/
│   ├── SummaryCard/
│   └── QuickStats/
├── PaymentsTable/
│   ├── PaymentRow/
│   ├── StatusBadge/
│   ├── TableFilters/
│   └── TablePagination/
├── PaymentDetails/
│   ├── PaymentSummary/
│   ├── PaymentTimeline/
│   ├── RelatedOrders/
│   └── ProofOfPayment/
├── ProofUpload/
│   ├── DropZone/
│   ├── FileList/
│   ├── FilePreview/
│   └── UploadProgress/
└── PaymentFilters/
```

#### State Management
```javascript
// Example state structure
const financesState = {
  overview: {
    totalReceived: 0,
    totalPending: 0,
    totalProcessing: 0,
    monthlyRevenue: 0,
    paymentCount: 0,
    loading: false
  },
  payments: {
    list: [],
    loading: false,
    error: null,
    filters: {
      status: 'all',
      dateRange: { start: null, end: null },
      amountRange: { min: null, max: null },
      searchTerm: ''
    },
    pagination: {
      page: 1,
      limit: 25,
      total: 0
    },
    sorting: {
      field: 'date',
      direction: 'desc'
    }
  },
  selectedPayment: {
    data: null,
    timeline: [],
    relatedOrders: [],
    proofFiles: [],
    loading: false,
    error: null
  },
  fileUpload: {
    files: [],
    uploading: false,
    progress: {},
    errors: []
  }
};
```

### Backend Requirements

#### API Endpoints
```javascript
// Payment management endpoints
GET    /api/seller/finances/overview           // Financial overview data
GET    /api/seller/finances/payments           // List all payments
GET    /api/seller/finances/payments/{id}      // Get payment details
GET    /api/seller/finances/payments/{id}/timeline // Payment history
PUT    /api/seller/finances/payments/{id}/notes    // Update payment notes

// Proof of payment endpoints
GET    /api/seller/finances/payments/{id}/proofs        // List proof files
POST   /api/seller/finances/payments/{id}/proofs        // Upload proof files
GET    /api/seller/finances/payments/{id}/proofs/{fileId} // Download proof file
DELETE /api/seller/finances/payments/{id}/proofs/{fileId} // Delete proof file

// Utility endpoints
GET    /api/seller/finances/export             // Export payments data
GET    /api/seller/finances/statistics         // Payment statistics
```

#### Database Schema
```sql
-- Payments table
CREATE TABLE payments (
    id VARCHAR(50) PRIMARY KEY,
    seller_id INTEGER NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status ENUM('received', 'processing', 'pending', 'failed', 'refunded') NOT NULL,
    payment_date DATETIME NOT NULL,
    payment_method VARCHAR(50),
    transaction_reference VARCHAR(100),
    processor_fee DECIMAL(10,2) DEFAULT 0.00,
    notes TEXT,
    system_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_seller_date (seller_id, payment_date DESC),
    INDEX idx_status (status),
    INDEX idx_amount (amount),
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE
);

-- Payment orders relationship
CREATE TABLE payment_orders (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    payment_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    order_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    UNIQUE KEY unique_payment_order (payment_id, order_id)
);

-- Payment status history
CREATE TABLE payment_status_history (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    payment_id VARCHAR(50) NOT NULL,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    reason TEXT,
    changed_by VARCHAR(50), -- system or user_id
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE,
    INDEX idx_payment_status (payment_id, changed_at DESC)
);

-- Proof of payment files
CREATE TABLE payment_proof_files (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    payment_id VARCHAR(50) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_by INTEGER NOT NULL, -- seller_id
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES sellers(id),
    INDEX idx_payment_files (payment_id),
    INDEX idx_upload_date (uploaded_at DESC)
);
```

#### File Storage Implementation
```javascript
// File storage service
class PaymentProofStorage {
  constructor() {
    this.uploadDir = process.env.PROOF_UPLOAD_DIR || './uploads/payment-proofs/';
    this.maxFileSize = 5 * 1024 * 1024; // 5MB
    this.allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf', 'application/msword'];
  }

  async uploadProofFile(paymentId, file, uploadedBy) {
    // Validate file
    this.validateFile(file);
    
    // Generate secure filename
    const filename = this.generateSecureFilename(file.originalname);
    const filePath = path.join(this.uploadDir, paymentId, filename);
    
    // Ensure directory exists
    await fs.ensureDir(path.dirname(filePath));
    
    // Save file
    await fs.move(file.path, filePath);
    
    // Save to database
    const proofFile = await PaymentProofFile.create({
      payment_id: paymentId,
      original_filename: file.originalname,
      stored_filename: filename,
      file_path: filePath,
      file_type: path.extname(file.originalname).toLowerCase(),
      file_size: file.size,
      mime_type: file.mimetype,
      uploaded_by: uploadedBy
    });
    
    return proofFile;
  }

  validateFile(file) {
    if (file.size > this.maxFileSize) {
      throw new Error('File size exceeds maximum allowed size (5MB)');
    }
    
    if (!this.allowedTypes.includes(file.mimetype)) {
      throw new Error('File type not supported');
    }
  }

  generateSecureFilename(originalName) {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2);
    const extension = path.extname(originalName);
    return `${timestamp}_${random}${extension}`;
  }
}
```

### Security and Access Control

#### Authentication and Authorization
```javascript
// Middleware for seller payment access
const requirePaymentAccess = async (req, res, next) => {
  try {
    const { paymentId } = req.params;
    const sellerId = req.user.sellerId;
    
    const payment = await Payment.findOne({
      where: { id: paymentId, seller_id: sellerId }
    });
    
    if (!payment) {
      return res.status(404).json({ 
        success: false, 
        error: 'Payment not found or access denied' 
      });
    }
    
    req.payment = payment;
    next();
  } catch (error) {
    res.status(500).json({ success: false, error: 'Server error' });
  }
};

// File access control
const requireProofFileAccess = async (req, res, next) => {
  try {
    const { fileId } = req.params;
    const sellerId = req.user.sellerId;
    
    const proofFile = await PaymentProofFile.findOne({
      where: { id: fileId, uploaded_by: sellerId },
      include: [{
        model: Payment,
        where: { seller_id: sellerId }
      }]
    });
    
    if (!proofFile) {
      return res.status(404).json({ 
        success: false, 
        error: 'File not found or access denied' 
      });
    }
    
    req.proofFile = proofFile;
    next();
  } catch (error) {
    res.status(500).json({ success: false, error: 'Server error' });
  }
};
```

#### Data Protection
- **Input Validation**: Sanitize all user inputs
- **SQL Injection Prevention**: Use parameterized queries
- **File Upload Security**: Validate file types and scan for malware
- **Access Logging**: Log all financial data access
- **Rate Limiting**: Limit API calls per seller
- **HTTPS Enforcement**: All financial data over secure connections

---

## Real-time Updates and Notifications

### Payment Status Updates
```javascript
// WebSocket integration for real-time payment updates
io.on('connection', (socket) => {
  socket.on('subscribe_payment_updates', (sellerId) => {
    socket.join(`seller_${sellerId}_payments`);
  });
});

// Notify payment status changes
const notifyPaymentUpdate = (sellerId, paymentUpdate) => {
  io.to(`seller_${sellerId}_payments`).emit('payment_status_update', {
    paymentId: paymentUpdate.id,
    newStatus: paymentUpdate.status,
    amount: paymentUpdate.amount,
    timestamp: paymentUpdate.updated_at
  });
};

// Automated payment processing updates
const processPaymentStatusUpdate = async (paymentId, newStatus, reason) => {
  const payment = await Payment.findByPk(paymentId);
  const oldStatus = payment.status;
  
  // Update payment status
  await payment.update({ status: newStatus });
  
  // Record status history
  await PaymentStatusHistory.create({
    payment_id: paymentId,
    from_status: oldStatus,
    to_status: newStatus,
    reason: reason,
    changed_by: 'system'
  });
  
  // Notify seller
  notifyPaymentUpdate(payment.seller_id, payment);
};
```

### Email Notifications
```javascript
// Payment notification system
const paymentNotifications = {
  paymentReceived: {
    template: 'payment-received',
    subject: 'Payment Received - {{paymentId}}',
    trigger: 'status_change_to_received'
  },
  paymentFailed: {
    template: 'payment-failed',
    subject: 'Payment Failed - {{paymentId}}',
    trigger: 'status_change_to_failed'
  },
  proofUploaded: {
    template: 'proof-uploaded',
    subject: 'Proof of Payment Uploaded - {{paymentId}}',
    trigger: 'proof_file_uploaded'
  }
};
```

---

## User Experience Features

### Loading States and Feedback
- **Table Loading**: Skeleton rows during data loading
- **Payment Details Loading**: Shimmer effect for detailed view
- **Upload Progress**: Real-time upload progress indicators
- **Status Updates**: Toast notifications for status changes
- **Refresh Indicators**: Visual feedback during data refresh

### Error Handling
```javascript
// Comprehensive error handling
const errorStates = {
  noPayments: {
    title: "No Payments Found",
    message: "You haven't received any payments yet. Payments will appear here once customers complete their orders.",
    icon: "payment",
    action: {
      text: "View Orders",
      link: "/seller/orders"
    }
  },
  paymentNotFound: {
    title: "Payment Not Found",
    message: "The requested payment could not be found or you don't have access to it.",
    icon: "error"
  },
  uploadError: {
    title: "Upload Failed",
    message: "There was an error uploading your file. Please check the file format and size, then try again.",
    icon: "upload_error",
    action: {
      text: "Try Again",
      callback: "retryUpload"
    }
  },
  networkError: {
    title: "Connection Error",
    message: "Unable to load payment information. Please check your internet connection.",
    icon: "wifi_off",
    action: {
      text: "Retry",
      callback: "reloadData"
    }
  }
};
```

### Mobile Responsiveness
- **Table Design**: Card layout for mobile devices
- **Upload Interface**: Touch-friendly file upload
- **Modal Dialogs**: Full-screen modals on mobile
- **Navigation**: Mobile-optimized navigation patterns

### Accessibility Features
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: WCAG 2.1 AA compliant color schemes
- **Focus Management**: Clear focus indicators
- **Alternative Text**: Descriptive alt text for all images

---

## Performance Optimization

### Data Loading Strategies
- **Lazy Loading**: Load payment details on demand
- **Pagination**: Efficient data pagination
- **Caching**: Cache frequently accessed data
- **Preloading**: Preload next page of results

### Database Optimization
```sql
-- Performance indexes
CREATE INDEX idx_payments_seller_status_date ON payments(seller_id, status, payment_date DESC);
CREATE INDEX idx_payments_amount_range ON payments(amount);
CREATE INDEX idx_payment_orders_lookup ON payment_orders(payment_id, order_id);
CREATE INDEX idx_proof_files_payment ON payment_proof_files(payment_id, uploaded_at DESC);

-- Query optimization
EXPLAIN SELECT p.*, 
               GROUP_CONCAT(po.order_id) as related_orders,
               COUNT(pf.id) as proof_file_count
FROM payments p
LEFT JOIN payment_orders po ON p.id = po.payment_id
LEFT JOIN payment_proof_files pf ON p.id = pf.payment_id
WHERE p.seller_id = ?
  AND p.status IN (?)
  AND p.payment_date BETWEEN ? AND ?
GROUP BY p.id
ORDER BY p.payment_date DESC
LIMIT ? OFFSET ?;
```

### Frontend Performance
- **Virtual Scrolling**: For large payment lists
- **Memoization**: Cache component renders
- **Code Splitting**: Lazy load payment details components
- **Image Optimization**: Optimize proof file thumbnails

---

## Analytics and Reporting

### Key Metrics Dashboard
- **Revenue Trends**: Monthly/weekly revenue charts
- **Payment Methods**: Distribution of payment methods
- **Success Rates**: Payment success vs failure rates
- **Processing Times**: Average payment processing duration
- **Proof Upload Rates**: Percentage of payments with proof files

### Export Functionality
```javascript
// Export service
class PaymentExportService {
  async exportPayments(sellerId, filters, format = 'csv') {
    const payments = await this.getFilteredPayments(sellerId, filters);
    
    const exportData = payments.map(payment => ({
      'Payment ID': payment.id,
      'Date': payment.payment_date,
      'Amount': payment.amount,
      'Currency': payment.currency,
      'Status': payment.status,
      'Related Orders': payment.related_orders?.join(', ') || '',
      'Payment Method': payment.payment_method,
      'Transaction Reference': payment.transaction_reference,
      'Proof Files': payment.proof_file_count || 0
    }));
    
    if (format === 'csv') {
      return this.generateCSV(exportData);
    } else if (format === 'excel') {
      return this.generateExcel(exportData);
    }
  }
}
```

### Financial Reports
- **Monthly Statements**: Automated monthly payment summaries
- **Tax Reports**: Export data formatted for tax reporting
- **Reconciliation Reports**: Compare payments with orders
- **Proof Documentation**: Generate proof file summaries

---

## Testing Strategy

### Unit Tests
```javascript
// Example test cases
describe('Finances Page Components', () => {
  test('renders payment table with correct data', () => {
    const mockPayments = [
      { id: 'P001', amount: 150.00, status: 'received' }
    ];
    render(<PaymentsTable payments={mockPayments} />);
    expect(screen.getByText('P001')).toBeInTheDocument();
  });

  test('filters payments by status correctly', () => {
    // Test filtering functionality
  });

  test('uploads proof file successfully', async () => {
    // Test file upload functionality
  });

  test('displays payment timeline in correct order', () => {
    // Test timeline component
  });
});
```

### Integration Tests
- **API Integration**: Test all payment API endpoints
- **File Upload Flow**: Complete file upload and storage testing
- **Database Queries**: Verify data filtering and relationships
- **Real-time Updates**: Test WebSocket payment notifications

### End-to-End Tests
- **Complete Payment Workflow**: From payment receipt to proof upload
- **Multi-device Testing**: Test responsive design across devices
- **Accessibility Testing**: Screen reader and keyboard navigation
- **Performance Testing**: Load testing with large datasets

---

## Security Considerations

### Data Protection
- **PCI Compliance**: Follow PCI DSS standards for payment data
- **Encryption**: Encrypt sensitive payment information
- **Access Logs**: Comprehensive audit logging
- **Data Retention**: Implement data retention policies

### File Security
- **Virus Scanning**: Scan all uploaded files
- **File Type Validation**: Strict file type checking
- **Storage Security**: Secure file storage with restricted access
- **Download Logging**: Log all file access activities

---

## Future Enhancements

### Advanced Features
- **Payment Predictions**: AI-based payment timing predictions
- **Automatic Reconciliation**: Auto