import pytest
from models.food import Food


def test_smart_recommendations_with_current_items(staff_client):
    """AI recommendations return relevant pairings based on current cart items."""
    dosa = Food.query.filter_by(name='Test Masala Dosa').first()

    res = staff_client.get(f'/api/ai/recommendations?food_ids={dosa.id}&limit=3')
    assert res.status_code == 200
    data = res.get_json()

    assert data['success'] is True
    assert 'recommendations' in data
    assert len(data['recommendations']) > 0

    first_rec = data['recommendations'][0]
    assert 'food' in first_rec
    assert 'score' in first_rec
    assert 'reason' in first_rec
    # Recommended dish must not be the one already in the cart
    assert first_rec['food']['id'] != dosa.id


def test_smart_recommendations_cold_start_empty_cart(staff_client):
    """When cart is empty, system returns popular baseline crowd-favorites."""
    res = staff_client.get('/api/ai/recommendations?limit=4')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['recommendations']) > 0


def test_demand_forecasting_7_days(staff_client):
    """Time-series demand forecast produces 7-day schedule and kitchen prep guide."""
    res = staff_client.get('/api/ai/forecast?days=7')
    assert res.status_code == 200
    data = res.get_json()

    assert data['success'] is True
    forecast = data['forecast']
    assert forecast['forecast_horizon_days'] == 7
    assert len(forecast['daily_forecast']) == 7
    assert forecast['projected_total_orders'] > 0
    assert forecast['projected_total_revenue'] > 0
    assert len(forecast['tomorrow_kitchen_prep']) > 0

    first_prep = forecast['tomorrow_kitchen_prep'][0]
    assert 'recommended_prep_qty' in first_prep
    assert 'safety_buffer' in first_prep
    assert first_prep['recommended_prep_qty'] >= first_prep['predicted_demand_units']


def test_dynamic_pricing_insights(staff_client):
    """Dynamic pricing returns rush hour detection and bounded pricing suggestions."""
    res = staff_client.get('/api/ai/dynamic-pricing')
    assert res.status_code == 200
    data = res.get_json()

    assert data['success'] is True
    pricing = data['pricing']
    assert 'current_window' in pricing
    assert 'demand_multiplier' in pricing
    assert 'pricing_recommendations' in pricing

    for rec in pricing['pricing_recommendations']:
        # Ensure bounded within +/- 20%
        ratio = rec['suggested_price'] / rec['current_price']
        assert 0.79 <= ratio <= 1.21


def test_menu_engineering_bcg_matrix(staff_client):
    """Menu engineering matrix groups dishes into BCG quadrants."""
    res = staff_client.get('/api/ai/menu-engineering')
    assert res.status_code == 200
    data = res.get_json()

    assert data['success'] is True
    matrix = data['menu_engineering']['matrix']
    assert 'stars' in matrix
    assert 'plowhorses' in matrix
    assert 'puzzles' in matrix
    assert 'dogs' in matrix


def test_ml_model_evaluation_metrics(staff_client):
    """Scikit-Learn ML model evaluation returns R2, MAE, RMSE, and feature importances."""
    res = staff_client.get('/api/ai/model-metrics')
    assert res.status_code == 200
    data = res.get_json()

    assert data['success'] is True
    eval_data = data['model_evaluation']
    assert 'model_name' in eval_data
    assert 'metrics' in eval_data
    metrics = eval_data['metrics']
    assert 'r2_score' in metrics
    assert 'mae' in metrics
    assert 'rmse' in metrics
    assert metrics['r2_score'] > 0
    assert 'feature_importance' in eval_data
    assert len(eval_data['feature_importance']) > 0
