import csv
import PyPDF2
import pdfplumber
import re
from datetime import datetime

def extract_transactions_from_pdf(pdf_path):
    """Extracts transactions from a PDF credit card bill by parsing the text."""
    transactions = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Iterate through all pages in the PDF
            for page in pdf.pages:
                # Extract text from the page
                text = page.extract_text()
                if text:
                    # Split the text into lines for easier processing
                    lines = text.split('\n')
                    
                    for line in lines:
                        
                        # Filter lines that contain a date (DD.MM.YYYY format)
                        if contains_date(line):
                            #print(f'line are...',line)
                            # Extract transaction details
                            # Match patterns for date, description, and amount using regular expressions
                            transaction = parse_transaction_line_nomral(line)
                            if transaction:
                                transactions.append(transaction)
                        
                       
    except Exception as e:
        print(f"Error reading PDF: {e}")
    
    print(f'final transactions are...',transactions)
    return transactions

def contains_date(line):
    """Check if the line contains a date in DD.MM.YYYY format."""
    date_pattern = r"\d{2}\.\d{2}\.\d{4}"  # Date pattern (DD.MM.YYYY)
    return bool(re.search(date_pattern, line))

def is_valid_date(date_str):
    """Check if the given string is a valid date in DD.MM.YYYY format."""
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except ValueError:
        return False

def is_invalid_line(line):
    """Check if the line contains multiple dates or a non-transactional format."""
    # Regex to detect multiple date patterns or date phrases (e.g., "Abrechnung vom")
    if re.search(r"\d{2}\.\d{2}\.\d{4}.*\d{2}\.\d{2}\.\d{4}", line):  # Two dates in the line
        return True
    if "Abrechnung vom" in line or "Rechnung vom" in line or "Mindestbetrag" in line or "Karteninhabers" in line or "Fällig" in line or "5.000,00EUR" in line or "NEUER" in line:  # Date phrases or other non-transactional formats
        return True
    return False

def parse_transaction_line_nomral(line):
    """Parse a single line of text to extract date, description, place, and amount."""
    # Split the line into parts
    parts = line.strip().split(' ')
    
    # Check if the first part is a valid date (DD.MM.YYYY format)
    if not is_valid_date(parts[0]) or is_invalid_line(line):
        return None  # If not a valid date or invalid line (e.g., Abrechnung), ignore this line
    

    # First part is the date (assumed to be in DD.MM.YYYY format)
    date = parts[0]
    
    # Try to find where the amount is located (the last part of the line)
    amount_str = parts[-1]
    
    # Convert the amount to a float (handle commas)
    amount = float(amount_str.replace(',', '.'))
    
    # The place is usually just before the amount
    place = parts[-2]

    # The description is everything between the date and the place
    description = ' '.join(parts[1:-2])
    
    return {
        'Date': date,
        'Description': description.strip(),
        'Category': place.strip(),
        'Amount': amount
    }
    
    
    # Check each category's keywords
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    
    return 'UNCATEGORIZED'

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
