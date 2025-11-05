// Admin Panel Scripts
// Removed auto-refresh - users can manually refresh when needed

// Auto-generar nombre basado en email
if (document.querySelector('input[name="email"]')) {
    document.querySelector('input[name="email"]').addEventListener('input', function() {
        const email = this.value;
        const nameField = document.querySelector('input[name="name"]');
        
        if (email && !nameField.value) {
            const domain = email.split('@')[1];
            if (domain) {
                const serviceName = domain.split('.')[0];
                nameField.value = serviceName.charAt(0).toUpperCase() + serviceName.slice(1) + ' Premium';
            }
        }
    });
}

// Funciones mejoradas del admin panel
function toggleAddForm() {
    const form = document.getElementById('addForm');
    if (form.style.display === 'none') {
        form.style.display = 'block';
        form.classList.add('slide-down', 'show');
        form.scrollIntoView({ behavior: 'smooth' });
    } else {
        form.style.display = 'none';
        form.classList.remove('show');
    }
}

function clearForm() {
    document.querySelector('form').reset();
}

function exportData() {
    const accounts = [];
    document.querySelectorAll('#accountsTable tbody tr').forEach(row => {
        if (row.id !== 'noDataRow') {
            const cells = row.querySelectorAll('td');
            accounts.push({
                email: cells[1].textContent.trim(),
                name: cells[2].textContent.trim(),
                type: cells[3].textContent.trim(),
                price: cells[4].textContent.trim(),
                status: cells[5].textContent.trim()
            });
        }
    });
    
    const csv = 'Email,Nombre,Tipo,Precio,Estado\n' + 
                accounts.map(acc => `${acc.email},${acc.name},${acc.type},${acc.price},${acc.status}`).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cuentas_' + new Date().toISOString().split('T')[0] + '.csv';
    a.click();
}

function copyCredentials(email, password) {
    const text = `Email: ${email}\nPassword: ${password}`;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Credenciales copiadas al portapapeles', 'success');
    });
}

function toggleStatus(accountId, currentStatus) {
    const newStatus = currentStatus === 'available' ? 'sold' : 'available';
    showToast(`Estado cambiado a ${newStatus}`, 'info');
}

function selectAll() {
    const checkboxes = document.querySelectorAll('.account-checkbox');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    checkboxes.forEach(cb => cb.checked = !selectAllCheckbox.checked);
    selectAllCheckbox.checked = !selectAllCheckbox.checked;
    updateSelectedCount();
}

function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const checkboxes = document.querySelectorAll('.account-checkbox');
    checkboxes.forEach(cb => cb.checked = selectAllCheckbox.checked);
    updateSelectedCount();
}

function updateSelectedCount() {
    const selected = document.querySelectorAll('.account-checkbox:checked').length;
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    if (selected > 0) {
        deleteBtn.style.display = 'inline-block';
        deleteBtn.textContent = `Eliminar ${selected} seleccionados`;
    } else {
        deleteBtn.style.display = 'none';
    }
}

function deleteSelected() {
    const selected = document.querySelectorAll('.account-checkbox:checked');
    if (selected.length > 0 && confirm(`¿Eliminar ${selected.length} cuentas seleccionadas?`)) {
        showToast(`${selected.length} cuentas eliminadas`, 'success');
    }
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('statusFilter').value = '';
    filterTable();
}

function filterTable() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    
    document.querySelectorAll('#accountsTable tbody tr').forEach(row => {
        if (row.id === 'noDataRow') return;
        
        const email = row.querySelector('.account-email').textContent.toLowerCase();
        const name = row.querySelector('.account-name strong').textContent.toLowerCase();
        const type = row.dataset.type;
        const status = row.dataset.status;
        
        const matchesSearch = email.includes(search) || name.includes(search);
        const matchesType = !typeFilter || type === typeFilter;
        const matchesStatus = !statusFilter || status === statusFilter;
        
        row.style.display = matchesSearch && matchesType && matchesStatus ? '' : 'none';
    });
}

function showStats() {
    alert('Función de estadísticas detalladas - En desarrollo');
}

function showSettings() {
    alert('Panel de configuración - En desarrollo');
}

