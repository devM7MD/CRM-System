# CRM Fulfillment System Setup Instructions

This document provides detailed steps to set up and run the CRM Fulfillment System on your local machine.

## Prerequisites

- Python 3.10+ installed
- pip (Python package manager)
- Git
- Virtual environment tool (venv, virtualenv, or conda)

## Step 1: Clone the Repository

```bash
git clone <repository_url>
cd DcrmProject
```

## Step 2: Create and Activate a Virtual Environment

### Using venv (recommended)
```bash
python -m venv .venv
```

#### Activate on Windows:
```bash
.venv\Scripts\activate
```

#### Activate on macOS/Linux:
```bash
source .venv/bin/activate
```

## Step 3: Install Required Packages

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

Create a `.env` file in the project root directory with the following content:

```
DEBUG=True
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///db.sqlite3
```

For production, you would change these settings and use PostgreSQL.

## Step 5: Setup Database

```bash
cd crm_fulfillment
python manage.py migrate
```

## Step 6: Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

## Step 7: Load Initial Data (Optional)

If you want to start with some sample data:

```bash
python manage.py loaddata initial_data
```

## Step 8: Run the Development Server

```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Step 9: Access the Admin Interface

Visit http://127.0.0.1:8000/admin/ and log in with the superuser credentials you created.

## Common Issues and Troubleshooting

### Template Not Found Errors
If you encounter template errors, make sure the project structure is correct:

```bash
mkdir -p crm_fulfillment/templates
```

### Module Not Found Errors
If you see module import errors, check that all app URLs are properly configured:

```bash
python manage.py check
```

### Database Migration Issues
If you have migration problems:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading
Make sure static files are configured properly:

```bash
python manage.py collectstatic
```

## Project Structure Overview

```
crm_fulfillment/
├── crm_fulfillment/         # Main project settings
├── dashboard/               # Dashboard app
├── users/                   # User management app
├── sellers/                 # Seller portal app
├── inventory/               # Inventory management app
├── sourcing/                # Sourcing app
├── orders/                  # Order processing app
├── callcenter/              # Call center app
├── packaging/               # Packaging app
├── delivery/                # Delivery app
├── finance/                 # Finance app
├── followup/                # Follow-up app
├── settings/                # System settings app
├── static/                  # Static files
└── templates/               # Global templates
```

## Project Completion Status

The project currently implements the following:

- ✅ User authentication and role-based permissions
- ✅ Dashboard interfaces for Super Admin and Sellers
- ✅ Product and inventory management
- ✅ Sourcing request workflow
- ✅ Modern UI with Tailwind CSS and yellow theme
- ✅ Charts for data visualization
- ✅ Mobile-responsive design

Remaining tasks:
- Complete remaining CRUD operations for all modules
- Implement order processing workflow 
- Connect with delivery services API
- Add comprehensive reports and exports 
- Implement notification system 