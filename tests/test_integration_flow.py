import pytest
from models.user import User
from models.food import Food
from models.order import Order
from models.bill import Bill


def test_integration_registration_and_login(client):
    """Integration flow: User registers a new account, then successfully logs in."""
    # 1. Register new staff user
    reg_payload = {
        'username': 'new_chef',
        'full_name': 'Head Chef Suresh',
        'email': 'suresh@grandroyal.com',
        'password': 'SecretPassword123!',
        'role': 'staff'
    }
    reg_res = client.post('/register', json=reg_payload)
    assert reg_res.status_code == 201
    assert reg_res.get_json()['success'] is True

    # 2. Login with registered credentials
    login_res = client.post('/login', json={
        'username': 'new_chef',
        'password': 'SecretPassword123!'
    })
    assert login_res.status_code == 200
    assert login_res.get_json()['success'] is True
    assert login_res.get_json()['user']['username'] == 'new_chef'


def test_integration_duplicate_registration_rejected(client):
    """Duplicate username or email must be rejected with 409 Conflict."""
    reg_payload = {
        'username': 'staff_tester',  # Already exists in conftest seed
        'full_name': 'Duplicate Person',
        'email': 'duplicate@grandroyal.com',
        'password': 'Password123!'
    }
    res = client.post('/register', json=reg_payload)
    assert res.status_code == 409
    assert res.get_json()['success'] is False


def test_integration_admin_user_management(admin_client):
    """Integration flow: Admin creates a new staff account, lists users, and deletes account."""
    # 1. Admin creates user
    create_res = admin_client.post('/api/users', json={
        'username': 'waiter_ramu',
        'full_name': 'Ramu Waiter',
        'email': 'ramu@grandroyal.com',
        'password': 'WaiterPass123!',
        'role': 'staff'
    })
    assert create_res.status_code == 201
    new_user_id = create_res.get_json()['user']['id']

    # 2. Admin lists users
    list_res = admin_client.get('/api/users')
    assert list_res.status_code == 200
    users = list_res.get_json()['users']
    assert any(u['username'] == 'waiter_ramu' for u in users)

    # 3. Admin deletes user
    del_res = admin_client.delete(f'/api/users/{new_user_id}')
    assert del_res.status_code == 200
    assert del_res.get_json()['success'] is True


def test_integration_reports_and_csv_export(staff_client):
    """Integration flow: Generate order, verify reports summary and CSV download."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()

    # Create order
    staff_client.post('/api/orders', json={
        'customer_name': 'Report Test Customer',
        'table_number': 'Table 10',
        'payment_method': 'UPI / GPay',
        'discount_pct': 0,
        'items': [{'food_id': dosa.id, 'quantity': 2}]
    })

    # Fetch reports data
    rep_res = staff_client.get('/api/reports?range=all')
    assert rep_res.status_code == 200
    data = rep_res.get_json()
    assert data['success'] is True
    assert data['summary']['total_orders'] >= 1
    assert data['summary']['total_revenue'] >= 210.00
    assert len(data['payment_breakdown']) > 0

    # Fetch CSV export
    csv_res = staff_client.get('/api/reports/export-csv')
    assert csv_res.status_code == 200
    assert 'text/csv' in csv_res.headers['Content-Type']
    csv_text = csv_res.get_data(as_text=True)
    assert 'Report Test Customer' in csv_text
    assert 'Order Number' in csv_text
