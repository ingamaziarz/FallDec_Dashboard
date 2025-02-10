# FallDec Dashboard

## Introduction
The **FallDec Dashboard** is a comprehensive and user-friendly web application designed for individuals using the **FallDec feet pressure measurement device**. This application enables users to monitor and analyze real-time foot pressure data, identify anomalies, and interact with graphical representations of sensor readings.

## Features
- **Patient List:** Displays essential patient details, including name, birthdate, disability status, and anomaly count.
- **Dropdown Selection:** Users can choose a specific patient from the database for detailed monitoring.
- **Real-time Graphs:** Visualizes foot pressure data using different colors for left and right foot sensors, highlighting anomalies in red.
- **Foot Diagram:** Represents real-time foot pressure distribution using dot sizes and colors corresponding to actual sensor values.
- **Dynamic Filtering:** Users can customize the displayed data by selecting specific pressure points.
- **Automatic Updates:** Data refreshes every second to ensure real-time monitoring.

## Getting Started
### Prerequisites
To run the application, ensure that:
- You have **Python 3** installed.
- Required dependencies from `requirements.txt` are installed.
- Your device is connected to the **EE VPN** (necessary to access the external API providing data).


## Architecture
### Database
- The application uses an **SQLite database (`patients.db`)** with two tables:
  - **`patients`**: Stores patient details.
  - **`anomalies`**: Stores detected anomalies for each patient.

### Data Processing
- The application **retrieves patient data** from an external API and stores it in the database.
- Anomalies are detected in the background and recorded in the `anomalies` table.

### Web Application
- Built using **Flask and Dash** to provide an interactive user interface.
- The **main components** of the UI include:
  - Patient list and selection dropdown.
  - Real-time graph with selectable data filters.
  - Foot diagram dynamically displaying sensor pressure data.
- Uses **Dash callbacks** to update UI components based on user interactions.

### Multithreading
- The application runs data fetching and anomaly detection functions in parallel to ensure a responsive user experience.

## Usage
1. **Select a patient** from the list to view their data.
2. The **real-time graph** and **foot diagram** will update with the latest sensor readings.
3. Use the **checkbox filters** to show or hide specific pressure points on the graph.
4. The **legend** helps interpret different data values.
5. Identified **anomalies appear in red** to highlight abnormal pressure readings.
6. Switch between patients at any time to monitor different data.

## Technologies Used
- **Python 3**
- **Flask** (Backend server)
- **Dash** (Frontend visualization)
- **Plotly** (Graph generation)
- **SQLite** (Database storage)
- **Requests & Pandas** (Data fetching and processing)


## Contributors
- **Konrad Skarżyński**
- **Inga Maziarz**
