from flask import Blueprint, jsonify, request
from services import (
    get_statistics,
    get_version_comparison,
    get_slicer_options,
    get_detailed_statistics,
    get_overall_summary,
    get_average_amounts,
    get_due_date_summary,
    get_balance_projection
)

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/analysis/summary', methods=['GET'])
def get_analysis_summary():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    business_type = request.args.get('business_type')
    cooperative_bank = request.args.get('cooperative_bank')
    is_technology_enterprise = request.args.get('is_technology_enterprise')

    # Convert is_technology_enterprise to boolean or None
    if is_technology_enterprise == 'true':
        is_technology_enterprise = True
    elif is_technology_enterprise == 'false':
        is_technology_enterprise = False
    elif is_technology_enterprise == 'N/A':
        is_technology_enterprise = None
    else:
        is_technology_enterprise = None # Default or if not provided
    
    summary_data = get_statistics(
        year=year, 
        month=month, 
        business_type=business_type, 
        cooperative_bank=cooperative_bank, 
        is_technology_enterprise=is_technology_enterprise
    )
    return jsonify(summary_data)

@analysis_bp.route('/compare', methods=['GET'])
def compare():
    ym1 = request.args.get('year_month1')
    ym2 = request.args.get('year_month2')

    if not ym1 or not ym2:
        return jsonify({"error": "Both year_month1 and year_month2 are required"}), 400

    comparison = get_version_comparison(ym1, ym2)
    return jsonify(comparison)

@analysis_bp.route('/slicer-options', methods=['GET'])
def slicer_options():
    options = get_slicer_options()
    return jsonify(options)

@analysis_bp.route('/statistics', methods=['GET'])
def get_statistics_data():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({"error": "Year and month are required"}), 400
    
    stats_data = get_detailed_statistics(year, month)
    return jsonify(stats_data)

@analysis_bp.route('/charts-data', methods=['GET'])
def get_charts_data():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({"error": "Year and month are required"}), 400

    charts_data = get_overall_summary(year, month)
    return jsonify(charts_data)

@analysis_bp.route('/analysis/average_amounts', methods=['GET'])
def get_average_amounts_data():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({"error": "Year and month are required"}), 400

    avg_data = get_average_amounts(year, month)
    return jsonify(avg_data)

@analysis_bp.route('/analysis/due_date_summary', methods=['GET'])
def get_due_date_summary_data():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({"error": "Year and month are required"}), 400

    due_date_data = get_due_date_summary(year, month)
    return jsonify(due_date_data)

@analysis_bp.route('/analysis/balance_projection', methods=['GET'])
def get_balance_projection_data():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({"error": "Year and month are required"}), 400

    projection_data = get_balance_projection(year, month)
    return jsonify(projection_data)
