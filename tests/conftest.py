import pytest
from app import create_app
from config import TestingConfig
from models import db
from models.user import User
from models.food import Food
from models.order import Order
from models.order_item import OrderItem
from models.bill import Bill


class CSRFTestingConfig(TestingConfig):
    """Testing configuration with CSRF explicitly enabled for security tests."""
    WTF_CSRF_ENABLED = True


@pytest.fixture(scope='function')
def app():
    """Create and configure a fresh test application for each test."""
    application = create_app(config_class=TestingConfig)

    with application.app_context():
        db.create_all()

        # Seed test users
        admin_user = User(
            username='admin_tester',
            full_name='Admin Tester',
            role='admin'
        )
        admin_user.set_password('AdminPass123!')

        staff_user = User(
            username='staff_tester',
            full_name='Staff Tester',
            role='staff'
        )
        staff_user.set_password('StaffPass123!')

        db.session.add(admin_user)
        db.session.add(staff_user)

        # Seed test menu items
        dosa = Food(
            name='Test Masala Dosa',
            category='Dosa',
            price=100.00,
            food_type='Veg',
            description='Test Dosa',
            is_available=True,
            rating=4.8
        )
        biryani = Food(
            name='Test Chicken Biryani',
            category='Biryani',
            price=240.00,
            food_type='Non-Veg',
            description='Test Biryani',
            is_available=True,
            rating=4.9
        )
        coffee = Food(
            name='Test Filter Coffee',
            category='Drinks',
            price=40.00,
            food_type='Veg',
            description='Test Coffee',
            is_available=True,
            rating=4.7
        )
        unavailable_dish = Food(
            name='Test Seasonal Halwa',
            category='Desserts',
            price=80.00,
            food_type='Veg',
            description='Unavailable test item',
            is_available=False,
            rating=4.2
        )

        db.session.add(dosa)
        db.session.add(biryani)
        db.session.add(coffee)
        db.session.add(unavailable_dish)
        db.session.commit()

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Unauthenticated test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def admin_client(app):
    """Test client authenticated with administrator privileges."""
    c = app.test_client()
    with c.session_transaction() as sess:
        admin_user = User.query.filter_by(username='admin_tester').first()
        sess['user_id'] = admin_user.id
        sess['username'] = admin_user.username
        sess['full_name'] = admin_user.full_name
        sess['role'] = 'admin'
    return c


@pytest.fixture(scope='function')
def staff_client(app):
    """Test client authenticated with staff privileges."""
    c = app.test_client()
    with c.session_transaction() as sess:
        staff_user = User.query.filter_by(username='staff_tester').first()
        sess['user_id'] = staff_user.id
        sess['username'] = staff_user.username
        sess['full_name'] = staff_user.full_name
        sess['role'] = 'staff'
    return c


@pytest.fixture(scope='function')
def csrf_app():
    """Test app with CSRF protection strictly enabled."""
    application = create_app(config_class=CSRFTestingConfig)
    with application.app_context():
        db.create_all()
        admin_user = User(
            username='admin_csrf',
            full_name='Admin CSRF',
            role='admin'
        )
        admin_user.set_password('AdminPass123!')
        db.session.add(admin_user)
        db.session.commit()

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def csrf_client(csrf_app):
    """Test client with CSRF protection enabled."""
    return csrf_app.test_client()
