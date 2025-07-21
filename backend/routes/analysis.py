from flask import Blueprint, request, jsonify
from services import (
    get_statistics,
    get_data_history,
    get_version_comparison
)

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/statistics', methods=['GET'])
def statistics():
    year_month = request.args.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month parameter is required"}), 400
    
    stats = get_statistics(year_month)
    return jsonify(stats)

@analysis_bp.route('/history/<int:data_id>', methods=['GET'])
def history(data_id):
    history_records = get_data_history(data_id)
    return jsonify(history_records)

@analysis_bp.route('/compare', methods=['GET'])
def compare():
    ym1 = request.args.get('year_month1')
    ym2 = request.args.get('year_month2')

    if not ym1 or not ym2:
        return jsonify({"error": "Both year_month1 and year_month2 are required"}), 400

    comparison = get_version_comparison(ym1, ym2)
    return jsonify(comparison)
