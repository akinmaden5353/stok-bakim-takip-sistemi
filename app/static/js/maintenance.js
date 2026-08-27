/**
 * Maintenance Logs & Action Logic
 */
const Maintenance = {
    cachedLogs: [],
    cachedPartsMap: {},

    async load() {
        const machineId = document.getElementById('log-machine-filter')?.value || '';
        const search = document.getElementById('log-search')?.value || '';

        try {
            const logs = await API.getMaintenanceLogs({
                machine_id: machineId || undefined,
                search: search || undefined
            });
            this.cachedLogs = logs;
            this.renderList(logs);
        } catch (e) {
            console.error("Bakım kayıtları yüklenirken hata:", e);
        }
    },

    renderList(logs) {
        const container = document.getElementById('logs-table-body');
        if (!container) return;

        if (!logs || logs.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="8" class="py-12 text-center text-slate-400">
                        <i data-lucide="clipboard-list" class="w-8 h-8 mx-auto mb-2 text-slate-300"></i>
                        <p class="text-sm">Kayıtlı bakım geçmişi bulunamadı.</p>
                    </td>
                </tr>
            `;
            lucide.createIcons();
            return;
        }

        container.innerHTML = logs.map(l => {
            let typeBadge = '';
            if (l.maintenance_type === 'Periyodik Bakım') {
                typeBadge = '<span class="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded text-xs font-semibold">Periyodik</span>';
            } else if (l.maintenance_type === 'Arıza Onarım') {
                typeBadge = '<span class="bg-rose-50 text-rose-700 border border-rose-200 px-2 py-0.5 rounded text-xs font-semibold">Arıza Onarım</span>';
            } else {
                typeBadge = '<span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-xs font-medium">Önleyici</span>';
            }

            return `
                <tr class="border-b border-slate-100 table-row-hover text-sm">
                    <td class="py-3 px-4 font-mono text-xs text-slate-600 whitespace-nowrap">${l.maintenance_date}</td>
                    <td class="py-3 px-4">
                        <div class="font-semibold text-slate-800">${l.machine_name}</div>
                        <span class="text-xs font-mono text-slate-400 bg-slate-100 px-1.5 py-0.2 rounded border">${l.machine_code}</span>
                    </td>
                    <td class="py-3 px-4">${typeBadge}</td>
                    <td class="py-3 px-4 text-xs text-slate-700">
                        ${l.part_name ? `<div class="font-medium">${l.part_name}</div><div class="text-slate-400 font-mono">${l.part_code} • <strong class="text-slate-800 font-bold">${l.quantity_used} Adet</strong></div>` : '<span class="text-slate-400 italic">Parça kullanılmadı</span>'}
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-600">${l.technician}</td>
                    <td class="py-3 px-4 text-xs text-slate-600 max-w-xs truncate" title="${l.description}">${l.description}</td>
                    <td class="py-3 px-4 text-xs font-mono text-slate-700 whitespace-nowrap">${l.cost ? l.cost.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + ' ₺' : '-'}</td>
                    <td class="py-3 px-4 text-right whitespace-nowrap">
                        <button onclick="Maintenance.deleteLog(${l.id}, '${l.machine_name}', ${l.quantity_used > 0})" title="Kaydı Sil" 
                                class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        lucide.createIcons();
    },

    async openNewLogModal(preselectedMachineId = null) {
        document.getElementById('maintenance-form').reset();
        
        // Set today's date
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('m-date').value = today;

        // Fetch latest machines & inventory for dropdowns
        try {
            const [machines, parts] = await Promise.all([
                API.getMachines(),
                API.getInventory()
            ]);

            // Populate Machines Select
            const machineSelect = document.getElementById('m-machine-select');
            machineSelect.innerHTML = '<option value="">-- Makine Seçiniz --</option>' +
                machines.map(m => `
                    <option value="${m.id}" ${preselectedMachineId == m.id ? 'selected' : ''}>
                        ${m.machine_code} - ${m.name} (${m.location || 'Konum yok'})
                    </option>
                `).join('');

            // Populate Parts Select & Cache Parts
            this.cachedPartsMap = {};
            parts.forEach(p => { this.cachedPartsMap[p.id] = p; });

            const partSelect = document.getElementById('m-part-select');
            partSelect.innerHTML = '<option value="">-- Parça Kullanılmadı --</option>' +
                parts.map(p => `
                    <option value="${p.id}">
                        ${p.part_code} - ${p.part_name} (Stok: ${p.stock_quantity} ${p.unit})
                    </option>
                `).join('');

            this.onPartChange();
            App.openModal('maintenance-modal');
        } catch (e) {
            console.error(e);
        }
    },

    onPartChange() {
        const partSelect = document.getElementById('m-part-select');
        const selectedId = partSelect.value;
        const infoBox = document.getElementById('m-part-stock-info');
        const qtyInput = document.getElementById('m-part-qty');
        const qtyContainer = document.getElementById('m-qty-container');

        if (!selectedId) {
            infoBox.classList.add('hidden');
            qtyContainer.classList.add('opacity-50');
            qtyInput.disabled = true;
            qtyInput.value = '0';
            return;
        }

        const part = this.cachedPartsMap[selectedId];
        if (part) {
            qtyContainer.classList.remove('opacity-50');
            qtyInput.disabled = false;
            if (qtyInput.value === '0') qtyInput.value = '1';

            infoBox.classList.remove('hidden');
            if (part.stock_quantity <= 0) {
                infoBox.className = 'mt-2 p-2 rounded-lg bg-rose-100 text-rose-800 text-xs flex items-center space-x-1.5 font-medium';
                infoBox.innerHTML = `<i data-lucide="alert-circle" class="w-4 h-4 text-rose-600 shrink-0"></i> <span>DİKKAT: Bu parçanın stoku bitmiştir (0 ${part.unit})!</span>`;
            } else if (part.is_critical) {
                infoBox.className = 'mt-2 p-2 rounded-lg bg-amber-100 text-amber-800 text-xs flex items-center space-x-1.5 font-medium';
                infoBox.innerHTML = `<i data-lucide="alert-triangle" class="w-4 h-4 text-amber-600 shrink-0"></i> <span>Mevcut Stok: <strong>${part.stock_quantity} ${part.unit}</strong> (Kritik Seviyede!)</span>`;
            } else {
                infoBox.className = 'mt-2 p-2 rounded-lg bg-emerald-50 text-emerald-800 text-xs flex items-center space-x-1.5';
                infoBox.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4 text-emerald-600 shrink-0"></i> <span>Mevcut Stok: <strong>${part.stock_quantity} ${part.unit}</strong></span>`;
            }
            lucide.createIcons();
        }
    },

    async saveLog(event) {
        event.preventDefault();
        const machineId = document.getElementById('m-machine-select').value;
        const partId = document.getElementById('m-part-select').value || null;
        const qty = parseInt(document.getElementById('m-part-qty').value, 10) || 0;

        if (!machineId) {
            App.showToast('Lütfen bir makine seçiniz.', 'error');
            return;
        }

        if (partId && qty > 0) {
            const part = this.cachedPartsMap[partId];
            if (part && qty > part.stock_quantity) {
                App.showToast(`Yetersiz Stok! '${part.part_name}' için mevcut stok: ${part.stock_quantity} ${part.unit}.`, 'error');
                return;
            }
        }

        const data = {
            machine_id: parseInt(machineId, 10),
            part_id: partId ? parseInt(partId, 10) : null,
            quantity_used: partId ? qty : 0,
            maintenance_date: document.getElementById('m-date').value,
            maintenance_type: document.getElementById('m-type').value,
            technician: document.getElementById('m-technician').value.trim(),
            description: document.getElementById('m-description').value.trim(),
            labor_hours: parseFloat(document.getElementById('m-labor-hours').value) || 1.0,
            cost: parseFloat(document.getElementById('m-cost').value) || 0.0
        };

        try {
            await API.createMaintenanceLog(data);
            App.showToast('Bakım kaydı başarıyla oluşturuldu ve stok otomatik düşüldü!', 'success');
            App.closeModal('maintenance-modal');
            this.load();
            Dashboard.load();
            Machines.load();
            Inventory.load();
        } catch (e) {}
    },

    async deleteLog(id, machineName, hadPart) {
        let restoreStock = false;
        if (hadPart) {
            restoreStock = confirm(`Bu bakımda yedek parça kullanılmıştır. Kullanılan parçayı stoğa geri iade etmek istiyor musunuz?\n\n[Tamam]: Stoğu geri artırarak sil\n[İptal]: Stoğa dokunmadan sil`);
        } else {
            if (!confirm(`'${machineName}' için girilen bakım kaydını silmek istediğinize emin misiniz?`)) return;
        }

        try {
            await API.deleteMaintenanceLog(id, restoreStock);
            App.showToast('Bakım kaydı başarıyla silindi.', 'success');
            this.load();
            Dashboard.load();
            Inventory.load();
            Machines.load();
        } catch (e) {}
    },

    exportCSV() {
        if (!this.cachedLogs || this.cachedLogs.length === 0) {
            App.showToast('Dışa aktarılacak bakım kaydı bulunamadı.', 'error');
            return;
        }

        const headers = ["Bakim_ID", "Tarih", "Makine_Kodu", "Makine_Adi", "Bakim_Turu", "Kullanilan_Parca", "Adet", "Teknisyen", "Aciklama", "Maliyet_TL"];
        const rows = this.cachedLogs.map(l => [
            l.id,
            `"${l.maintenance_date}"`,
            `"${l.machine_code}"`,
            `"${l.machine_name}"`,
            `"${l.maintenance_type}"`,
            `"${l.part_name || 'Yok'}"`,
            l.quantity_used,
            `"${l.technician}"`,
            `"${(l.description || '').replace(/"/g, '""')}"`,
            l.cost || 0
        ]);

        const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", `Bakim_Gecmisi_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        App.showToast('Bakım geçmişi CSV olarak indirildi.', 'success');
    }
};
