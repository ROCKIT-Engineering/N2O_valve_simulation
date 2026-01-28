import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
### Variabls
# Test 3
start_time_stamp = 400
end_time_stamp = 450

T0 = 413.1

old_file_path = r"ethanol\data_raw\16_01_2026\log_Valve_test_3_2026-01-16_17-36-26.csv"
new_file_path = r"ethanol\data_processed\valve_test_3_2026-01-16_17-36-26.csv"
result_file_path = r"ethanol\data_processed\valve_test_3_2026-01-16_17-36-26_results.png"

stepper_revs = [0.05, 0.1, 0.2, 0.3, .4, 0.5, .75, 1, 1.25, 1.5, 2, 2.5, 3, 4]
stepper_sleep_time = 2
stepper_move_time = 0.5

columns = {"timestamp" : "timestamp", "Ethanol Mass": "Ethanol Mass", "Torchy Chamber Pressure": "P1", "Ethanol Tank Pressure": "P2"} # Rename columns and delete unneeded rows

# Injector
Cd = 0.6
A = 1.3129335472274698e-06  # m2, calculated with oilnozzle_converter (1.56e-6 )

rho = 1000  # kg/m3
### Hauptprogramm
df = pd.read_csv(
    old_file_path,
    sep=",",
    decimal="."
)

## Column selection and renaming
df = df[columns.keys()]  # Keep only needed columns
df = df.rename(columns=columns)
## Time selection
df = df[(df["timestamp"] >= start_time_stamp) & (df["timestamp"] <= end_time_stamp)]
## Time reset
df["timestamp"] = df["timestamp"] - T0
## Add stepper position column
df["stepper_position"] = 0
for i in range(len(stepper_revs)):
    mask = (df["timestamp"] >= stepper_sleep_time * i) & (df["timestamp"] < stepper_sleep_time * (i+1))
    df.loc[mask, "stepper_position"] = stepper_revs[i]

## Smoth data
df["P1*"] = df["P1"].rolling(window=50).mean()
df["P2*"] = df["P2"].rolling(window=50).mean()

## Mass flow rate
df["Ethanol Mass Flow - Load Cell"] = savgol_filter(
    df["Ethanol Mass"].values,
    window_length=5001,  # must be odd, increase if very noisy
    polyorder=1,
    deriv=1,
    delta=np.mean(np.diff(df["timestamp"]))
) # chatGPT


## Delta P
df["delta_P*"] = df["P2*"] - df["P1*"]
## Theoretical mass flow rate
df["Ethanol Mass Flow - Delta P"] = - Cd * A * np.sqrt(2 * rho * df["P1*"] * 1e5) * 1000 # g/s

## Mass flow as a function of stepper position
stepper_revs_mass_flow_load_cell = []
stepper_revs_mass_flow_delta_P = []
stepper_revs_delta_P = []
for i in range(len(stepper_revs)):
    time_lower = stepper_sleep_time * i + stepper_move_time / 2
    time_upper = stepper_sleep_time * (i+1) - stepper_move_time / 2
    
    mean_mass_flow = - df[(df["timestamp"] >= time_lower) & (df["timestamp"] <= time_upper)]["Ethanol Mass Flow - Load Cell"].mean()
    stepper_revs_mass_flow_load_cell.append(mean_mass_flow)

    mean_mass_flow = - df[(df["timestamp"] >= time_lower) & (df["timestamp"] <= time_upper)]["Ethanol Mass Flow - Delta P"].mean()
    stepper_revs_mass_flow_delta_P.append(mean_mass_flow)

    delta_P = df[(df["timestamp"] >= time_lower) & (df["timestamp"] <= time_upper)]["delta_P*"].mean()
    stepper_revs_delta_P.append(delta_P)
### Save new data
df.to_csv(new_file_path, index=False)
print(df.head())

# Plt flow rate vs stepper revs
plt.figure()
plt.plot([0] + stepper_revs, [0] + stepper_revs_mass_flow_load_cell, label="Mass Flow - Load Cell")
plt.plot([0] + stepper_revs, [0] + stepper_revs_mass_flow_delta_P, label="Mass Flow - Delta P")
plt.xlabel("rev")
plt.ylabel("Mass Flow (g/s)")
plt.legend()
plt.title("Ethanol Mass Flow Rate")
plt.savefig(result_file_path)
#plt.show()

# Plt theoretical delta P vs stepper revs for set Massflow
water_proportion = 0.30
theoratical_rho = 1 / (water_proportion / 998 + (1 - water_proportion) / 786)  # kg/m3
theoratical_mass_flow = 35  # g/s
theoratical_p0 = 20  # bar
theoratical_p1 = (theoratical_mass_flow / 1000 / (Cd * A))**2 / (2 * theoratical_rho) * 1e-5  + theoratical_p0 # bar
theoratical_p2s = []
print(f"Hochrechnung für {theoratical_mass_flow} g/s bei P0 = {theoratical_p0} bar (Brennkammerdruck) und {water_proportion*100:.0f}% Wasseranteil im IPA")
for rev in [.75, 2, 4]:
    i = stepper_revs.index(rev)
    theoratical_CdA = (stepper_revs_mass_flow_delta_P[i] / 1000) / np.sqrt(2 * rho * stepper_revs_delta_P[i] * 1e5)
    theoratical_p2 = (theoratical_mass_flow / 1000 / theoratical_CdA)**2 / (2 * theoratical_rho) * 1e-5 + theoratical_p1
    theoratical_p2s.append(theoratical_p2)
    print(f"Stepper Revs: {rev}     \tTankdruck: {theoratical_p2:.2f} bar\tDelta P Ventil: {theoratical_p2 - theoratical_p1:.2f} bar\tDelta P Injektor {theoratical_p1 - theoratical_p0:.2f} bar")

from viewer_propulsion_team import run
run()