document.addEventListener('DOMContentLoaded', function() {
    loadTransactions();
    
    // Handle form submission
    document.getElementById('transaction-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const transaction = {
            description: document.getElementById('description').value,
            amount: document.getElementById('amount').value,
            category: document.getElementById('category').value,
            type: document.getElementById('type').value
        };

        try {
            const response = await fetch('/api/transactions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(transaction)
            });

            if (response.ok) {
                // Clear form
                this.reset();
                // Reload transactions
                loadTransactions();
            } else {
                alert('Error adding transaction');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error adding transaction');
        }
    });
});

async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();
        
        updateTransactionsList(transactions);
        updateSummary(transactions);
    } catch (error) {
        console.error('Error:', error);
    }
}

function updateTransactionsList(transactions) {
    const tbody = document.getElementById('transactions-table');
    tbody.innerHTML = '';
    
    transactions.forEach(transaction => {
        const row = document.createElement('tr');
        const amountClass = transaction.type === 'income' ? 'transaction-amount-positive' : 'transaction-amount-negative';
        const amountPrefix = transaction.type === 'income' ? '+' : '-';
        
        row.innerHTML = `
            <td>${transaction.date}</td>
            <td>${transaction.description}</td>
            <td>${transaction.category}</td>
            <td class="${amountClass}">${amountPrefix}$${Math.abs(transaction.amount).toFixed(2)}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function updateSummary(transactions) {
    let income = 0;
    let expenses = 0;
    
    transactions.forEach(transaction => {
        if (transaction.type === 'income') {
            income += parseFloat(transaction.amount);
        } else {
            expenses += parseFloat(transaction.amount);
        }
    });
    
    const balance = income - expenses;
    
    document.getElementById('total-income').textContent = `$${income.toFixed(2)}`;
    document.getElementById('total-expenses').textContent = `$${expenses.toFixed(2)}`;
    document.getElementById('balance').textContent = `$${balance.toFixed(2)}`;
}
