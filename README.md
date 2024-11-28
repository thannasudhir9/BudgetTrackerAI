# Budget Tracker
Last Updated: November 26, 2024

A comprehensive web application for personal finance management with role-based access control, user management, and advanced tracking features. This application provides a secure and user-friendly interface to manage your financial life.

## Features

### PDF Export Features (New)
- Client-side PDF generation for instant downloads
- Clean, professional report layout
- Automatic date-stamped filenames (BudgetTracker_YYYYMMDD.pdf)
- High-quality chart and graph rendering
- Smart element hiding for PDF output
- Responsive layout optimization
- Custom print styling for better PDF appearance

### User Management
- Role-based access control (NORMAL, PRO, ADMIN, SUPER_ADMIN)
- Secure user authentication with password strength validation
- User account activation/deactivation
- Admin dashboard for user management
- Activity monitoring and logging

### Financial Management
- Add income and expenses with descriptions
- Categorize transactions (Food, Transportation, Entertainment, Bills, Shopping, etc.)
- View complete transaction history in a clean, organized table
- Real-time balance updates with color-coded amounts
- Summary cards showing total income, expenses, and current balance

### Admin Features
- Comprehensive admin dashboard
- User statistics and analytics
- Activity monitoring
- Role management
- System settings (Super Admin only)
- User activity logs

### Security Features
- Strong password requirements
- Role-based access restrictions
- Active/inactive user status
- Session management
- Remember me functionality

### UI/UX Features
- Responsive design for desktop and mobile
- Modern, clean interface with Bootstrap 5
- Real-time form validation
- Dynamic transaction tables
- Role-specific navigation
- Interactive charts and statistics
- Professional PDF report generation
- Optimized print layouts

### File Import Features
- **CSV Import**
  - Upload transaction data from CSV files
  - Automatic category creation
  - Bulk transaction processing
  - Sample CSV template available
  - Error handling and validation

- **PDF Import**
  - Extract transactions from PDF statements
  - Support for structured PDF formats
  - Automatic text extraction
  - Transaction parsing capabilities

## Import File Requirements

#### CSV Format
```csv
Date,Description,Amount,Type,Category
2024-01-15,Grocery Shopping,-125.50,expense,Food
2024-01-15,Salary,5000.00,income,Salary
```

- **Required Columns**:
  - `Date`: YYYY-MM-DD format
  - `Description`: Transaction description
  - `Amount`: Positive for income, negative for expenses
  - `Type`: 'income' or 'expense'
  - `Category`: Must match existing categories or will be created

#### PDF Format
- Clear, readable text
- Structured transaction data
- One transaction per line (preferred)
- Common bank statement formats supported

## Import Process
1. **Accessing Import Feature**
   - Navigate to Dashboard
   - Locate "Import Transactions" card
   - Choose file type (CSV/PDF)

2. **File Selection**
   - Click "Choose File" button
   - Select CSV or PDF file
   - Maximum file size: 16MB

3. **Processing**
   - Automatic validation
   - Category matching/creation
   - Transaction creation
   - Error handling

4. **Results**
   - Success/error count displayed
   - Failed transactions logged
   - Automatic file cleanup

## Sample Files
- Download sample CSV template
- Use as reference for formatting
- Test import functionality

## Security Measures
- File type validation
- Size restrictions
- Secure filename handling
- Automatic file cleanup
- User data isolation

## Database Setup and Management

### Default Users
The application comes with four default user types:

1. **Super Admin**
   - Username: superadmin
   - Email: superadmin@example.com
   - Password: superadmin123
   - Role: Super Administrator
   - Full system access and management capabilities

2. **Admin**
   - Username: admin
   - Email: admin@example.com
   - Password: admin123
   - Role: Administrator
   - System management and user oversight

3. **Pro User**
   - Username: prouser
   - Email: prouser@example.com
   - Password: pro123
   - Role: Pro User
   - Access to advanced features

4. **Normal User**
   - Username: testuser
   - Email: testuser@example.com
   - Password: test123
   - Role: Normal User
   - Basic feature access

### Default Categories
Each user is initialized with the following categories:

