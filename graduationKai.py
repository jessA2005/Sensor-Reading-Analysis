import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import tkinter as tk
from tkinter import messagebox


class SensorApp:
    def __init__(self, sensor_data):
        self.sensor_data = sensor_data
        self.columns = ['ID', 'Timestamp', 'temperature', 'stress', 'displacement']
        self.df = pd.DataFrame(sensor_data, columns=self.columns)

    def prepare_data(self):
        print(self.df.head())

        dtypes = {
            'temperature': float,
            'stress': float,
            'displacement': float,
        }

        self.df = self.df.astype(dtypes)
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'], format='%Y-%m-%d %H:%M')

        print(self.df.dtypes)

        isMissingValue = self.df.isnull().sum()
        isDublicated = self.df.duplicated().sum()

        self.df = self.timeForML()

        numerical_cols = self.df.select_dtypes(include=np.number).columns.tolist()
        print(numerical_cols)

        if (isMissingValue.sum()):
            print("A missing value found")
            for col in self.columns:
                if self.df[col].isnull().any():
                    if (col in numerical_cols):
                        col_mean = self.df[col].mean()
                        self.df[col].fillna(col_mean, inplace=True)
        else:
            print("No missing value")

        if (isDublicated):
            print("A doublicated value found")
            self.df.drop_duplicates(inplace=True)
        else:
            print("no doublicate found")

        scaler = StandardScaler()
        standard_scaled = self.df.copy()
        scaled = scaler.fit_transform(standard_scaled[numerical_cols])
        print("Scaled Data: ", scaled)

    def timeForML(self):
        self.df['hour'] = self.df['Timestamp'].dt.hour
        self.df['weekDay'] = self.df['Timestamp'].dt.dayofweek
        return self.df

    def computeAverage(self):
        return self.df.groupby('ID').agg(
            avgTemp=('temperature', 'mean'),
            avgStress=('stress', 'mean'),
            avgDisp=('displacement', 'mean')
        ).reset_index()

    def identifySensorMaxAvgStress(self):
        avgComputations = self.computeAverage()
        maxAvgStressSensor = avgComputations.loc[avgComputations['avgStress'].idxmax(), 'ID']
        print(f'Max Avg Stress sensor: {maxAvgStressSensor}')
        messagebox.showinfo("Max Avg Stress", f"Sensor: {maxAvgStressSensor}")

    def filterSensorReadings(self):
        filtered = self.df[self.df['temperature'] > 36.0]
        print(f"Sensor Readings of temperatures > 36.0°C:\n {filtered}")
        messagebox.showinfo("Temp > 36°C", filtered[['ID', 'Timestamp', 'temperature']].to_string(index=False))

    def variablesOverTimeVisual(self, variable):
        self.df.sort_values(by=['Timestamp'])

        plt.figure(figsize=(10, 6))
        for sid in self.df['ID'].unique():
            perSensor = self.df[self.df['ID'] == sid]
            plt.plot(perSensor['Timestamp'], perSensor[variable], marker='o', label=f'Sensor {sid}')

        plt.xlabel('Time (day & hour)')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel(variable)
        plt.title(f'{variable} vs Time per sensor')
        plt.tight_layout()
        plt.legend()
        plt.grid(True)
        plt.show()

    def runAll(self):
        self.prepare_data()
        avgComputations = self.computeAverage()
        for index, sensor in avgComputations.iterrows():
            print(f'ID: {sensor["ID"]}, avgTemp: {sensor["avgTemp"]}, avgStress: {sensor["avgStress"]}, avgDisp: {sensor["avgDisp"]}')


# ---------------- GUI ----------------
sensor_data = [
    ("S1", "2025-04-28 10:00", 35.2, 12.1, 0.002),
    ("S2", "2025-04-28 10:00", 36.5, 14.0, 0.003),
    ("S1", "2025-04-28 11:00", 36.1, 12.5, 0.0021),
    ("S3", "2025-04-28 10:00", 34.0, 11.8, 0.0025),
    ("S2", "2025-04-28 11:00", 37.2, 14.3, 0.0031),
    ("S1", "2025-04-28 12:00", 37.0, 13.0, 0.0022),
]

app = SensorApp(sensor_data)

root = tk.Tk()
root.title("Sensor App GUI")

tk.Button(root, text="1. Prepare Data", command=app.prepare_data).pack(pady=5)
tk.Button(root, text="2. Compute Averages", command=lambda: [print(f'ID: {s["ID"]}, avgTemp: {s["avgTemp"]}, avgStress: {s["avgStress"]}, avgDisp: {s["avgDisp"]}') for _, s in app.computeAverage().iterrows()]).pack(pady=5)
tk.Button(root, text="3. Max Avg Stress Sensor", command=app.identifySensorMaxAvgStress).pack(pady=5)
tk.Button(root, text="4. Temp > 36°C", command=app.filterSensorReadings).pack(pady=5)
tk.Label(root, text="5. Plot Variable").pack()
tk.Button(root, text="Plot Stress", command=lambda: app.variablesOverTimeVisual("stress")).pack(pady=2)
tk.Button(root, text="Plot Temperature", command=lambda: app.variablesOverTimeVisual("temperature")).pack(pady=2)
tk.Button(root, text="Plot Displacement", command=lambda: app.variablesOverTimeVisual("displacement")).pack(pady=2)

root.mainloop()
