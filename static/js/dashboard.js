/**
 * GRAND ROYAL HOTEL - Dashboard Analytics & AI Intelligence Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    loadAIForecast();
    loadAIDynamicPricing();
    loadAIMenuMatrix();
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

/**
 * AI Demand Forecast & Kitchen Prep Guide
 */
async function loadAIForecast() {
    const tableBody = document.getElementById('forecastTableBody');
    const prepBody = document.getElementById('kitchenPrepTableBody');
    if (!tableBody) return;

    try {
        const res = await fetch('/api/ai/forecast?days=7');
        const data = await res.json();

        if (res.ok && data.success && data.forecast) {
            const f = data.forecast;

            // Render 7-day schedule
            tableBody.innerHTML = f.daily_forecast.map(day => `
                <tr class="${day.is_weekend ? 'table-warning-subtle fw-semibold' : ''}">
                    <td><strong>${day.date}</strong></td>
                    <td>
                        <span class="badge ${day.is_weekend ? 'bg-warning text-dark' : 'bg-light text-secondary border'}">
                            ${day.day_name}
                        </span>
                    </td>
                    <td class="text-muted">${day.peak_shift}</td>
                    <td>
                        <span class="badge ${day.seasonality_factor > 1.2 ? 'bg-danger-subtle text-danger' : 'bg-secondary-subtle text-secondary'}">
                            ${(day.seasonality_factor * 100).toFixed(0)}%
                        </span>
                    </td>
                    <td class="text-end fw-bold text-dark">${day.predicted_orders}</td>
                    <td class="text-end fw-bold text-success">₹${day.predicted_revenue.toLocaleString('en-IN')}</td>
                </tr>
            `).join('');

            // Render Kitchen Prep Checklist
            if (prepBody && f.tomorrow_kitchen_prep) {
                prepBody.innerHTML = f.tomorrow_kitchen_prep.map(item => `
                    <tr>
                        <td class="fw-bold text-dark">${item.name}</td>
                        <td class="text-muted">${item.category}</td>
                        <td>${item.predicted_demand_units} portions</td>
                        <td class="text-success">+${item.safety_buffer} buffer</td>
                        <td><span class="badge bg-dark fs-6">${item.recommended_prep_qty} portions</span></td>
                        <td>
                            <span class="badge ${item.stockout_risk === 'High' ? 'bg-danger' : 'bg-warning text-dark'}">
                                ${item.stockout_risk}
                            </span>
                        </td>
                    </tr>
                `).join('');
            }
        }
    } catch (e) {
        console.warn('AI Forecast error:', e);
    }
}

/**
 * AI Real-Time Dynamic Pricing Insights
 */
async function loadAIDynamicPricing() {
    const badge = document.getElementById('currentShiftBadge');
    const container = document.getElementById('dynamicPricingContainer');
    if (!container) return;

    try {
        const res = await fetch('/api/ai/dynamic-pricing');
        const data = await res.json();

        if (res.ok && data.success && data.pricing) {
            const p = data.pricing;
            if (badge) {
                badge.textContent = `${p.current_window} (${(p.demand_multiplier * 100).toFixed(0)}% demand)`;
                badge.className = `badge ${p.is_peak_hour ? 'bg-danger' : 'bg-success'} text-white fw-bold`;
            }

            container.innerHTML = `
                <div class="alert alert-${p.is_peak_hour ? 'danger-subtle text-danger' : 'success-subtle text-success'} py-2 px-3 mb-3 d-flex align-items-center">
                    <i class="bi ${p.is_peak_hour ? 'bi-fire' : 'bi-clock'} me-2 fs-5"></i>
                    <div>
                        <strong>${p.current_window}:</strong>
                        ${p.is_peak_hour ? 'High table velocity detected. AI recommends peak optimization on core dishes.' : 'Off-peak window. AI suggests happy hour incentives to boost footfall.'}
                    </div>
                </div>
                <div class="list-group list-group-flush border rounded-3">
                    ${p.pricing_recommendations.slice(0, 5).map(rec => `
                        <div class="list-group-item d-flex justify-content-between align-items-center py-2 px-3">
                            <div>
                                <strong class="text-dark">${rec.name}</strong>
                                <div class="text-muted small">${rec.action} • <span class="text-success fw-bold">${rec.projected_lift}</span></div>
                            </div>
                            <div class="text-end">
                                <div class="fw-bold text-dark">₹${rec.suggested_price}</div>
                                <small class="text-muted text-decoration-line-through">₹${rec.current_price}</small>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (e) {
        console.warn('AI Dynamic Pricing error:', e);
    }
}

/**
 * BCG Menu Engineering Matrix
 */
async function loadAIMenuMatrix() {
    const container = document.getElementById('menuMatrixContainer');
    if (!container) return;

    try {
        const res = await fetch('/api/ai/menu-engineering');
        const data = await res.json();

        if (res.ok && data.success && data.menu_engineering) {
            const m = data.menu_engineering.matrix;
            const summary = data.menu_engineering.summary;

            container.innerHTML = `
                <div class="row g-2 mb-2">
                    <div class="col-6">
                        <div class="p-2 border rounded bg-warning-subtle text-dark">
                            <strong>⭐ Stars (${summary.stars_count})</strong>
                            <div class="text-muted small">High Margin & Volume</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="p-2 border rounded bg-primary-subtle text-dark">
                            <strong>🐴 Plowhorses (${summary.plowhorses_count})</strong>
                            <div class="text-muted small">High Volume, Mod. Margin</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="p-2 border rounded bg-info-subtle text-dark">
                            <strong>🧩 Puzzles (${summary.puzzles_count})</strong>
                            <div class="text-muted small">High Margin, Low Volume</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="p-2 border rounded bg-secondary-subtle text-dark">
                            <strong>🐕 Dogs (${summary.dogs_count})</strong>
                            <div class="text-muted small">Low Margin & Volume</div>
                        </div>
                    </div>
                </div>
                <div class="small text-muted fst-italic">
                    AI recommendation: Promote "Puzzles" via waiter upsell pairing prompts; protect ingredient consistency on "Stars".
                </div>
            `;
        }
    } catch (e) {
        console.warn('AI Menu Matrix error:', e);
    }
}