| Category       | Icon           | Color Code | Description           |
|---------------|----------------|------------|----------------------|
| Housing       | home           | #FF9999    | Light red           |
| Transportation| car            | #99FF99    | Light green         |
| Food          | utensils       | #9999FF    | Light blue          |
| Utilities     | bolt           | #FFFF99    | Light yellow        |
| Insurance     | shield         | #FF99FF    | Light magenta       |
| Healthcare    | heart          | #99FFFF    | Light cyan          |
| Savings       | piggy-bank     | #FFB366    | Light orange        |
| Entertainment | film           | #B366FF    | Light purple        |
| Shopping      | shopping-cart  | #66FFB3    | Light mint          |
| Miscellaneous | ellipsis-h     | #808080    | Gray                |

### Database Management Scripts

The application includes two important database management scripts:

1. **Database Setup Script** (`migrations/setup_database.py`)
   - Creates all necessary database tables
   - Initializes default users with appropriate roles
   - Creates default categories for each user
   - Sets up proper relationships and constraints

   To run the setup script:
   ```bash
   python migrations/setup_database.py
   ```

2. **Database Cleanup Script** (`migrations/cleanup_tables.py`)
   - Removes unnecessary tables while preserving essential ones
   - Maintains data integrity
   - Useful for database maintenance and cleanup

   To run the cleanup script:
   ```bash
   python migrations/cleanup_tables.py
   ```

### Database Setup Process

1. **Initial Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   venv\Scripts\activate     # On Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Database Initialization**
   ```bash
   # Clean up any existing tables (if needed)
   python migrations/cleanup_tables.py

   # Create tables and initialize data
   python migrations/setup_database.py
   ```

3. **Verify Setup**
   - Log in with any of the default user accounts
   - Check that categories are properly created
   - Verify user roles and permissions

### Important Notes

- Change default passwords immediately after first login
- The cleanup script preserves essential tables: user, budget_transaction, category
- Each user gets their own set of categories with unique icons and colors
- All passwords are securely hashed using werkzeug's password hashing
- The `is_active` flag is set to True by default for all users

## Project Structure

```
budget_tracker/
├── app.py                 # Flask application and routes
├── models.py             # Database models and role definitions
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── static/
│   ├── css/
│   │   ├── style.css    # Main styling
│   │   └── admin.css    # Admin panel styling
│   └── js/
│       ├── main.js      # Main JavaScript
│       └── dashboard.js # Dashboard charts and stats
├── templates/
│   ├── admin/
│   │   ├── base.html    # Admin base template
│   │   └── dashboard.html # Admin dashboard
│   ├── auth/
│   │   ├── login.html   # Login page
│   │   └── register.html # Registration page
│   ├── base.html        # Main base template
│   └── dashboard.html   # User dashboard
└── venv/                # Python virtual environment
```

## Technical Details

### Backend
- **Framework**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy
- **Authentication**: Flask-Login
- **API Endpoints**:
  - User Management:
    - `POST /api/users`: Create new user
    - `PUT /api/users/<id>`: Update user
    - `POST /api/users/<id>/toggle-status`: Toggle user status
  - Transactions:
    - `GET /api/transactions`: Retrieve transactions
    - `POST /api/transactions`: Add transaction
  - Authentication:
    - `POST /login`: User login
    - `POST /register`: User registration
    - `GET /logout`: User logout

