# CRM Fulfillment System

A comprehensive Customer Relationship Management (CRM) system with integrated order fulfillment capabilities designed for e-commerce businesses. This system handles the complete customer journey from lead generation to post-purchase follow-up.

## 🌟 Features

- **User Management**: Role-based access control with customizable permissions
- **Seller Management**: Track seller information, orders, and performance
- **Order Processing**: Complete order lifecycle management
- **Inventory Management**: Track product stock across warehouses
- **Call Center Integration**: Customer support and outreach management
- **Packaging & Delivery**: Order fulfillment and shipping management
- **Financial Tracking**: Payment processing and invoice generation
- **Customer Follow-up**: Post-purchase communication and feedback collection
- **Warehouse Management**: Multiple warehouse inventory tracking
- **Notifications System**: Real-time alerts and updates
- **Multilingual Support**: English and Arabic language support
- **Responsive Dashboard**: Comprehensive analytics and reporting

## 📋 Requirements

- Python 3.8+
- Django 5.2
- SQLite (default) or other compatible database
- Additional dependencies listed in requirements.txt

## 🚀 Installation

1. Clone the repository
```bash
git clone https://github.com/organization/crm-system.git
cd crm-system
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create a .env file in the project root)
```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create a superuser
```bash
python manage.py createsuperuser
```

7. Run the development server
```bash
python manage.py runserver
```

8. Access the application at http://127.0.0.1:8000

## 🏗️ Project Structure

```
crm-system/
├── crm_fulfillment/           # Main project configuration
│   ├── __init__.py
│   ├── asgi.py                # ASGI configuration
│   ├── settings.py            # Project settings
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── views.py               # Error handlers
│
├── dashboard/                 # Dashboard and analytics
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── dashboard/         # Dashboard templates
│
├── users/                     # User authentication and management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Custom User model
│   ├── urls.py
│   ├── views.py
│   ├── management/            # Management commands
│   │   └── commands/
│   └── templates/
│       └── users/             # User-related templates
│
├── roles/                     # Role-based permission management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Role and Permission models
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── roles/             # Role management templates
│
├── sellers/                   # Seller management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── sellers/           # Seller-related templates
│
├── orders/                    # Order processing
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Order models
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── orders/            # Order-related templates
│
├── inventory/                 # Inventory management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── inventory/         # Inventory templates
│
├── callcenter/                # Call center functionality
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── callcenter/        # Call center templates
│
├── packaging/                 # Packaging management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── packaging/         # Packaging templates
│
├── delivery/                  # Delivery management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── delivery/          # Delivery templates
│           └── panel/         # Delivery panel templates
│
├── finance/                   # Financial tracking
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── finance/           # Finance templates
│           └── widgets/       # Finance widgets
│
├── followup/                  # Customer follow-up
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── followup/          # Follow-up templates
│
├── settings/                  # System settings
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── settings/          # Settings templates
│
├── warehouse/                 # Warehouse management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── warehouse/         # Warehouse templates
│
├── warehouse_inventory/       # Warehouse inventory
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── static/
│   │   └── warehouse_inventory/
│   │       └── css/           # Inventory-specific CSS
│   └── templates/
│       └── warehouse_inventory/ # Inventory templates
│
├── notifications/             # System notifications
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── notifications/     # Notification templates
│
├── landing/                   # Public-facing pages
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── landing/           # Landing page templates
│
├── products/                  # Product management
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── subscribers/               # Subscriber management
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── sync_sellers.py
│   └── templates/
│       └── subscribers/       # Subscriber templates
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── language_utils.py
│   ├── views.py
│   └── templatetags/          # Custom template tags
│
├── static/                    # Static files
│   ├── css/                   # CSS stylesheets
│   ├── js/                    # JavaScript files
│   ├── img/                   # Images and icons
│   └── tailwind/              # Tailwind configuration
│
├── media/                     # User-uploaded files
│   ├── products/              # Product images
│   └── profile_images/        # User profile images
│
├── templates/                 # Global templates
│   ├── 400.html              # Error pages
│   ├── 403.html
│   ├── 404.html
│   └── followup/              # Global followup templates
│
├── locale/                    # Translation files
│   ├── ar/                    # Arabic translations
│   │   └── LC_MESSAGES/
│   └── en/                    # English translations
│       └── LC_MESSAGES/
│
├── manage.py                  # Django management script
├── requirements.txt           # Project dependencies
└── .env                       # Environment variables (to be created)
```

### Core Apps

