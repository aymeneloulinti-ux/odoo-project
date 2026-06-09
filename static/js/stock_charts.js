// stock_charts.js
// Expects globals: movementBreakdown, warehouseActivity, stock_by_warehouse

const countsCtx = document.getElementById('movementCountChart').getContext('2d');
new Chart(countsCtx, {
    type: 'doughnut',
    data: {
        labels: window.movementBreakdown.labels,
        datasets: [{
            data: window.movementBreakdown.counts,
            backgroundColor: ['#6366f1', '#ec4899'],
            borderColor: ['#e0e7ff', '#fbcfe8'],
            borderWidth: 2,
        }],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { padding: 16, font: { size: 14, weight: '500' }, usePointStyle: true },
            },
        },
    },
});

const quantityCtx = document.getElementById('movementQuantityChart').getContext('2d');
new Chart(quantityCtx, {
    type: 'bar',
    data: {
        labels: window.movementBreakdown.labels,
        datasets: [{
            label: 'Quantity',
            data: window.movementBreakdown.quantities,
            backgroundColor: ['#0ea5e9', '#f97316'],
            borderColor: ['#0284c7', '#ea580c'],
            borderWidth: 1,
            borderRadius: 6,
        }],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                labels: { padding: 16, font: { size: 14, weight: '500' } },
            },
        },
        scales: {
            y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } },
        },
    },
});

let currentSelectedWarehouseId = null;
let warehouseTrendChart = null;
let currentPeriod = 'daily';

initializeTrendChart(null, 'All warehouses');

async function initializeTrendChart(warehouseId = null, warehouseName = 'All warehouses') {
    try {
        let url = '/ui/api/warehouse-trend-data?period=' + currentPeriod;
        if (warehouseId) url += '&warehouse_id=' + warehouseId;

        const response = await fetch(url);
        if (!response.ok) {
            console.error('Error loading trend data');
            return;
        }

        const data = await response.json();

        if (warehouseTrendChart) warehouseTrendChart.destroy();

        const activityCtx = document.getElementById('warehouseActivityChart').getContext('2d');
        warehouseTrendChart = new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Entries (IN)',
                        data: data.in_data,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: '#10b981',
                    },
                    {
                        label: 'Exits (OUT)',
                        data: data.out_data,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: '#ef4444',
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: { padding: 16, font: { size: 14, weight: '500' } },
                    },
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                    x: { grid: { display: false } },
                },
            },
        });

        document.getElementById('trendChartTitle').textContent = 'Movement trend - ' + warehouseName;
    } catch (error) {
        console.error('Error initializing trend chart:', error);
    }
}

function selectWarehouse(warehouseId, warehouseName) {
    currentSelectedWarehouseId = warehouseId;
    initializeTrendChart(warehouseId, warehouseName);
}

function changePeriod(period, event) {
    currentPeriod = period;
    const buttons = document.querySelectorAll('.period-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
    initializeTrendChart(currentSelectedWarehouseId, currentSelectedWarehouseId ? 'Selected warehouse' : 'All warehouses');
}

function openWarehouseModal(warehouseId, warehouseName) {
    const warehouse = window.warehousesByWarehouse.find(w => w.id === warehouseId);
    if (!warehouse) return;

    document.getElementById('modalTitle').textContent = 'Modifier un entrepot';
    document.getElementById('warehouseId').value = warehouseId;
    document.getElementById('warehouseName').value = warehouseName;
    document.getElementById('warehouseLocation').value = warehouse.location || '';
    document.getElementById('warehouseModal').style.display = 'flex';
}

function closeWarehouseModal() { document.getElementById('warehouseModal').style.display = 'none'; }

const warehouseFormEl = document.getElementById('warehouseForm');
if (warehouseFormEl) {
    warehouseFormEl.addEventListener('submit', async (event) => {
        event.preventDefault();
        const warehouseId = document.getElementById('warehouseId').value;
        const payload = { name: document.getElementById('warehouseName').value, location: document.getElementById('warehouseLocation').value };
        try {
            const response = await fetch('/warehouses/' + warehouseId, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            if (response.ok) { closeWarehouseModal(); location.reload(); } else { const error = await response.json(); alert('Error: ' + (error.detail || 'An error occurred')); }
        } catch (error) { console.error('Error saving warehouse:', error); alert('Error saving warehouse'); }
    });
}

function attachMovementHistoryPagination() {
    const container = document.getElementById('movement-history-container');
    if (!container) return;
    const links = container.querySelectorAll('.pagination-controls a.page-link');
    links.forEach((link) => {
        link.addEventListener('click', (event) => {
            if (link.classList.contains('disabled') || link.classList.contains('active')) { event.preventDefault(); return; }
            event.preventDefault();
            const url = new URL(link.href, window.location.origin);
            const nextPage = url.searchParams.get('page') || '1';
            loadMovementHistory(parseInt(nextPage, 10));
        });
    });
}

async function loadMovementHistory(page) {
    const response = await fetch('/ui/stock/history?page=' + page);
    if (!response.ok) { console.error('Error loading movement history'); return; }
    const html = await response.text();
    const container = document.getElementById('movement-history-container');
    if (!container) return;
    container.innerHTML = html;
    attachMovementHistoryPagination();
    window.history.pushState({}, '', '?page=' + page);
}

document.addEventListener('DOMContentLoaded', () => { attachMovementHistoryPagination(); });

window.onclick = function(event) { const modal = document.getElementById('warehouseModal'); if (event.target === modal) modal.style.display = 'none'; };
