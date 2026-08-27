/**
 * Inventory & Spare Parts Management Logic
 */
const Inventory = {
    cachedParts: [],

    async load() {
        const search = document.getElementById('inventory-search')?.value || '';
        const category = document.getElementById('inventory-category-filter')?.value || '';
        const onlyCritical = document.getElementById('inventory-critical-toggle')?.checked || false;

        try {
            const parts = await API.getInventory(search, category, onlyCritical);
            this.cachedParts = parts;
            this.renderList(parts);
        } catch (e) {
            console.error("Yedek parçalar yüklenirken hata:", e);
        }
    },

    renderList(parts) {
        const container = document.getElementById('inventory-table-body');
        if (!container) return;

        if (!parts || parts.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="7" class="py-12 text-center text-slate-400">
                        <i data-lucide="package-open" class="w-8 h-8 mx-auto mb-2 text-slate-300"></i>
                        <p class="text-sm">Kayıtlı yedek parça bulunamadı.</p>
                    </td>
                </tr>
            `;
            lucide.createIcons();
            return;
        }

        container.innerHTML = parts.map(p => {
            const isCritical = p.is_critical;
            const stockBadge = isCritical
                ? `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">
                    <span class="w-2 h-2 rounded-full bg-rose-600 mr-1.5 animate-ping"></span>${p.stock_quantity} ${p.unit} (Kritik!)
                   </span>`
                : `<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    ${p.stock_quantity} ${p.unit}
                   </span>`;

            return `
                <tr class="border-b border-slate-100 table-row-hover text-sm ${isCritical ? 'bg-rose-50/20' : ''}">
                    <td class="py-3 px-4">
                        <span class="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-1 rounded border">${p.part_code}</span>
                    </td>
                    <td class="py-3 px-4">
                        <div class="font-semibold text-slate-800">${p.part_name}</div>
                        <div class="text-xs text-slate-400">${p.notes || '-'}</div>
                    </td>
                    <td class="py-3 px-4 text-xs">
                        <span class="bg-slate-100 text-slate-600 px-2 py-0.5 rounded">${p.category}</span>
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-600 font-mono">${p.shelf_location || '-'}</td>
                    <td class="py-3 px-4">${stockBadge}</td>
                    <td class="py-3 px-4 text-xs text-slate-500 font-semibold">${p.critical_level} ${p.unit}</td>
                    <td class="py-3 px-4 text-right whitespace-nowrap">
                        <div class="flex items-center justify-end space-x-1.5">
                            <button onclick="Inventory.openAdjustModal(${p.id}, '${p.part_name}', ${p.stock_quantity}, '${p.unit}')" title="Stok Giriş/Çıkış" 
                                    class="px-2.5 py-1 bg-slate-100 hover:bg-slate-800 hover:text-white text-slate-700 rounded-lg text-xs font-medium transition flex items-center space-x-1">
                                <i data-lucide="plus-minus" class="w-3.5 h-3.5"></i>
                                <span>Stok Ayarla</span>
                            </button>
                            <button onclick="Inventory.openEditModal(${p.id})" title="Düzenle" 
                                    class="p-1.5 text-slate-700 hover:text-amber-700 hover:bg-amber-50 rounded-lg transition">
                                <i data-lucide="edit-3" class="w-4 h-4"></i>
                            </button>
                            <button onclick="Inventory.deletePart(${p.id}, '${p.part_name}')" title="Sil" 
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
        document.getElementById('part-modal-title').textContent = 'Yeni Yedek Parça Ekle';
        document.getElementById('part-id').value = '';
        document.getElementById('part-form').reset();
        document.getElementById('part-stock').value = '0';
        document.getElementById('part-critical').value = '5';
        document.getElementById('part-unit').value = 'Adet';
        App.openModal('part-modal');
    },

    async openEditModal(id) {
        try {
            const p = await API.getPart(id);
            document.getElementById('part-modal-title').textContent = 'Yedek Parça Düzenle';
            document.getElementById('part-id').value = p.id;
            document.getElementById('part-code').value = p.part_code;
            document.getElementById('part-name').value = p.part_name;
            document.getElementById('part-category').value = p.category || 'Genel';
            document.getElementById('part-stock').value = p.stock_quantity;
            document.getElementById('part-critical').value = p.critical_level;
            document.getElementById('part-unit').value = p.unit || 'Adet';
            document.getElementById('part-price').value = p.unit_price || '0';
            document.getElementById('part-shelf').value = p.shelf_location || '';
            document.getElementById('part-notes').value = p.notes || '';
            App.openModal('part-modal');
        } catch (e) {}
    },

    async savePart(event) {
        event.preventDefault();
        const id = document.getElementById('part-id').value;
        const data = {
            part_code: document.getElementById('part-code').value.trim(),
            part_name: document.getElementById('part-name').value.trim(),
            category: document.getElementById('part-category').value.trim() || 'Genel',
            stock_quantity: parseInt(document.getElementById('part-stock').value, 10) || 0,
            critical_level: parseInt(document.getElementById('part-critical').value, 10) || 0,
            unit: document.getElementById('part-unit').value.trim() || 'Adet',
            unit_price: parseFloat(document.getElementById('part-price').value) || 0.0,
            shelf_location: document.getElementById('part-shelf').value.trim() || null,
            notes: document.getElementById('part-notes').value.trim() || null
        };

        try {
            if (id) {
                await API.updatePart(id, data);
                App.showToast('Parça bilgileri başarıyla güncellendi.', 'success');
            } else {
                await API.createPart(data);
                App.showToast('Yeni yedek parça başarıyla eklendi.', 'success');
            }
            App.closeModal('part-modal');
            this.load();
            Dashboard.load();
        } catch (e) {}
    },

    openAdjustModal(partId, partName, currentStock, unit) {
        document.getElementById('adjust-part-id').value = partId;
        document.getElementById('adjust-part-name').textContent = partName;
        document.getElementById('adjust-current-stock').textContent = `${currentStock} ${unit}`;
        document.getElementById('adjust-amount').value = '1';
        document.getElementById('adjust-type').value = 'add';
        document.getElementById('adjust-reason').value = 'Depo Girişi / Tedarik';
        App.openModal('adjust-stock-modal');
    },

    async saveStockAdjustment(event) {
        event.preventDefault();
        const partId = document.getElementById('adjust-part-id').value;
        const type = document.getElementById('adjust-type').value;
        const amount = parseInt(document.getElementById('adjust-amount').value, 10) || 0;
        const reason = document.getElementById('adjust-reason').value.trim();

        if (amount <= 0) {
            App.showToast('Lütfen 0\'dan büyük bir miktar giriniz.', 'error');
            return;
        }

        const finalAdjustment = type === 'add' ? amount : -amount;

        try {
            await API.adjustStock(partId, finalAdjustment, reason);
            App.showToast('Stok miktarı başarıyla güncellendi.', 'success');
            App.closeModal('adjust-stock-modal');
            this.load();
            Dashboard.load();
        } catch (e) {}
    },

    async deletePart(id, name) {
        if (!confirm(`'${name}' adlı yedek parçayı silmek istediğinize emin misiniz?`)) return;
        try {
            await API.deletePart(id);
            App.showToast('Yedek parça başarıyla silindi.', 'success');
            this.load();
            Dashboard.load();
        } catch (e) {}
    }
};