### Frontend
- **UI Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS with Fetch API
- **Styling**: Custom CSS with responsive design
- **Features**:
  - Real-time form validation
  - Dynamic UI based on user role
  - Interactive charts and statistics
  - Automatic balance calculations

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd budget_tracker
```

2. Create a Python virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

## User Roles

1. **NORMAL User**:
   - Basic transaction management
   - Personal dashboard access
   - Profile management

2. **PRO User**:
   - Advanced reporting features
   - Extended transaction history
   - Additional categories
   - Priority support

3. **ADMIN User**:
   - User management
   - Transaction oversight
   - Activity monitoring
   - Report generation

4. **SUPER_ADMIN**:
   - System configuration
   - Role management
   - Full system access
   - Security settings

## Security Implementation

1. **Password Requirements**:
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one number
   - At least one special character

2. **Access Control**:
   - Role-based route protection
   - Session management
   - Active status verification
   - API endpoint protection

3. **User Management**:
   - Account activation/deactivation
   - Role assignment restrictions
   - Activity logging
   - Login attempt tracking

## Development

The application follows a modular architecture:

1. **User Management**:
   - Role-based access control
   - User authentication
   - Profile management
   - Activity tracking

2. **Transaction Management**:
   - CRUD operations
   - Category management
   - Balance calculations
   - Transaction history

3. **Admin Interface**:
   - User oversight
   - System monitoring
   - Statistics generation
   - Configuration management

4. **Frontend Components**:
   - Role-specific navigation
   - Dynamic form validation
   - Real-time updates
   - Interactive charts

## Technologies Used

- **Backend**:
  - Python 3.12
  - Flask 2.3.3
  - SQLAlchemy 3.0.5
  - Flask-Login 0.6.2
  - Werkzeug 2.3.7

- **Frontend**:
  - HTML5/CSS3
  - JavaScript (ES6+)
  - Bootstrap 5
  - Bootstrap Icons
  - Chart.js

- **Database**:
  - SQLite (Development)
  - Migrations support

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## Updates (Nov 26, 2024)

### Major Changes
1. Reorganized project structure for better modularity
2. Implemented Flask factory pattern
3. Separated user routes into dedicated module
4. Enhanced role-based access control
5. Added test users with sample transactions

### Project Structure Update
The project has been reorganized for better modularity:

```
budget_tracker/
├── app.py              # Application factory and configuration
├── extensions.py       # Flask extensions (SQLAlchemy, Login Manager)
├── models.py           # Database models
├── routes.py          # Main application routes
├── user_routes.py     # User management routes
├── migrations/        # Database migrations and setup
│   └── setup_database.py  # Database initialization script
├── static/           # Static files (CSS, JS, images)
├── templates/        # HTML templates
└── instance/         # Instance-specific files
    └── budget_tracker.db  # SQLite database
