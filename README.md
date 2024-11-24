# Budget Tracker

A comprehensive web application for personal finance management with role-based access control, user management, and advanced tracking features. This application provides a secure and user-friendly interface to manage your financial life.

## Features

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