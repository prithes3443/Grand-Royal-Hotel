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

@main_views.route('/dashboard')
@login_required
def dashboard_page():
    return render_template('dashboard.html', user=session)

@main_views.route('/dashboard.html')
@login_required
def dashboard_html():
    return render_template('dashboard.html', user=session)

@main_views.route('/bill-history')
@login_required
def bill_history_page():
    return render_template('bill-history.html', user=session)

@main_views.route('/bill-history.html')
@login_required
def bill_history_html():
    return render_template('bill-history.html', user=session)

@main_views.route('/create-order')
@login_required
def create_order_page():
    return render_template('create-order.html', user=session)

@main_views.route('/create-order.html')
@login_required
def create_order_html():
    return render_template('create-order.html', user=session)
