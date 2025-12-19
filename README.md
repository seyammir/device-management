# Device Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Status](https://img.shields.io/badge/Status-Pre--Release-orange)

> **Note:** This project is currently in pre-release. Features are subject to change.

A simple device management system built with Python and Streamlit. This application allows you to manage users, devices, and reservations.

## Features

- **Dashboard**: Overview of system statistics.
- **User Management**: Add, view, and manage users.
- **Device Management**: Track devices and their status.
- **Reservations**: Manage device reservations.

## Features to be Implemented

- **Admin Authentication**
- **Enhanching Database Manager**: Full CRUD operations.
- **Enhanching Models with Validation**.
- **Comprehensiv Unit Tests**: Tests for all model classes and database operations.
- **Improving UI**: Calender view for reservations, statistics for all models, device status management, settings page: data export, backup and restore, . . .
- . . .

## Installation

1. Clone the repository.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application using Streamlit:

```bash
streamlit run main.py
```

## Database

The application uses a JSON-based database. An example database file with initial data can be found at [`assets/db_example/db.json`](assets/db_example/db.json). Copy the file **db.json** and paste it in your **data** folder.

## Screenshots

Screenshots of the application interface are in [assets](assets/screenshots/) folder.

