import widget
from flask import Flask
import requests
import time
import sqlite3
import pandas as pd
import threading
import plotly
import json
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
from dash import Dash, dcc, html
import plotly.express as px


# Tworzenie bazy danych
def create_database():
    # Połącz się z bazą danych (lub utwórz ją, jeśli nie istnieje)
    conn = sqlite3.connect('patients.db')

    # Utwórz kursor do wykonywania poleceń SQL
    c = conn.cursor()

    # Patients - sprawdź, czy tabela istnieje
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patients'")
    if c.fetchone():
        print("Table 'patients' exists.")
    else:
        # Tabela nie istnieje, więc ją utwórz
        c.execute('''
            CREATE TABLE patients (
                birthdate TEXT,
                disabled BOOLEAN,
                firstname TEXT,
                id INTEGER,
                lastname TEXT,
                trace_id INTEGER,
                name TEXT,
                anomaly BOOLEAN,
                sensor_id INTEGER,
                sensor_name TEXT,
                sensor_value INTEGER,
                timestamp DATETIME
            )
        ''')
        print("Table 'patients' was created.")

    # Anomalies - sprawdź, czy tabela istnieje
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='anomalies'")
    if c.fetchone():
        print("Table 'anomalies' exists.")
    else:
        # Tabela nie istnieje, więc ją utwórz
        c.execute('''
            CREATE TABLE anomalies (
                birthdate TEXT,
                disabled BOOLEAN,
                firstname TEXT,
                id INTEGER,
                lastname TEXT,
                trace_id INTEGER,
                name TEXT,
                anomaly BOOLEAN,
                sensor_id INTEGER,
                sensor_name TEXT,
                sensor_value INTEGER,
                timestamp DATETIME
            )
        ''')
        print("Table 'anomalies' was created.")

    # Zatwierdź zmiany i zamknij połączenie
    conn.commit()
    conn.close()


# Usuwanie starych danych z bazy danych (tabela patients tylko)
def delete_old_data():
    # Połącz się z bazą danych
    conn = sqlite3.connect('patients.db')

    # Oblicz czas 10 minut temu
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)

    # Usuń stare dane z bazy danych
    c = conn.cursor()
    c.execute("DELETE FROM patients WHERE timestamp < ?", (ten_minutes_ago,))
    conn.commit()

    # Zamknij połączenie z bazą danych
    conn.close()


# Pobieranie danych z API i zapisywanie ich do bazy danych
def fetch_and_store_data():
    # Połącz się z bazą danych
    conn = sqlite3.connect('patients.db')

    # Lista ID pacjentów
    patient_ids = range(1, 7)

    while True:

        time.sleep(0.2)
        # Usuń z bazy dane starsze niż 10 minut
        delete_old_data()

        for patient_id in patient_ids:
            try:
                # Pobierz dane dla pacjenta
                res = requests.get(f'http://tesla.iem.pw.edu.pl:9080/v2/monitor/{patient_id}')
                res.raise_for_status()  # Status dla odpowiedzi różnych od 200

                data = res.json()

                # Konwertuj dane na DataFrame i usuwanie dublujących się lub nieistotnych kolumn
                df1 = pd.json_normalize(data, sep='_')
                df1.rename(columns={'id': 'person_id'}, inplace=True)

                df2 = pd.json_normalize(data['trace'], sep='_')
                df2.drop(columns=['id'], inplace=True)
                df2.rename(columns={'name': 'sname'}, inplace=True)

                df3 = pd.json_normalize(data['trace']['sensors'], sep='_')
                df3.rename(columns={'id': 'sensor_id', 'name': 'sensor_name'}, inplace=True)

                temp_df = pd.concat([df1, df2], axis=1)
                temp_df.rename(columns={'person_id': 'id', 'sname': 'name'}, inplace=True)

                temp_df = pd.concat([temp_df] * len(df3), ignore_index=True)
                temp_df = pd.concat([temp_df, df3], axis=1)
                temp_df.drop(columns=['trace_name', 'sensors', 'trace_sensors', ], inplace=True)
                temp_df.rename(columns={'value': 'sensor_value'}, inplace=True)
                # Dodaj kolumnę timestamp
                temp_df['timestamp'] = pd.Timestamp.now()

                # Zapisz DataFrame do bazy danych patients
                temp_df.to_sql('patients', conn, if_exists='append', index=False)

            except requests.exceptions.RequestException as e:
                # Obsłużenie błędu
                print(f"An error occurred while fetching data for patient {patient_id}: {e}")
                time.sleep(1)
                break

        conn.commit()


