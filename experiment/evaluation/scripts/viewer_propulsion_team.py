import os
import csv
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go

CSV_FILE = r"data\ethanol\valve_test_3_2026-01-16_17-36-26.csv"

if not os.path.isfile(CSV_FILE):
    raise FileNotFoundError(f"Datei nicht gefunden:\n{CSV_FILE}")

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)

    data = {col: [] for col in header}
    for row in reader:
        for col, val in zip(header, row):
            try:
                data[col].append(float(val))
            except ValueError:
                data[col].append(float("nan"))  # Falls leere Werte vorkommen

#Timestamp-Spalte bestimmen
timestamp_col = None
for col in header:
    if col.lower() == "timestamp":
        timestamp_col = col
        break

if timestamp_col is None:
    raise ValueError("Keine 'timestamp'-Spalte in der CSV gefunden!")

timestamps = data[timestamp_col]

# Messkanäle außer Timestamp
channels = [c for c in header if c != timestamp_col]

# ====================================
#Dash-App
# ====================================
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Propulsion Team Daten ", style={"textAlign": "center"}),

    html.Label("Sensor/Sensoren:"),
    dcc.Dropdown(
        id="channel-select",
        options=[{"label": c, "value": c} for c in channels],
        value=[channels[0]],         # Standard: Liste!
        multi=True,                 # 👉 MEHRFACH-AUSWAHL
        clearable=False
    ),

    html.Div([
        html.Label("Y-Min:"),
        dcc.Input(id="y-min", type="number", placeholder="Auto", style={"marginRight": "20px"}),

        html.Label("Y-Max:"),
        dcc.Input(id="y-max", type="number", placeholder="Auto"),
    ], style={"margin": "10px"}),

    dcc.Graph(id="plot", style={"height": "80vh"})
])


# ====================================
#Update-Funktion für den Plot
# ====================================
@app.callback(
    Output("plot", "figure"),
    Input("channel-select", "value"),
    Input("y-min", "value"),
    Input("y-max", "value")
)
def update_plot(selected_channels, y_min, y_max):

    fig = go.Figure()

    # Falls nur ein Element ausgewählt wurde → Liste daraus machen
    if isinstance(selected_channels, str):
        selected_channels = [selected_channels]

    # Alle ausgewählten Sensoren plotten
    for channel in selected_channels:
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=data[channel],
            mode="lines",
            name=channel
        ))

    # Achsen anpassen
    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="Sensorwerte",
        hovermode="x unified"
    )

    # Manuelle Y-Skalierung falls angegeben
    yaxis_settings = {}
    if y_min is not None:
        yaxis_settings["range"] = [y_min, y_max if y_max is not None else max(data[selected_channels[0]])]

    if y_max is not None and y_min is None:
        yaxis_settings["range"] = [min(data[selected_channels[0]]), y_max]

    if yaxis_settings:
        fig.update_yaxes(**yaxis_settings)

    return fig


# ====================================
#App starten
# ====================================
def run():
    print("Starte Dashboard → öffne: http://127.0.0.1:8050/")
    app.run(debug=True)

if __name__ == "__main__":
    run()