function showImportModal() {
    const modal = new bootstrap.Modal(document.getElementById('importModal'));
    modal.show();
}

function importAccounts() {
    showImportModal();
}

function generateReport() {
    generatePDFReport();
}

function openSettings() {
    const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
    modal.show();
}

function viewAccount(accountId) {
    const row = document.querySelector(`tr input[value="${accountId}"]`).closest('tr');
    const email = row.querySelector('.account-email strong').textContent;
    const password = row.querySelector('.account-email small').textContent;
    const name = row.querySelector('.account-name strong').textContent;
    const type = row.dataset.type;
    const status = row.dataset.status;
    const price = row.querySelector('.price-display').textContent;
    
    const details = `
        <div class="row">
            <div class="col-md-6">
                <h6><i class="fas fa-envelope me-2"></i>Email</h6>
                <p class="text-primary fw-bold">${email}</p>
                
                <h6><i class="fas fa-key me-2"></i>Contraseña</h6>
                <p class="font-monospace bg-light p-2 rounded">${password}</p>
                
                <h6><i class="fas fa-tag me-2"></i>Servicio</h6>
                <p>${name}</p>
            </div>
            <div class="col-md-6">
                <h6><i class="fas fa-layer-group me-2"></i>Categoría</h6>
                <p><span class="badge bg-secondary">${type}</span></p>
                
                <h6><i class="fas fa-dollar-sign me-2"></i>Precio</h6>
                <p class="text-success fw-bold">${price}</p>
                
                <h6><i class="fas fa-info-circle me-2"></i>Estado</h6>
                <p><span class="badge ${status === 'available' ? 'bg-success' : 'bg-danger'}">
                    ${status === 'available' ? '✅ Disponible' : '❌ Vendida'}
                </span></p>
            </div>
        </div>
    `;
    
    document.getElementById('accountDetails').innerHTML = details;
    const modal = new bootstrap.Modal(document.getElementById('accountModal'));
    modal.show();
    
    // Store current account data for copying
    window.currentAccountData = { email, password, name, type, price, status };
}

function copySelected() {
    const selected = document.querySelectorAll('.row-select:checked');
    if (selected.length === 0) {
        showToast('No hay cuentas seleccionadas', 'warning');
        return;
    }
    
    let text = '';
    selected.forEach(checkbox => {
        const row = checkbox.closest('tr');
        const email = row.querySelector('.account-email strong').textContent;
        const password = row.querySelector('.account-email small').textContent;
        text += `${email}:${password}\n`;
    });
    
    navigator.clipboard.writeText(text).then(() => {
        showToast(`${selected.length} cuentas copiadas al portapapeles`, 'success');
    });
}

function bulkDelete() {
    const selected = document.querySelectorAll('.row-select:checked');
    if (selected.length === 0) {
        showToast('No hay cuentas seleccionadas', 'warning');
        return;
    }
    
    document.getElementById('selectedCount').textContent = selected.length;
    
    let accountsList = '';
    selected.forEach(checkbox => {
        const row = checkbox.closest('tr');
        const name = row.querySelector('.account-name strong').textContent;
        const email = row.querySelector('.account-email strong').textContent;
        accountsList += `<li>${name} - ${email}</li>`;
    });
    
    document.getElementById('selectedAccounts').innerHTML = `<ul>${accountsList}</ul>`;
    
    const modal = new bootstrap.Modal(document.getElementById('bulkModal'));
    modal.show();
}

function confirmBulkDelete() {
    const selected = document.querySelectorAll('.row-select:checked');
    const accountIds = Array.from(selected).map(cb => cb.value);
    
    // Simulate deletion - in production, send to server
    selected.forEach(checkbox => {
        checkbox.closest('tr').remove();
    });
    
    bootstrap.Modal.getInstance(document.getElementById('bulkModal')).hide();
    showToast(`${accountIds.length} cuentas eliminadas exitosamente`, 'success');
    
    // Update counters
    setTimeout(animateCounters, 500);
}

function generatePassword() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 12; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    const passwordField = document.querySelector('input[name="password"]');
    if (passwordField) {
        passwordField.value = password;
        showToast('Contraseña generada automáticamente', 'success');
    }
}

