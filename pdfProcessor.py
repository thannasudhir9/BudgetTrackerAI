import pdfplumber
import re
from datetime import datetime
from typing import List, Dict, Any

def extract_transactions_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract transactions from a PDF file.
    Returns a list of dictionaries containing transaction information.
    """
    transactions = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Split text into lines
                lines = text.split('\n')
                
                for line in lines:
                    # Skip empty lines
                    if not line.strip():
                        continue
                    
                    # Try to extract transaction information
                    transaction = parse_transaction_line(line)
                    if transaction:
                        transactions.append(transaction)
    
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return []
    
    return transactions

def parse_transaction_line(line: str) -> Dict[str, Any]:
    """
    Parse a single line of text to extract transaction information.
    Returns a dictionary with transaction details if successful, None otherwise.
    """
    try:
        # Common date patterns
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}-\d{2}-\d{2}'   # YYYY-MM-DD
        ]
        
        # Amount pattern (handles negative amounts and decimals)
        amount_pattern = r'-?\$?\d+(?:,\d{3})*(?:\.\d{2})?'
        
        # Try to find date
        date_str = None
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                date_str = match.group()
                break
        
        if not date_str:
            return None
        
        # Try to find amount
        amount_match = re.search(amount_pattern, line)
        if not amount_match:
            return None
            
        amount_str = amount_match.group()
        # Clean up amount string
        amount = float(amount_str.replace('$', '').replace(',', ''))
        
        # Extract description (everything between date and amount)
        description = line
        for pattern in date_patterns:
            description = re.sub(pattern, '', description)
        description = re.sub(amount_pattern, '', description)
        description = re.sub(r'\s+', ' ', description).strip()
        
        # Try different date formats
        date = None
        date_formats = [
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%Y-%m-%d'
        ]
        
        for fmt in date_formats:
            try:
                date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if not date:
            return None
        
        # Determine transaction type based on amount
        transaction_type = 'income' if amount > 0 else 'expense'
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'description': description,
            'amount': abs(amount),
            'type': transaction_type,
            'category': guess_transaction_category(description)  # Guess category
        }
        
    except Exception as e:
        print(f"Error parsing line: {str(e)}")
        return None

def guess_transaction_category(description: str) -> str:
    """
    Guess the transaction category based on the description.
    Returns a category name from the TransactionCategory enum.
    """
    description = description.lower()
    
    # Define category keywords
    categories = {
        'FOOD': ['restaurant', 'cafe', 'food', 'grocery', 'meal', 'lunch', 'dinner', 'breakfast'],
        'TRANSPORTATION': ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'parking', 'transit', 'train', 'bus'],
        'ENTERTAINMENT': ['movie', 'theatre', 'concert', 'netflix', 'spotify', 'game', 'entertainment'],
        'SHOPPING': ['amazon', 'walmart', 'target', 'store', 'shop', 'mall'],
        'BILLS': ['bill', 'utility', 'electric', 'water', 'rent', 'insurance', 'phone', 'internet'],
        'SALARY': ['salary', 'payroll', 'payment', 'deposit'],
        'OTHER_INCOME': ['refund', 'return', 'credit', 'interest']
    }
    
    # Check each category's keywords
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    
    return 'UNCATEGORIZED'

def extract_transactions_from_csv(csv_path):
    """Reads a CSV credit card bill and extracts transactions."""
    transactions = []
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    transaction = {
                        'date': row.get('Date', '').strip(),
                        'description': row.get('Description', '').strip(),
                        'amount': float(row.get('Amount', 0).replace('€', '').replace(',', '.').strip())
                    }
                    if transaction['date'] and transaction['description'] and transaction['amount']:
                        transactions.append(transaction)
                except (ValueError, KeyError) as e:
                    # Skip malformed or incomplete rows
                    print(f"Skipping row due to error: {e}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return transactions

def read_credit_card_bill(file_path):
    """Main function to handle both PDF and CSV files."""
    if file_path.endswith('.pdf'):
        return extract_transactions_from_pdf(file_path)
    elif file_path.endswith('.csv'):
        return extract_transactions_from_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and CSV files are supported.")

# Example Usage
if __name__ == "__main__":
    pdf_path = r"D:\NeatDownloader\expense_tracker_app\Docs\Rechnung_03.11.2024_40005522888.pdf"
    transactions = read_credit_card_bill(pdf_path)
    
    # Print first 5 transactions as an example
    #for i, transaction in enumerate(transactions[:5]):
    #    print(f"{i+1}. Date: {transaction['date']}, Description: {transaction['description']}, Amount: €{transaction['amount']:.2f}")

    # Print extracted transactions
    for transaction in transactions:
        print(f"Date: {transaction['date']}, Description: {transaction['description']}, Amount: €{transaction['amount']:.2f}")
