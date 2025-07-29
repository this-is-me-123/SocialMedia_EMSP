// Dashboard JavaScript for Test Results

// Global variables
let testData = {
    suites: [],
    stats: {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        duration: 0
    },
    performance: {
        responseTimes: [],
        requestsPerSecond: 0,
        failures: 0,
        p95: 0
    },
    lastUpdated: new Date().toISOString()
};

// Chart instances
let pieChart, timeChart, performanceChart;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', async () => {
    // Set last updated time
    document.getElementById('last-updated').textContent = new Date().toLocaleString();
    
    // Load test data
    try {
        await loadTestData();
        updateSummaryCards();
        renderTestSuites();
        initCharts();
        setupEventListeners();
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Failed to load test data. Please check the console for details.');
    }
});

// Load test data from JSON files
async function loadTestData() {
    try {
        // In a real implementation, this would fetch data from your test results
        // For now, we'll use mock data
        testData = {
            suites: [
                {
                    name: 'Unit Tests',
                    passed: 42,
                    failed: 2,
                    skipped: 1,
                    duration: 1234,
                    testCases: [
                        { name: 'test_user_creation', status: 'passed', duration: 120 },
                        { name: 'test_post_validation', status: 'passed', duration: 85 },
                        { name: 'test_api_authentication', status: 'failed', duration: 45, error: 'Authentication failed' },
                        { name: 'test_skip_example', status: 'skipped', duration: 0 }
                    ]
                },
                {
                    name: 'Integration Tests',
                    passed: 28,
                    failed: 1,
                    skipped: 0,
                    duration: 3456,
                    testCases: [
                        { name: 'test_database_connection', status: 'passed', duration: 320 },
                        { name: 'test_external_api', status: 'failed', duration: 1500, error: 'Timeout' }
                    ]
                },
                {
                    name: 'Performance Tests',
                    passed: 5,
                    failed: 0,
                    skipped: 0,
                    duration: 12000,
                    testCases: [
                        { name: 'test_load_homepage', status: 'passed', duration: 1200 },
                        { name: 'test_api_response_time', status: 'passed', duration: 8500 }
                    ]
                }
            ],
            stats: {
                total: 75,
                passed: 70,
                failed: 3,
                skipped: 2,
                duration: 16690
            },
            performance: {
                responseTimes: [120, 85, 150, 200, 180, 220, 190, 210, 230, 250],
                requestsPerSecond: 45.7,
                failures: 2,
                p95: 215
            },
            lastUpdated: new Date().toISOString()
        };
        
        // Update last updated time
        testData.lastUpdated = new Date().toISOString();
        document.getElementById('last-updated').textContent = new Date(testData.lastUpdated).toLocaleString();
        
        return testData;
    } catch (error) {
        console.error('Error loading test data:', error);
        throw error;
    }
}

// Update summary cards with test statistics
function updateSummaryCards() {
    const { total, passed, failed, skipped } = testData.stats;
    
    document.getElementById('total-count').textContent = total;
    document.getElementById('passed-count').textContent = passed;
    document.getElementById('failed-count').textContent = failed;
    document.getElementById('skipped-count').textContent = skipped;
    
    // Calculate percentages
    const passedPercent = total > 0 ? Math.round((passed / total) * 100) : 0;
    const failedPercent = total > 0 ? Math.round((failed / total) * 100) : 0;
    const skippedPercent = total > 0 ? Math.round((skipped / total) * 100) : 0;
    
    document.getElementById('passed-percent').textContent = `${passedPercent}%`;
    document.getElementById('failed-percent').textContent = `${failedPercent}%`;
    document.getElementById('skipped-percent').textContent = `${skippedPercent}%`;
    
    // Update performance metrics
    const avgResponseTime = testData.performance.responseTimes.length > 0 
        ? Math.round(testData.performance.responseTimes.reduce((a, b) => a + b, 0) / testData.performance.responseTimes.length)
        : 0;
    
    document.getElementById('avg-response-time').textContent = `${avgResponseTime} ms`;
    document.getElementById('requests-per-sec').textContent = testData.performance.requestsPerSecond.toFixed(1);
    document.getElementById('p95').textContent = `${testData.performance.p95} ms`;
    document.getElementById('failure-count').textContent = testData.performance.failures;
}

