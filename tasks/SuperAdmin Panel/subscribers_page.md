# Subscribers Management Module

## Sidebar Navigation Update

A new "Subscribers" page is to be added to the main sidebar navigation menu. This module will function as an audit log for new registrations and provide comprehensive user management capabilities.

## Features

### Subscribers Audit Log Table

The main section will display a table with the following columns:

| Column | Description |
|--------|-------------|
| Full Name | Complete name of the subscriber |
| E-mail | Subscriber's email address (used for login) |
| Phone Number | Subscriber's contact phone number |
| Business Name | Name of the subscriber's business |
| Residence Country | Country where the subscriber resides |
| Date | Registration date of the subscriber |
| Actions | View Details and Delete options |

#### Action Buttons
- **View Details**: Navigates to the detailed subscriber information page
- **Delete**: Removes the subscriber with confirmation dialog to prevent accidental deletion

### Add New User Functionality

- A prominent "Add User" button will be positioned near the subscribers table
- Button click navigates to a dedicated form page with the following fields:
  - Full Name
  - E-mail
  - Phone Number
  - Business Name
  - Residence Country
  - Date (auto-generated)
  - **Password** (required field to set initial password for new subscriber's seller account)

### Subscriber Details View

Accessed via the "View Details" button, this dedicated page will display:

1. **Standard Information**
   - Full Name
   - E-mail
   - Phone Number
   - Business Name
   - Residence Country
   - Registration Date

2. **Additional Critical Information**
   - **Store Link**: URL to the subscriber's store entered during registration
   - **Services**: List of services added by the subscriber during registration or through their seller panel

## Implementation Notes

- Ensure consistent styling with existing interface elements
- Implement proper form validation for all input fields
- Ensure password field follows security best practices
- Create proper routing for the subscriber details page
- Format dates consistently throughout the interface
