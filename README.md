# Budget Tracker

A simple and elegant web application to track your personal finances. This application provides a user-friendly interface to manage your income and expenses, helping you maintain better control over your financial life.

## Features

- Add income and expenses with descriptions
- Categorize transactions (Food, Transportation, Entertainment, Bills, Shopping, etc.)
- View complete transaction history in a clean, organized table
- Real-time balance updates with color-coded amounts
- Responsive design that works on both desktop and mobile devices
- Summary cards showing total income, expenses, and current balance
- SQLite database for persistent data storage
- Clean and modern UI using Bootstrap 5

## Project Structure

```
budget_tracker/
├── app.py              # Flask application and database models
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── static/
│   ├── css/
│   │   └── style.css  # Custom styling
│   └── js/
│       └── main.js    # Frontend JavaScript
├── templates/
│   └── index.html     # Main HTML template
└── venv/              # Python virtual environment
```

## Technical Details

### Backend
- **Framework**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy
- **API Endpoints**:
  - `GET /api/transactions`: Retrieve all transactions
  - `POST /api/transactions`: Add a new transaction

### Frontend
- **UI Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS with Fetch API
- **Styling**: Custom CSS with responsive design
- **Features**:
  - Real-time updates without page reload
  - Form validation
  - Dynamic transaction table
  - Automatic balance calculations

## Installation

1. Clone or download this repository:
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

## Usage Guide

1. **Adding Transactions**:
   - Fill in the transaction description
   - Enter the amount
   - Select a category from the dropdown
   - Choose the transaction type (income/expense)
   - Click "Add Transaction"

2. **Viewing Transactions**:
   - All transactions are displayed in the table below the form
   - Income is shown in green with a '+' prefix
   - Expenses are shown in red with a '-' prefix

3. **Monitoring Summary**:
   - Top cards show your current financial status
   - Green card: Total Income
   - Red card: Total Expenses
   - Blue card: Current Balance

## Development

The application uses a simple but effective architecture:

1. **Database Model** (`app.py`):
   - Handles transaction data storage
   - Manages database operations

2. **API Routes** (`app.py`):
   - Processes incoming requests
   - Returns JSON responses
   - Handles data validation

3. **Frontend** (`static/js/main.js`):
   - Manages user interactions
   - Updates UI in real-time
   - Handles API communication

4. **Styling** (`static/css/style.css`):
   - Custom styling for components
   - Responsive design adjustments
   - Color schemes for financial data

## Technologies Used

- **Backend**: Python/Flask
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Bootstrap Icons
- **API**: RESTful architecture

## Contributing

Feel free to fork this project and make improvements. Pull requests are welcome!


The repository includes all the files we created:

app.py - Flask application
requirements.txt - Python dependencies
README.md - Project documentation
static/css/style.css - Custom styling
static/js/main.js - Frontend JavaScript
templates/index.html - Main HTML template
.gitignore - Git ignore rules