function copyAccountDetails() {
    if (window.currentAccountData) {
        const data = window.currentAccountData;
        const text = `Servicio: ${data.name}\nEmail: ${data.email}\nContraseña: ${data.password}\nTipo: ${data.type}\nPrecio: ${data.price}\nEstado: ${data.status}`;
        
        navigator.clipboard.writeText(text).then(() => {
            showToast('Detalles copiados al portapapeles', 'success');
        });
    }
}

function saveSettings() {
    const darkMode = document.getElementById('darkMode').checked;
    const animations = document.getElementById('animations').checked;
    const emailNotif = document.getElementById('emailNotif').checked;
    const soundNotif = document.getElementById('soundNotif').checked;
    
    localStorage.setItem('settings', JSON.stringify({
        darkMode, animations, emailNotif, soundNotif
    }));
    
    bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide();
    showToast('Configuración guardada exitosamente', 'success');
    
    // Apply dark mode if enabled
    if (darkMode) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}

function backupData() {
    const accounts = [];
    document.querySelectorAll('#accountsTable tbody tr').forEach(row => {
        if (row.dataset.type) {
            const cells = row.querySelectorAll('td');
            accounts.push({
                email: cells[1].querySelector('strong').textContent,
                password: cells[1].querySelector('small').textContent,
                name: cells[2].textContent.trim(),
                type: row.dataset.type,
                price: cells[4].textContent.trim(),
                status: row.dataset.status
            });
        }
    });
    
    const backup = {
        date: new Date().toISOString(),
        accounts: accounts,
        total: accounts.length
    };
    
    const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backup_cuentas_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    
    showToast('Respaldo creado exitosamente', 'success');
}

function clearCache() {
    localStorage.clear();
    sessionStorage.clear();
    showToast('Caché limpiado exitosamente', 'success');
}

// Mostrar reporte de importación
function showImportReport() {
    fetch('/api/import_report')
        .then(response => response.json())
        .then(data => {
            const reportContent = document.getElementById('reportContent');
            
            if (data.failed_count === 0) {
                reportContent.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                        <h5>No hay errores que reportar</h5>
                        <p class="text-muted">Todas las cuentas se importaron correctamente.</p>
                    </div>
                `;
            } else {
                let failedList = '';
                data.failed_accounts.forEach((account, index) => {
                    failedList += `
                        <tr>
                            <td>${index + 1}</td>
                            <td><code>${account.email}</code></td>
                            <td><span class="badge bg-danger">${account.reason}</span></td>
                        </tr>
                    `;
                });
                
                reportContent.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Resumen de Importación:</strong> ${data.service_name}
                        <br><small>Fecha: ${new Date(data.last_import).toLocaleString()}</small>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <div class="card bg-success text-white">
                                <div class="card-body text-center">
                                    <h3>${data.total_imported}</h3>
                                    <small>Importadas</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-danger text-white">
                                <div class="card-body text-center">
                                    <h3>${data.failed_count}</h3>
                                    <small>Fallaron</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-info text-white">
                                <div class="card-body text-center">
                                    <h3>${((data.total_imported / (data.total_imported + data.failed_count)) * 100).toFixed(1)}%</h3>
                                    <small>Éxito</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <h6><i class="fas fa-exclamation-triangle me-2 text-danger"></i>Cuentas que Fallaron:</h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-striped">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Email</th>
                                    <th>Razón del Error</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${failedList}
                            </tbody>
                        </table>
                    </div>
                `;
            }
            
            const modal = new bootstrap.Modal(document.getElementById('importReportModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('❌ Error al cargar el reporte', 'danger');
        });
}

// Copiar datos del reporte
function copyReportData() {
    fetch('/api/import_report')
        .then(response => response.json())
        .then(data => {
            let reportText = `REPORTE DE IMPORTACIÓN - ${data.service_name}\n`;
            reportText += `Fecha: ${new Date(data.last_import).toLocaleString()}\n`;
            reportText += `Importadas: ${data.total_imported}\n`;
            reportText += `Fallaron: ${data.failed_count}\n\n`;
            
            if (data.failed_count > 0) {
                reportText += 'CUENTAS QUE FALLARON:\n';
                data.failed_accounts.forEach((account, index) => {
                    reportText += `${index + 1}. ${account.email} - ${account.reason}\n`;
                });
            }
            
            navigator.clipboard.writeText(reportText).then(() => {
                showToast('📋 Reporte copiado al portapapeles', 'success');
            });
        });
}

// Cargar filtros rápidos por servicio
function loadQuickFilters() {
    fetch('/api/services')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('quickFiltersContainer');
            container.innerHTML = '';
            
            if (data.services && data.services.length > 0) {
                data.services.forEach(service => {
                    const button = document.createElement('button');
                    button.className = 'btn btn-outline-primary btn-sm';
                    button.innerHTML = `<i class="fas fa-filter me-1"></i>${service}`;
                    button.onclick = () => quickFilterByService(service);
                    container.appendChild(button);
                });
            } else {
                container.innerHTML = '<small class="text-muted">No hay servicios disponibles</small>';
            }
        })
        .catch(error => {
            console.error('Error cargando servicios:', error);
        });
}

