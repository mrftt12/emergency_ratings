/**
 * Emergency Rating Calculator - Frontend JavaScript
 * Handles user interactions, API calls, and data visualizations
 */

class EmergencyRatingCalculator {
    constructor() {
        this.apiBase = '/api/thermal';
        this.charts = {};
        this.currentTab = 'emergency-rating';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupTabNavigation();
        this.loadInitialData();
    }
    
    setupEventListeners() {
        // Emergency Rating Tab
        document.getElementById('calculateEmergencyBtn').addEventListener('click', () => {
            this.calculateEmergencyRating();
        });
        
        // Conductor Temperature Tab
        document.getElementById('calculateTempBtn').addEventListener('click', () => {
            this.calculateConductorTemperature();
        });
        
        // Transient Analysis Tab
        document.getElementById('calculateTransientBtn').addEventListener('click', () => {
            this.calculateTransientAnalysis();
        });
        
        // Radial Temperature Tab
        document.getElementById('calculateRadialBtn').addEventListener('click', () => {
            this.calculateRadialTemperature();
        });
        
        // Help Modal
        document.getElementById('helpBtn').addEventListener('click', () => {
            this.showHelpModal();
        });
        
        document.getElementById('closeHelpModal').addEventListener('click', () => {
            this.hideHelpModal();
        });
        
        // Close modal when clicking outside
        document.getElementById('helpModal').addEventListener('click', (e) => {
            if (e.target.id === 'helpModal') {
                this.hideHelpModal();
            }
        });
    }
    
    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabPanels = document.querySelectorAll('.tab-panel');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Update active states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanels.forEach(panel => panel.classList.remove('active'));
                
                button.classList.add('active');
                document.getElementById(targetTab).classList.add('active');
                
