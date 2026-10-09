import pytest
from models.food import Food
from models.order import Order
from models.bill import Bill


def test_unauthenticated_page_access_redirects_to_login(client):
    """Unauthenticated users must be redirected to the login page."""
    protected_urls = ['/', '/dashboard', '/create-order', '/bill-history']
    for url in protected_urls:
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 302
        assert '/login' in res.headers['Location']


def test_unauthenticated_api_endpoints_return_401(client):
    """Unauthenticated API requests must receive 401 Unauthorized."""
    endpoints = [
        ('/api/orders', 'GET'),
        ('/api/orders', 'POST'),
        ('/api/bills', 'GET'),
        ('/api/dashboard', 'GET'),
        ('/api/ai/recommendations', 'GET'),
        ('/api/ai/forecast', 'GET'),
        ('/api/ai/dynamic-pricing', 'GET')
    ]
    for url, method in endpoints:
        if method == 'GET':
            res = client.get(url)
        else:
            res = client.post(url, json={})
        assert res.status_code == 401
        data = res.get_json()
        assert data['success'] is False


def test_staff_cannot_create_food_returns_403(staff_client):
    """Staff member cannot add new dishes to catalog (admin only)."""
    payload = {
        'name': 'Unauthorized Dish',
        'category': 'Starters',
        'price': 150.0,
        'food_type': 'Veg'
    }
    res = staff_client.post('/api/foods', json=payload)
    assert res.status_code == 403
    data = res.get_json()
    assert data['success'] is False
    assert 'Administrator privileges required' in data['error']


def test_staff_cannot_modify_food_returns_403(staff_client):
    """Staff member cannot modify existing dishes."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    res = staff_client.put(f'/api/foods/{dosa.id}', json={'price': 120.0})
    assert res.status_code == 403
    data = res.get_json()
    assert data['success'] is False


def test_staff_cannot_delete_food_returns_403(staff_client):
    """Staff member cannot delete dishes."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    res = staff_client.delete(f'/api/foods/{dosa.id}')
    assert res.status_code == 403
    data = res.get_json()
    assert data['success'] is False


def test_staff_cannot_delete_bill_returns_403(staff_client):
    """Staff member cannot delete customer bills (audit protection)."""
    # Create sample bill first
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    order_res = staff_client.post('/api/orders', json={
        'customer_name': 'Bill Delete Test',
        'table_number': 'Table 1',
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    })
    bill_id = order_res.get_json()['bill']['id']

    # Attempt delete as staff
    res = staff_client.delete(f'/api/bills/{bill_id}')
    assert res.status_code == 403
    data = res.get_json()
    assert data['success'] is False


def test_admin_can_manage_food_catalog(admin_client):
    """Administrator can successfully create, update, and delete food items."""
    # 1. Create Food
    create_res = admin_client.post('/api/foods', json={
        'name': 'Admin Paneer Tikka',
        'category': 'Starters',
        'price': 220.0,
        'food_type': 'Veg',
        'description': 'Clay oven cooked cottage cheese',
        'rating': 4.9
    })
    assert create_res.status_code == 201
    created_id = create_res.get_json()['food']['id']

    # 2. Update Food
    update_res = admin_client.put(f'/api/foods/{created_id}', json={
        'price': 250.0,
        'description': 'Updated recipe'
    })
    assert update_res.status_code == 200
    assert update_res.get_json()['food']['price'] == 250.0

    # 3. Delete Food
    del_res = admin_client.delete(f'/api/foods/{created_id}')
    assert del_res.status_code == 200
    assert del_res.get_json()['success'] is True

    # Verify no longer exists
    get_res = admin_client.get(f'/api/foods/{created_id}')
    assert get_res.status_code == 404


def test_admin_can_delete_bill(admin_client, staff_client):
    """Administrator can delete bills when adjustments/refunds are required."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()
    order_res = staff_client.post('/api/orders', json={
        'customer_name': 'Admin Delete Bill Test',
        'table_number': 'Table 7',
        'items': [{'food_id': dosa.id, 'quantity': 1}]
    })
    bill_id = order_res.get_json()['bill']['id']

    # Admin delete
    del_res = admin_client.delete(f'/api/bills/{bill_id}')
    assert del_res.status_code == 200
    assert del_res.get_json()['success'] is True