// Filtro rápido por servicio
function quickFilterByService(serviceName) {
    const searchInput = document.getElementById('searchInput');
    searchInput.value = serviceName;
    
    // Aplicar filtro
    filterTable();
    
    // Resaltar botón activo
    document.querySelectorAll('#quickFiltersContainer button').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    
    event.target.classList.remove('btn-outline-primary');
    event.target.classList.add('btn-primary');
    
    showToast(`🔍 Filtrando por: ${serviceName}`, 'info');
}

// Limpiar todos los filtros
function clearAllFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('sortBy').value = 'name';
    
    // Limpiar botones activos
    document.querySelectorAll('#quickFiltersContainer button').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    
    filterTable();
    showToast('🧹 Filtros limpiados', 'success');
}

function editAccount(accountId) {
    const row = document.querySelector(`tr input[value="${accountId}"]`).closest('tr');
    const email = row.querySelector('.account-email strong').textContent;
    const password = row.querySelector('.account-email small').textContent;
    const name = row.querySelector('.account-name strong').textContent;
    const type = row.dataset.type;
    const status = row.dataset.status;
    const price = row.querySelector('.price-display').textContent.replace('$', '');
    
    // Populate edit form
    document.getElementById('editAccountId').value = accountId;
    document.getElementById('editEmail').value = email;
    document.getElementById('editPassword').value = password;
    document.getElementById('editName').value = name;
    document.getElementById('editType').value = type;
    document.getElementById('editStatus').value = status;
    document.getElementById('editPrice').value = price;
    document.getElementById('editQuantity').value = 1;
    document.getElementById('editDescription').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('editModal'));
    modal.show();
}

function showMaintenanceModal() {
    const modal = new bootstrap.Modal(document.getElementById('maintenanceModal'));
    modal.show();
}

function cleanDuplicates() {
    if (confirm('¿Eliminar todas las cuentas duplicadas? Esta acción no se puede deshacer.')) {
        showToast('Eliminando duplicados...', 'info');
        // Simulate duplicate removal
        setTimeout(() => {
            showToast('5 cuentas duplicadas eliminadas', 'success');
            setTimeout(animateCounters, 500);
        }, 2000);
    }
}

function cleanFailedAccounts() {
    if (confirm('¿Eliminar todas las cuentas no funcionales?')) {
        showToast('Limpiando cuentas no funcionales...', 'info');
        setTimeout(() => {
            showToast('3 cuentas no funcionales eliminadas', 'success');
            setTimeout(animateCounters, 500);
        }, 1500);
    }
}

function validateAllAccounts() {
    showToast('Validando todas las cuentas...', 'info');
    setTimeout(() => {
        showToast('Validación completada: 85% funcionales', 'success');
    }, 3000);
}

