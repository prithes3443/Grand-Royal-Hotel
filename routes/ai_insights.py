"""
Routes for AI & Data Science Module:
- /api/ai/recommendations (Market Basket Analysis & Smart Pairing)
- /api/ai/forecast (Time-Series Demand & Kitchen Prep Forecasting)
- /api/ai/dynamic-pricing (Peak Hours & Elasticity Optimization)
- /api/ai/menu-engineering (Kasavana & Smith BCG Matrix)
"""

from flask import Blueprint, request, jsonify
from routes.auth import login_required
from services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/api/ai/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Returns AI-generated complementary dish recommendations for the current cart/table order."""
    food_ids_param = request.args.get('food_ids', '').strip()
    limit = int(request.args.get('limit', 4))
    
    current_food_ids = []
    if food_ids_param:
        for fid in food_ids_param.split(','):
            fid = fid.strip()
            if fid.isdigit():
                current_food_ids.append(int(fid))
                
    recommendations = AIService.get_smart_recommendations(current_food_ids=current_food_ids, top_n=limit)
    return jsonify({
        'success': True,
        'count': len(recommendations),
        'recommendations': recommendations
    })

@ai_bp.route('/api/ai/forecast', methods=['GET'])
@login_required
def get_demand_forecast():
    """Returns time-series demand forecasting and kitchen preparation targets."""
    days = int(request.args.get('days', 7))
    if days < 1:
        days = 1
    if days > 30:
        days = 30
        
    forecast_data = AIService.forecast_demand(days_ahead=days)
    return jsonify({
        'success': True,
        'forecast': forecast_data
    })

@ai_bp.route('/api/ai/dynamic-pricing', methods=['GET'])
@login_required
def get_dynamic_pricing():
    """Returns real-time dynamic pricing suggestions based on dining rush windows and elasticity."""
    pricing_data = AIService.get_dynamic_pricing_insights()
    return jsonify({
        'success': True,
        'pricing': pricing_data
    })

@ai_bp.route('/api/ai/menu-engineering', methods=['GET'])
@login_required
def get_menu_engineering():
    """Returns BCG menu matrix segmentation (Stars, Plowhorses, Puzzles, Dogs)."""
    matrix_data = AIService.get_menu_engineering_matrix()
    return jsonify({
        'success': True,
        'menu_engineering': matrix_data
    })

@ai_bp.route('/api/ai/model-metrics', methods=['GET'])
@login_required
def get_model_metrics():
    """Returns Machine Learning model training, evaluation metrics (R2, MAE, RMSE), and feature weights."""
    evaluation_data = AIService.get_ml_model_evaluation()
    return jsonify({
        'success': True,
        'model_evaluation': evaluation_data
    })
