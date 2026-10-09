/**
 * GRAND ROYAL HOTEL - Restaurant & Food Ordering Management
 * Handles Order State, Real-time Calculation, and Bill Generation
 */

class OrderManager {
    constructor() {
        this.cart = []; // Array of { food_id, name, price, quantity, food_type }
        this.discountPct = 0;
        this.gstRate = 0.05; // 5% GST
        this.init();
    }

    init() {
        this.bindEvents();
        this.renderOrderPanel();
    }

    bindEvents() {
        // Discount input change
        const discountInput = document.getElementById('discountInput');
        if (discountInput) {
            discountInput.addEventListener('input', (e) => {
                let val = parseFloat(e.target.value) || 0;
                if (val < 0) val = 0;
                if (val > 100) val = 100;
                this.discountPct = val;
                this.calculateTotals();
            });
        }

        // Clear order button
        const clearBtn = document.getElementById('btnClearOrder');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (this.cart.length > 0 && confirm('Are you sure you want to clear the current order?')) {
                    this.clearOrder();
                }
            });
        }

        // Generate Bill button
        const genBillBtn = document.getElementById('btnGenerateBill');
        if (genBillBtn) {
            genBillBtn.addEventListener('click', () => this.submitOrder());
        }
    }

    addItem(food) {
        const existing = this.cart.find(item => item.food_id === food.id);
        if (existing) {
            existing.quantity += 1;
        } else {
            this.cart.push({
                food_id: food.id,
                name: food.name,
                price: parseFloat(food.price),
                quantity: 1,
                food_type: food.food_type
            });
        }
        this.renderOrderPanel();
        this.calculateTotals();
        this.showToast(`Added ${food.name} to order`);
    }

    updateQuantity(foodId, delta) {
        const item = this.cart.find(i => i.food_id === foodId);
        if (!item) return;

        item.quantity += delta;
        if (item.quantity <= 0) {
            this.removeItem(foodId);
            return;
        }
        this.renderOrderPanel();
        this.calculateTotals();
    }

    removeItem(foodId) {
        this.cart = this.cart.filter(i => i.food_id !== foodId);
        this.renderOrderPanel();
        this.calculateTotals();
    }

    clearOrder() {
        this.cart = [];
        this.discountPct = 0;
        const discountInput = document.getElementById('discountInput');
        if (discountInput) discountInput.value = 0;
        this.renderOrderPanel();
        this.calculateTotals();
    }

    calculateTotals() {
        const subtotal = this.cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
        const discountAmount = (subtotal * this.discountPct) / 100;
        const taxableAmount = Math.max(0, subtotal - discountAmount);
        const gstAmount = taxableAmount * this.gstRate;
        const grandTotal = taxableAmount + gstAmount;

        // Update DOM elements
        const subtotalEl = document.getElementById('orderSubtotal');
        const discountAmtEl = document.getElementById('orderDiscountAmt');
        const gstEl = document.getElementById('orderGst');
        const grandTotalEl = document.getElementById('orderGrandTotal');
        const itemCountBadge = document.getElementById('orderItemCount');

        if (subtotalEl) subtotalEl.textContent = `₹${subtotal.toFixed(2)}`;
        if (discountAmtEl) discountAmtEl.textContent = `-₹${discountAmount.toFixed(2)}`;
        if (gstEl) gstEl.textContent = `₹${gstAmount.toFixed(2)}`;
        if (grandTotalEl) grandTotalEl.textContent = `₹${grandTotal.toFixed(2)}`;
        if (itemCountBadge) itemCountBadge.textContent = `${this.cart.reduce((s, i) => s + i.quantity, 0)} Items`;

        return { subtotal, discountAmount, gstAmount, grandTotal };
    }

    renderOrderPanel() {
        const container = document.getElementById('orderItemsContainer');
        const emptyState = document.getElementById('orderEmptyState');
        const billingSummary = document.getElementById('billingSummarySection');

        if (!container) return;

        if (this.cart.length === 0) {
            container.innerHTML = '';
            if (emptyState) emptyState.classList.remove('d-none');
            if (billingSummary) billingSummary.classList.add('opacity-50');
            return;
        }

        if (emptyState) emptyState.classList.add('d-none');
        if (billingSummary) billingSummary.classList.remove('opacity-50');

        container.innerHTML = this.cart.map(item => `
            <li class="order-item-row">
                <div class="order-item-info">
                    <div class="order-item-name">
                        <span class="veg-dot ${item.food_type === 'Veg' ? 'veg' : 'non-veg'} me-1"></span>
                        ${item.name}
                    </div>
                    <div class="order-item-price">₹${item.price.toFixed(2)} each</div>
                </div>
                <div class="order-qty-controls">
                    <button type="button" class="btn-qty" onclick="window.orderManager.updateQuantity(${item.food_id}, -1)">-</button>
                    <span class="qty-display">${item.quantity}</span>
                    <button type="button" class="btn-qty" onclick="window.orderManager.updateQuantity(${item.food_id}, 1)">+</button>
                </div>
                <div class="order-item-total">
                    ₹${(item.price * item.quantity).toFixed(2)}
                </div>
                <button type="button" class="btn-remove-item" onclick="window.orderManager.removeItem(${item.food_id})" title="Remove">
                    <i class="bi bi-trash3"></i>
                </button>
            </li>
        `).join('');

        // Trigger AI Smart Recommendations
        this.fetchAIRecommendations();
    }

    async fetchAIRecommendations() {
        const section = document.getElementById('aiRecommendationsSection');
        const list = document.getElementById('aiRecommendationsList');
        if (!section || !list) return;

        if (this.cart.length === 0) {
            section.classList.add('d-none');
            return;
        }

        try {
            const foodIds = this.cart.map(i => i.food_id).join(',');
            const res = await fetch(`/api/ai/recommendations?food_ids=${foodIds}&limit=3`);
            const data = await res.json();

            if (res.ok && data.success && data.recommendations && data.recommendations.length > 0) {
                section.classList.remove('d-none');
                list.innerHTML = data.recommendations.map(rec => `
                    <div class="d-flex align-items-center justify-content-between p-1 px-2 border rounded bg-white small mb-1 shadow-sm">
                        <div class="d-flex align-items-center gap-1 text-truncate" style="max-width: 180px;">
                            <span class="veg-dot ${rec.food.food_type === 'Veg' ? 'veg' : 'non-veg'} me-1"></span>
                            <span class="fw-bold text-dark text-truncate">${rec.food.name}</span>
                            <span class="text-muted small">₹${rec.food.price.toFixed(0)}</span>
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-danger py-0 px-2 btn-ai-add"
                            title="${rec.reason}">
                            <i class="bi bi-plus"></i> Add
                        </button>
                    </div>
                `).join('');

                list.querySelectorAll('.btn-ai-add').forEach((btn, idx) => {
                    const targetFood = data.recommendations[idx].food;
                    btn.addEventListener('click', () => {
                        this.addItem(targetFood);
                    });
                });
            } else {
                section.classList.add('d-none');
            }
        } catch (e) {
            section.classList.add('d-none');
        }
    }

    async submitOrder() {
        const customerName = document.getElementById('customerName')?.value.trim();
        const tableNumber = document.getElementById('tableNumber')?.value.trim();
        const orderType = document.querySelector('input[name="orderType"]:checked')?.value || 'Dine-In';
        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked')?.value || 'Cash';

        if (!customerName) {
            alert('Please enter Customer Name.');
            document.getElementById('customerName')?.focus();
            return;
        }
        if (!tableNumber) {
            alert('Please select or enter Table / Token Number.');
            document.getElementById('tableNumber')?.focus();
            return;
        }
        if (this.cart.length === 0) {
            alert('Your order is empty. Please select food items from the menu.');
            return;
        }

        const payload = {
            customer_name: customerName,
            table_number: tableNumber,
            order_type: orderType,
            payment_method: paymentMethod,
            discount_pct: this.discountPct,
            items: this.cart.map(i => ({
                food_id: i.food_id,
                quantity: i.quantity
            }))
        };

        const btn = document.getElementById('btnGenerateBill');
        const origText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing Bill...';

        try {
            const res = await fetch('/api/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await res.json();

            if (res.ok && result.success) {
                // Clear cart
                this.clearOrder();
                document.getElementById('customerName').value = '';

                // Open printable invoice modal or navigate to bill page
                if (result.bill && result.bill.id) {
                    window.location.href = `/bill/${result.bill.id}`;
                } else {
                    alert('Order and Bill generated successfully!');
                    window.location.reload();
                }
            } else {
                alert('Error creating bill: ' + (result.error || 'Server error'));
                btn.disabled = false;
                btn.innerHTML = origText;
            }
        } catch (err) {
            alert('Failed to connect to Flask server. Please check backend.');
            btn.disabled = false;
            btn.innerHTML = origText;
        }
    }

    showToast(msg) {
        const toastEl = document.getElementById('quickToast');
        if (toastEl) {
            const msgEl = toastEl.querySelector('.toast-body');
            if (msgEl) msgEl.textContent = msg;
            const toast = new bootstrap.Toast(toastEl, { delay: 1800 });
            toast.show();
        }
    }
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
    window.orderManager = new OrderManager();
});