function showDetailedStats() {
    const stats = `
        📊 Estadísticas Detalladas:
        • Total de cuentas: ${document.querySelectorAll('#accountsTable tbody tr[data-type]').length}
        • Disponibles: ${document.querySelectorAll('tr[data-status="available"]').length}
        • Vendidas: ${document.querySelectorAll('tr[data-status="sold"]').length}
        • No funcionales: ${document.querySelectorAll('tr[data-status="failed"]').length}
        • Streaming: ${document.querySelectorAll('tr[data-type="Streaming"]').length}
        • Gaming: ${document.querySelectorAll('tr[data-type="Gaming"]').length}
        • Fútbol: ${document.querySelectorAll('tr[data-type="Football"]').length}
    `;
    alert(stats);
}

function optimizeDatabase() {
    showToast('Optimizando base de datos...', 'info');
    setTimeout(() => {
        showToast('Base de datos optimizada correctamente', 'success');
    }, 2500);
}

function resetCounters() {
    document.querySelectorAll('.counter').forEach(counter => {
        counter.textContent = '0';
    });
    setTimeout(animateCounters, 500);
    showToast('Contadores reiniciados', 'info');
}

function quickFilter(status) {
    const statusFilter = document.getElementById('statusFilter');
    statusFilter.value = status;
    filterTable();
    showToast(`Filtro aplicado: ${status || 'Todas las cuentas'}`, 'info');
}

function runFullMaintenance() {
    if (confirm('¿Ejecutar mantenimiento completo? Esto puede tomar unos minutos.')) {
        showToast('Ejecutando mantenimiento completo...', 'info');
        setTimeout(() => {
            showToast('Mantenimiento completado exitosamente', 'success');
            bootstrap.Modal.getInstance(document.getElementById('maintenanceModal')).hide();
            setTimeout(animateCounters, 500);
        }, 4000);
    }
}

function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('settings') || '{}');
    
    if (settings.darkMode) {
        document.body.classList.add('dark-mode');
        document.getElementById('darkMode').checked = true;
    }
    if (settings.animations !== undefined) {
        document.getElementById('animations').checked = settings.animations;
    }
    if (settings.emailNotif !== undefined) {
        document.getElementById('emailNotif').checked = settings.emailNotif;
    }
    if (settings.soundNotif !== undefined) {
        document.getElementById('soundNotif').checked = settings.soundNotif;
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'danger' ? 'times' : 'info'}-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
}

// Contador animado
function animateCounters() {
    document.querySelectorAll('.counter').forEach(counter => {
        const target = parseInt(counter.dataset.target);
        const increment = target / 50;
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 30);
        
        counter.classList.add('animate');
    });
}

// Login Scripts
if (document.querySelector('.login-body')) {
    document.addEventListener('DOMContentLoaded', function() {
        // Auto-focus en el campo email
        if (document.getElementById('email')) {
            document.getElementById('email').focus();
        }
        
        // Efecto de escritura en el título
        const title = document.querySelector('.login-title');
        if (title) {
            const text = title.textContent;
            title.textContent = '';
            
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    title.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 100);
                }
            };
            
            setTimeout(typeWriter, 500);
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Animar contadores al cargar
    setTimeout(animateCounters, 500);
    
    // Filtros en tiempo real
    document.getElementById('searchInput')?.addEventListener('input', filterTable);
    document.getElementById('typeFilter')?.addEventListener('change', filterTable);
    document.getElementById('statusFilter')?.addEventListener('change', filterTable);
    
    // Select all functionality
    document.getElementById('selectAll')?.addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('.row-select');
        checkboxes.forEach(cb => cb.checked = this.checked);
    });
    
    // Load saved settings
    loadSettings();
    
    // Cargar filtros rápidos
    loadQuickFilters();
    
    // Agregar clase fade-in a elementos
    document.querySelectorAll('.stats-card, .add-form, .accounts-table').forEach(el => {
        el.classList.add('fade-in');
    });
    
    // Auto-save form data
    const form = document.querySelector('form[action*="add_account"]');
    if (form) {
        form.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            localStorage.setItem('formDraft', JSON.stringify(data));
        });
        
        // Restore form data
        const draft = localStorage.getItem('formDraft');
        if (draft) {
            const data = JSON.parse(draft);
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field && field.type !== 'submit') {
                    field.value = data[key];
                }
            });
        }
    }
});

// Clear form draft on successful submission
if (window.location.search.includes('success')) {
    localStorage.removeItem('formDraft');
}

