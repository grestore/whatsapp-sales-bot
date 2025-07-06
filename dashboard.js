// Dashboard JavaScript functionality

// Global variables
let sendMessageModal;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    sendMessageModal = new bootstrap.Modal(document.getElementById('sendMessageModal'));
    
    // Auto-refresh conversations every 30 seconds
    setInterval(refreshConversations, 30000);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Refresh conversations table
function refreshConversations() {
    const tableBody = document.getElementById('conversationsTable');
    const refreshBtn = document.querySelector('[onclick="refreshConversations()"]');
    
    // Show loading state
    if (refreshBtn) {
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Actualizando...';
        refreshBtn.disabled = true;
    }
    
    fetch('/api/conversations')
        .then(response => response.json())
        .then(data => {
            updateConversationsTable(data);
        })
        .catch(error => {
            console.error('Error refreshing conversations:', error);
            showAlert('Error al actualizar las conversaciones', 'danger');
        })
        .finally(() => {
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-refresh me-1"></i>Actualizar';
                refreshBtn.disabled = false;
            }
        });
}

// Update conversations table with new data
function updateConversationsTable(conversations) {
    const tableBody = document.getElementById('conversationsTable');
    
    if (!tableBody) return;
    
    tableBody.innerHTML = conversations.map(conversation => `
        <tr>
            <td>
                <div class="d-flex align-items-center">
                    <div class="avatar-sm bg-success rounded-circle d-flex align-items-center justify-content-center me-3">
                        <i class="fas fa-user text-white"></i>
                    </div>
                    <div>
                        <div class="fw-bold">${conversation.customer_name || 'Cliente'}</div>
                        <small class="text-muted">${conversation.phone_number}</small>
                    </div>
                </div>
            </td>
            <td>
                <span class="text-truncate d-inline-block" style="max-width: 200px;">
                    ${conversation.last_message || 'Sin mensajes'}
                </span>
            </td>
            <td>
                <span class="badge ${getStatusBadgeClass(conversation.status)}">${getStatusText(conversation.status)}</span>
            </td>
            <td>
                <small class="text-muted">${formatDate(conversation.updated_at)}</small>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="viewConversation(${conversation.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-success" onclick="sendMessage('${conversation.phone_number}')">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Get status badge class
function getStatusBadgeClass(status) {
    switch(status) {
        case 'active': return 'bg-success';
        case 'closed': return 'bg-secondary';
        case 'follow_up': return 'bg-warning';
        default: return 'bg-secondary';
    }
}

// Get status text
function getStatusText(status) {
    switch(status) {
        case 'active': return 'Activo';
        case 'closed': return 'Cerrado';
        case 'follow_up': return 'Seguimiento';
        default: return 'Desconocido';
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Show send message modal
function showSendMessageModal() {
    document.getElementById('phoneNumber').value = '';
    document.getElementById('messageBody').value = '';
    sendMessageModal.show();
}

// Send message to specific number
function sendMessage(phoneNumber) {
    document.getElementById('phoneNumber').value = phoneNumber;
    document.getElementById('messageBody').value = '';
    sendMessageModal.show();
}

// Send manual message
function sendManualMessage() {
    const phoneNumber = document.getElementById('phoneNumber').value;
    const messageBody = document.getElementById('messageBody').value;
    
    if (!phoneNumber || !messageBody) {
        showAlert('Por favor completa todos los campos', 'warning');
        return;
    }
    
    // Show loading state
    const sendBtn = document.querySelector('[onclick="sendManualMessage()"]');
    const originalText = sendBtn.innerHTML;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Enviando...';
    sendBtn.disabled = true;
    
    fetch('/api/send-message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            phone_number: phoneNumber,
            message: messageBody
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Mensaje enviado correctamente', 'success');
            sendMessageModal.hide();
            refreshConversations();
        } else {
            showAlert(data.error || 'Error al enviar el mensaje', 'danger');
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
        showAlert('Error al enviar el mensaje', 'danger');
    })
    .finally(() => {
        sendBtn.innerHTML = originalText;
        sendBtn.disabled = false;
    });
}

// View conversation details
function viewConversation(conversationId) {
    // This would typically open a modal or navigate to a detailed view
    // For now, we'll just show an alert
    showAlert(`Funcionalidad de vista detallada para conversación ${conversationId} próximamente`, 'info');
}

// Export data
function exportData() {
    showAlert('Funcionalidad de exportación próximamente', 'info');
}

// Show alert
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-remove alert after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Create alert container if it doesn't exist
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Handle form submission for send message modal
document.getElementById('sendMessageForm').addEventListener('submit', function(e) {
    e.preventDefault();
    sendManualMessage();
});

// Handle Enter key in message textarea
document.getElementById('messageBody').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey) {
        sendManualMessage();
    }
});

// Phone number formatting
document.getElementById('phoneNumber').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 0 && !value.startsWith('1')) {
        value = '1' + value;
    }
    if (value.length > 0) {
        value = '+' + value;
    }
    e.target.value = value;
});
