# Business Success Metrics (BSM) Analysis Platform

This is a web-based platform for analyzing and visualizing business success metrics from imported data. It allows users to upload business data from Excel files, view the data, analyze it through a dashboard with various filters, and compare data from different time periods.

## Features

*   **Data Import**: Import business data from Excel files. The backend processes and stores the data in a database.
*   **Data Visualization**: View data in a table format with pagination and search functionality.
*   **Dashboard**: An interactive dashboard provides a summary of key metrics, including:
    *   "累计担保企业数量" (Cumulative Guaranteed Companies)
    *   "累计借款金额（万元）" (Cumulative Loan Amount)
    *   "累计担保金额（万元）" (Cumulative Guarantee Amount)
    *   "本年新增担保企业数量" (New Guaranteed Companies This Year)
    *   "本年新增借款金额（万元）" (New Loan Amount This Year)
    *   "本年新增担保金额（万元）" (New Guarantee Amount This Year)
    *   "月新增担保企业数量" (New Guaranteed Companies This Month)
    *   "月新增借款金额（万元）" (New Loan Amount This Month)
    *   "月新增担保金额（万元）" (New Guarantee Amount This Month)
    *   "在保企业数量" (In-force Companies Count)
    *   "借款余额（万元）" (Loan Balance)
    *   "担保余额（万元）" (Guarantee Balance)
*   **Data Filtering**: Filter data on the dashboard and data management pages by:
    *   Year and month
    *   Business type
    *   Cooperative bank
    *   Technology enterprise status
*   **Chart Analysis**: The dashboard includes a variety of charts to visualize the data:
    *   Business Proportions (Pie Charts)
    *   New Business (Bar Charts)
    *   Averages (Bar Charts)
    *   Due Dates (Bar Charts)
    *   Balance Projection (Line Charts)
*   **Comparison Analysis**: Compare data from two different time periods to see the changes in key metrics.
*   **Data Management**: Edit and delete individual data entries.

## Project Structure

The project is divided into two main parts: a Flask backend and a React frontend.

### Backend

The backend is a Flask application that provides a RESTful API for the frontend.

*   `app.py`: The main entry point for the Flask application.
*   `models.py`: Defines the database schema using SQLAlchemy.
*   `services.py`: Contains the business logic for data processing and analysis.
*   `routes/`: Contains the API endpoints for data management and analysis.
*   `requirements.txt`: Lists the Python dependencies for the backend.

### Frontend

The frontend is a React application that provides the user interface for the platform.

*   `App.js`: The main component that sets up the application's routing.
*   `pages/`: Contains the main pages of the application (Dashboard, Data Management, etc.).
*   `components/`: Contains reusable UI components (e.g., charts, data slicers).
*   `DataContext.js`: A React Context for managing global state.
*   `package.json`: Lists the JavaScript dependencies for the frontend.

## Getting Started

To get the project up and running, you will need to install the dependencies and run both the backend and frontend servers.

### Prerequisites

*   Python 3.x
*   Node.js and npm

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
4.  Install the Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Initialize the database:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```
6.  Run the Flask application:
    ```bash
    python app.py
    ```
    The backend server will start on `http://127.0.0.1:5000`.

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install the JavaScript dependencies:
    ```bash
    npm install
    ```
3.  Run the React application:
    ```bash
    npm start
    ```
    The frontend development server will start on `http://localhost:3000`.

Once both servers are running, you can access the application by opening your web browser and navigating to `http://localhost:3000`.

## API Endpoints

The backend provides the following API endpoints:

*   `GET /api/slicer-options`: Get the options for the data slicers.
*   `GET /api/analysis/summary`: Get the summary statistics for the dashboard.
*   `GET /api/analysis/monthly_growth`: Get the monthly growth statistics for the dashboard.
*   `GET /api/charts-data`: Get the data for the charts on the dashboard.
*   `GET /api/analysis/average_amounts`: Get the average loan and guarantee amounts.
*   `GET /api/analysis/due_date_summary`: Get the summary of due dates.
*   `GET /api/analysis/balance_projection`: Get the balance projection data.
*   `POST /api/import`: Import data from an Excel file.
*   `GET /api/data`: Get the business data with pagination and filtering.
*   `PUT /api/data/<int:id>`: Update a data entry.
*   `DELETE /api/data/<int:id>`: Delete a data entry.