# Zapisywanie anomalii w tabeli anomalies
def copy_anomalies():
    # Połącz się z bazą danych
    conn = sqlite3.connect('patients.db')

    while True:
        time.sleep(1)

        # Pobierz listę pacjentów z tabeli patients, którzy mieli anomalie
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT id FROM patients WHERE anomaly = 1")
        patients_with_anomalies = cursor.fetchall()

        for patient_id in patients_with_anomalies:
            # Pobierz czas rozpoczęcia i zakończenia anomalii dla danego pacjenta
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM patients WHERE id = ? AND anomaly = 1",
                           (patient_id[0],))
            anomaly_times = cursor.fetchone()

            # Konwertuj czas rozpoczęcia anomalii na obiekt datetime
            start_time = datetime.strptime(anomaly_times[0].split('.')[0], '%Y-%m-%d %H:%M:%S') - timedelta(seconds=10)

            # Oblicz czas 10 sekund po zakończeniu anomalii
            end_time = datetime.strptime(anomaly_times[1].split('.')[0], '%Y-%m-%d %H:%M:%S') + timedelta(seconds=10)

            # Skopiuj odpowiednie wiersze z tabeli patients do tabeli anomalies
            cursor.execute(
                "INSERT INTO anomalies SELECT * FROM patients WHERE id = ? AND timestamp >= ? AND timestamp <= ? AND anomaly = 1",
                (patient_id[0], start_time, end_time))
            conn.commit()


# Pobieranie aktualnych wartości sensorów dla wybranego pacjenta (do customowego widgetu)
def get_latest_sensor_values(patient_id, one_record=False):
    # Połącz się z bazą danych
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()

    patient_firstname = patient_id.split("_")[1]
    patient_lastname = patient_id.split("_")[0]

    # Pobierz ostatnio dodane wartości sensorów dla wybranego pacjenta
    if one_record:
        cursor.execute(
            "SELECT sensor_name, sensor_value, anomaly, timestamp FROM patients WHERE firstname = ? AND lastname = ? ORDER BY timestamp DESC LIMIT 6",
            (patient_firstname, patient_lastname,))
    else:
        cursor.execute(
            "SELECT sensor_name, sensor_value, anomaly, timestamp FROM patients WHERE firstname = ? AND lastname = ? ORDER BY timestamp DESC ",
            (patient_firstname, patient_lastname,))
    sensor_values = cursor.fetchall()

    # Zamknij połączenie z bazą danych
    cursor.close()
    conn.close()

    # Przekształć wyniki do listy słowników
    sensor_values_list = []
    for row in sensor_values:
        sensor_values_list.append(
            {'sensor_name': row[0], 'sensor_value': row[1], 'anomaly': row[2], 'timestamp': row[3]})

    return sensor_values_list


# Pobieranie listy pacjentów
def get_patient_list():
    # Połącz się z bazą danych
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()

    # Pobierz listę pacjentów z tabeli patients
    cursor.execute(
        "SELECT lastname, firstname, birthdate, disabled, SUM(anomaly) FROM patients GROUP BY lastname, firstname, birthdate, disabled")
    patients = cursor.fetchall()

    # Zamknij połączenie z bazą danych
    cursor.close()
    conn.close()

    return patients


server = Flask(__name__)
app = Dash(__name__, server=server)
create_database()
patients = get_patient_list()

