/**
 * GRAND ROYAL HOTEL - Main Catalog & Menu Interactivity
 */

let allFoods = [];
let currentCategory = 'All Items';
let currentSearch = '';
let currentDietFilter = 'all'; // 'all', 'Veg', 'Non-Veg'

document.addEventListener('DOMContentLoaded', () => {
    loadFoodCatalog();
    bindCatalogFilters();
    bindAdminFoodEvents();
});

// Load food catalog from Flask REST API
async function loadFoodCatalog() {
    const grid = document.getElementById('foodGrid');
    if (!grid) return;

    try {
        grid.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="spinner-border text-danger" role="status"></div>
                <p class="text-muted mt-2">Loading fresh dishes from kitchen...</p>
            </div>
        `;

        const res = await fetch('/api/foods');
        const data = await res.json();

        if (res.ok && data.success) {
            allFoods = data.foods || [];
            renderFoods();
        } else {
            grid.innerHTML = `<div class="col-12 text-danger text-center py-5">Failed to load menu: ${data.error || 'Server error'}</div>`;
        }
    } catch (err) {
        grid.innerHTML = `<div class="col-12 text-danger text-center py-5">Unable to connect to Flask backend. Please make sure Flask is running.</div>`;
    }
}

// Render foods to the grid based on current filters
function renderFoods() {
    const grid = document.getElementById('foodGrid');
    const countBadge = document.getElementById('dishesCountBadge');
    if (!grid) return;

    let filtered = allFoods.filter(item => {
        // Category filter
        const matchCat = (currentCategory === 'All Items') || 
            (item.category.toLowerCase() === currentCategory.toLowerCase());
        
        // Search filter
        const matchSearch = !currentSearch || 
            item.name.toLowerCase().includes(currentSearch.toLowerCase()) || 
            item.description.toLowerCase().includes(currentSearch.toLowerCase());

        // Veg / Non-veg filter
        const matchDiet = (currentDietFilter === 'all') || (item.food_type === currentDietFilter);

        return matchCat && matchSearch && matchDiet;
    });

    if (countBadge) {
        countBadge.textContent = `${filtered.length} Dishes`;
    }

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-search display-4 text-muted"></i>
                <h5 class="mt-3 text-secondary">No dishes found</h5>
                <p class="text-muted small">Try searching for something else or clearing filters.</p>
                <button class="btn btn-sm btn-outline-danger" onclick="resetFilters()">Reset All Filters</button>
            </div>
        `;
        return;
    }

    grid.innerHTML = filtered.map(dish => {
        // Ensure image fallback
        const imgSrc = `/static/images/${dish.image || 'idly.jpg'}`;
        const isVeg = dish.food_type === 'Veg';
        const isAvailable = dish.is_available;

        return `
            <div class="col-sm-6 col-lg-4 col-xl-4 mb-4">
                <div class="food-card ${!isAvailable ? 'opacity-75' : ''}">
                    <div class="food-card-img-wrapper">
                        <img src="${imgSrc}" alt="${dish.name}" class="food-card-img" onerror="this.src='/static/images/idly.jpg'">
                        
                        <div class="veg-badge">
                            <span class="veg-dot ${isVeg ? 'veg' : 'non-veg'}"></span>
                            <span style="color: ${isVeg ? '#16a34a' : '#dc2626'};">${dish.food_type}</span>
                        </div>

                        <div class="rating-badge">
                            <i class="bi bi-star-fill"></i> ${dish.rating.toFixed(1)}
                        </div>

                        ${!isAvailable ? '<div class="position-absolute top-0 end-0 bg-dark text-white px-2 py-1 m-2 rounded small fw-bold">Sold Out</div>' : ''}
                    </div>

                    <div class="food-card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <h6 class="food-title">${dish.name}</h6>
                            <span class="badge bg-light text-secondary border small">${dish.category}</span>
                        </div>
                        <p class="food-desc">${dish.description || 'Delicious freshly prepared authentic dish.'}</p>
                        
                        <div class="food-card-footer">
                            <div class="food-price">₹${dish.price.toFixed(0)}</div>
                            
                            ${isAvailable ? `
                                <button type="button" class="btn-add-food" onclick='window.addDishToOrder(${JSON.stringify(dish).replace(/'/g, "&apos;")})'>
                                    <i class="bi bi-plus-lg"></i> ADD +
                                </button>
                            ` : `
                                <button type="button" class="btn btn-sm btn-secondary disabled" disabled>Sold Out</button>
                            `}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Global hook to add dish to order panel
window.addDishToOrder = function(dish) {
    if (window.orderManager) {
        window.orderManager.addItem(dish);
    }
};

// Bind category buttons and search inputs
function bindCatalogFilters() {
    // Category items
    const catItems = document.querySelectorAll('.category-item');
    catItems.forEach(btn => {
        btn.addEventListener('click', () => {
            catItems.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category || 'All Items';
            renderFoods();
        });
    });

    // Search box
    const searchInput = document.getElementById('foodSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.trim();
            renderFoods();
        });
    }

    // Diet radio filters (All, Veg, Non-Veg)
    const dietRadios = document.querySelectorAll('input[name="dietFilter"]');
    dietRadios.forEach(r => {
        r.addEventListener('change', (e) => {
            currentDietFilter = e.target.value;
            renderFoods();
        });
    });
}

function resetFilters() {
    currentCategory = 'All Items';
    currentSearch = '';
    currentDietFilter = 'all';

    const searchInput = document.getElementById('foodSearchInput');
    if (searchInput) searchInput.value = '';

    const allDietRadio = document.getElementById('dietAll');
    if (allDietRadio) allDietRadio.checked = true;

    const catItems = document.querySelectorAll('.category-item');
    catItems.forEach(b => {
        b.classList.toggle('active', b.dataset.category === 'All Items');
    });

    renderFoods();
}

// ADMIN FOOD MANAGEMENT
function bindAdminFoodEvents() {
    const addFoodForm = document.getElementById('adminAddFoodForm');
    if (addFoodForm) {
        addFoodForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = addFoodForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;

            const payload = {
                name: document.getElementById('newFoodName').value.trim(),
                category: document.getElementById('newFoodCategory').value.trim(),
                price: parseFloat(document.getElementById('newFoodPrice').value),
                food_type: document.getElementById('newFoodType').value,
                description: document.getElementById('newFoodDesc').value.trim(),
                image: document.getElementById('newFoodImage').value.trim() || 'idly.jpg',
                rating: parseFloat(document.getElementById('newFoodRating').value) || 4.5,
                is_available: document.getElementById('newFoodAvailable').checked
            };

            try {
                const res = await fetch('/api/foods', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();

                if (res.ok && result.success) {
                    alert('Food item created successfully!');
                    addFoodForm.reset();
                    const modalEl = document.getElementById('addFoodModal');
                    if (modalEl) {
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        if (modal) modal.hide();
                    }
                    loadFoodCatalog();
                } else {
                    alert('Error: ' + (result.error || 'Failed to add food'));
                }
            } catch (err) {
                alert('Connection error with server.');
            } finally {
                submitBtn.disabled = false;
            }
        });
    }
}
