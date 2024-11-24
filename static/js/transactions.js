// Global variables
let categories = [];
let transactions = [];
let currentPeriod = 'all';

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    Promise.all([loadCategories(), loadTransactions()])
        .then(() => {
            console.log('Initial data loaded');
        })
        .catch(error => {
            console.error('Error loading initial data:', error);
        });
    
    // Set up period filter buttons
    document.querySelectorAll('[data-period]').forEach(button => {
        button.addEventListener('click', (e) => {
            currentPeriod = e.target.dataset.period;
            // Update active state
            document.querySelectorAll('[data-period]').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            // Reload transactions
            loadTransactions();
        });
    });
    
    // Set up transaction form submissions
    const transactionForm = document.getElementById('transactionForm');
    if (transactionForm) {
        transactionForm.addEventListener('submit', handleTransactionSubmit);
    }
    
    const editTransactionForm = document.getElementById('editTransactionForm');
    if (editTransactionForm) {
        editTransactionForm.addEventListener('submit', handleEditTransactionSubmit);
    }
    
    // Set up category form submissions
    const categoryForm = document.getElementById('categoryForm');
    if (categoryForm) {
        categoryForm.addEventListener('submit', handleCategorySubmit);
    }
    
    const editCategoryForm = document.getElementById('editCategoryForm');
    if (editCategoryForm) {
        editCategoryForm.addEventListener('submit', handleEditCategorySubmit);
    }
    
    // Set up modal event listeners
    const addTransactionModal = document.getElementById('addTransactionModal');
    if (addTransactionModal) {
        addTransactionModal.addEventListener('show.bs.modal', function () {
            console.log('Add Transaction modal opening');
            updateCategoryDropdowns();
        });
        
        addTransactionModal.addEventListener('shown.bs.modal', function () {
            // Focus on description field when modal is fully shown
            document.getElementById('description').focus();
        });
        
        addTransactionModal.addEventListener('hidden.bs.modal', function () {
            // Reset form when modal is closed
            transactionForm.reset();
            const today = new Date().toISOString().split('T')[0];
            document.querySelector('#transactionForm input[type="date"]').value = today;
        });
    }
});

