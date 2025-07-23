from flask import Blueprint, jsonify, request
from services import (
    get_statistics,
    get_data_history,
    get_version_comparison
)

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/analysis/summary', methods=['GET'])
def get_analysis_summary():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    summary_data = get_statistics(year=year, month=month)
    return jsonify(summary_data)

@analysis_bp.route('/compare', methods=['GET'])
def compare():
    ym1 = request.args.get('year_month1')
    ym2 = request.args.get('year_month2')

    if not ym1 or not ym2:
        return jsonify({"error": "Both year_month1 and year_month2 are required"}), 400

    comparison = get_version_comparison(ym1, ym2)
    return jsonify(comparison)