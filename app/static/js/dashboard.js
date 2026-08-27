/**
 * Dashboard Logic & Rendering
 */
const Dashboard = {
    monthlyChart: null,
    partsChart: null,

    async load() {
        try {
            const [summary, chartData] = await Promise.all([
                API.getDashboardSummary(),
                API.getDashboardCharts()
            ]);

            this.renderKPIs(summary.kpis);
            this.renderCriticalParts(summary.critical_parts);
            this.renderUpcomingMaintenances(summary.upcoming_maintenances);
            this.renderRecentLogs(summary.recent_logs);
            this.renderCharts(chartData);
        } catch (e) {
            console.error("Dashboard yüklenirken hata:", e);
        }
    },

    renderKPIs(kpis) {
        document.getElementById('kpi-total-machines').textContent = kpis.total_machines;
        document.getElementById('kpi-active-machines').textContent = `${kpis.active_machines} Aktif`;
        
        document.getElementById('kpi-due-maintenances').textContent = kpis.machines_needing_maintenance;
        const dueSub = document.getElementById('kpi-due-sub');
        if (kpis.machines_needing_maintenance > 0) {
            dueSub.textContent = 'Acil & Yaklaşan Bakımlar';
            dueSub.className = 'text-xs text-amber-600 font-semibold';
        } else {
            dueSub.textContent = 'Planlı bakım gecikmesi yok';
            dueSub.className = 'text-xs text-slate-500';
        }

        document.getElementById('kpi-total-parts').textContent = kpis.total_parts;
        
        const critElem = document.getElementById('kpi-critical-parts');
        critElem.textContent = kpis.critical_parts_count;
        const critSub = document.getElementById('kpi-critical-sub');
        if (kpis.critical_parts_count > 0) {
            critSub.textContent = 'Kritik Seviye Altında!';
            critSub.className = 'text-xs text-rose-600 font-bold';
        } else {
            critSub.textContent = 'Tüm stoklar güvenli seviyede';
            critSub.className = 'text-xs text-emerald-600 font-medium';
        }

        document.getElementById('kpi-month-maintenances').textContent = kpis.total_maintenances_this_month;
    },

    renderCriticalParts(parts) {
        const container = document.getElementById('dashboard-critical-list');
        const countBadge = document.getElementById('dashboard-critical-count');
        countBadge.textContent = `${parts.length} Parça`;

        if (!parts || parts.length === 0) {
            container.innerHTML = `
                <div class="py-8 text-center text-slate-500">
                    <div class="inline-flex p-3 bg-emerald-50 text-emerald-600 rounded-full mb-2">
                        <i data-lucide="check-circle-2" class="w-6 h-6"></i>
                    </div>
                    <p class="text-sm font-medium text-emerald-800">Kritik stok uyarısı yok!</p>
                    <p class="text-xs text-slate-400 mt-0.5">Tüm yedek parçalar belirlenen kritik eşiğin üzerinde.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        container.innerHTML = parts.map(p => `
            <div class="flex items-center justify-between p-3.5 bg-rose-50/70 border border-rose-200/80 rounded-xl transition hover:bg-rose-50">
                <div class="flex items-start space-x-3">
                    <div class="p-2 bg-rose-100 text-rose-600 rounded-lg shrink-0 mt-0.5">
                        <i data-lucide="alert-triangle" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="font-semibold text-slate-800 text-sm">${p.part_name}</span>
                            <span class="text-xs font-mono bg-white px-2 py-0.5 rounded text-slate-600 border border-rose-200">${p.part_code}</span>
                        </div>
                        <div class="text-xs text-rose-700 mt-1 flex items-center space-x-3">
                            <span>Mevcut: <strong class="text-rose-900">${p.stock_quantity} ${p.unit}</strong></span>
                            <span>•</span>
                            <span>Kritik Eşik: <strong>${p.critical_level} ${p.unit}</strong></span>
                            <span>•</span>
                            <span class="bg-rose-200 text-rose-800 px-1.5 py-0.2 rounded font-semibold">-${p.deficit} Eksik</span>
                        </div>
                    </div>
                </div>
                <button onclick="Inventory.openAdjustModal(${p.id}, '${p.part_name}', ${p.stock_quantity}, '${p.unit}')" 
                        class="px-3 py-1.5 bg-white border border-rose-300 text-rose-700 hover:bg-rose-600 hover:text-white rounded-lg text-xs font-medium shadow-sm transition flex items-center space-x-1 shrink-0">
                    <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                    <span>Stok Ekle</span>
                </button>
            </div>
        `).join('');

        lucide.createIcons();
    },

    renderUpcomingMaintenances(maintenances) {
        const container = document.getElementById('dashboard-upcoming-list');
        const countBadge = document.getElementById('dashboard-upcoming-count');
        countBadge.textContent = `${maintenances.length} Makine`;

        if (!maintenances || maintenances.length === 0) {
            container.innerHTML = `
                <div class="py-8 text-center text-slate-500">
                    <div class="inline-flex p-3 bg-emerald-50 text-emerald-600 rounded-full mb-2">
                        <i data-lucide="calendar-check" class="w-6 h-6"></i>
                    </div>
                    <p class="text-sm font-medium text-emerald-800">Yakın zamanda planlı bakım yok</p>
                    <p class="text-xs text-slate-400 mt-0.5">Tüm makineler periyodik bakım takvimine uygun çalışıyor.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        container.innerHTML = maintenances.map(m => {
            const isOverdue = m.is_overdue;
            const bgClass = isOverdue ? 'bg-rose-50/70 border-rose-200' : 'bg-amber-50/70 border-amber-200';
            const iconBg = isOverdue ? 'bg-rose-100 text-rose-600' : 'bg-amber-100 text-amber-600';
            const badgeClass = isOverdue ? 'bg-rose-600 text-white' : 'bg-amber-500 text-white';
            const statusText = isOverdue 
                ? `<span class="text-rose-700 font-bold">${Math.abs(m.days_left)} gün gecikti!</span>` 
                : (m.days_left === 0 ? '<span class="text-amber-800 font-bold">Bugün bakım günü!</span>' : `<span class="text-amber-800 font-semibold">${m.days_left} gün kaldı</span>`);

            return `
                <div class="flex items-center justify-between p-3.5 ${bgClass} border rounded-xl transition">
                    <div class="flex items-start space-x-3">
                        <div class="p-2 ${iconBg} rounded-lg shrink-0 mt-0.5">
                            <i data-lucide="${isOverdue ? 'alert-octagon' : 'clock'}" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <div class="flex items-center space-x-2">
                                <span class="font-semibold text-slate-800 text-sm">${m.machine_name}</span>
                                <span class="text-xs font-mono bg-white px-2 py-0.5 rounded text-slate-600 border">${m.machine_code}</span>
                            </div>
                            <div class="text-xs text-slate-600 mt-1 flex items-center space-x-2">
                                <span>${m.location || 'Konum belirtilmedi'}</span>
                                <span>•</span>
                                <span>Tarih: <strong>${m.next_maintenance_date}</strong></span>
                                <span>•</span>
                                ${statusText}
                            </div>
                        </div>
                    </div>
                    <button onclick="Maintenance.openNewLogModal(${m.machine_id})" 
                            class="px-3 py-1.5 bg-slate-900 text-white hover:bg-slate-800 rounded-lg text-xs font-medium shadow-sm transition flex items-center space-x-1 shrink-0">
                        <i data-lucide="wrench" class="w-3.5 h-3.5"></i>
                        <span>Bakım Yap</span>
                    </button>
                </div>
            `;
        }).join('');

        lucide.createIcons();
    },

    renderRecentLogs(logs) {
        const container = document.getElementById('dashboard-recent-logs');
        if (!logs || logs.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="5" class="py-8 text-center text-slate-400 text-sm">Henüz kayıtlı bakım geçmişi bulunmuyor.</td>
                </tr>
            `;
            return;
        }

        container.innerHTML = logs.map(log => `
            <tr class="border-b border-slate-100 table-row-hover text-sm">
                <td class="py-3 px-4 text-slate-500 font-mono text-xs whitespace-nowrap">${log.maintenance_date}</td>
                <td class="py-3 px-4">
                    <div class="font-medium text-slate-800">${log.machine_name}</div>
                    <div class="text-xs text-slate-400 font-mono">${log.machine_code}</div>
                </td>
                <td class="py-3 px-4">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                        log.maintenance_type === 'Periyodik Bakım' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                        log.maintenance_type === 'Arıza Onarım' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                        'bg-slate-100 text-slate-700'
                    }">
                        ${log.maintenance_type}
                    </span>
                </td>
                <td class="py-3 px-4 text-slate-600">
                    ${log.part_name ? `<span class="font-medium text-slate-700">${log.part_name}</span> <span class="text-xs text-slate-400">(${log.quantity_used} Adet)</span>` : '<span class="text-slate-400 italic">Parça kullanılmadı</span>'}
                </td>
                <td class="py-3 px-4 text-slate-600 text-xs">${log.technician}</td>
            </tr>
        `).join('');
    },

    renderCharts(chartData) {
        // 1. Monthly Maintenance Trend Chart
        const ctxMonthly = document.getElementById('chart-monthly-maintenance');
        if (ctxMonthly) {
            if (this.monthlyChart) this.monthlyChart.destroy();

            this.monthlyChart = new Chart(ctxMonthly, {
                type: 'line',
                data: {
                    labels: chartData.monthly.labels,
                    datasets: [{
                        label: 'Bakım Sayısı',
                        data: chartData.monthly.data,
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.08)',
                        fill: true,
                        tension: 0.35,
                        borderWidth: 2,
                        pointBackgroundColor: '#2563eb',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    }
                }
            });
        }

        // 2. Top Used Parts Chart
        const ctxParts = document.getElementById('chart-top-parts');
        if (ctxParts) {
            if (this.partsChart) this.partsChart.destroy();

            this.partsChart = new Chart(ctxParts, {
                type: 'bar',
                data: {
                    labels: chartData.top_parts.labels,
                    datasets: [{
                        label: 'Kullanılan Adet',
                        data: chartData.top_parts.data,
                        backgroundColor: '#6366f1',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    }
                }
            });
        }
    }
};
