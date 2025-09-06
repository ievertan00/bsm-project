from flask import Blueprint, request, jsonify, send_file
from models import db, BusinessData, DataHistory
from services import (
    import_data_from_excel,
    update_business_data,
    get_all_business_data
)
import pandas as pd
from io import BytesIO
import logging
import re

data_bp = Blueprint('data_bp', __name__)
logger = logging.getLogger(__name__)

def extract_year_month_from_filename(filename):
    match = re.search(r'_(\d{4})[-_](\d{1,2})\.xlsx?$', filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return year, month

    match = re.search(r'(\d{4})年(\d{1,2})月', filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return year, month

    return None, None

@data_bp.route('/data', methods=['GET'])
def get_data():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    company_name = request.args.get('company_name')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    business_type = request.args.get('business_type')
    cooperative_bank = request.args.get('cooperative_bank')
    is_technology_enterprise = request.args.get('is_technology_enterprise')

    if is_technology_enterprise == 'true':
        is_technology_enterprise = True
    elif is_technology_enterprise == 'false':
        is_technology_enterprise = False
    else:
        is_technology_enterprise = None

    data_response = get_all_business_data(
        page=page, 
        per_page=per_page, 
        company_name=company_name, 
        year=year, 
        month=month,
        business_type=business_type,
        cooperative_bank=cooperative_bank,
        is_technology_enterprise=is_technology_enterprise
    )

    return jsonify(data_response)

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
    logger.info(f"Import request received. Files: {list(request.files.keys())}, Form: {request.form}")

    # --- Single File Import Logic ---
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        try:
            year = request.form.get('year', type=int)
            month = request.form.get('month', type=int)
            logger.info(f"Single import for Year: {year}, Month: {month}")

            if not year or not month:
                return jsonify({"error": "Year and month are required for single file import."}), 400

            import_data_from_excel(file, year, month)
            return jsonify({"message": f"Data for {year}-{month} imported successfully"}), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to import data from {file.filename}: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    # --- Batch File Import Logic ---
    elif 'files[]' in request.files:
        files = request.files.getlist('files[]')
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected for batch import"}), 400

        results = []
        for file in files:
            filename = file.filename
            year, month = extract_year_month_from_filename(filename)
            logger.info(f"Batch import for {filename}. Extracted Year: {year}, Month: {month}")

            if not year or not month:
                results.append({"filename": filename, "status": "failed", "message": "Could not extract year and month from filename."})
                continue
            
            try:
                # Use a nested transaction for each file
                db.session.begin_nested()
                import_data_from_excel(file, year, month)
                db.session.commit()
                results.append({"filename": filename, "status": "success", "message": f"Data for {year}-{month} imported successfully"})
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to import data from {filename}: {e}", exc_info=True)
                results.append({"filename": filename, "status": "failed", "message": str(e)})
        
        failed_count = sum(1 for r in results if r['status'] == 'failed')
        if failed_count > 0:
            return jsonify({"error": f"{failed_count} files failed to import.", "results": results}), 500
        else:
            return jsonify({"message": "All files imported successfully.", "results": results}), 200

    return jsonify({"error": "Invalid import request. No 'file' or 'files[]' part found."}), 400


@data_bp.route('/export', methods=['GET'])
def export_excel():
    data = BusinessData.query.all()
    df = pd.DataFrame([d.to_dict() for d in data])

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Business Data')
    writer.close()
    output.seek(0)

    return send_file(
        output, 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True, 
        download_name='business_data_export.xlsx'
    )

@data_bp.route('/available-dates', methods=['GET'])
def get_available_dates():
    years = db.session.query(BusinessData.snapshot_year).distinct().order_by(BusinessData.snapshot_year).all()
    months = db.session.query(BusinessData.snapshot_year, BusinessData.snapshot_month).distinct().order_by(BusinessData.snapshot_year, BusinessData.snapshot_month).all()
    
    return jsonify({
        'years': sorted([y[0] for y in years]),
        'months': [{'year': m[0], 'month': m[1]} for m in months]
    })
