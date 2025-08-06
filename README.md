# Business Success Metrics (BSM) Analysis Platform

This is a web-based platform for analyzing and visualizing business success metrics from imported data. It allows users to upload business data from Excel files, view the data, analyze it through a dashboard with various filters, and compare data from different time periods.

## Features

*   **Data Import**: Import business data from Excel files. The backend processes and stores the data in a SQLite database.
*   **Data Visualization**: View data in a table format with pagination and search functionality.
*   **Dashboard**: An interactive dashboard provides a summary of key metrics, including:
    *   Cumulative loan and guarantee amounts.
    *   New companies and loan amounts for the current year.
    *   Number of companies with active loans.
    *   Total loan and guarantee balances.
*   **Data Filtering**: Filter data on the dashboard and data management pages by:
    *   Year and month
    *   Business type
    *   Cooperative bank
    *   Technology enterprise status
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
5.  Run the Flask application:
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
