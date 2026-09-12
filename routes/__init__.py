from routes.auth import auth_bp
from routes.food import food_bp
from routes.orders import orders_bp
from routes.bills import bills_bp
from routes.dashboard import dashboard_bp
from routes.main_views import main_views

__all__ = ['auth_bp', 'food_bp', 'orders_bp', 'bills_bp', 'dashboard_bp', 'main_views']
