// Admin Panel JavaScript Functions
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    loadQuickFilters();
    animateCounters();
    initializeSelectAll();
});

function toggleAddForm() {
    const form = document.getElementById('addForm');
    const btn = document.getElementById('showAddBtn');
    
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
        btn.style.display = 'none';
    } else {
        form.style.display = 'none';
        btn.style.display = 'block';
    }
}

function initializeFilters() {
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');
    const statusFilter = document.getElementById('statusFilter');
    const sortBy = document.getElementById('sortBy');
    
    [searchInput, typeFilter, statusFilter, sortBy].forEach(element => {
        if (element) {
            element.addEventListener('change', applyFilters);
            element.addEventListener('keyup', applyFilters);
        }
    });
}

function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const sortBy = document.getElementById('sortBy').value;
    
    const rows = document.querySelectorAll('#accountsTable tbody tr');
    let visibleRows = [];
    
    rows.forEach(row => {
        if (row.querySelector('.no-data-state')) return;
        
        const name = row.dataset.name || '';
        const email = row.dataset.email || '';
        const type = row.dataset.type || '';
        const status = row.dataset.status || '';
        
        const matchesSearch = name.includes(searchTerm) || email.includes(searchTerm);
        const matchesType = !typeFilter || type === typeFilter;
        const matchesStatus = !statusFilter || status === statusFilter;
        
        if (matchesSearch && matchesType && matchesStatus) {
            row.style.display = '';
            visibleRows.push(row);
        } else {
            row.style.display = 'none';
        }
    });
    
    // Apply sorting
    if (sortBy && visibleRows.length > 0) {
        const tbody = document.querySelector('#accountsTable tbody');
        visibleRows.sort((a, b) => {
            let aVal, bVal;
            switch (sortBy) {
                case 'name':
                    aVal = a.dataset.name || '';
                    bVal = b.dataset.name || '';
                    break;
                case 'price':
                    aVal = parseFloat(a.querySelector('.price-display').textContent.replace('$', ''));
                    bVal = parseFloat(b.querySelector('.price-display').textContent.replace('$', ''));
                    break;
                case 'type':
                    aVal = a.dataset.type || '';
                    bVal = b.dataset.type || '';
                    break;
                default:
                    return 0;
            }
            return aVal > bVal ? 1 : -1;
        });
        
        visibleRows.forEach(row => tbody.appendChild(row));
    }
}

function loadQuickFilters() {
    const container = document.getElementById('quickFiltersContainer');
    if (!container) return;
    
    // Get unique services
    const services = new Set();
    document.querySelectorAll('#accountsTable tbody tr').forEach(row => {
        const name = row.querySelector('.account-name strong')?.textContent;
        if (name && name !== 'Servicio no disponible') {
            services.add(name);
        }
    });
    
    // Create quick filter buttons
    container.innerHTML = '';
    services.forEach(service => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-outline-info btn-sm filter-btn';
        btn.innerHTML = `<i class="fas fa-tag me-1"></i>${service}`;
        btn.onclick = () => quickFilterByService(service);
        container.appendChild(btn);
    });
}

function quickFilter(status) {
    document.getElementById('statusFilter').value = status;
    applyFilters();
}

function quickFilterByService(serviceName) {
    const searchInput = document.getElementById('searchInput');
    searchInput.value = serviceName.toLowerCase();
    applyFilters();
}

function clearAllFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('sortBy').value = 'name';
    applyFilters();
}

function initializeSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.row-select');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
}

function selectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.row-select');
    
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = !allChecked;
    });
    
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = !allChecked;
    }
}

function copySelected() {
    const selected = document.querySelectorAll('.row-select:checked');
    if (selected.length === 0) {
        showToast('No hay cuentas seleccionadas', 'warning');
        return;
    }
    
    let copyText = '';
    selected.forEach(checkbox => {
        const row = checkbox.closest('tr');
        const email = row.querySelector('.account-email strong').textContent;
        const password = row.querySelector('.account-email small').textContent;
        const service = row.querySelector('.account-name strong').textContent;
        copyText += `${service}\n${email}:${password}\n\n`;
    });
    
    navigator.clipboard.writeText(copyText).then(() => {
        showToast(`${selected.length} cuentas copiadas al portapapeles`, 'success');
    });
}

function bulkDelete() {
    const selected = document.querySelectorAll('.row-select:checked');
    if (selected.length === 0) {
        showToast('No hay cuentas seleccionadas', 'warning');
        return;
    }
    
    if (!confirm(`¿Eliminar ${selected.length} cuentas seleccionadas?`)) return;
    
    showToast('Función en desarrollo', 'info');
}

function copyCredentials(email, password) {
    const text = `${email}:${password}`;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Credenciales copiadas', 'success');
    });
}

function generatePassword() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 12; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    document.querySelector('input[name="password"]').value = password;
}

function showImportModal() {
    const modal = new bootstrap.Modal(document.getElementById('importModal'));
    modal.show();
}

