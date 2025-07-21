from flask import Blueprint, request, jsonify, send_file
from models import db, BusinessData, DataHistory
from services import (
    import_data_from_excel,
    update_business_data
)
import pandas as pd
from io import BytesIO
import logging

data_bp = Blueprint('data_bp', __name__)
logger = logging.getLogger(__name__)

@data_bp.route('/year_months', methods=['GET'])
def get_year_months():
    year_months = db.session.query(BusinessData.year_month).distinct().all()
    return jsonify([ym[0] for ym in year_months])

@data_bp.route('/data', methods=['GET'])
def get_data():
    year_month = request.args.get('year_month') # e.g., '2023-07'
    if not year_month:
        return jsonify({"error": "year_month parameter is required"}), 400

    data = BusinessData.query.filter_by(year_month=year_month).all()
    return jsonify([d.to_dict() for d in data])

@data_bp.route('/data/<int:data_id>', methods=['PUT'])
def update_data(data_id):
    new_data = request.json
    try:
        updated_entry = update_business_data(data_id, new_data)
        return jsonify(updated_entry.to_dict()), 200
    except Exception as e:
        logger.error(f"Error updating data for id {data_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@data_bp.route('/data/<int:data_id>', methods=['DELETE'])
def delete_data(data_id):
    data_entry = BusinessData.query.get(data_id)
    if not data_entry:
        return jsonify({"error": "Data not found"}), 404
    
    DataHistory.query.filter_by(data_id=data_id).delete()

    db.session.delete(data_entry)
    db.session.commit()
    return jsonify({"message": "Data deleted successfully"}), 200

@data_bp.route('/import', methods=['POST'])
def import_excel():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    year_month = request.form.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month is required"}), 400

    try:
        import_data_from_excel(file, year_month)
        return jsonify({"message": "Data imported successfully"}), 200
    except Exception as e:
        logger.error(f"Failed to import data for {year_month} from {file.filename}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@data_bp.route('/export', methods=['GET'])
def export_excel():
    year_month = request.args.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month parameter is required"}), 400

    data = BusinessData.query.filter_by(year_month=year_month).all()
    df = pd.DataFrame([d.to_dict() for d in data])

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    output.seek(0)

    return send_file(
        output, 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True, 
        download_name=f'business_data_{year_month}.xlsx'
    )