# Wygląd strony głównej
app.layout = html.Div([
    html.Center([html.H1("Patient monitoring system")]),
    html.Center([
        # dropdown menu
        dcc.Dropdown(
            id='patient-dropdown',
            options=(
                    [{'label': 'Choose patient', 'value': 'choose_patient'}] +
                    [{'label': html.B(f'{patient[0]} {patient[1]}'), 'value': f'{patient[0]}_{patient[1]}'}
                     for patient in patients]
            ),
            style={'width': '50%', 'display': 'inline-block'}
        ),
        html.Br(),
        html.Br(), html.Br()
    ], style={'textAlign': 'center'}),
    # Lista pacjentów na stronie głównej
    html.Center([
        html.H1("List of patients"),
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Last Name ", style={'border-right': '1px solid black', 'border-left': '1px solid black'}),
                    html.Th("First Name ", style={'border-right': '1px solid black'}),
                    html.Th("Birthdate ", style={'border-right': '1px solid black'}),
                    html.Th("Disabled ", style={'border-right': '1px solid black'}),
                    html.Th("Anomalies Count ", style={'border-right': '1px solid black'}),
                    html.Br(), html.Br()
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(patient[0]+" ", style={'border-right': '1px solid black', 'border-left': '1px solid black'}),
                    html.Td(patient[1], style={'border-right': '1px solid black'}),
                    html.Td(patient[2], style={'text-align': 'center', 'border-right': '1px solid black'}),
                    html.Td("Yes" if patient[3] == 1 else "No", style={'text-align': 'center', 'border-right': '1px solid black'}),
                    html.Td(patient[4] / 6, style={'text-align': 'center', 'border-right': '1px solid black'}),
                    html.Br()
                ]) for patient in patients
            ])
        ], style={'border-spacing': '10px'})
    ]),
    html.Center([
        dcc.Graph(id='graph'),
        dcc.Interval(id='interval', interval=1 * 1000, n_intervals=0)
    ], className='row'),
    html.Center([dcc.Checklist(
        id='sensor-checklist',
        options=['L0', 'L1', 'L2', 'R0', 'R1', 'R2'],
        value=['L0', 'L1', 'L2'],
        inline=True)
    ]),
    html.Center([
        widget.Widget(
            id='sensor-widget',
            value='my-value',
            label='my-label'
        )
    ]),
    dcc.Store(id='store-chosen-patient', data=[], storage_type='memory')
])


@app.callback(Output('store-chosen-patient', 'data'), Input('patient-dropdown', 'value'))
def store_chosen_patient(value):
    return value


color_dict = {
    'L0': 'rgba(51,85,62, 0.9)',
    'L1': 'rgba(109,144,120, 0.9)',
    'L2': 'rgba(164,193,173, 0.9)',
    'R2': 'rgba(165,171,237, 0.9)',
    'R1': 'rgba(107,116,208, 0.9)',
    'R0': 'rgba(55,66,181, 0.9)'
}


@app.callback(Output('sensor-widget', 'data'),
              Input('store-chosen-patient', 'data'),
              Input('interval', 'n_intervals'))
def update_image(patient_id, n):
    if patient_id is not None:
        return get_latest_sensor_values(patient_id, one_record=True)

@app.callback(Output('graph', 'figure'),
              [Input('interval', 'n_intervals'),
               Input('store-chosen-patient', 'data')],
              Input('sensor-checklist', 'value'))
def update_graph_live(n, chosen_patient, checked_sensor):
    print(checked_sensor)
    print(chosen_patient)
    graph_data = {
        'time': [],
        'sensor': []
    }
    x = []
    y = []
    fig = go.Figure()
    if chosen_patient is not None:
        sensor_list = get_latest_sensor_values(chosen_patient)
        for s in checked_sensor:
            print(s)
            x = [sensor['timestamp'] for sensor in sensor_list if sensor['sensor_name'] == s]
            x_anomalies = [sensor['timestamp'] for sensor in sensor_list if
                           sensor['sensor_name'] == s and sensor['anomaly'] == 1]
            y = [sensor['sensor_value'] for sensor in sensor_list if sensor['sensor_name'] == s]
            y_anomalies = [sensor['sensor_value'] for sensor in sensor_list if
                           sensor['sensor_name'] == s and sensor['anomaly'] == 1]
            fig.add_trace(go.Scatter(
                name='foot pressure ' + s,
                x=x,
                y=y,
                mode='lines+markers',
                line=dict(color=color_dict[s]),
            ))
            fig.add_trace(go.Scatter(
                name='anomaly ' + s,
                x=x_anomalies,
                y=y_anomalies,
                mode='markers',
                marker=dict(color='red'),
            ))

    return fig


if __name__ == '__main__':
    create_database()

    # Rozpocznij działanie funkcji pobierania i zapisywania w tle
    thread = threading.Thread(target=fetch_and_store_data)
    thread.start()
    thread_anomalies = threading.Thread(target=copy_anomalies)
    thread_anomalies.start()

    app.run_server()
