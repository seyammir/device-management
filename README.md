# Device Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-red.svg)

A comprehensive device management system built with Python and Streamlit. This application allows you to manage users, devices, reservations, and maintenance schedules with a modern, theme-aware UI.

## Features

### 📊 Dashboard
- System statistics overview with metrics
- Device status and maintenance alerts
- Recent reservations view
- Maintenance schedule tracking
- Cost analysis with charts

### 👥 User Management
- Full CRUD operations (Create, Read, Update, Delete)
- Search and filter by name, email, department, status
- Export to CSV/JSON
- Email validation

### 🔧 Device Management
- Complete device lifecycle tracking
- Maintenance scheduling and alerts
- Status management (active, maintenance, retired)
- Location and tag support
- Cost tracking per device
- Overdue/upcoming maintenance indicators

### 📅 Reservations
- Device booking with conflict detection
- Time slot availability checking
- Weekly calendar view
- Reservation status management
- Purpose and notes tracking

### 🛠️ Technical Features
- **Validation**: All models include comprehensive validation
- **Theme Support**: UI adapts to light/dark mode
- **Export**: CSV and JSON export for all data
- **Logging**: Rotating file logging for debugging
- **Unit Tests**: 83 tests covering models, database, and utilities
- **Type Safety**: TypedDict for API return types

## Project Structure

```
device-management/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── data/
│   └── db.json            # TinyDB database
├── src/
│   ├── core/
│   │   ├── config.py      # Application configuration
│   │   ├── logger.py      # Logging setup
│   │   └── utils.py       # Utility functions
│   ├── database/
│   │   └── db_manager.py  # Database operations
│   ├── models/
│   │   ├── device.py      # Device model
│   │   ├── user.py        # User model
│   │   └── reservation.py # Reservation model
│   └── ui/
│       ├── components.py  # Shared UI components
│       ├── dashboard_ui.py
│       ├── devices_ui.py
│       ├── users_ui.py
│       └── reservations_ui.py
├── tests/
│   ├── conftest.py        # Test fixtures
│   ├── test_user.py
│   ├── test_device.py
│   ├── test_reservation.py
│   ├── test_db_manager.py
│   └── test_utils.py
└── logs/                   # Application logs
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd device-management
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application using Streamlit:

```bash
streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`.

## Running Tests

Execute the test suite with pytest:

```bash
python -m pytest tests/ -v
```

## Database

The application uses TinyDB, a lightweight JSON-based database. The database file is located at `data/db.json`.

An example database with sample data can be found at [`assets/db_example/db.json`](assets/db_example/db.json). Copy this file to your `data/` folder to get started with sample data.

## Configuration

Application settings can be modified in `src/core/config.py`:
- Database path
- Date/time formats
- Maintenance warning thresholds
- Device statuses and reservation statuses
- Logging configuration

## Screenshots

Screenshots of the application interface are available in the [assets/screenshots/](assets/screenshots/) folder.

## Future Enhancements

- Admin authentication and authorization
- Email notifications for maintenance
- Backup and restore functionality
- Advanced reporting and analytics
- Mobile-responsive design improvements

