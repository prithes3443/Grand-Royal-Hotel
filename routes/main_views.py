from flask import Blueprint, render_template, session, redirect, url_for
from routes.auth import login_required, admin_required

main_views = Blueprint('main_views', __name__)

@main_views.route('/')
@login_required
def index_page():
    return render_template('index.html', user=session)

@main_views.route('/index.html')
@login_required
def index_html():
    return render_template('index.html', user=session)

@main_views.route('/menu')
@main_views.route('/menu.html')
@login_required
def menu_page():
    return render_template('index.html', user=session)

@main_views.route('/dashboard')
@main_views.route('/dashboard.html')
@login_required
def dashboard_page():
    return render_template('dashboard.html', user=session)

@main_views.route('/bill-history')
@main_views.route('/bill-history.html')
@main_views.route('/billing')
@login_required
def bill_history_page():
    return render_template('bill-history.html', user=session)

@main_views.route('/create-order')
@main_views.route('/create-order.html')
@main_views.route('/orders')
@main_views.route('/orders.html')
@login_required
def create_order_page():
    return render_template('create-order.html', user=session)

@main_views.route('/ai-dashboard')
@main_views.route('/ai-dashboard.html')
@login_required
def ai_dashboard_page():
    return render_template('ai_dashboard.html', user=session)

@main_views.route('/reports')
@main_views.route('/reports.html')
@login_required
def reports_page():
    return render_template('reports.html', user=session)