// Initialize charts
function initCharts() {
    const { passed, failed, skipped } = testData.stats;
    
    // Pie Chart for Test Results
    const pieCtx = document.getElementById('resultsPieChart').getContext('2d');
    pieChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: ['Passed', 'Failed', 'Skipped'],
            datasets: [{
                data: [passed, failed, skipped],
                backgroundColor: [
                    '#10B981', // green-500
                    '#EF4444', // red-500
                    '#F59E0B'  // yellow-500
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Bar Chart for Execution Time
    const timeCtx = document.getElementById('executionTimeChart').getContext('2d');
    timeChart = new Chart(timeCtx, {
        type: 'bar',
        data: {
            labels: testData.suites.map(suite => suite.name),
            datasets: [{
                label: 'Execution Time (ms)',
                data: testData.suites.map(suite => suite.duration),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(245, 158, 11, 0.7)'
                ],
                borderColor: [
                    'rgba(59, 130, 246, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Time (ms)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Performance Chart
    const perfCtx = document.getElementById('performanceChart').getContext('2d');
    performanceChart = new Chart(perfCtx, {
        type: 'line',
        data: {
            labels: testData.performance.responseTimes.map((_, i) => `Req ${i + 1}`),
            datasets: [
                {
                    label: 'Response Time (ms)',
                    data: testData.performance.responseTimes,
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: '95th Percentile',
                    data: Array(testData.performance.responseTimes.length).fill(testData.performance.p95),
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    yAxisID: 'y'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Response Time (ms)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    position: 'bottom'
                }
            },
            hover: {
                mode: 'nearest',
                intersect: true
            }
        }
    });
}

// Render test suites in the UI
function renderTestSuites() {
    const suitesContainer = document.getElementById('test-suites');
    
    if (!testData.suites || testData.suites.length === 0) {
        suitesContainer.innerHTML = `
            <div class="p-4 text-center text-gray-500">
                No test suites found.
            </div>
        `;
        return;
    }
    
    suitesContainer.innerHTML = testData.suites.map((suite, index) => {
        const passRate = suite.passed + suite.failed > 0 
            ? Math.round((suite.passed / (suite.passed + suite.failed)) * 100) 
            : 0;
        
        return `
            <div class="border-b border-gray-200">
                <button class="w-full px-4 py-4 text-left hover:bg-gray-50 focus:outline-none" 
                        onclick="toggleTestSuite(${index})">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <span class="text-sm font-medium text-gray-900">${suite.name}</span>
                            <span class="ml-2 px-2 py-0.5 text-xs rounded-full 
                                      ${suite.failed > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">
                                ${passRate}% Pass Rate
                            </span>
                        </div>
                        <div class="flex items-center">
                            <span class="text-sm text-gray-500 mr-4">${suite.duration} ms</span>
                            <svg class="h-5 w-5 text-gray-400 transform transition-transform" 
                                 id="icon-${index}" 
                                 fill="none" 
                                 viewBox="0 0 24 24" 
                                 stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                            </svg>
                        </div>
                    </div>
                    <div class="mt-2 flex space-x-4 text-xs text-gray-500">
                        <span class="text-green-600">${suite.passed} Passed</span>
                        <span class="text-red-600">${suite.failed} Failed</span>
                        ${suite.skipped > 0 ? `<span class="text-yellow-600">${suite.skipped} Skipped</span>` : ''}
                    </div>
                </button>
                <div id="suite-${index}" class="hidden px-4 pb-4">
                    ${renderTestCases(suite.testCases)}
                </div>
            </div>
        `;
    }).join('');
}

// Render test cases for a suite
function renderTestCases(testCases) {
    if (!testCases || testCases.length === 0) {
        return '<div class="p-2 text-sm text-gray-500">No test cases found.</div>';
    }
    
    return `
        <div class="ml-4 border-l-2 border-gray-200 pl-4 space-y-2">
            ${testCases.map(test => {
                const statusClass = {
                    'passed': 'text-green-600',
                    'failed': 'text-red-600',
                    'skipped': 'text-yellow-600'
                }[test.status] || 'text-gray-600';
                
                const icon = {
                    'passed': 'M5 13l4 4L19 7',
                    'failed': 'M6 18L18 6M6 6l12 12',
                    'skipped': 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
                }[test.status] || 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z';
                
                return `
                    <div class="p-2 rounded ${test.status === 'failed' ? 'bg-red-50' : ''}">
                        <div class="flex items-center">
                            <span class="flex-shrink-0 w-5 h-5 ${statusClass}">
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${icon}" />
                                </svg>
                            </span>
                            <span class="ml-2 text-sm font-medium text-gray-900">${test.name}</span>
                            <span class="ml-auto text-xs text-gray-500">${test.duration} ms</span>
                        </div>
                        ${test.error ? `
                            <div class="mt-1 ml-7 text-xs text-red-600 bg-red-50 p-2 rounded">
                                ${test.error}
                            </div>
                        ` : ''}
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// Toggle test suite visibility
function toggleTestSuite(index) {
    const suiteElement = document.getElementById(`suite-${index}`);
    const icon = document.getElementById(`icon-${index}`);
    
    if (suiteElement.classList.contains('hidden')) {
        suiteElement.classList.remove('hidden');
        icon.classList.add('rotate-180');
    } else {
        suiteElement.classList.add('hidden');
        icon.classList.remove('rotate-180');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Expand all button
    document.getElementById('expand-all').addEventListener('click', () => {
        testData.suites.forEach((_, index) => {
            const suiteElement = document.getElementById(`suite-${index}`);
            const icon = document.getElementById(`icon-${index}`);
            if (suiteElement && icon) {
                suiteElement.classList.remove('hidden');
                icon.classList.add('rotate-180');
            }
        });
    });
    
    // Collapse all button
    document.getElementById('collapse-all').addEventListener('click', () => {
        testData.suites.forEach((_, index) => {
            const suiteElement = document.getElementById(`suite-${index}`);
            const icon = document.getElementById(`icon-${index}`);
            if (suiteElement && icon) {
                suiteElement.classList.add('hidden');
                icon.classList.remove('rotate-180');
            }
        });
    });
    
    // Auto-refresh every 5 minutes
    setInterval(async () => {
        try {
            await loadTestData();
            updateSummaryCards();
            renderTestSuites();
            
            // Update charts
            updateCharts();
            
            // Show notification
            showNotification('Test data refreshed successfully');
        } catch (error) {
            console.error('Error refreshing test data:', error);
            showError('Failed to refresh test data');
        }
    }, 5 * 60 * 1000);
}

// Update charts with new data
function updateCharts() {
    const { passed, failed, skipped } = testData.stats;
    
    // Update pie chart
    pieChart.data.datasets[0].data = [passed, failed, skipped];
    pieChart.update();
    
    // Update time chart
    timeChart.data.datasets[0].data = testData.suites.map(suite => suite.duration);
    timeChart.update();
    
    // Update performance chart
    performanceChart.data.datasets[0].data = testData.performance.responseTimes;
    performanceChart.data.datasets[1].data = Array(testData.performance.responseTimes.length).fill(testData.performance.p95);
    performanceChart.update();
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 p-4 rounded-md shadow-lg ${
        type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('opacity-0', 'transition-opacity', 'duration-500');
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-50 border-l-4 border-red-500 p-4 mb-4';
    errorDiv.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
            </div>
            <div class="ml-3">
                <p class="text-sm text-red-700">
                    ${message}
                </p>
            </div>
        </div>
    `;
    
    const main = document.querySelector('main');
    if (main.firstChild) {
        main.insertBefore(errorDiv, main.firstChild);
    } else {
        main.appendChild(errorDiv);
    }
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 10000);
}

// Make functions available globally
window.toggleTestSuite = toggleTestSuite;
