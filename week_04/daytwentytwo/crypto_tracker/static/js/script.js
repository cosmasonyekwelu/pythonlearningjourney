// Custom JavaScript for Trading Journal
document.addEventListener('DOMContentLoaded', function() {
    console.log('Trading Journal loaded successfully!');
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Auto-refresh crypto prices every 60 seconds
    if (window.location.pathname.includes('/crypto/prices')) {
        setupCryptoAutoRefresh();
    }
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.textContent.includes('Refresh') || this.textContent.includes('Update')) {
                showButtonLoading(this);
            }
        });
    });
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('alert-dismissible')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
    
    // Trade row click handlers
    const tradeRows = document.querySelectorAll('.trade-row');
    tradeRows.forEach(row => {
        row.addEventListener('click', function() {
            const tradeId = this.dataset.tradeId;
            if (tradeId) {
                window.location.href = `/trade/${tradeId}`;
            }
        });
    });
    
    // Portfolio value formatting
    formatPortfolioValues();
});

function setupCryptoAutoRefresh() {
    // Auto-refresh every 60 seconds
    setInterval(() => {
        console.log('Auto-refreshing crypto prices...');
        showRefreshNotification();
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }, 60000);
    
    // Show initial refresh notification
    showRefreshNotification();
}

function showRefreshNotification() {
    // Remove existing notification
    const existingAlert = document.querySelector('.refresh-notification');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Create new notification
    const refreshInfo = document.createElement('div');
    refreshInfo.className = 'alert alert-info alert-dismissible fade show refresh-notification mt-3';
    refreshInfo.innerHTML = `
        <strong>Info:</strong> Prices auto-refresh every 60 seconds.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(refreshInfo, container.firstChild);
    }
}

function showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Loading...';
    button.disabled = true;
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 2000);
}

function formatPortfolioValues() {
    // Format portfolio values with commas
    const valueElements = document.querySelectorAll('.portfolio-value');
    valueElements.forEach(element => {
        const value = parseFloat(element.textContent.replace(/[^0-9.-]+/g, ""));
        if (!isNaN(value)) {
            element.textContent = '$' + value.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    });
}

// API call functions
async function fetchPortfolioData() {
    try {
        const response = await fetch('/api/portfolio');
        const data = await response.json();
        updatePortfolioDisplay(data);
    } catch (error) {
        console.error('Error fetching portfolio data:', error);
    }
}

function updatePortfolioDisplay(data) {
    // Update portfolio stats on the page
    console.log('Portfolio data updated:', data);
}

// Utility function to format numbers
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatNumber(number) {
    return new Intl.NumberFormat('en-US').format(number);
}