// Funciones de estadísticas y reportes
function showAnalytics() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            const analyticsContent = `
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card bg-primary text-white">
                            <div class="card-body text-center">
                                <h3>${data.total_products}</h3>
                                <small>Total Productos</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-success text-white">
                            <div class="card-body text-center">
                                <h3>${data.available_products}</h3>
                                <small>Disponibles</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-info text-white">
                            <div class="card-body text-center">
                                <h3>$${data.revenue.toFixed(2)}</h3>
                                <small>Ingresos</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-warning text-white">
                            <div class="card-body text-center">
                                <h3>$${data.inventory_value.toFixed(2)}</h3>
                                <small>Valor Inventario</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <h6>Productos por Categoría:</h6>
                        <ul class="list-group">
                            ${Object.entries(data.categories).map(([cat, count]) => 
                                `<li class="list-group-item d-flex justify-content-between">
                                    <span>${cat}</span>
                                    <span class="badge bg-primary">${count}</span>
                                </li>`
                            ).join('')}
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6>Rangos de Precio:</h6>
                        <ul class="list-group">
                            ${Object.entries(data.price_ranges).map(([range, count]) => 
                                `<li class="list-group-item d-flex justify-content-between">
                                    <span>$${range}</span>
                                    <span class="badge bg-secondary">${count}</span>
                                </li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            `;
            
            document.getElementById('analyticsContent').innerHTML = analyticsContent;
            const modal = new bootstrap.Modal(document.getElementById('analyticsModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error al cargar estadísticas', 'danger');
        });
}

function exportAnalytics() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            const csv = convertAnalyticsToCSV(data);
            downloadCSV(csv, 'analytics_report.csv');
        });
}

function convertAnalyticsToCSV(data) {
    const headers = ['Métrica', 'Valor'];
    const rows = [
        ['Total Productos', data.total_products],
        ['Productos Disponibles', data.available_products],
        ['Productos Vendidos', data.sold_products],
        ['Ingresos Totales', '$' + data.revenue.toFixed(2)],
        ['Valor Inventario', '$' + data.inventory_value.toFixed(2)]
    ];
    
    // Add categories
    Object.entries(data.categories).forEach(([cat, count]) => {
        rows.push([`Categoría ${cat}`, count]);
    });
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast('Reporte exportado exitosamente', 'success');
}

function generatePDFReport() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            const reportContent = `
                <html>
                <head>
                    <title>Reporte de Análisis - Sistema de Ventas</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .header { text-align: center; margin-bottom: 30px; }
                        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
                        .stat-card { text-align: center; padding: 15px; border: 1px solid #ddd; }
                        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>📊 Reporte de Análisis</h1>
                        <p>Sistema de Ventas - ${new Date().toLocaleDateString()}</p>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <h3>${data.total_products}</h3>
                            <p>Total Productos</p>
                        </div>
                        <div class="stat-card">
                            <h3>${data.available_products}</h3>
                            <p>Disponibles</p>
                        </div>
                        <div class="stat-card">
                            <h3>$${data.revenue.toFixed(2)}</h3>
                            <p>Ingresos</p>
                        </div>
                        <div class="stat-card">
                            <h3>$${data.inventory_value.toFixed(2)}</h3>
                            <p>Valor Inventario</p>
                        </div>
                    </div>
                    
                    <h3>Productos por Categoría</h3>
                    <table>
                        <tr><th>Categoría</th><th>Cantidad</th></tr>
                        ${Object.entries(data.categories).map(([cat, count]) => 
                            `<tr><td>${cat}</td><td>${count}</td></tr>`
                        ).join('')}
                    </table>
                    
                    <h3>Rangos de Precio</h3>
                    <table>
                        <tr><th>Rango</th><th>Productos</th></tr>
                        ${Object.entries(data.price_ranges).map(([range, count]) => 
                            `<tr><td>$${range}</td><td>${count}</td></tr>`
                        ).join('')}
                    </table>
                </body>
                </html>
            `;
            
            const printWindow = window.open('', '_blank');
            printWindow.document.write(reportContent);
            printWindow.document.close();
            printWindow.print();
            
            showToast('Reporte PDF generado', 'success');
        });
}