- **crm_fulfillment/**: Main project configuration
  - `settings.py`: Project settings and configurations
  - `urls.py`: Main URL routing
  - `asgi.py` & `wsgi.py`: Server configurations

- **dashboard/**: Main dashboard and analytics
  - Provides overview statistics and activity monitoring
  - Includes system status monitoring and reporting tools

- **users/**: User authentication and management
  - Custom User model with email-based authentication
  - Role-based access control integration
  - User profile management and audit logging

- **roles/**: Role-based permission management
  - Dynamic permission system with granular access control
  - Custom roles with specific required fields
  - Permission categories by functional area

### Business Process Apps

- **sellers/**: Seller profiles and management
  - Seller onboarding and profile management
  - Performance tracking and analytics

- **orders/**: Order processing and management
  - Complete order lifecycle from creation to completion
  - Order status tracking and management
  - Integration with other modules

- **inventory/**: Product inventory tracking
  - Product catalog management
  - Stock level monitoring
  - Inventory adjustments and history

- **callcenter/**: Customer support integration
  - Call logging and tracking
  - Customer interaction management
  - Support ticket system

- **packaging/**: Order preparation and packaging
  - Packaging workflow management
  - Package tracking and quality control

- **delivery/**: Shipping and delivery management
  - Delivery company integration
  - Courier assignment and tracking
  - Delivery status updates

- **finance/**: Payment processing and financial tracking
  - Invoice generation and management
  - Payment tracking and reconciliation
  - Financial reporting

- **followup/**: Customer follow-up and feedback
  - Post-purchase communication
  - Customer feedback collection and analysis
  - Satisfaction tracking

### Support Apps

- **settings/**: System configuration
  - Global system settings
  - Regional and localization settings

- **warehouse/**: Warehouse management
  - Multiple warehouse support
  - Warehouse inventory allocation

- **warehouse_inventory/**: Detailed inventory tracking
  - Barcode scanning integration
  - Inventory movement tracking

- **notifications/**: System notifications
  - Real-time alerts
  - User notification preferences

- **landing/**: Public-facing pages
  - Marketing pages and public information
  - Multilingual support

- **products/**: Product management
  - Product catalog and details
  - Product categorization and attributes

- **subscribers/**: Subscriber management
  - Subscription tracking and management
  - Subscriber communication

- **sourcing/**: Sourcing management
  - Supplier management
  - Sourcing requests and tracking

### Static Files Organization

- **static/**: Contains all static assets
  - `css/`: Custom CSS styles including responsive design
  - `js/`: JavaScript files for interactive features
  - `img/`: Images and icons
  - `tailwind/`: Tailwind CSS configuration and utilities

- **media/**: User-uploaded content
  - `products/`: Product images
  - `profile_images/`: User profile pictures

### Templates Structure

Each app contains its own templates directory with app-specific templates. The main template structure follows:

- `base.html`: Base template with common layout elements
- `dashboard.html`: App-specific dashboard view
- Component-specific templates (e.g., `create_order.html`, `order_list.html`)

## 🎨 UI Components and Design

The system uses a modern, responsive UI built with:

- **Tailwind CSS**: Utility-first CSS framework for responsive design
- **Custom Components**: Neo-brutalism inspired UI elements with custom shadows and transitions
- **Responsive Design**: Mobile-friendly interface that adapts to different screen sizes
- **RTL Support**: Full right-to-left language support for Arabic
- **Custom Animations**: Subtle animations for improved user experience
- **Dashboard Widgets**: Interactive charts and data visualization
- **Color Scheme**: 
  - Primary: Yellow (#FFCC00) with various shades
  - Secondary: Dark gray (#333333)
  - Background: White (#FFFFFF)
  - Accent colors for notifications and alerts

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True|False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3
# For PostgreSQL:
# DATABASE_URL=postgres://user:password@localhost:5432/dbname

# Email Configuration
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True

# Language Settings
LANGUAGE_CODE=en
```

### Custom Settings

Additional system settings can be configured through the admin interface:

1. **General Settings**: System name, logo, contact information
2. **Regional Settings**: Default country, currency, timezone
3. **Notification Settings**: Email templates, notification preferences
4. **Integration Settings**: Third-party service connections

## 🛠️ Development

### Creating New Apps

```bash
python manage.py startapp new_app_name
```

Remember to add the new app to INSTALLED_APPS in settings.py

### Role-Based Development

When developing new features, consider the role-based permission system:

1. Define required permissions in the Permission model
2. Assign permissions to appropriate roles
3. Use permission checks in views and templates

### Running Tests

```bash
python manage.py test
```

### Internationalization

To add or update translations:

```bash
python manage.py makemessages -l ar  # For Arabic
python manage.py compilemessages
```

## 📝 License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## 👥 Contributors

- CodixVerse Development Team

---

© 2025 CodixVerse. All Rights Reserved.
