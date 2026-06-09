// dashboard_kpis.js
// Relies on globals defined inline in the template:
// monthlyTrend, dailyTrend, annualRevenueChart, monthlyRevenueChart,
// annualMovementBreakdown, monthlyMovementBreakdown

const monthlyTrendData = window.monthlyTrend;
const annualTrend = monthlyTrendData;
const dailyTrendData = window.dailyTrend;
const annualRevenue = window.annualRevenueChart;
const monthlyRevenue = window.monthlyRevenueChart;
const annualMovement = window.annualMovementBreakdown;
const monthlyMovement = window.monthlyMovementBreakdown;

const monthlyTrendCtx = document.getElementById('monthlyTrendChart').getContext('2d');
const trendChart = new Chart(monthlyTrendCtx, {
    type: 'line',
    data: {
        labels: annualTrend.labels,
        datasets: [
            {
                label: 'Revenue',
                data: annualTrend.revenue,
                backgroundColor: 'rgba(34, 197, 94, 0.2)',
                borderColor: '#22c55e',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
            },
            {
                label: 'Cost',
                data: monthlyTrendData.cost,
                backgroundColor: 'rgba(249, 115, 22, 0.2)',
                borderColor: '#f97316',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
            },
            {
                label: 'Profit',
                data: monthlyTrendData.profit,
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: '#3b82f6',
                borderWidth: 2,
                tension: 0.3,
                fill: false,
            },
        ],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    padding: 12,
                    font: { size: 13, weight: '500' },
                },
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: { callback: value => value },
                grid: { color: '#f1f5f9' },
            },
            x: { grid: { display: false } },
        },
    },
});

const revenueCtx = document.getElementById('revenueCostChart').getContext('2d');
const revenueChartObj = new Chart(revenueCtx, {
    type: 'bar',
    data: {
        labels: annualRevenue.labels,
        datasets: [{
            label: 'Valeur (€)',
            data: annualRevenue.values,
            backgroundColor: ['#22c55e', '#f97316'],
            borderColor: ['#15803d', '#c2410c'],
            borderWidth: 1,
            borderRadius: 6,
        }],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            y: { beginAtZero: true, ticks: { callback: value => value }, grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } },
        },
    },
});

const movementTypeCtx = document.getElementById('movementTypeChart').getContext('2d');
const movementTypeChartObj = new Chart(movementTypeCtx, {
    type: 'doughnut',
    data: {
        labels: annualMovement.labels,
        datasets: [{
            data: annualMovement.counts,
            backgroundColor: ['#0ea5e9', '#f97316'],
            borderColor: ['#dbeafe', '#fee2e2'],
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

// KPI Toggle logic
const annualBtn = document.getElementById('showAnnual');
const monthlyBtn = document.getElementById('showMonthly');
const annualKpis = document.getElementById('annualKpis');
const monthlyKpis = document.getElementById('monthlyKpis');

const trendTitle = document.getElementById('trendTitle');
const revenueCostTitle = document.getElementById('revenueCostTitle');
const movementTypeTitle = document.getElementById('movementTypeTitle');

function updateCharts(showAnnual) {
    if (showAnnual) {
        trendChart.data.labels = annualTrend.labels;
        trendChart.data.datasets[0].data = annualTrend.revenue;
        trendChart.data.datasets[1].data = annualTrend.cost;
        trendChart.data.datasets[2].data = annualTrend.profit;
        revenueChartObj.data.labels = annualRevenue.labels;
        revenueChartObj.data.datasets[0].data = annualRevenue.values;
        movementTypeChartObj.data.labels = annualMovement.labels;
        movementTypeChartObj.data.datasets[0].data = annualMovement.counts;
            trendTitle.textContent = 'Monthly trend';
            revenueCostTitle.textContent = 'Revenue vs Cost';
            movementTypeTitle.textContent = 'Movements by type';
        } else {
            trendChart.data.labels = dailyTrendData.labels;
            trendChart.data.datasets[0].data = dailyTrendData.revenue;
            trendChart.data.datasets[1].data = dailyTrendData.cost;
            trendChart.data.datasets[2].data = dailyTrendData.profit;
            revenueChartObj.data.labels = monthlyRevenue.labels;
            revenueChartObj.data.datasets[0].data = monthlyRevenue.values;
            movementTypeChartObj.data.labels = monthlyMovement.labels;
            movementTypeChartObj.data.datasets[0].data = monthlyMovement.counts;
            trendTitle.textContent = 'Daily trend';
            revenueCostTitle.textContent = 'Monthly revenue vs cost';
            movementTypeTitle.textContent = 'Monthly movements by type';
        annualKpis.style.display = '';
        monthlyKpis.style.display = 'none';
        annualBtn.classList.add('active');
        monthlyBtn.classList.remove('active');
    } {
        annualKpis.style.display = 'none';
        monthlyKpis.style.display = '';
        annualBtn.classList.remove('active');
        monthlyBtn.classList.add('active');
    }
    updateCharts(showAnnual);
}

annualBtn.addEventListener('click', () => setActive(true));
monthlyBtn.addEventListener('click', () => setActive(false));

// Initial state
updateCharts(true);
