//filename : utilizationmetrics.js
// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Budget management and gauge visualization
    window.gauges = {};
    let budgetModal;

    // Initialize modal after Bootstrap is loaded
    function initModal() {
        const modalElement = document.getElementById('budgetEditModal');
        if (modalElement && window.bootstrap) {
            budgetModal = new bootstrap.Modal(modalElement);
        } else {
            console.error('Bootstrap Modal initialization failed');
        }
    }

    function initializeGauges() {
        const gaugeTypes = ['monthly', 'quarterly', 'yearly'];
        gaugeTypes.forEach(type => {
            const canvas = document.getElementById(`${type}Gauge`);
            if (!canvas) {
                console.error(`Canvas element for ${type} gauge not found`);
                return;
            }

            const container = canvas.closest('.gauge-container');
            if (container) {
                container.style.position = 'relative';
                container.style.height = '200px';
            }

            const ctx = canvas.getContext('2d');
            window.gauges[type] = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [0, 100],
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.9)',  // Green for spent (more opaque)
                            'rgba(200, 200, 200, 0.2)' // Light gray for remaining (more transparent)
                        ],
                        borderWidth: 1,
                        borderColor: ['rgba(40, 167, 69, 1)', 'rgba(200, 200, 200, 0.5)']
                    }]
                },
                options: {
                    cutout: '85%',
                    rotation: -90,
                    circumference: 180,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    }
                }
            });
        });
    }

    function updateUtilizationMeters() {
        const yearSelect = document.getElementById('yearSelect');
        const monthSelect = document.getElementById('monthSelect');
        
        if (!yearSelect || !monthSelect) {
            console.error('Year or month select elements not found');
            return;
        }

        const currentDate = new Date();
        const year = yearSelect.value || currentDate.getFullYear();
        const month = monthSelect.value || (currentDate.getMonth() + 1);

        const validYear = parseInt(year);
        const validMonth = parseInt(month);

        if (isNaN(validYear) || isNaN(validMonth)) {
            console.error('Invalid year or month values:', year, month);
            return;
        }

        fetch(`/api/utilization-metrics/${validYear}/${validMonth}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data && typeof data === 'object') {
                    // Monthly gauge update
                    if (data.monthly) {
                        const monthlyPercentage = (data.monthly.spent / data.monthly.budget) * 100;
                        updateGaugeAndText('monthly', data.monthly, monthlyPercentage);
                    }

                    // Quarterly gauge update
                    if (data.quarterly) {
                        const quarterlyPercentage = (data.quarterly.spent / data.quarterly.budget) * 100;
                        updateGaugeAndText('quarterly', data.quarterly, quarterlyPercentage);
                    }

                    // Yearly gauge update
                    if (data.yearly) {
                        const yearlyPercentage = (data.yearly.spent / data.yearly.budget) * 100;
                        updateGaugeAndText('yearly', data.yearly, yearlyPercentage);
                    }
                } else {
                    console.error('Invalid data format received from server');
                }
            })
            .catch(error => {
                console.error('Error updating utilization meters:', error);
            });
    }

    function updateGaugeAndText(type, data, percentage) {
        // Update gauge
        const gauge = window.gauges[type];
        if (gauge) {
            gauge.data.datasets[0].data = [percentage, Math.max(0, 100 - percentage)];
            
            // Update colors based on percentage
            let color, backgroundColor;
            if (percentage >= 90) {
                color = 'rgba(220, 53, 69, 1)';  // Bright red
                backgroundColor = 'rgba(220, 53, 69, 0.3)';
            } else if (percentage >= 75) {
                color = 'rgba(255, 193, 7, 1)';  // Bright yellow
                backgroundColor = 'rgba(255, 193, 7, 0.3)';
            } else {
                color = 'rgba(40, 167, 69, 1)';  // Bright green
                backgroundColor = 'rgba(40, 167, 69, 0.3)';
            }
            
            gauge.data.datasets[0].backgroundColor = [color, backgroundColor];
            gauge.data.datasets[0].borderColor = [color, color];
            gauge.data.datasets[0].borderWidth = 2;
            gauge.update();
        }

        // Update text displays
        const spentElement = document.getElementById(`${type}Spent`);
        const budgetElement = document.getElementById(`${type}Budget`);
        const percentageElement = document.getElementById(`${type}Percentage`);

        if (spentElement) {
            spentElement.textContent = formatCurrency(data.spent);
            spentElement.classList.add('spent-amount');
        }
        if (budgetElement) {
            budgetElement.textContent = formatCurrency(data.budget);
            budgetElement.classList.add('budget-amount');
        }
        if (percentageElement) {
            percentageElement.textContent = `${percentage.toFixed(1)}%`;
            // Update percentage color based on value
            percentageElement.classList.remove('utilization-low', 'utilization-medium', 'utilization-high');
            if (percentage >= 90) {
                percentageElement.classList.add('utilization-high');
            } else if (percentage >= 75) {
                percentageElement.classList.add('utilization-medium');
            } else {
                percentageElement.classList.add('utilization-low');
            }
        }
    }

    function editBudget(type) {
        if (!budgetModal) {
            console.error('Budget modal not initialized');
            return;
        }

        const typeInput = document.getElementById('editBudgetType');
        const amountInput = document.getElementById('budgetAmount');
        const currentBudgetElement = document.getElementById(`${type}Budget`);

        if (!typeInput || !amountInput) {
            console.error('Required modal elements not found');
            return;
        }

        typeInput.value = type;
        if (currentBudgetElement) {
            const currentBudget = currentBudgetElement.textContent;
            amountInput.value = parseFloat(currentBudget.replace(/[^0-9.-]+/g, ''));
        }
        budgetModal.show();
    }

    function saveBudget() {
        const typeInput = document.getElementById('editBudgetType');
        const amountInput = document.getElementById('budgetAmount');

        if (!typeInput || !amountInput) {
            console.error('Required form elements not found');
            return;
        }

        const amount = parseFloat(amountInput.value);
        if (isNaN(amount) || amount <= 0) {
            alert('Please enter a valid positive number');
            return;
        }

        fetch('/api/save-budget', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: typeInput.value,
                amount: amount
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            budgetModal.hide();
            updateUtilizationMeters();
        })
        .catch(error => {
            console.error('Error saving budget:', error);
            alert('Failed to save budget. Please try again.');
        });
    }

    // Helper function to format currency
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    // Make functions globally accessible
    window.editBudget = editBudget;
    window.saveBudget = saveBudget;
    window.formatCurrency = formatCurrency;

    // Initialize components
    initModal();
    initializeGauges();
    updateUtilizationMeters();

    // Add event listeners for updates
    const monthSelect = document.getElementById('monthSelect');
    const yearSelect = document.getElementById('yearSelect');
    
    if (monthSelect) {
        monthSelect.addEventListener('change', updateUtilizationMeters);
    }
    if (yearSelect) {
        yearSelect.addEventListener('change', updateUtilizationMeters);
    }
});