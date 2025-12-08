// Anti-Fraud Security Dashboard JavaScript

// Global variables
let currentView = 'dashboard';
let transactionChart = null;
let patternChart = null;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the dashboard
    initializeDashboard();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadDashboardData();
});

// Initialize the dashboard
function initializeDashboard() {
    // Set up navigation
    setupNavigation();
    
    // Initialize charts
    initializeCharts();
    
    // Set up periodic data refresh
    setInterval(refreshCurrentView, 30000); // Refresh every 30 seconds
}

// Set up navigation event listeners
function setupNavigation() {
    // Navigation menu items
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const view = this.getAttribute('data-view');
            if (view) {
                switchView(view);
            }
        });
    });
    
    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', function() {
        refreshCurrentView();
    });
}

// Set up other event listeners
function setupEventListeners() {
    // Flag transaction button in modal
    document.getElementById('flag-transaction-btn').addEventListener('click', function() {
        const transactionId = document.getElementById('flag-transaction-id').value;
        openFlagModal(transactionId);
    });
    
    // Block client button in modal
    document.getElementById('block-client-btn').addEventListener('click', function() {
        // Get client ID from transaction details
        const clientId = document.getElementById('sender-client-id').value;
        blockClient(clientId);
    });
    
    // Confirm flag button in flag modal
    document.getElementById('confirm-flag-btn').addEventListener('click', function() {
        flagTransaction();
    });
    
    // Block client detail button
    document.getElementById('block-client-detail-btn').addEventListener('click', function() {
        const clientId = document.getElementById('client-id-detail').value;
        blockClient(clientId);
    });
    
    // Investigate client button
    document.getElementById('investigate-client-btn').addEventListener('click', function() {
        const clientId = document.getElementById('client-id-detail').value;
        alert(`Запущено расширенное исследование для клиента ID: ${clientId}`);
    });
    
    // Period selection for dashboard charts
    document.querySelectorAll('[data-period]').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('[data-period]').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            // In a real implementation, this would reload the chart data for the selected period
        });
    });
}

// Switch between different views
function switchView(view) {
    // Hide all views
    document.querySelectorAll('.view-content').forEach(el => {
        el.classList.add('d-none');
    });
    
    // Show selected view
    const viewElement = document.getElementById(`${view}-view`);
    if (viewElement) {
        viewElement.classList.remove('d-none');
    }
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
    
    // Load data for the view
    switch (view) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'transactions':
            loadTransactions();
            break;
        case 'flagged':
            loadFlaggedTransactions();
            break;
        case 'clients':
            loadHighRiskClients();
            break;
        case 'patterns':
            loadTransactionPatterns();
            break;
        case 'create-transaction':
            loadCreateTransactionView();
            break;
        case 'search':
            // Search view doesn't need initial data loading
            break;
        case 'reports':
            // Reports view doesn't need initial data loading
            break;
        case 'alerts':
            // Alerts view doesn't need initial data loading
            break;
    }
    
    currentView = view;
}

// Refresh current view
function refreshCurrentView() {
    switch (currentView) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'transactions':
            loadTransactions();
            break;
        case 'flagged':
            loadFlaggedTransactions();
            break;
        case 'clients':
            loadHighRiskClients();
            break;
        case 'patterns':
            loadTransactionPatterns();
            break;
    }
}

