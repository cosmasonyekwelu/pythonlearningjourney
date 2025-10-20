class CryptoDashboard {
    constructor() {
        this.prices = {};
        this.chart = null;
        this.selectedSymbol = 'BTCUSDT';
        this.updateInterval = 2000; // 2 seconds
        
        this.init();
    }

    init() {
        this.loadPrices();
        this.setupAutoRefresh();
        this.setupChart();
        
        // Update statistics
        this.loadStatistics();
        setInterval(() => this.loadStatistics(), 5000);
    }

    async loadPrices() {
        try {
            const response = await fetch('/api/prices');
            const data = await response.json();
            
            this.updateConnectionStatus(data.connection_status);
            this.updateLastUpdate(data.last_update);
            this.updatePriceGrid(data.prices);
            this.updateChartData();
            
        } catch (error) {
            console.error('Error loading prices:', error);
            this.updateConnectionStatus('error');
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/statistics');
            const data = await response.json();
            
            if (!data.error) {
                document.getElementById('message-count').textContent = data.message_count;
                document.getElementById('symbol-count').textContent = data.connected_symbols;
                document.getElementById('ws-status').textContent = data.connection_status;
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        statusElement.className = `status-${status}`;
    }

    updateLastUpdate(timestamp) {
        const time = new Date(timestamp).toLocaleTimeString();
        document.getElementById('last-update').textContent = `Last update: ${time}`;
    }

    updatePriceGrid(prices) {
        const grid = document.getElementById('price-grid');
        grid.innerHTML = '';

        Object.entries(prices).forEach(([symbol, data]) => {
            const change = data.change_percent || 0;
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const changeSymbol = change >= 0 ? '↗' : '↘';
            
            const card = document.createElement('div');
            card.className = `price-card ${changeClass}`;
            card.onclick = () => this.selectSymbol(symbol);
            
            card.innerHTML = `
                <div class="symbol">${symbol.replace('USDT', '')}</div>
                <div class="price">$${data.price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 4})}</div>
                <div class="change ${changeClass}">
                    ${changeSymbol} ${Math.abs(change).toFixed(2)}%
                </div>
                ${data.volume ? `<div class="volume">Vol: ${this.formatVolume(data.volume)}</div>` : ''}
                <div class="time">${new Date(data.timestamp * 1000).toLocaleTimeString()}</div>
            `;
            
            grid.appendChild(card);
        });
    }

    formatVolume(volume) {
        if (volume >= 1000000) {
            return (volume / 1000000).toFixed(2) + 'M';
        } else if (volume >= 1000) {
            return (volume / 1000).toFixed(2) + 'K';
        }
        return volume.toFixed(2);
    }

    selectSymbol(symbol) {
        this.selectedSymbol = symbol;
        this.updateChartData();
    }

    setupChart() {
        const ctx = document.getElementById('price-chart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Price',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Price History'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }

    async updateChartData() {
        try {
            const response = await fetch(`/api/history/${this.selectedSymbol}`);
            const history = await response.json();
            
            if (history.length > 0) {
                const labels = history.map(item => item.time);
                const prices = history.map(item => item.price);
                
                this.chart.data.labels = labels;
                this.chart.data.datasets[0].data = prices;
                this.chart.data.datasets[0].label = `${this.selectedSymbol} Price`;
                this.chart.update();
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    setupAutoRefresh() {
        setInterval(() => this.loadPrices(), this.updateInterval);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new CryptoDashboard();
});