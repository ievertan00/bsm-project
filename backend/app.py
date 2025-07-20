
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from models import db, BusinessData, DataHistory
from services import (
    import_data_from_excel,
    get_statistics,
    get_data_history,
    get_version_comparison
)
import pandas as pd
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/business_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def create_tables():
    # The first request to the application will create the database and tables.
    if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')):
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'))
    db.create_all()

@app.route('/api/year_months', methods=['GET'])
def get_year_months():
    year_months = db.session.query(BusinessData.year_month).distinct().all()
    return jsonify([ym[0] for ym in year_months])

@app.route('/api/data', methods=['GET'])
def get_data():
    year_month = request.args.get('year_month') # e.g., '2023-07'
    if not year_month:
        return jsonify({"error": "year_month parameter is required"}), 400

    data = BusinessData.query.filter_by(year_month=year_month).all()
    return jsonify([d.to_dict() for d in data])

@app.route('/api/data/<int:data_id>', methods=['PUT'])
def update_data(data_id):
    new_data = request.json
    try:
        updated_entry = update_business_data(data_id, new_data)
        return jsonify(updated_entry.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/import', methods=['POST'])
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
        return jsonify({"error": str(e)}), 500

@app.route('/api/export', methods=['GET'])
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

@app.route('/api/statistics', methods=['GET'])
def statistics():
    year_month = request.args.get('year_month')
    if not year_month:
        return jsonify({"error": "year_month parameter is required"}), 400
    
    stats = get_statistics(year_month)
    return jsonify(stats)

@app.route('/api/history/<int:data_id>', methods=['GET'])
def history(data_id):
    history_records = get_data_history(data_id)
    return jsonify(history_records)

@app.route('/api/compare', methods=['GET'])
def compare():
    ym1 = request.args.get('year_month1')
    ym2 = request.args.get('year_month2')

    if not ym1 or not ym2:
        return jsonify({"error": "Both year_month1 and year_month2 are required"}), 400

    comparison = get_version_comparison(ym1, ym2)
    return jsonify(comparison)

if __name__ == '__main__':
    app.run(debug=True)
