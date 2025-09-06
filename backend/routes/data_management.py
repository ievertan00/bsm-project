from flask import Blueprint, request, jsonify, send_file
from models import db, BusinessData, DataHistory
from services import (
    import_data_from_excel,
    update_business_data,
    get_all_business_data # Import the enhanced function
)
import pandas as pd
from io import BytesIO
import logging
import re

data_bp = Blueprint('data_bp', __name__)
logger = logging.getLogger(__name__)

def extract_year_month_from_filename(filename):
    # Expected format: sample_data_YYYY-MM.xlsx or YYYY年MM月...
    # Handles sample_data_YYYY-MM.xlsx, sample_data_YYYY_M.xlsx, etc.
    match = re.search(r'_(\d{4})[-_](\d{1,2})\.xlsx?$', filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return year, month

    # Handles YYYY年M月...
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

    # Convert is_technology_enterprise to boolean or None
    if is_technology_enterprise == 'true':
        is_technology_enterprise = True
    elif is_technology_enterprise == 'false':
        is_technology_enterprise = False
    elif is_technology_enterprise == 'N/A':
        is_technology_enterprise = None
    else:
        is_technology_enterprise = None # Default or if not provided

    from flask import Blueprint, request, jsonify, send_file
from models import db, BusinessData, DataHistory
from services import (
    import_data_from_excel,
    update_business_data,
    get_all_business_data # Import the enhanced function
)
import pandas as pd
from io import BytesIO
import logging
import re

data_bp = Blueprint('data_bp', __name__)
logger = logging.getLogger(__name__)

def extract_year_month_from_filename(filename):
    # Expected format: sample_data_YYYY-MM.xlsx or YYYY年MM月...
    # Handles sample_data_YYYY-MM.xlsx, sample_data_YYYY_M.xlsx, etc.
    match = re.search(r'_(\d{4})[-_](\d{1,2})\.xlsx?

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
    logger.debug(f"Received import request. Files: {request.files}, Form: {request.form}")

    if not request.files and not request.form:
        return jsonify({"error": "No file or form data received"}), 400

    # Handle multiple files (batch import)
    # Check if multiple files are sent using the 'files[]' key
    if 'files[]' in request.files and len(request.files.getlist('files[]')) > 0:
        results = []
        for file in request.files.getlist('files[]'): # Iterate directly over the list of files
            logger.debug(f"Processing batch file: {file.filename}")
            if file.filename == '':
                results.append({"filename": file.filename, "status": "failed", "error": "No selected file"})
                continue
            
            try:
                db.session.rollback() # Rollback any pending transaction from previous failed imports
                year, month = extract_year_month_from_filename(file.filename)
                logger.debug(f"Extracted from filename {file.filename}: Year={year}, Month={month}")
                if year is None or month is None:
                    results.append({"filename": file.filename, "status": "failed", "error": "Filename must be in format 'sample_data_YYYY-MM.xlsx'"})
                    continue

                import_data_from_excel(file, year, month)
                results.append({"filename": file.filename, "status": "success", "message": f"Data for {year}-{month} imported successfully"})
            except Exception as e:
                db.session.rollback() # Rollback on error to clear the session
                logger.error(f"Failed to import data from {file.filename}: {e}", exc_info=True)
                results.append({"filename": file.filename, "status": "failed", "error": str(e)})
        
        # Check if all imports were successful
        if all(r['status'] == 'success' for r in results):
            return jsonify({"message": "All files imported successfully", "results": results}), 200
        else:
            return jsonify({"error": "Some files failed to import", "results": results}), 500

    # Handle single file import (either with UI selected year/month or filename extracted)
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        db.session.rollback() # Rollback any pending transaction from previous failed imports
        year = request.form.get('year', type=int)
        month = request.form.get('month', type=int)

        if year is None or month is None:
            # Fallback to filename extraction if year/month not provided via form (e.g., for existing frontend behavior)
            year, month = extract_year_month_from_filename(file.filename)
            if year is None or month is None:
                return jsonify({"error": "For single file import, either provide year/month in form data or use filename format 'sample_data_YYYY-MM.xlsx'"}), 400

        import_data_from_excel(file, year, month)
        return jsonify({"message": f"Data for {year}-{month} imported successfully"}), 200
    except Exception as e:
        db.session.rollback() # Rollback on error to clear the session
        logger.error(f"Failed to import data from {file.filename}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

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
    }), filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return year, month

    # Handles YYYY年M月...
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

    # Convert is_technology_enterprise to boolean or None
    if is_technology_enterprise == 'true':
        is_technology_enterprise = True
    elif is_technology_enterprise == 'false':
        is_technology_enterprise = False
    elif is_technology_enterprise == 'N/A':
        is_technology_enterprise = None
    else:
        is_technology_enterprise = None # Default or if not provided

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
    logger.debug(f"Received import request. Files: {request.files}, Form: {request.form}")

    if not request.files and not request.form:
        return jsonify({"error": "No file or form data received"}), 400

    # Handle multiple files (batch import)
    # Check if multiple files are sent using the 'files[]' key
    if 'files[]' in request.files and len(request.files.getlist('files[]')) > 0:
        results = []
        for file in request.files.getlist('files[]'): # Iterate directly over the list of files
            logger.debug(f"Processing batch file: {file.filename}")
            if file.filename == '':
                results.append({"filename": file.filename, "status": "failed", "error": "No selected file"})
                continue
            
            try:
                db.session.rollback() # Rollback any pending transaction from previous failed imports
                year, month = extract_year_month_from_filename(file.filename)
                logger.debug(f"Extracted from filename {file.filename}: Year={year}, Month={month}")
                if year is None or month is None:
                    results.append({"filename": file.filename, "status": "failed", "error": "Filename must be in format 'sample_data_YYYY-MM.xlsx'"})
                    continue

                import_data_from_excel(file, year, month)
                results.append({"filename": file.filename, "status": "success", "message": f"Data for {year}-{month} imported successfully"})
            except Exception as e:
                db.session.rollback() # Rollback on error to clear the session
                logger.error(f"Failed to import data from {file.filename}: {e}", exc_info=True)
                results.append({"filename": file.filename, "status": "failed", "error": str(e)})
        
        # Check if all imports were successful
        if all(r['status'] == 'success' for r in results):
            return jsonify({"message": "All files imported successfully", "results": results}), 200
        else:
            return jsonify({"error": "Some files failed to import", "results": results}), 500

    # Handle single file import (either with UI selected year/month or filename extracted)
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        db.session.rollback() # Rollback any pending transaction from previous failed imports
        year = request.form.get('year', type=int)
        month = request.form.get('month', type=int)

        if year is None or month is None:
            # Fallback to filename extraction if year/month not provided via form (e.g., for existing frontend behavior)
            year, month = extract_year_month_from_filename(file.filename)
            if year is None or month is None:
                return jsonify({"error": "For single file import, either provide year/month in form data or use filename format 'sample_data_YYYY-MM.xlsx'"}), 400

        import_data_from_excel(file, year, month)
        return jsonify({"message": f"Data for {year}-{month} imported successfully"}), 200
    except Exception as e:
        db.session.rollback() # Rollback on error to clear the session
        logger.error(f"Failed to import data from {file.filename}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

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