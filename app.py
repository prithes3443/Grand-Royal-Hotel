import os
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_wtf.csrf import CSRFProtect, CSRFError
from config import Config, config_by_name
from models import db
from models.user import User
from models.food import Food
from models.order import Order
from models.order_item import OrderItem
from models.bill import Bill
from models.payment import Payment

from routes.auth import auth_bp
from routes.food import food_bp
from routes.orders import orders_bp
from routes.bills import bills_bp
from routes.dashboard import dashboard_bp
from routes.main_views import main_views
from routes.ai_insights import ai_bp

csrf = CSRFProtect()

def create_app(config_class=None):
    if config_class is None:
        env_name = os.environ.get('FLASK_ENV', 'development').lower()
        config_class = config_by_name.get(env_name, Config)

    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(bills_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(main_views)
    app.register_blueprint(ai_bp)

    # Error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': f'CSRF token validation failed: {error.description}'
            }), 400
        flash('Security validation failed or session expired. Please refresh the page and try again.', 'danger')
        return redirect(url_for('auth.login_page'))

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('login.html', error="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal server error occurred.'}), 500

    # Auto-seed database tables and initial records in non-testing environments
    if not app.config.get('TESTING'):
        with app.app_context():
            try:
                db.create_all()
                ensure_database_schema()
                seed_initial_data()
            except Exception as e:
                print(f"[Warning] Database initialization error: {e}")

    return app

def ensure_database_schema():
    """Ensure any newly added model columns exist in existing database schemas."""
    from sqlalchemy import text, inspect
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        with db.engine.connect() as conn:
            if 'users' in tables:
                cols = [c['name'] for c in inspector.get_columns('users')]
                if 'email' not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(120)"))
                    conn.commit()

            if 'orders' in tables:
                cols = [c['name'] for c in inspector.get_columns('orders')]
                if 'payment_status' not in cols:
                    conn.execute(text("ALTER TABLE orders ADD COLUMN payment_status VARCHAR(50) DEFAULT 'Paid'"))
                    conn.commit()
                if 'service_charge' not in cols:
                    conn.execute(text("ALTER TABLE orders ADD COLUMN service_charge FLOAT DEFAULT 0.0"))
                    conn.commit()
                if 'status' not in cols:
                    conn.execute(text("ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'Completed'"))
                    conn.commit()
                if 'created_by' not in cols:
                    conn.execute(text("ALTER TABLE orders ADD COLUMN created_by VARCHAR(100)"))
                    conn.commit()

            if 'bills' in tables:
                cols = [c['name'] for c in inspector.get_columns('bills')]
                if 'payment_status' not in cols:
                    conn.execute(text("ALTER TABLE bills ADD COLUMN payment_status VARCHAR(50) DEFAULT 'Paid'"))
                    conn.commit()
                if 'service_charge' not in cols:
                    conn.execute(text("ALTER TABLE bills ADD COLUMN service_charge FLOAT DEFAULT 0.0"))
                    conn.commit()
    except Exception as ex:
        print(f"[Notice] Schema verification note: {ex}")


def seed_initial_data():
    """Seed default admin, staff, 38 authentic dishes and sample order if empty."""
    # 1. Seed Users
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            full_name='Restaurant General Manager',
            role='admin'
        )
        admin_user.set_password('admin123')

        staff_user = User(
            username='staff',
            full_name='Front Desk Staff',
            role='staff'
        )
        staff_user.set_password('staff123')

        db.session.add(admin_user)
        db.session.add(staff_user)
        db.session.commit()
        print("[Database] Default users 'admin' and 'staff' created.")

    # 2. Seed Foods
    if Food.query.count() == 0:
        dishes = [
            # Tiffin
            ('Steaming Hot Idly', 'Tiffin', 'Soft, fluffy steamed rice cakes served with sambar and 3 chutneys', 60.00, 'Veg', 'idly.jpg', 4.8),
            ('Crispy Medu Vada', 'Tiffin', 'Deep-fried crispy lentil doughnuts seasoned with pepper and curry leaves', 60.00, 'Veg', 'medu_vada.jpg', 4.7),
            ('Ven Pongal', 'Tiffin', 'Ghee tempered hot rice and moong dal porridge with cashews and peppercorns', 80.00, 'Veg', 'idly.jpg', 4.6),
            ('Poori Masala', 'Tiffin', 'Fluffy deep-fried golden wheat pooris served with spiced potato masala', 85.00, 'Veg', 'samosa.jpg', 4.5),

            # Dosa
            ('Crispy Ghee Roast Dosa', 'Dosa', 'Thin, golden crispy crepe roasted in pure desi ghee served with chutneys', 110.00, 'Veg', 'dosa.jpg', 4.9),
            ('Masala Dosa', 'Dosa', 'Classic crispy crepe folded with spiced potato & onion filling', 100.00, 'Veg', 'dosa.jpg', 4.8),
            ('Onion Rava Dosa', 'Dosa', 'Lacy semolina crepe studded with diced onions, green chilies, and coriander', 120.00, 'Veg', 'dosa.jpg', 4.6),
            ('Paneer Butter Dosa', 'Dosa', 'Rich crispy dosa generously filled with spiced shredded paneer and butter', 150.00, 'Veg', 'dosa.jpg', 4.7),

            # Biryani
            ('Special Chicken Biryani', 'Biryani', 'Aromatic basmati rice cooked with tender marinated chicken pieces and rich spices', 240.00, 'Non-Veg', 'biryani.jpg', 4.9),
            ('Mutton Dum Biryani', 'Biryani', 'Traditional slow-cooked dum biryani with succulent mutton cubes & aromatic herbs', 300.00, 'Non-Veg', 'biryani.jpg', 4.8),
            ('Royal Veg Biryani', 'Biryani', 'Fragrant basmati rice layered with garden-fresh vegetables and saffron essence', 180.00, 'Veg', 'biryani.jpg', 4.5),
            ('Egg Dum Biryani', 'Biryani', 'Flavor-packed dum biryani served with roasted seasoned boiled eggs and gravy', 200.00, 'Non-Veg', 'biryani.jpg', 4.6),

            # Noodles
            ('Chicken Hakka Noodles', 'Noodles', 'Wok-tossed noodles with shredded chicken, crisp cabbage, capsicum and scallions', 190.00, 'Non-Veg', 'noodles.jpg', 4.7),
            ('Veg Hakka Noodles', 'Noodles', 'Stir-fried noodles with fresh julienned vegetables and mild Chinese seasonings', 150.00, 'Veg', 'noodles.jpg', 4.5),
            ('Schezwan Chicken Noodles', 'Noodles', 'Spicy wok-tossed noodles tossed in fiery home-made Schezwan chili paste', 210.00, 'Non-Veg', 'noodles.jpg', 4.8),
            ('Veg Schezwan Noodles', 'Noodles', 'Spicy wok noodles tossed with crunchy vegetables in hot garlic sauce', 170.00, 'Veg', 'noodles.jpg', 4.4),

            # Parotta
            ('Malabar Flaky Parotta', 'Parotta', 'Multi-layered flaky, soft Kerala style parottas served with salna gravy', 80.00, 'Veg', 'parotta.jpg', 4.8),
            ('Veg Kothu Parotta', 'Parotta', 'Shredded flaky parotta stir-fried on a griddle with vegetables and spices', 150.00, 'Veg', 'parotta.jpg', 4.6),
            ('Chicken Kothu Parotta', 'Parotta', 'Iconic street food delicacy: shredded parotta scrambled with eggs, chicken & gravy', 200.00, 'Non-Veg', 'parotta.jpg', 4.9),

            # Samosa
            ('Crispy Punjabi Samosa', 'Samosa', 'Crisp, golden pastry crust stuffed with savory spiced potato and peas filling (2 pcs)', 50.00, 'Veg', 'samosa.jpg', 4.7),
            ('Samosa Chaat', 'Samosa', 'Crushed samosas topped with spicy chole, sweetened yogurt, tamarind and mint chutney', 80.00, 'Veg', 'samosa.jpg', 4.8),

            # Starters
            ('Chicken 65', 'Starters', 'Crispy, deep-fried spicy boneless chicken morsels coated in Southern spices', 170.00, 'Non-Veg', 'chicken65.jpg', 4.8),
            ('Tandoori Chicken (Half)', 'Starters', 'Clay-oven charcoal roasted chicken marinated in yogurt and tandoori masala', 280.00, 'Non-Veg', 'tandoori.jpg', 4.9),
            ('Chicken Lollipop', 'Starters', 'Crisp seasoned winglets tossed in sweet spicy Schezwan sauce with scallions', 220.00, 'Non-Veg', 'chicken65.jpg', 4.7),
            ('Crispy Paneer 65', 'Starters', 'Tender cottage cheese cubes tossed in spicy yogurt batter with curry leaves', 160.00, 'Veg', 'paneer.jpg', 4.6),
            ('Gobi Manchurian Dry', 'Starters', 'Crisp cauliflower florets tossed with garlic, ginger, soya and green chillies', 140.00, 'Veg', 'paneer.jpg', 4.5),

            # Main Course
            ('Paneer Butter Masala', 'Main Course', 'Succulent cottage cheese cubes simmered in a silky, buttery tomato cream gravy', 180.00, 'Veg', 'paneer.jpg', 4.9),
            ('Butter Naan', 'Main Course', 'Soft tandoori leavened flatbread brushed with generous dairy butter', 45.00, 'Veg', 'parotta.jpg', 4.7),
            ('Royal Chicken Curry', 'Main Course', 'Traditional home-style chicken curry infused with roasted aromatic spices', 220.00, 'Non-Veg', 'chicken65.jpg', 4.8),
            ('Chettinad Mutton Curry', 'Main Course', 'Fiery spiced mutton gravy with freshly stone-ground Chettinad spices', 290.00, 'Non-Veg', 'biryani.jpg', 4.7),

            # Rice
            ('Veg Fried Rice', 'Rice', 'Wok-tossed basmati rice with finely chopped garden vegetables and soy sauce', 140.00, 'Veg', 'friedrice.jpg', 4.5),
            ('Egg Fried Rice', 'Rice', 'Fluffy rice tossed with scrambled farm eggs, spring onions, and pepper', 160.00, 'Non-Veg', 'friedrice.jpg', 4.6),
            ('Chicken Fried Rice', 'Rice', 'Classic Asian style fried rice tossed with juicy diced chicken and vegetables', 180.00, 'Non-Veg', 'friedrice.jpg', 4.8),

            # Desserts
            ('Gulab Jamun (2 pcs)', 'Desserts', 'Soft melt-in-mouth milk solids dumplings soaked in rose cardamom sugar syrup', 80.00, 'Veg', 'desserts.jpg', 4.8),
            ('Royal Ice Cream Sundae', 'Desserts', 'Triple scoop ice cream topped with chocolate fudge sauce, nuts and a cherry', 110.00, 'Veg', 'desserts.jpg', 4.7),

            # Drinks
            ('South Indian Filter Coffee', 'Drinks', 'Freshly brewed decoction coffee frothed with creamy hot milk in brass davarah', 40.00, 'Veg', 'coffee.jpg', 4.9),
            ('Masala Chai', 'Drinks', 'Invigorating Indian tea brewed with crushed ginger, cardamom, and whole spices', 35.00, 'Veg', 'coffee.jpg', 4.8),
            ('Fresh Lime Soda', 'Drinks', 'Refreshing chilled sparkling soda mixed with fresh lemon juice and mint', 60.00, 'Veg', 'coffee.jpg', 4.6),
            ('Mango Milkshake', 'Drinks', 'Thick creamy milkshake prepared with sweet Alphonso mango pulp and vanilla ice cream', 120.00, 'Veg', 'desserts.jpg', 4.8),
        ]

        for name, cat, desc, price, ftype, img, rating in dishes:
            food = Food(
                name=name,
                category=cat,
                description=desc,
                price=price,
                food_type=ftype,
                image=img,
                rating=rating,
                is_available=True
            )
            db.session.add(food)
        db.session.commit()
        print(f"[Database] {len(dishes)} authentic food menu items seeded successfully.")

    # 3. Seed Sample Order & Bill
    if Order.query.count() == 0:
        biri = Food.query.filter_by(name='Special Chicken Biryani').first()
        dosa = Food.query.filter_by(name='Crispy Ghee Roast Dosa').first()

        sample_order = Order(
            order_number='ORD-1001',
            customer_name='Ramesh Kumar',
            table_number='Table 4',
            order_type='Dine-In',
            subtotal=590.00,
            discount=59.00,
            gst=26.55,
            grand_total=557.55,
            payment_method='UPI / GPay',
            status='Completed',
            created_by='staff'
        )
        db.session.add(sample_order)
        db.session.flush()

        if biri:
            item1 = OrderItem(order_id=sample_order.id, food_id=biri.id, quantity=2, price=240.0, total=480.0)
            db.session.add(item1)
        if dosa:
            item2 = OrderItem(order_id=sample_order.id, food_id=dosa.id, quantity=1, price=110.0, total=110.0)
            db.session.add(item2)

        sample_bill = Bill(
            bill_number='BILL-1001',
            order_id=sample_order.id,
            customer_name='Ramesh Kumar',
            table_number='Table 4',
            subtotal=590.00,
            discount=59.00,
            gst=26.55,
            grand_total=557.55,
            payment_method='UPI / GPay'
        )
        db.session.add(sample_bill)
        db.session.flush()

        sample_payment = Payment(
            order_id=sample_order.id,
            bill_id=sample_bill.id,
            amount=557.55,
            payment_method='UPI / GPay',
            payment_status='Paid',
            transaction_ref='UPI-TXN-1001-OK'
        )
        db.session.add(sample_payment)
        db.session.commit()
        print("[Database] Sample Order ORD-1001, Bill BILL-1001, and Payment initialized.")

app = create_app()

if __name__ == '__main__':
    import socket
    def find_available_port(preferred_port=5000):
        if 'PORT' in os.environ:
            return int(os.environ['PORT'])
        candidate_ports = [preferred_port, 5050, 8000, 8080, 5001, 5002]
        for p in candidate_ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                try:
                    s.connect(('127.0.0.1', p))
                    # Port is in use
                    continue
                except (ConnectionRefusedError, socket.timeout, OSError):
                    pass
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                    s2.bind(('127.0.0.1', p))
                    return p
            except OSError:
                continue
        return 5050

    port = find_available_port(5000)

    debug_mode = app.config.get('DEBUG', False)
    env_mode = app.config.get('ENV', 'development')
    print(f" Environment : {env_mode.upper()} (Debug: {debug_mode})")
    print(f" CSRF Protect: {app.config.get('WTF_CSRF_ENABLED', True)}")
    print(f"=======================================================")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