                this.currentTab = targetTab;
            });
        });
    }
    
    async loadInitialData() {
        try {
            const response = await fetch(`${this.apiBase}/cable-types`);
            const data = await response.json();
            
            if (data.cable_types) {
                this.populateCableTypes(data.cable_types);
            }
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load cable types');
        }
    }
    
    populateCableTypes(cableTypes) {
        // Get all cable type select elements
        const selects = document.querySelectorAll('select[id*="cableType"], select[id*="CableType"]');
        
        selects.forEach(select => {
            select.innerHTML = '';
            
            cableTypes.forEach(cable => {
                const option = document.createElement('option');
                option.value = cable.id;
                option.textContent = cable.name;
                option.title = cable.description;
                select.appendChild(option);
            });
        });
    }
    
    async calculateEmergencyRating() {
        const data = this.getEmergencyRatingInputs();
        
        if (!this.validateEmergencyInputs(data)) {
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBase}/emergency-rating`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayEmergencyResults(result);
            } else {
                this.showError(result.error || 'Calculation failed');
            }
        } catch (error) {
            console.error('Error calculating emergency rating:', error);
            this.showError('Network error occurred');
        } finally {
            this.hideLoading();
        }
    }
    
    getEmergencyRatingInputs() {
        return {
            cable_type: document.getElementById('cableType').value,
            initial_current: parseFloat(document.getElementById('initialCurrent').value),
            emergency_duration: parseFloat(document.getElementById('emergencyDuration').value),
            max_temperature: parseFloat(document.getElementById('maxTemperature').value),
            ambient_temperature: parseFloat(document.getElementById('ambientTemp').value)
        };
    }
    
    validateEmergencyInputs(data) {
        if (data.initial_current <= 0) {
            this.showError('Initial current must be greater than 0');
            return false;
        }
        
        if (data.emergency_duration < 0.17) {
            this.showError('Emergency duration must be at least 10 minutes (0.17 hours)');
            return false;
        }
        
        if (data.max_temperature <= data.ambient_temperature) {
            this.showError('Maximum temperature must be greater than ambient temperature');
            return false;
        }
        
        return true;
    }
    
    displayEmergencyResults(result) {
        document.getElementById('emergencyCurrentResult').textContent = result.emergency_current.toFixed(0);
        document.getElementById('scalingFactorResult').textContent = result.scaling_factor.toFixed(2);
        document.getElementById('initialTempResult').textContent = result.initial_temperature.toFixed(1);
        
        const complianceElement = document.getElementById('iecComplianceResult');
        const complianceIndicator = document.getElementById('complianceIndicator');
        
        if (result.within_iec_limit) {
            complianceElement.textContent = 'PASS';
            complianceIndicator.className = 'compliance-indicator success';
            complianceIndicator.innerHTML = '<i class="fas fa-check-circle"></i><span>Within IEC 60853-2 limits (≤2.5×)</span>';
        } else {
            complianceElement.textContent = 'EXCEED';
            complianceIndicator.className = 'compliance-indicator warning';
            complianceIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Exceeds IEC 60853-2 limits (>2.5×)</span>';
        }
    }
    
    async calculateConductorTemperature() {
        const data = {
            cable_type: document.getElementById('cableType').value,
            current: parseFloat(document.getElementById('conductorCurrent').value),
            ambient_temperature: parseFloat(document.getElementById('conductorAmbient').value)
        };
        
        if (data.current <= 0) {
            this.showError('Current must be greater than 0');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBase}/steady-state-temperature`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayTemperatureResults(result);
            } else {
                this.showError(result.error || 'Calculation failed');
            }
        } catch (error) {
            console.error('Error calculating temperature:', error);
            this.showError('Network error occurred');
        } finally {
            this.hideLoading();
        }
    }
    
    displayTemperatureResults(result) {
        document.getElementById('tempValue').textContent = result.conductor_temperature.toFixed(1);
        document.getElementById('tempRiseValue').textContent = result.temperature_rise.toFixed(1);
        document.getElementById('lossesValue').textContent = result.conductor_losses.toFixed(2);
        
        // Update temperature gauge
        this.updateTemperatureGauge(result.conductor_temperature);
    }
    
    updateTemperatureGauge(temperature) {
        const gauge = document.getElementById('tempGaugeFill');
        const maxTemp = 150; // Maximum scale temperature
        const percentage = Math.min(temperature / maxTemp, 1) * 100;
        
        // Create gradient based on temperature
        let color;
        if (temperature < 40) {
            color = '#3b82f6'; // Blue
        } else if (temperature < 60) {
            color = '#10b981'; // Green
        } else if (temperature < 80) {
            color = '#f59e0b'; // Yellow
        } else {
            color = '#ef4444'; // Red
        }
        
        gauge.style.background = `conic-gradient(${color} 0% ${percentage}%, #e2e8f0 ${percentage}% 100%)`;
    }
    
    async calculateTransientAnalysis() {
        const data = {
            cable_type: document.getElementById('cableType').value,
            initial_current: parseFloat(document.getElementById('transientInitial').value),
            emergency_current: parseFloat(document.getElementById('transientEmergency').value),
            duration_hours: parseFloat(document.getElementById('transientDuration').value),
            ambient_temperature: 20,
            time_points: 100
        };
        
        if (data.initial_current <= 0 || data.emergency_current <= 0) {
            this.showError('Currents must be greater than 0');
            return;
        }
        
        if (data.duration_hours < 0.17) {
            this.showError('Duration must be at least 10 minutes (0.17 hours)');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBase}/transient-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayTransientChart(result);
            } else {
                this.showError(result.error || 'Calculation failed');
            }
        } catch (error) {
            console.error('Error calculating transient analysis:', error);
            this.showError('Network error occurred');
        } finally {
            this.hideLoading();
        }
    }
    
    displayTransientChart(data) {
        const ctx = document.getElementById('transientChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts.transient) {
            this.charts.transient.destroy();
        }
        
        this.charts.transient = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.time_hours.map(t => t.toFixed(1)),
                datasets: [{
                    label: 'Conductor Temperature (°C)',
                    data: data.temperature_celsius,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            title: function(tooltipItems) {
                                return `Time: ${tooltipItems[0].label} hours`;
                            },
                            label: function(context) {
                                return `Temperature: ${context.parsed.y.toFixed(1)}°C`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time (hours)'
                        },
                        grid: {
                            color: '#e2e8f0'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Temperature (°C)'
                        },
                        grid: {
                            color: '#e2e8f0'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
    
    async calculateRadialTemperature() {
        const data = {
            cable_type: document.getElementById('cableType').value,
            current: parseFloat(document.getElementById('radialCurrent').value),
            ambient_temperature: parseFloat(document.getElementById('radialAmbient').value),
            radial_points: 50
        };
        
        if (data.current <= 0) {
            this.showError('Current must be greater than 0');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBase}/radial-temperature`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayRadialChart(result);
                this.updateTemperatureScale(result);
            } else {
                this.showError(result.error || 'Calculation failed');
            }
        } catch (error) {
            console.error('Error calculating radial temperature:', error);
            this.showError('Network error occurred');
        } finally {
            this.hideLoading();
        }
    }
    
    displayRadialChart(data) {
        const ctx = document.getElementById('radialChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts.radial) {
            this.charts.radial.destroy();
        }
        
        // Create gradient for temperature visualization
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, '#ef4444');
        gradient.addColorStop(0.3, '#f59e0b');
        gradient.addColorStop(0.6, '#10b981');
        gradient.addColorStop(1, '#3b82f6');
        
        this.charts.radial = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.radius_mm.map(r => r.toFixed(1)),
                datasets: [{
                    label: 'Temperature (°C)',
                    data: data.temperature_celsius,
                    borderColor: '#3b82f6',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            title: function(tooltipItems) {
                                return `Radius: ${tooltipItems[0].label} mm`;
                            },
                            label: function(context) {
                                return `Temperature: ${context.parsed.y.toFixed(1)}°C`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Radius (mm)'
                        },
                        grid: {
                            color: '#e2e8f0'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Temperature (°C)'
                        },
                        grid: {
                            color: '#e2e8f0'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
        
        // Add vertical lines for cable boundaries
        this.addCableBoundaries(data.cable_boundaries);
    }
    
    addCableBoundaries(boundaries) {
        // This would add vertical lines to show cable layer boundaries
        // Implementation would depend on Chart.js annotation plugin
        console.log('Cable boundaries:', boundaries);
    }
    
    updateTemperatureScale(data) {
        const minTemp = Math.min(...data.temperature_celsius);
        const maxTemp = Math.max(...data.temperature_celsius);
        
        document.getElementById('minTempScale').textContent = `${minTemp.toFixed(0)}°C`;
        document.getElementById('maxTempScale').textContent = `${maxTemp.toFixed(0)}°C`;
    }
    
    showLoading() {
        document.getElementById('loadingOverlay').classList.add('active');
    }
    
    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('active');
    }
    
    showHelpModal() {
        document.getElementById('helpModal').classList.add('active');
    }
    
    hideHelpModal() {
        document.getElementById('helpModal').classList.remove('active');
    }
    
    showError(message) {
        // Create a simple error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-circle"></i>
                <span>${message}</span>
                <button class="error-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add error styles if not already present
        if (!document.querySelector('.error-notification-styles')) {
            const style = document.createElement('style');
            style.className = 'error-notification-styles';
            style.textContent = `
                .error-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    padding: 16px;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                    z-index: 1001;
                    max-width: 400px;
                    animation: slideIn 0.3s ease-out;
                }
                
                .error-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    color: #dc2626;
                }
                
                .error-close {
                    background: none;
                    border: none;
                    color: #dc2626;
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                    margin-left: auto;
                }
                
                .error-close:hover {
                    background: #fecaca;
                }
                
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }
}

// Utility functions for number formatting
function formatNumber(num, decimals = 2) {
    return num.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function formatCurrency(num) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(num);
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EmergencyRatingCalculator();
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal-overlay.active');
        if (activeModal) {
            activeModal.classList.remove('active');
        }
    }
    
    // Ctrl/Cmd + Enter to calculate in active tab
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeTab = document.querySelector('.tab-panel.active');
        if (activeTab) {
            const calculateBtn = activeTab.querySelector('.btn-primary');
            if (calculateBtn) {
                calculateBtn.click();
            }
        }
    }
});

// Handle window resize for charts
window.addEventListener('resize', () => {
    Object.values(window.calculator?.charts || {}).forEach(chart => {
        if (chart) {
            chart.resize();
        }
    });
});

// Export for global access if needed
window.EmergencyRatingCalculator = EmergencyRatingCalculator;