// Load categories
async function loadCategories() {
    try {
        console.log('Loading categories...');
        const response = await fetch('/api/categories');
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load categories');
        }
        
        categories = await response.json();
        console.log('Loaded categories:', categories);
        
        // Update categories list
        const categoriesList = document.getElementById('categoriesList');
        if (categoriesList) {
            if (categories.length === 0) {
                categoriesList.innerHTML = `
                    <div class="list-group-item text-center">
                        <p class="mb-0">No categories found</p>
                        <small class="text-muted">Click the + button to add a category</small>
                    </div>
                `;
            } else {
                categoriesList.innerHTML = categories.map(category => `
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <i class="bi ${category.icon} text-${category.color}"></i>
                            <span class="ms-2">${category.name}</span>
                        </div>
                        <div class="d-flex align-items-center">
                            <span class="me-2 ${category.total_amount >= 0 ? 'text-success' : 'text-danger'}">
                                ${formatCurrency(Math.abs(category.total_amount || 0))}
                            </span>
                            <button class="btn btn-sm btn-outline-primary" onclick="editCategory(${category.id})">
                                <i class="bi bi-pencil"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        }
        
        // Update dropdowns after loading categories
        updateCategoryDropdowns();
        return categories;
    } catch (error) {
        console.error('Error loading categories:', error);
        showAlert('danger', error.message);
        throw error;
    }
}

// Update category dropdowns
function updateCategoryDropdowns() {
    console.log('Updating category dropdowns with categories:', categories);
    // Select both add and edit transaction dropdowns
    const addDropdown = document.getElementById('category_id');
    const editDropdown = document.getElementById('editTransactionCategory');
    
    if (!addDropdown && !editDropdown) {
        console.log('No category dropdowns found');
        return;
    }
    
    const defaultOption = '<option value="">Select a category</option>';
    const categoryOptions = categories.map(category => 
        `<option value="${category.id}">
            <i class="bi ${category.icon} text-${category.color}"></i>
            ${category.name}
        </option>`
    ).join('');
    
    console.log('Category options:', categoryOptions);
    
    // Update add transaction dropdown
    if (addDropdown) {
        addDropdown.innerHTML = defaultOption + categoryOptions;
    }
    
    // Update edit transaction dropdown
    if (editDropdown) {
        editDropdown.innerHTML = defaultOption + categoryOptions;
    }
}

// Load transactions
async function loadTransactions() {
    try {
        console.log('Loading transactions...');
        const response = await fetch('/api/transactions');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load transactions');
        }
        
        transactions = await response.json();
        console.log('Loaded transactions:', transactions);
        
        const tbody = document.querySelector('#transactionTableBody');
        if (!tbody) {
            console.error('Could not find transactions table body');
            return;
        }
        
        if (transactions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">
                        <p class="mb-0">No transactions found</p>
                        <small class="text-muted">Click the "Add Transaction" button to create one</small>
                    </td>
                </tr>
            `;
            // Reset summary when no transactions
            document.getElementById('totalIncome').textContent = formatCurrency(0);
            document.getElementById('totalExpenses').textContent = formatCurrency(0);
            document.getElementById('balance').textContent = formatCurrency(0);
            return;
        }
        
        tbody.innerHTML = transactions.map(transaction => `
            <tr>
                <td>${transaction.date.split('T')[0]}</td>
                <td>${transaction.description}</td>
                <td>
                    <i class="bi ${transaction.category.icon} text-${transaction.category.color}"></i>
                    ${transaction.category.name}
                </td>
                <td class="${transaction.amount >= 0 ? 'text-success' : 'text-danger'}">
                    ${formatCurrency(Math.abs(transaction.amount))}
                </td>
                <td>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-primary" onclick="editTransaction(${transaction.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTransaction(${transaction.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
        
        updateTransactionSummary();
    } catch (error) {
        console.error('Error loading transactions:', error);
        showAlert('danger', error.message);
    }
}

// Handle transaction form submission
async function handleTransactionSubmit(event) {
    event.preventDefault();
    
    try {
        const formData = new FormData(event.target);
        const categoryId = formData.get('category_id');
        
        if (!categoryId) {
            throw new Error('Please select a category');
        }
        
        const data = {
            description: formData.get('description'),
            amount: parseFloat(formData.get('amount')),
            category_id: parseInt(categoryId),
            type: formData.get('type'),
            date: formData.get('date')
        };
        
        console.log('Submitting transaction with data:', data);

        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add transaction');
        }

        // Reset form and close modal
        event.target.reset();
        const modal = bootstrap.Modal.getInstance(document.getElementById('addTransactionModal'));
        modal.hide();

        // Reload transactions and show success message
        await Promise.all([loadTransactions(), loadCategories()]);
        showAlert('success', 'Transaction added successfully');
    } catch (error) {
        console.error('Error submitting transaction:', error);
        showAlert('danger', error.message);
    }
}

// Edit transaction
async function editTransaction(transactionId) {
    try {
        // First get the transaction details
        const response = await fetch(`/api/transactions/${transactionId}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to fetch transaction details');
        }
        const transaction = await response.json();
        
        // Populate the edit form
        const form = document.getElementById('editTransactionForm');
        form.querySelector('#editTransactionId').value = transaction.id;
        form.querySelector('#editTransactionDescription').value = transaction.description;
        form.querySelector('#editTransactionAmount').value = transaction.amount;
        form.querySelector('#editTransactionCategory').value = transaction.category_id;
        form.querySelector('#editTransactionType').value = transaction.type;
        form.querySelector('#editTransactionDate').value = transaction.date;
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('editTransactionModal'));
        modal.show();
    } catch (error) {
        console.error('Error fetching transaction:', error);
        showAlert('danger', error.message);
    }
}

// Handle edit transaction submission
async function handleEditTransactionSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const transactionId = form.querySelector('#editTransactionId').value;
    let amount = parseFloat(form.querySelector('#editTransactionAmount').value);
    const type = form.querySelector('#editTransactionType').value;
    
    // Make amount negative for expenses
    if (type === 'expense') {
        amount = -Math.abs(amount);
    } else {
        amount = Math.abs(amount);
    }
    
    const formData = {
        description: form.querySelector('#editTransactionDescription').value,
        amount: amount,
        type: type,
        category_id: parseInt(form.querySelector('#editTransactionCategory').value),
        date: form.querySelector('#editTransactionDate').value
    };

    try {
        const response = await fetch(`/api/transactions/${transactionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update transaction');
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editTransactionModal'));
        modal.hide();
        
        // Refresh transactions and update summary
        await Promise.all([loadTransactions(), updateTransactionSummary()]);
        showAlert('success', 'Transaction updated successfully');
    } catch (error) {
        console.error('Error updating transaction:', error);
        showAlert('danger', error.message);
    }
}

// Delete transaction
async function deleteTransaction(id) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;
    
    try {
        const response = await fetch(`/api/transactions/${id}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) throw new Error('Failed to delete transaction');
        
        showAlert('success', 'Transaction deleted successfully');
        loadTransactions();
    } catch (error) {
        showAlert('error', 'Failed to delete transaction');
        console.error('Error deleting transaction:', error);
    }
}