```

### New Test Users
The setup script now creates the following test users:

| Username  | Email                    | Password      | Role        |
|-----------|--------------------------|---------------|-------------|
| admin     | admin@example.com        | admin123      | Admin       |
| superadmin | superadmin@example.com  | superadmin123 | Super Admin |
| user      | user@example.com         | user123       | Normal      |
| pro_user  | pro@example.com          | pro123        | Pro         |

### Updated Database Models

#### User Model Enhancements
- Role-based access using UserRole enum
- Last login tracking
- Activity timestamps (created_at, updated_at)
- Enhanced role validation methods
- Secure password hashing

#### Transaction Model Updates
- Improved category system using TransactionCategory enum
- Built-in type validation (income/expense)
- Automatic timestamp management
- Enhanced relationship with User model

### Transaction Categories
Now using an enum-based system with predefined categories:
- Food
- Transportation
- Entertainment
- Shopping
- Bills
- Salary
- Other Income

Each category includes:
- Name
- Bootstrap Icon
- Color scheme for UI

### API Endpoints Update

#### User Management
- GET `/users` - List all users (Admin only)
- GET `/api/users/<id>` - Get user details
- PUT `/api/users/<id>` - Update user
- POST `/api/users` - Create new user
- POST `/api/users/<id>/toggle-status` - Toggle user status

#### Transactions
- GET `/` - Dashboard with transaction overview
- POST `/transactions` - Create new transaction
- GET `/transactions` - List user's transactions
- PUT `/transactions/<id>` - Update transaction
- DELETE `/transactions/<id>` - Delete transaction

### Role-Based Access Updates

1. **Normal User**
   - Basic transaction management
   - Personal dashboard
   - Limited features

2. **Pro User**
   - Advanced reporting
   - Extended transaction history
   - Additional features

3. **Admin**
   - User management
   - System monitoring
   - Access to all features

4. **Super Admin**
   - Full system control
   - User role management
   - System configuration

### Quick Start with New Features

1. Initialize the database with test data:
```bash
python migrations/setup_database.py
```

2. Run the application:
```bash
python app.py
```

3. Access the application:
   - URL: http://localhost:5000
   - Login with any test user credentials
   - Explore role-specific features

### Development Notes

#### Adding New Features
1. Create new routes in appropriate route files
2. Update models if needed
3. Add new templates
4. Update role permissions if required

#### Database Updates
1. Modify models in `models.py`
2. Update `setup_database.py` if needed
3. Run setup script to recreate database

### Security Enhancements
- Improved password hashing using Werkzeug
- Enhanced role-based access control
- Better session management
- Added CSRF protection
- Improved input validation


1. Enhanced PDF Export Functionality
   - Implemented client-side PDF generation using html2pdf.js
   - Added smart element hiding for cleaner PDF output
   - Improved chart rendering in PDF exports
   - Optimized layout for professional appearance
   - Added dynamic date-stamped filenames

2. Dashboard Improvements
   - Updated transaction view endpoints
   - Added period-specific transaction filtering
   - Enhanced mobile responsiveness
   - Improved chart display
   - Added "View All" functionality for each time period

3. Technical Enhancements
   - Removed server-side PDF generation dependencies
   - Optimized client-side performance
   - Enhanced print media queries
   - Improved cross-browser compatibility

4. UI/UX Improvements
   - Better button visibility control
   - Enhanced layout consistency
   - Improved responsive design
   - Cleaner PDF output formatting
   
For more details on specific features or development guidelines, refer to the documentation above.


# Budget Tracker Application
*Last Updated: November 29, 2024*

## Overview
A comprehensive web-based budget tracking application that helps users manage their personal finances through intuitive visualizations and detailed transaction tracking.

## Features
- **Dashboard Overview**
  - Monthly income, expenses, and net income summary cards
  - Category-wise distribution of income and expenses
  - Detailed transaction history

- **Financial Visualization**
  - Separate pie charts for income and expense categories
  - Monthly trend analysis
  - Weekly transaction breakdown
  - Yearly financial overview

- **Transaction Management**
  - Add, edit, and categorize transactions
  - Multiple currency support (USD, EUR, INR)
  - Category-based organization
  - Date-based filtering

- **Data Analysis**
  - Category-wise statistics and percentages
  - Time-based trend analysis (Daily, Weekly, Monthly, Yearly)
  - Dynamic data updates

## Technical Stack
- **Backend**: Flask (Python)
- **Frontend**: JavaScript, HTML5, CSS3
- **Database**: SQLAlchemy
- **Visualization**: Chart.js
- **Styling**: Bootstrap
- **PDF Export**: html2pdf.js

## Key Components
1. **Dashboard Interface**
   - Real-time financial overview
   - Interactive charts and graphs
   - Responsive design for all devices

2. **Transaction Management**
   - Multi-currency support
   - Category management
   - Date-based organization

3. **Data Visualization**
   - Income/Expense pie charts
   - Time-series analysis
   - Category distribution

4. **Export Functionality**
   - PDF report generation
   - Data backup options

## Currency Support
- USD (US Dollar)
- EUR (Euro)
- INR (Indian Rupee)
- Dynamic currency conversion
- Persistent currency preference

## Security Features
- User authentication
- Secure API endpoints
- Data validation
- Session management

## Performance Optimizations
- Efficient data loading
- Chart instance management
- Responsive data updates
- Browser storage utilization

## Browser Compatibility
- Chrome (Recommended)
- Firefox
- Safari
- Edge

## Future Enhancements
1. Advanced filtering options
2. Machine learning for category predictions
3. Budget goal setting
4. Mobile application
5. More currency options
6. Enhanced reporting features

## Dependencies
- Flask
- SQLAlchemy
- Chart.js
- Bootstrap
- html2pdf.js

## Installation
1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Set up the database
4. Configure environment variables
5. Run the Flask application

## Usage
1. Register/Login to your account
2. Add transactions
3. View financial overview
4. Generate reports
5. Manage categories
6. Export data

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, please open an issue in the repository or contact the development team.

---
*Note: This README is regularly updated to reflect the latest changes and improvements to the Budget Tracker application.*