// Initialize charts
function initializeCharts() {
    // Transaction chart
    const transactionCtx = document.getElementById('transactionChart').getContext('2d');
    transactionChart = new Chart(transactionCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Транзакции',
                data: [],
                borderColor: 'rgb(13, 110, 253)',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
    
    // Pattern chart
    const patternCtx = document.getElementById('patternChart').getContext('2d');
    patternChart = new Chart(patternCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Количество транзакций',
                data: [],
                backgroundColor: 'rgba(13, 110, 253, 0.7)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// Load dashboard data
function loadDashboardData() {
    // Load real statistics from API
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-transactions').textContent = data.total_transactions.toLocaleString('ru-RU');
            document.getElementById('today-transactions').textContent = data.today_transactions.toLocaleString('ru-RU');
            document.getElementById('flagged-transactions').textContent = data.flagged_transactions.toLocaleString('ru-RU');
            document.getElementById('flagged-increase').textContent = '0';
            document.getElementById('high-risk-clients').textContent = data.high_risk_clients.toLocaleString('ru-RU');
            document.getElementById('risk-increase').textContent = '0';
            document.getElementById('blocked-accounts').textContent = data.blocked_clients.toLocaleString('ru-RU');
        })
        .catch(error => {
            console.error('Error loading stats:', error);
            // Fallback to zeros on error
            document.getElementById('total-transactions').textContent = '0';
            document.getElementById('today-transactions').textContent = '0';
            document.getElementById('flagged-transactions').textContent = '0';
            document.getElementById('high-risk-clients').textContent = '0';
            document.getElementById('blocked-accounts').textContent = '0';
        });
    
    // Load flagged transactions for the recent list
    loadRecentFlaggedTransactions();
    
    // Load chart data
    loadMockChartData();
}

// Load mock chart data
function loadMockChartData() {
    // Mock data for transaction chart
    const hours = [];
    const counts = [];
    for (let i = 23; i >= 0; i--) {
        const hour = new Date();
        hour.setHours(hour.getHours() - i);
        hours.push(hour.toLocaleTimeString('ru-RU', { hour: '2-digit', hour12: false }));
        // Generate mock data with some variation
        counts.push(Math.floor(Math.random() * 500) + 800);
    }
    
    if (transactionChart) {
        transactionChart.data.labels = hours;
        transactionChart.data.datasets[0].data = counts;
        transactionChart.update();
    }
    
    // Mock data for pattern chart
    const days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    const dayCounts = [];
    days.forEach(() => {
        dayCounts.push(Math.floor(Math.random() * 3000) + 2000);
    });
    
    if (patternChart) {
        patternChart.data.labels = days;
        patternChart.data.datasets[0].data = dayCounts;
        patternChart.update();
    }
}

// Load recent flagged transactions
function loadRecentFlaggedTransactions() {
    const container = document.getElementById('recent-flagged');
    container.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary" role="status"></div></div>';
    
    fetch('/api/flagged-transactions')
        .then(response => response.json())
        .then(data => {
            container.innerHTML = '';
            
            if (!data.transactions || data.transactions.length === 0) {
                container.innerHTML = '<div class="text-center text-muted py-3">Нет подозрительных транзакций</div>';
                return;
            }
            
            data.transactions.slice(0, 5).forEach(tx => {
                const item = document.createElement('a');
                item.href = '#';
                item.className = 'list-group-item list-group-item-action';
                item.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">#${tx.transaction_id}</h6>
                        <small>${formatDate(tx.transaction_date)}</small>
                    </div>
                    <p class="mb-1">
                        <strong>${tx.sender_first_name} ${tx.sender_last_name}</strong> → 
                        <strong>${tx.receiver_first_name} ${tx.receiver_last_name}</strong>
                    </p>
                    <div class="d-flex justify-content-between">
                        <small>Сумма: ${formatMoney(tx.amount)}</small>
                        <span class="fraud-score-${tx.fraud_score >= 0.8 ? 'high' : tx.fraud_score >= 0.5 ? 'medium' : 'low'}">
                            ${(tx.fraud_score * 100).toFixed(0)}%
                        </span>
                    </div>
                    ${tx.flagged_reason ? `<small class="text-muted">${tx.flagged_reason}</small>` : ''}
                `;
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    showTransactionDetails(tx.transaction_id);
                });
                container.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Error loading flagged transactions:', error);
            container.innerHTML = '<div class="text-center text-danger py-3">Ошибка загрузки</div>';
        });
}

// Load all transactions
function loadTransactions() {
    const tbody = document.querySelector('#transactions-table tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="8" class="text-center">
                <div class="py-5">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="text-muted mt-2">Загрузка транзакций...</p>
                </div>
            </td>
        </tr>
    `;
    
    fetch('/api/transactions')
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = '';
            
            if (!data.transactions || data.transactions.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center text-muted py-4">Нет транзакций</td>
                    </tr>
                `;
                return;
            }
            
            data.transactions.forEach(tx => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>#${tx.transaction_id}</td>
                    <td>${formatDate(tx.transaction_date)}</td>
                    <td>${tx.sender_first_name} ${tx.sender_last_name}</td>
                    <td>${tx.receiver_first_name} ${tx.receiver_last_name}</td>
                    <td>${formatMoney(tx.amount)}</td>
                    <td>
                        <span class="badge bg-${getStatusClass(tx.status)}">${getStatusTextRu(tx.status)}</span>
                        ${tx.is_flagged ? '<span class="status-flagged ms-1">⚠️</span>' : ''}
                    </td>
                    <td>
                        <span class="fraud-score-${tx.fraud_score >= 0.8 ? 'high' : tx.fraud_score >= 0.5 ? 'medium' : 'low'}">
                            ${(tx.fraud_score * 100).toFixed(0)}%
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary view-transaction" data-id="${tx.transaction_id}">
                            <i class="bi bi-eye"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
            
            // Add event listeners to view buttons
            document.querySelectorAll('.view-transaction').forEach(btn => {
                btn.addEventListener('click', function() {
                    const transactionId = this.getAttribute('data-id');
                    showTransactionDetails(transactionId);
                });
            });
        })
        .catch(error => {
            console.error('Error loading transactions:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-danger py-4">Ошибка загрузки транзакций</td>
                </tr>
            `;
        });
}

// Load flagged transactions
function loadFlaggedTransactions() {
    const tbody = document.querySelector('#flagged-table tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="9" class="text-center">
                <div class="py-5">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="text-muted mt-2">Загрузка подозрительных транзакций...</p>
                </div>
            </td>
        </tr>
    `;
    
    fetch('/api/flagged-transactions')
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = '';
            
            if (!data.transactions || data.transactions.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center text-muted py-4">Нет подозрительных транзакций</td>
                    </tr>
                `;
                return;
            }
            
            data.transactions.forEach(tx => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>#${tx.transaction_id}</td>
                    <td>${formatDate(tx.transaction_date)}</td>
                    <td>${tx.sender_first_name} ${tx.sender_last_name}</td>
                    <td>${tx.receiver_first_name} ${tx.receiver_last_name}</td>
                    <td>${formatMoney(tx.amount)}</td>
                    <td><span class="badge bg-${getStatusClass(tx.status)}">${getStatusTextRu(tx.status)}</span></td>
                    <td>
                        <span class="fraud-score-${tx.fraud_score >= 0.8 ? 'high' : tx.fraud_score >= 0.5 ? 'medium' : 'low'}">
                            ${(tx.fraud_score * 100).toFixed(0)}%
                        </span>
                    </td>
                    <td><small>${tx.flagged_reason || 'Не указана'}</small></td>
                    <td>
                        <button class="btn btn-sm btn-primary view-transaction" data-id="${tx.transaction_id}">
                            <i class="bi bi-eye"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
            
            // Add event listeners to view buttons
            document.querySelectorAll('.view-transaction').forEach(btn => {
                btn.addEventListener('click', function() {
                    const transactionId = this.getAttribute('data-id');
                    showTransactionDetails(transactionId);
                });
            });
        })
        .catch(error => {
            console.error('Error loading flagged transactions:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-danger py-4">Ошибка загрузки</td>
                </tr>
            `;
        });
}

// Load high-risk clients
function loadHighRiskClients() {
    const tbody = document.querySelector('#clients-table tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="text-center">
                <div class="py-5">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="text-muted mt-2">Загрузка клиентов высокого риска...</p>
                </div>
            </td>
        </tr>
    `;
    
    fetch('/api/high-risk-clients')
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = '';
            
            if (!data.clients || data.clients.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center text-muted py-4">Нет клиентов высокого риска</td>
                    </tr>
                `;
                return;
            }
            
            data.clients.forEach(client => {
                const riskLevel = parseFloat(client.risk_level) || 0;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>#${client.client_id}</td>
                    <td>${client.first_name} ${client.last_name}</td>
                    <td>${client.phone_number || '-'}</td>
                    <td>${client.email || '-'}</td>
                    <td>
                        <span class="fraud-score-${riskLevel >= 0.8 ? 'high' : riskLevel >= 0.5 ? 'medium' : 'low'}">
                            ${(riskLevel * 100).toFixed(0)}%
                        </span>
                    </td>
                    <td>
                        ${client.is_blocked ? 
                            '<span class="badge bg-danger">Заблокирован</span>' : 
                            '<span class="badge bg-success">Активен</span>'}
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary view-client" data-id="${client.client_id}">
                            <i class="bi bi-eye"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
            
            // Add event listeners to view buttons
            document.querySelectorAll('.view-client').forEach(btn => {
                btn.addEventListener('click', function() {
                    const clientId = this.getAttribute('data-id');
                    showClientDetails(clientId);
                });
            });
        })
        .catch(error => {
            console.error('Error loading clients:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-danger py-4">Ошибка загрузки</td>
                </tr>
            `;
        });
}

// Load transaction patterns
function loadTransactionPatterns() {
    // In a real implementation, this would load actual pattern data
    // For now, we're using mock data in the chart initialization
}

// Show transaction details in modal
function showTransactionDetails(transactionId) {
    const content = document.getElementById('transaction-details-content');
    content.innerHTML = `
        <div class="text-center py-5">
            <i class="bi bi-hourglass-split text-muted" style="font-size: 2rem;"></i>
            <p class="text-muted mt-2">Загрузка деталей транзакции...</p>
        </div>
    `;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
    modal.show();
    
    // Mock data for transaction details
    setTimeout(() => {
        const mockTransaction = {
            id: transactionId,
            date: '15.09.2025 14:30',
            amount: '150,000 ₽',
            currency: 'RUB',
            type: 'P2P Перевод',
            status: 'completed',
            score: 9.2,
            flagged: true,
            flaggedReason: 'Высокая сумма и новое устройство',
            sender: {
                name: 'Иванов Иван Иванович',
                account: '4276 **** **** 9012',
                phone: '+7 (999) 123-45-67',
                clientId: 'CL-001'
            },
            receiver: {
                name: 'Петров Петр Петрович',
                account: '4276 **** **** 1098',
                phone: '+7 (999) 987-65-43',
                clientId: 'CL-002'
            },
            device: {
                fingerprint: 'DEV-789456',
                type: 'Мобильное устройство',
                os: 'Android 12',
                browser: 'Chrome Mobile'
            },
            location: {
                ip: '192.168.1.100',
                country: 'Россия',
                city: 'Москва'
            }
        };
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h5>Информация о транзакции</h5>
                    <div class="detail-row">
                        <span class="detail-label">ID:</span>
                        <span>${mockTransaction.id}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Дата и время:</span>
                        <span>${mockTransaction.date}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Сумма:</span>
                        <span>${mockTransaction.amount}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Тип:</span>
                        <span>${mockTransaction.type}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Статус:</span>
                        <span>${getStatusText(mockTransaction.status)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Оценка риска:</span>
                        <span class="fraud-score-${getFraudScoreClass(mockTransaction.score)}">${mockTransaction.score}</span>
                    </div>
                    ${mockTransaction.flagged ? `
                    <div class="detail-row">
                        <span class="detail-label">Причина пометки:</span>
                        <span>${mockTransaction.flaggedReason}</span>
                    </div>
                    ` : ''}
                </div>
                <div class="col-md-6">
                    <h5>Информация об отправителе</h5>
                    <div class="detail-row">
                        <span class="detail-label">ФИО:</span>
                        <span>${mockTransaction.sender.name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Счет:</span>
                        <span>${mockTransaction.sender.account}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Телефон:</span>
                        <span>${mockTransaction.sender.phone}</span>
                    </div>
                    
                    <h5 class="mt-3">Информация о получателе</h5>
                    <div class="detail-row">
                        <span class="detail-label">ФИО:</span>
                        <span>${mockTransaction.receiver.name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Счет:</span>
                        <span>${mockTransaction.receiver.account}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Телефон:</span>
                        <span>${mockTransaction.receiver.phone}</span>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <h5>Информация об устройстве</h5>
                    <div class="detail-row">
                        <span class="detail-label">ID устройства:</span>
                        <span>${mockTransaction.device.fingerprint}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Тип:</span>
                        <span>${mockTransaction.device.type}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">ОС:</span>
                        <span>${mockTransaction.device.os}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Браузер:</span>
                        <span>${mockTransaction.device.browser}</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <h5>Информация о местоположении</h5>
                    <div class="detail-row">
                        <span class="detail-label">IP адрес:</span>
                        <span>${mockTransaction.location.ip}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Страна:</span>
                        <span>${mockTransaction.location.country}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Город:</span>
                        <span>${mockTransaction.location.city}</span>
                    </div>
                </div>
            </div>
            <input type="hidden" id="flag-transaction-id" value="${mockTransaction.id}">
            <input type="hidden" id="sender-client-id" value="${mockTransaction.sender.clientId}">
        `;
    }, 800);
}

// Show client details in modal
function showClientDetails(clientId) {
    const content = document.getElementById('client-details-content');
    content.innerHTML = `
        <div class="text-center py-5">
            <i class="bi bi-hourglass-split text-muted" style="font-size: 2rem;"></i>
            <p class="text-muted mt-2">Загрузка деталей клиента...</p>
        </div>
    `;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('clientModal'));
    modal.show();
    
    // Mock data for client details
    setTimeout(() => {
        const mockClient = {
            id: clientId,
            name: 'Иванов Иван Иванович',
            dob: '15.03.1985',
            phone: '+7 (999) 123-45-67',
            email: 'ivanov@example.com',
            regDate: '12.01.2022',
            kycStatus: 'Подтверждён',
            risk: 0.92,
            blocked: false
        };
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h5>Информация о клиенте</h5>
                    <div class="detail-row">
                        <span class="detail-label">ID:</span>
                        <span>${mockClient.id}</span>
                        <input type="hidden" id="client-id-detail" value="${mockClient.id}">
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">ФИО:</span>
                        <span>${mockClient.name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Дата рождения:</span>
                        <span>${mockClient.dob}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Телефон:</span>
                        <span>${mockClient.phone}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Email:</span>
                        <span>${mockClient.email}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Дата регистрации:</span>
                        <span>${mockClient.regDate}</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <h5>Информация о риске</h5>
                    <div class="detail-row">
                        <span class="detail-label">Статус KYC:</span>
                        <span>${mockClient.kycStatus}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Уровень риска:</span>
                        <span class="fraud-score-${getFraudScoreClass(mockClient.risk * 10)}">
                            ${mockClient.risk.toFixed(2)}
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Статус:</span>
                        <span>
                            ${mockClient.blocked ? 
                                '<span class="badge bg-danger">Заблокирован</span>' : 
                                '<span class="badge bg-success">Активен</span>'}
                        </span>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h5>Счета клиента</h5>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Номер счета</th>
                                <th>Тип</th>
                                <th>Баланс</th>
                                <th>Статус</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>4276 **** **** 9012</td>
                                <td>Дебетовая карта</td>
                                <td>45,200 ₽</td>
                                <td>
                                    <span class="badge bg-success">Активен</span>
                                </td>
                            </tr>
                            <tr>
                                <td>4081 **** **** 5678</td>
                                <td>Кредитная карта</td>
                                <td>120,500 ₽</td>
                                <td>
                                    <span class="badge bg-success">Активен</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h5>Последние транзакции</h5>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Дата</th>
                                <th>Получатель</th>
                                <th>Сумма</th>
                                <th>Статус</th>
                                <th>Оценка риска</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>TX-789456</td>
                                <td>15.09.2025</td>
                                <td>Петров П.П.</td>
                                <td>150,000 ₽</td>
                                <td>Завершена</td>
                                <td>
                                    <span class="fraud-score-high">9.2</span>
                                </td>
                            </tr>
                            <tr>
                                <td>TX-112233</td>
                                <td>14.09.2025</td>
                                <td>Сидорова М.А.</td>
                                <td>75,000 ₽</td>
                                <td>Завершена</td>
                                <td>
                                    <span class="fraud-score-medium">6.8</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }, 800);
}

// Open flag modal
function openFlagModal(transactionId) {
    document.getElementById('flag-transaction-id').value = transactionId;
    document.getElementById('flag-reason-select').value = '';
    document.getElementById('flag-reason-details').value = '';
    
    // Hide transaction modal and show flag modal
    const transactionModal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
    if (transactionModal) {
        transactionModal.hide();
    }
    
    const flagModal = new bootstrap.Modal(document.getElementById('flagModal'));
    flagModal.show();
}

// Flag a transaction
function flagTransaction() {
    const transactionId = document.getElementById('flag-transaction-id').value;
    const reasonSelect = document.getElementById('flag-reason-select').value;
    const reasonDetails = document.getElementById('flag-reason-details').value;
    
    if (!transactionId || !reasonSelect) {
        alert('Пожалуйста, выберите причину пометки транзакции');
        return;
    }
    
    const reason = reasonDetails ? `${reasonSelect}: ${reasonDetails}` : reasonSelect;
    
    // Hide flag modal
    const flagModal = bootstrap.Modal.getInstance(document.getElementById('flagModal'));
    if (flagModal) {
        flagModal.hide();
    }
    
    // Show success message
    alert(`Транзакция ${transactionId} успешно помечена как подозрительная по причине: ${reason}`);
    
    // Reload current view
    refreshCurrentView();
}

// Block a client
function blockClient(clientId) {
    if (!clientId) {
        alert('Неверный ID клиента');
        return;
    }
    
    if (!confirm('Вы уверены, что хотите заблокировать этого клиента?')) {
        return;
    }
    
    // Hide modals
    const clientModal = bootstrap.Modal.getInstance(document.getElementById('clientModal'));
    const transactionModal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
    if (clientModal) clientModal.hide();
    if (transactionModal) transactionModal.hide();
    
    // Show success message
    alert(`Клиент ${clientId} успешно заблокирован`);
    
    // Reload current view
    refreshCurrentView();
}

// Helper functions
function getStatusText(status) {
    const statusMap = {
        'completed': 'Завершена',
        'pending': 'В обработке',
        'failed': 'Ошибка',
        'reversed': 'Отменена'
    };
    return statusMap[status] || status;
}

function getFraudScoreClass(score) {
    if (score >= 8) return 'high';
    if (score >= 5) return 'medium';
    return 'low';
}

// =====================================================
// CREATE TRANSACTION FUNCTIONALITY
// =====================================================

let accountsData = [];

// Load create transaction view
function loadCreateTransactionView() {
    loadAccounts();
    loadRecentTransactions();
    setupCreateTransactionForm();
}

// Load accounts for dropdowns
function loadAccounts() {
    fetch('/api/accounts')
        .then(response => response.json())
        .then(data => {
            if (data.accounts) {
                accountsData = data.accounts;
                populateAccountDropdowns(data.accounts);
            }
        })
        .catch(error => {
            console.error('Error loading accounts:', error);
            showNotification('Ошибка загрузки счетов', 'danger');
        });
}

// Populate account dropdowns
function populateAccountDropdowns(accounts) {
    const senderSelect = document.getElementById('sender-account');
    const receiverSelect = document.getElementById('receiver-account');
    
    // Clear existing options
    senderSelect.innerHTML = '<option value="">Выберите счёт отправителя...</option>';
    receiverSelect.innerHTML = '<option value="">Выберите счёт получателя...</option>';
    
    accounts.forEach(account => {
        const riskClass = account.risk_level > 0.5 ? 'text-danger' : '';
        const blockedText = account.is_blocked ? ' [ЗАБЛОКИРОВАН]' : '';
        const optionText = `${account.last_name} ${account.first_name} - ${account.account_number} (${formatMoney(account.balance)})${blockedText}`;
        
        const senderOption = document.createElement('option');
        senderOption.value = account.account_id;
        senderOption.textContent = optionText;
        senderOption.dataset.balance = account.balance;
        senderOption.dataset.riskLevel = account.risk_level;
        senderOption.dataset.isBlocked = account.is_blocked;
        senderOption.dataset.clientName = `${account.first_name} ${account.last_name}`;
        if (account.is_blocked) senderOption.disabled = true;
        senderSelect.appendChild(senderOption);
        
        const receiverOption = document.createElement('option');
        receiverOption.value = account.account_id;
        receiverOption.textContent = optionText;
        receiverOption.dataset.riskLevel = account.risk_level;
        receiverOption.dataset.isBlocked = account.is_blocked;
        receiverOption.dataset.clientName = `${account.first_name} ${account.last_name}`;
        receiverSelect.appendChild(receiverOption);
    });
    
    // Add change event listeners
    senderSelect.addEventListener('change', updateSenderInfo);
    receiverSelect.addEventListener('change', updateReceiverInfo);
}

// Update sender info display
function updateSenderInfo() {
    const select = document.getElementById('sender-account');
    const balanceDiv = document.getElementById('sender-balance');
    const selectedOption = select.options[select.selectedIndex];
    
    if (selectedOption && selectedOption.value) {
        const balance = parseFloat(selectedOption.dataset.balance);
        const riskLevel = parseFloat(selectedOption.dataset.riskLevel);
        const riskText = riskLevel > 0.5 ? `<span class="text-danger">⚠️ Высокий риск: ${(riskLevel * 100).toFixed(0)}%</span>` : '';
        balanceDiv.innerHTML = `Доступно: <strong>${formatMoney(balance)}</strong> ${riskText}`;
    } else {
        balanceDiv.innerHTML = '';
    }
}

// Update receiver info display
function updateReceiverInfo() {
    const select = document.getElementById('receiver-account');
    const infoDiv = document.getElementById('receiver-info');
    const selectedOption = select.options[select.selectedIndex];
    
    if (selectedOption && selectedOption.value) {
        const riskLevel = parseFloat(selectedOption.dataset.riskLevel);
        const isBlocked = selectedOption.dataset.isBlocked === 'true';
        
        let infoText = '';
        if (isBlocked) {
            infoText = '<span class="text-danger">🚫 Клиент заблокирован - перевод будет отклонён</span>';
        } else if (riskLevel > 0.5) {
            infoText = `<span class="text-warning">⚠️ Получатель с повышенным риском: ${(riskLevel * 100).toFixed(0)}%</span>`;
        } else {
            infoText = '<span class="text-success">✓ Получатель проверен</span>';
        }
        infoDiv.innerHTML = infoText;
    } else {
        infoDiv.innerHTML = '';
    }
}

// Setup create transaction form
function setupCreateTransactionForm() {
    const form = document.getElementById('create-transaction-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitTransaction();
    });
    
    // Refresh button
    const refreshBtn = document.getElementById('refresh-recent-transactions');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadRecentTransactions);
    }
}

// Submit transaction
function submitTransaction() {
    const senderAccountId = document.getElementById('sender-account').value;
    const receiverAccountId = document.getElementById('receiver-account').value;
    const amount = document.getElementById('amount').value;
    const description = document.getElementById('description').value;
    
    // Validation
    if (!senderAccountId || !receiverAccountId || !amount) {
        showNotification('Заполните все обязательные поля', 'warning');
        return;
    }
    
    if (senderAccountId === receiverAccountId) {
        showNotification('Отправитель и получатель не могут совпадать', 'warning');
        return;
    }
    
    // Check balance
    const senderSelect = document.getElementById('sender-account');
    const selectedOption = senderSelect.options[senderSelect.selectedIndex];
    const balance = parseFloat(selectedOption.dataset.balance);
    
    if (parseFloat(amount) > balance) {
        showNotification('Недостаточно средств на счёте', 'danger');
        return;
    }
    
    // Disable submit button
    const submitBtn = document.getElementById('submit-transaction-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Обработка...';
    
    // Send request
    fetch('/api/create-transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sender_account_id: parseInt(senderAccountId),
            receiver_account_id: parseInt(receiverAccountId),
            amount: parseFloat(amount),
            description: description
        })
    })
    .then(response => response.json())
    .then(data => {
        displayTransactionResult(data);
        if (data.success) {
            // Clear form
            document.getElementById('amount').value = '';
            document.getElementById('description').value = '';
            // Reload accounts and recent transactions
            loadAccounts();
            loadRecentTransactions();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при выполнении транзакции', 'danger');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-send"></i> Выполнить перевод';
    });
}

// Display transaction result
function displayTransactionResult(data) {
    const resultCard = document.getElementById('transaction-result-card');
    const resultHeader = document.getElementById('result-header');
    const resultBody = document.getElementById('transaction-result');
    
    resultCard.classList.remove('d-none');
    
    if (data.error) {
        resultHeader.className = 'card-header bg-danger text-white';
        resultHeader.innerHTML = '<i class="bi bi-x-circle"></i> Ошибка';
        resultBody.innerHTML = `
            <div class="alert alert-danger mb-0">
                <strong>Транзакция отклонена:</strong> ${data.error}
                ${data.reason ? `<br><small>${data.reason}</small>` : ''}
            </div>
        `;
        return;
    }
    
    const fraudCheck = data.fraud_check;
    const score = fraudCheck.score;
    const scoreClass = score >= 0.8 ? 'danger' : score >= 0.5 ? 'warning' : score >= 0.4 ? 'info' : 'success';
    const statusClass = data.status === 'completed' ? 'success' : data.status === 'review' ? 'warning' : 'danger';
    const statusIcon = data.status === 'completed' ? 'check-circle' : data.status === 'review' ? 'hourglass-split' : 'x-circle';
    
    resultHeader.className = `card-header bg-${statusClass} text-white`;
    resultHeader.innerHTML = `<i class="bi bi-${statusIcon}"></i> ${data.message}`;
    
    let flagsHtml = '';
    if (fraudCheck.flags && fraudCheck.flags.length > 0) {
        flagsHtml = `
            <div class="mt-2">
                <strong>Сработавшие правила:</strong><br>
                ${fraudCheck.flags.map(flag => `<span class="badge bg-secondary me-1">${flag}</span>`).join('')}
            </div>
        `;
    }
    
    resultBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>ID транзакции:</strong> #${data.transaction_id}</p>
                <p><strong>Статус:</strong> 
                    <span class="badge bg-${statusClass}">${getStatusTextRu(data.status)}</span>
                </p>
            </div>
            <div class="col-md-6">
                <p><strong>Fraud Score:</strong> 
                    <span class="fraud-score-${score >= 0.8 ? 'high' : score >= 0.5 ? 'medium' : 'low'}">
                        ${(score * 100).toFixed(0)}%
                    </span>
                </p>
                <p><strong>Помечена:</strong> ${fraudCheck.is_flagged ? 'Да ⚠️' : 'Нет ✓'}</p>
            </div>
        </div>
        ${fraudCheck.reason ? `
            <div class="alert alert-${scoreClass} mt-2 mb-0">
                <strong>Причины:</strong> ${fraudCheck.reason}
            </div>
        ` : ''}
        ${flagsHtml}
    `;
}

// Load recent transactions
function loadRecentTransactions() {
    fetch('/api/transactions')
        .then(response => response.json())
        .then(data => {
            if (data.transactions) {
                displayRecentTransactions(data.transactions.slice(0, 10));
            }
        })
        .catch(error => {
            console.error('Error loading transactions:', error);
        });
}

// Display recent transactions in table
function displayRecentTransactions(transactions) {
    const tbody = document.getElementById('recent-transactions-body');
    if (!tbody) return;
    
    if (transactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-4">
                    <i class="bi bi-inbox" style="font-size: 2rem;"></i>
                    <p class="mt-2 mb-0">Нет транзакций</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = transactions.map(tx => `
        <tr>
            <td>#${tx.transaction_id}</td>
            <td>${formatDate(tx.transaction_date)}</td>
            <td>${tx.sender_first_name} ${tx.sender_last_name}</td>
            <td>${tx.receiver_first_name} ${tx.receiver_last_name}</td>
            <td>${formatMoney(tx.amount)}</td>
            <td>
                <span class="badge bg-${getStatusClass(tx.status)}">${getStatusTextRu(tx.status)}</span>
                ${tx.is_flagged ? '<span class="badge bg-warning ms-1">⚠️</span>' : ''}
            </td>
            <td>
                <span class="fraud-score-${tx.fraud_score >= 0.8 ? 'high' : tx.fraud_score >= 0.5 ? 'medium' : 'low'}">
                    ${(tx.fraud_score * 100).toFixed(0)}%
                </span>
            </td>
        </tr>
    `).join('');
}

// Helper functions
function formatMoney(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 2
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getStatusClass(status) {
    const classes = {
        'completed': 'success',
        'pending': 'primary',
        'review': 'warning',
        'blocked': 'danger',
        'failed': 'secondary'
    };
    return classes[status] || 'secondary';
}

function getStatusTextRu(status) {
    const texts = {
        'completed': 'Выполнена',
        'pending': 'В обработке',
        'review': 'На проверке',
        'blocked': 'Заблокирована',
        'failed': 'Ошибка'
    };
    return texts[status] || status;
}

function showNotification(message, type = 'info') {
    // Create toast notification
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 5000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1100';
    document.body.appendChild(container);
    return container;
}