/**
 * Machines Management Logic
 */
const Machines = {
    cachedMachines: [],

    async load() {
        const search = document.getElementById('machine-search')?.value || '';
        const status = document.getElementById('machine-status-filter')?.value || '';
        
        try {
            const machines = await API.getMachines(search, status);
            this.cachedMachines = machines;
            this.renderList(machines);
        } catch (e) {
            console.error("Makineler yüklenirken hata:", e);
        }
    },

    renderList(machines) {
        const container = document.getElementById('machines-table-body');
        if (!container) return;

        if (!machines || machines.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="7" class="py-12 text-center text-slate-400">
                        <i data-lucide="inbox" class="w-8 h-8 mx-auto mb-2 text-slate-300"></i>
                        <p class="text-sm">Kayıtlı makine bulunamadı.</p>
                    </td>
                </tr>
            `;
            lucide.createIcons();
            return;
        }

        container.innerHTML = machines.map(m => {
            let statusBadge = '';
            if (m.maintenance_status_flag === 'overdue') {
                statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-600 mr-1.5 animate-ping"></span>Gecikti (${Math.abs(m.days_until_next_maintenance)} gün)
                </span>`;
            } else if (m.maintenance_status_flag === 'upcoming') {
                statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1.5"></span>${m.days_until_next_maintenance} gün kaldı
                </span>`;
            } else {
                statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                    ${m.days_until_next_maintenance !== null ? m.days_until_next_maintenance + ' gün sonra' : 'Planlandı'}
                </span>`;
            }

            return `
                <tr class="border-b border-slate-100 table-row-hover text-sm">
                    <td class="py-3 px-4">
                        <span class="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-1 rounded border">${m.machine_code}</span>
                    </td>
                    <td class="py-3 px-4">
                        <div class="font-semibold text-slate-800">${m.name}</div>
                        <div class="text-xs text-slate-400">${m.model || '-'} ${m.serial_number ? '• SN: ' + m.serial_number : ''}</div>
                    </td>
                    <td class="py-3 px-4 text-slate-600 text-xs">${m.location || '-'}</td>
                    <td class="py-3 px-4 text-slate-600 text-xs font-mono">${m.last_maintenance_date || 'Kayıt Yok'}</td>
                    <td class="py-3 px-4 text-center">
                        <span class="text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">${m.maintenance_interval_days} Gün</span>
                    </td>
                    <td class="py-3 px-4">
                        <div class="font-mono text-xs text-slate-700 mb-1">${m.next_maintenance_date || '-'}</div>
                        ${statusBadge}
                    </td>
                    <td class="py-3 px-4 text-right whitespace-nowrap">
                        <div class="flex items-center justify-end space-x-1.5">
                            <button onclick="Maintenance.openNewLogModal(${m.id})" title="Bakım Yap" 
                                    class="p-1.5 text-slate-700 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg transition">
                                <i data-lucide="wrench" class="w-4 h-4"></i>
                            </button>
                            <button onclick="Machines.openHistoryModal(${m.id}, '${m.name}')" title="Bakım Geçmişi" 
                                    class="p-1.5 text-slate-700 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition">
                                <i data-lucide="history" class="w-4 h-4"></i>
                            </button>
                            <button onclick="Machines.openEditModal(${m.id})" title="Düzenle" 
                                    class="p-1.5 text-slate-700 hover:text-amber-700 hover:bg-amber-50 rounded-lg transition">
                                <i data-lucide="edit-3" class="w-4 h-4"></i>
                            </button>
                            <button onclick="Machines.deleteMachine(${m.id}, '${m.name}')" title="Sil" 
                                    class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition">
                                <i data-lucide="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        lucide.createIcons();
    },

    openAddModal() {
        document.getElementById('machine-modal-title').textContent = 'Yeni Makine / Ekipman Ekle';
        document.getElementById('machine-id').value = '';
        document.getElementById('machine-form').reset();
        document.getElementById('machine-interval').value = '30';
        document.getElementById('machine-status').value = 'Aktif';
        App.openModal('machine-modal');
    },

    async openEditModal(id) {
        try {
            const m = await API.getMachine(id);
            document.getElementById('machine-modal-title').textContent = 'Makine Düzenle';
            document.getElementById('machine-id').value = m.id;
            document.getElementById('machine-code').value = m.machine_code;
            document.getElementById('machine-name').value = m.name;
            document.getElementById('machine-model').value = m.model || '';
            document.getElementById('machine-serial').value = m.serial_number || '';
            document.getElementById('machine-location').value = m.location || '';
            document.getElementById('machine-interval').value = m.maintenance_interval_days;
            document.getElementById('machine-last-date').value = m.last_maintenance_date || '';
            document.getElementById('machine-status').value = m.status;
            document.getElementById('machine-notes').value = m.notes || '';
            App.openModal('machine-modal');
        } catch (e) {
            console.error(e);
        }
    },

    async saveMachine(event) {
        event.preventDefault();
        const id = document.getElementById('machine-id').value;
        const data = {
            machine_code: document.getElementById('machine-code').value.trim(),
            name: document.getElementById('machine-name').value.trim(),
            model: document.getElementById('machine-model').value.trim() || null,
            serial_number: document.getElementById('machine-serial').value.trim() || null,
            location: document.getElementById('machine-location').value.trim() || null,
            maintenance_interval_days: parseInt(document.getElementById('machine-interval').value, 10) || 30,
            last_maintenance_date: document.getElementById('machine-last-date').value || null,
            status: document.getElementById('machine-status').value,
            notes: document.getElementById('machine-notes').value.trim() || null,
        };

        try {
            if (id) {
                await API.updateMachine(id, data);
                App.showToast('Makine bilgileri başarıyla güncellendi.', 'success');
            } else {
                await API.createMachine(data);
                App.showToast('Yeni makine başarıyla eklendi.', 'success');
            }
            App.closeModal('machine-modal');
            this.load();
            Dashboard.load();
        } catch (e) {
            // Toast handled by API wrapper
        }
    },

    async deleteMachine(id, name) {
        if (!confirm(`'${name}' adlı makineyi silmek istediğinize emin misiniz? (Tüm bakım geçmişi de silinecektir.)`)) return;
        try {
            await API.deleteMachine(id);
            App.showToast('Makine başarıyla silindi.', 'success');
            this.load();
            Dashboard.load();
        } catch (e) {}
    },

    async openHistoryModal(machineId, machineName) {
        document.getElementById('history-machine-name').textContent = machineName;
        const container = document.getElementById('machine-history-list');
        container.innerHTML = '<tr><td colspan="5" class="py-8 text-center text-slate-400">Yükleniyor...</td></tr>';
        App.openModal('machine-history-modal');

        try {
            const logs = await API.getMaintenanceLogs({ machine_id: machineId });
            if (!logs || logs.length === 0) {
                container.innerHTML = '<tr><td colspan="5" class="py-8 text-center text-slate-400">Bu makineye ait henüz bakım kaydı bulunmamaktadır.</td></tr>';
                return;
            }

            container.innerHTML = logs.map(l => `
                <tr class="border-b border-slate-100 text-xs">
                    <td class="py-2.5 px-3 font-mono text-slate-600">${l.maintenance_date}</td>
                    <td class="py-2.5 px-3 font-medium text-slate-800">${l.maintenance_type}</td>
                    <td class="py-2.5 px-3 text-slate-600">${l.description}</td>
                    <td class="py-2.5 px-3 text-slate-600">${l.part_name ? `${l.part_name} (${l.quantity_used} Ad.)` : '-'}</td>
                    <td class="py-2.5 px-3 text-slate-600">${l.technician}</td>
                </tr>
            `).join('');
        } catch (e) {
            container.innerHTML = '<tr><td colspan="5" class="py-8 text-center text-rose-500">Geçmiş yüklenemedi.</td></tr>';
        }
    }
};