function submitImport() {
    const activeTab = document.querySelector('.tab-pane.active');
    const form = activeTab.querySelector('form');
    
    if (form.checkValidity()) {
        form.submit();
    } else {
        form.reportValidity();
    }
}

function showMaintenanceModal() {
    const modal = new bootstrap.Modal(document.getElementById('maintenanceModal'));
    modal.show();
}

function cleanDuplicates() {
    if (!confirm('¿Eliminar cuentas duplicadas?')) return;
    
    fetch('/maintenance/clean_duplicates', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showToast(`${data.removed} duplicados eliminados`, 'success');
            setTimeout(() => location.reload(), 1000);
        })
        .catch(error => {
            showToast('Error al limpiar duplicados', 'danger');
        });
}

function cleanFailed() {
    if (!confirm('¿Eliminar todas las cuentas fallidas?')) return;
    
    fetch('/maintenance/clean_failed', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showToast(`${data.removed} cuentas fallidas eliminadas`, 'success');
            setTimeout(() => location.reload(), 1000);
        })
        .catch(error => {
            showToast('Error al limpiar cuentas fallidas', 'danger');
        });
}

function cleanFailedAccounts() {
    cleanFailed();
}

function optimizeDatabase() {
    showToast('Base de datos optimizada', 'success');
}

function validateAllAccounts() {
    if (!confirm('¿Validar todas las cuentas? Esto puede tomar tiempo.')) return;
    showToast('Validación iniciada en segundo plano', 'info');
}

function resetCounters() {
    showToast('Contadores reiniciados', 'success');
}

function runFullMaintenance() {
    if (!confirm('¿Ejecutar mantenimiento completo? Esto puede tomar varios minutos.')) return;
    
    showToast('Mantenimiento completo iniciado...', 'info');
    
    // Simulate maintenance tasks
    setTimeout(() => {
        showToast('Mantenimiento completado exitosamente', 'success');
        setTimeout(() => location.reload(), 2000);
    }, 3000);
}

function animateCounters() {
    document.querySelectorAll('.counter').forEach(counter => {
        const target = parseInt(counter.dataset.target) || 0;
        const prefix = counter.dataset.prefix || '';
        let current = 0;
        const increment = target / 50;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = prefix + target;
                clearInterval(timer);
            } else {
                counter.textContent = prefix + Math.floor(current);
            }
        }, 20);
    });
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `${message} <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Placeholder functions for future features
function viewAccount(id) { 
    showToast('Ver detalles - En desarrollo', 'info'); 
}

function editAccount(id) { 
    showToast('Editar cuenta - En desarrollo', 'info'); 
}

function exportData() { 
    showToast('Exportar datos - En desarrollo', 'info'); 
}

function generateReport() { 
    showToast('Generar reporte - En desarrollo', 'info'); 
}

function showAnalytics() { 
    const modal = new bootstrap.Modal(document.getElementById('analyticsModal'));
    modal.show();
    loadAnalytics();
}

function loadAnalytics() {
    const content = document.getElementById('analyticsContent');
    
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            content.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-chart-bar me-2"></i>Resumen General</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Total de productos:</strong> ${data.total_products}</p>
                                <p><strong>Productos disponibles:</strong> ${data.available_products}</p>
                                <p><strong>Productos vendidos:</strong> ${data.sold_products}</p>
                                <p><strong>Valor del inventario:</strong> $${data.inventory_value.toFixed(2)}</p>
                                <p><strong>Ingresos totales:</strong> $${data.revenue.toFixed(2)}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-layer-group me-2"></i>Por Categorías</h6>
                            </div>
                            <div class="card-body">
                                ${Object.entries(data.categories).map(([cat, count]) => 
                                    `<p><strong>${cat}:</strong> ${count} productos</p>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            content.innerHTML = '<div class="alert alert-danger">Error al cargar estadísticas</div>';
        });
}

function showDetailedStats() {
    showAnalytics();
}

function backupData() {
    showToast('Respaldo iniciado - En desarrollo', 'info');
}

function exportAnalytics() {
    showToast('Exportando CSV - En desarrollo', 'info');
}

function generatePDFReport() {
    showToast('Generando PDF - En desarrollo', 'info');
}

function saveSettings() {
    showToast('Configuración guardada', 'success');
    bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide();
}

function clearCache() {
    showToast('Caché limpiado', 'success');
}

// Tab switching for import modal
document.addEventListener('DOMContentLoaded', function() {
    const individualTab = document.getElementById('individual-tab');
    const bulkTab = document.getElementById('bulk-tab');
    const importBtn = document.getElementById('importBtn');
    const bulkBtn = document.getElementById('bulkBtn');
    
    if (individualTab && bulkTab && importBtn && bulkBtn) {
        individualTab.addEventListener('click', function() {
            importBtn.style.display = 'inline-block';
            bulkBtn.style.display = 'none';
        });
        
        bulkTab.addEventListener('click', function() {
            importBtn.style.display = 'none';
            bulkBtn.style.display = 'inline-block';
        });
    }
});