// Update transaction summary
function updateTransactionSummary() {
    const income = transactions
        .filter(t => t.amount > 0)
        .reduce((sum, t) => sum + t.amount, 0);
    
    const expenses = transactions
        .filter(t => t.amount < 0)
        .reduce((sum, t) => sum + Math.abs(t.amount), 0);
    
    const balance = income - expenses;
    
    document.getElementById('totalIncome').textContent = formatCurrency(income);
    document.getElementById('totalExpenses').textContent = formatCurrency(expenses);
    document.getElementById('balance').textContent = formatCurrency(balance);
    
    // Update balance color based on value
    const balanceElement = document.getElementById('balance');
    balanceElement.className = balance >= 0 ? 'card-title text-success' : 'card-title text-danger';
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(amount);
}

// Category Management Functions
async function addCategory() {
    const form = document.getElementById('addCategoryForm');
    const formData = {
        name: form.querySelector('#categoryName').value,
        icon: form.querySelector('#categoryIcon').value,
        color: form.querySelector('#categoryColor').value
    };

    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add category');
        }

        const result = await response.json();
        console.log('Category added:', result);
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
        modal.hide();
        form.reset();
        
        // Refresh categories
        await loadCategories();
        showAlert('success', 'Category added successfully');
    } catch (error) {
        console.error('Error adding category:', error);
        showAlert('danger', error.message);
    }
}

async function editCategory(categoryId) {
    try {
        // First get the category details
        const response = await fetch(`/api/categories/${categoryId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch category details');
        }
        const category = await response.json();
        
        // Populate the edit form
        const form = document.getElementById('editCategoryForm');
        form.querySelector('#editCategoryId').value = category.id;
        form.querySelector('#editCategoryName').value = category.name;
        form.querySelector('#editCategoryIcon').value = category.icon;
        form.querySelector('#editCategoryColor').value = category.color;
        
        // Show the modal
        const editModal = new bootstrap.Modal(document.getElementById('editCategoryModal'));
        editModal.show();
    } catch (error) {
        console.error('Error fetching category:', error);
        showAlert('danger', error.message);
    }
}

async function saveEditedCategory() {
    const form = document.getElementById('editCategoryForm');
    const categoryId = form.querySelector('#editCategoryId').value;
    const formData = {
        name: form.querySelector('#editCategoryName').value,
        icon: form.querySelector('#editCategoryIcon').value,
        color: form.querySelector('#editCategoryColor').value
    };

    try {
        const response = await fetch(`/api/categories/${categoryId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update category');
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editCategoryModal'));
        modal.hide();
        
        // Refresh categories
        await loadCategories();
        showAlert('success', 'Category updated successfully');
    } catch (error) {
        console.error('Error updating category:', error);
        showAlert('danger', error.message);
    }
}

async function deleteCategory(categoryId) {
    if (!confirm('Are you sure you want to delete this category? All associated transactions will be affected.')) {
        return;
    }

    try {
        const response = await fetch(`/api/categories/${categoryId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete category');
        }

        // Refresh categories
        await loadCategories();
        showAlert('success', 'Category deleted successfully');
    } catch (error) {
        console.error('Error deleting category:', error);
        showAlert('danger', error.message);
    }
}

// Utility function to show alerts
function showAlert(type, message) {
    const alertsContainer = document.getElementById('alerts');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Handle category form submission
async function handleCategorySubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = {
        name: form.querySelector('#name').value,
        icon: form.querySelector('#icon').value,
        color: form.querySelector('#color').value
    };

    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add category');
        }

        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
        modal.hide();
        form.reset();
        
        // Refresh categories
        await loadCategories();
        showAlert('success', 'Category added successfully');
    } catch (error) {
        console.error('Error adding category:', error);
        showAlert('danger', error.message);
    }
}

// Handle edit category form submission
async function handleEditCategorySubmit(event) {
    event.preventDefault();
    const form = event.target;
    const categoryId = form.querySelector('#editCategoryId').value;
    const formData = {
        name: form.querySelector('#editCategoryName').value,
        icon: form.querySelector('#editCategoryIcon').value,
        color: form.querySelector('#editCategoryColor').value
    };

    try {
        const response = await fetch(`/api/categories/${categoryId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update category');
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editCategoryModal'));
        modal.hide();
        
        // Refresh categories
        await loadCategories();
        showAlert('success', 'Category updated successfully');
    } catch (error) {
        console.error('Error updating category:', error);
        showAlert('danger', error.message);
    }
}
