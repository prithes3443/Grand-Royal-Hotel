/**
 * GRAND ROYAL HOTEL - Dashboard Analytics Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();

        if (res.ok && data.success) {
            renderMetrics(data.metrics);
            renderRecentInvoices(data.recent_invoices);
            renderTopDishes(data.top_dishes);
        } else {
            console.error('Failed to load dashboard:', data.error);
        }
    } catch (err) {
        console.error('Error fetching dashboard analytics:', err);
    }
}

function renderMetrics(metrics) {
    if (!metrics) return;

    const todayOrdersEl = document.getElementById('statTodayOrders');
    const todayRevEl = document.getElementById('statTodayRevenue');
    const totalOrdersEl = document.getElementById('statTotalOrders');
    const totalRevEl = document.getElementById('statTotalRevenue');

    if (todayOrdersEl) todayOrdersEl.textContent = metrics.today_orders ?? 0;
    if (todayRevEl) todayRevEl.textContent = `₹${(metrics.today_revenue ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
    if (totalOrdersEl) totalOrdersEl.textContent = metrics.total_orders ?? 0;
    if (totalRevEl) totalRevEl.textContent = `₹${(metrics.total_revenue ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
}

function renderRecentInvoices(invoices) {
    const tbody = document.getElementById('recentInvoicesTbody');
    if (!tbody) return;

    if (!invoices || invoices.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No invoices generated yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = invoices.map(inv => `
        <tr>
            <td>
                <span class="fw-bold text-danger">${inv.bill_number}</span>
            </td>
            <td>
                <div class="fw-bold text-dark">${inv.customer_name}</div>
                <small class="text-muted">${inv.table_number}</small>
            </td>
            <td class="fw-bold text-dark">₹${inv.grand_total.toFixed(2)}</td>
            <td>
                <span class="badge bg-light text-secondary border">${inv.payment_method}</span>
            </td>
            <td class="text-muted small">${inv.created_at}</td>
            <td>
                <a href="/bill/${inv.id}" class="btn btn-sm btn-outline-danger" title="View & Print">
                    <i class="bi bi-printer"></i> Print
                </a>
            </td>
        </tr>
    `).join('');
}

function renderTopDishes(dishes) {
    const container = document.getElementById('topDishesList');
    if (!container) return;

    if (!dishes || dishes.length === 0) {
        container.innerHTML = `<div class="text-muted text-center py-3">No dish sales recorded yet.</div>`;
        return;
    }

    container.innerHTML = dishes.map(dish => `
        <div class="d-flex align-items-center justify-content-between p-3 mb-2 bg-light rounded-3 border">
            <div class="d-flex align-items-center gap-3">
                <span class="badge ${dish.rank === 1 ? 'bg-warning text-dark' : 'bg-secondary'} rounded-circle p-2 fw-bold" style="width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;">
                    #${dish.rank}
                </span>
                <img src="/static/images/${dish.image || 'idly.jpg'}" alt="${dish.name}" class="rounded" style="width: 46px; height: 46px; object-fit: cover;" onerror="this.src='/static/images/idly.jpg'">
                <div>
                    <div class="fw-bold text-dark">${dish.name}</div>
                    <small class="text-muted">${dish.category} • ₹${dish.price.toFixed(0)}</small>
                </div>
            </div>
            <div class="text-end">
                <span class="badge bg-danger-subtle text-danger fw-bold fs-6">
                    ${dish.total_ordered} Orders
                </span>
            </div>
        </div>
    `).join('');
}
