// Global variables
let categoryChart = null;
let trendChart = null;
let categories = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    loadCategories();
    
    // Add event listeners for period buttons
    document.querySelectorAll('[data-period]').forEach(button => {
        button.addEventListener('click', (e) => {
            // Update active state
            document.querySelectorAll('[data-period]').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            
            // Reload data
            loadDashboardData();
        });
    });
});

// Load dashboard data
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard/summary');
        if (!response.ok) throw new Error('Failed to load dashboard summary');
        
        const data = await response.json();
        
        // Update summary cards
        document.getElementById('totalBalance').textContent = formatCurrency(data.total_balance);
        document.getElementById('monthlyIncome').textContent = formatCurrency(data.monthly_income);
        document.getElementById('monthlyExpenses').textContent = formatCurrency(data.monthly_expenses);
        document.getElementById('savingsRate').textContent = formatPercentage(data.savings_rate);
        
        // Update charts
        updateCategoryChart(data.category_data);
        updateTrendChart(data.trend_data);
    } catch (error) {
        showAlert('error', 'Failed to load dashboard summary');
        console.error('Error loading dashboard data:', error);
    }
}

// Load categories
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        if (!response.ok) throw new Error('Failed to load categories');
        
        categories = await response.json();
        
        // Update categories list
        const categoriesList = document.getElementById('categoriesList');
        if (!categoriesList) return;
        
        categoriesList.innerHTML = categories.map(category => `
            <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <i class="bi ${category.icon} text-${category.color}"></i>
                    <span class="ms-2">${category.name}</span>
                </div>
                <div class="d-flex align-items-center">
                    <span class="me-2 ${category.total_amount >= 0 ? 'text-success' : 'text-danger'}">
                        ${formatCurrency(Math.abs(category.total_amount))}
                    </span>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-primary" onclick="editCategory(${category.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteCategory(${category.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        showAlert('error', 'Failed to load categories');
        console.error('Error loading categories:', error);
    }
}

// Update category chart
function updateCategoryChart(data) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.name),
            datasets: [{
                data: data.map(item => item.amount),
                backgroundColor: data.map(item => getColorForCategory(item.name)),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// Update trend chart
function updateTrendChart(data) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Income',
                    data: data.income,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Expenses',
                    data: data.expenses,
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => formatCurrency(value)
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

// Handle category form submission
async function handleCategorySubmit(event) {
    event.preventDefault();
    
    const form = document.getElementById('categoryForm');
    const formData = new FormData(form);
    const category = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(category),
        });
        
        if (!response.ok) throw new Error('Failed to add category');
        
        // Close modal and reload data
        const modal = bootstrap.Modal.getInstance(document.getElementById('addCategoryModal'));
        modal.hide();
        form.reset();
        
        showAlert('success', 'Category added successfully');
        loadCategories();
        loadDashboardData();
    } catch (error) {
        showAlert('error', 'Failed to add category');
        console.error('Error adding category:', error);
    }
}

// Delete category
async function deleteCategory(id) {
    if (!confirm('Are you sure you want to delete this category? All associated transactions will be moved to "Uncategorized".')) return;
    
    try {
        const response = await fetch(`/api/categories/${id}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) throw new Error('Failed to delete category');
        
        showAlert('success', 'Category deleted successfully');
        loadCategories();
        loadDashboardData();
    } catch (error) {
        showAlert('error', 'Failed to delete category');
        console.error('Error deleting category:', error);
    }
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(amount);
}

function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
    }).format(value / 100);
}

function getColorForCategory(categoryName) {
    const category = categories.find(c => c.name === categoryName);
    if (!category) return '#6c757d';  // Default color
    
    const colorMap = {
        'primary': '#0d6efd',
        'success': '#198754',
        'danger': '#dc3545',
        'warning': '#ffc107',
        'info': '#0dcaf0',
        'secondary': '#6c757d',
        'dark': '#212529'
    };
    
    return colorMap[category.color] || colorMap.secondary;
}

// Show alert message
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    // Auto dismiss after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
