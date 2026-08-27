from pathlib import Path

import numpy as np
import pandas as pd

runs = np.linspace(1, 21, 21).astype(int)

index_col = 0

writer = pd.ExcelWriter(
    Path(
        "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/2-output/dashboard/dashboard_2026_data_runs_from_python_QWaal.xlsx"
    )
)

######################################################################
# the inflow door de Waal
######################################################################

print("Working on inflow Rijn")

distributions = ["waal"]
# hier ook even iets als column_names.append([""])

column_names = []

for distribution in distributions:
    column_names.append(f"P0_Distribution_{distribution}")

column_names = ["time"] + column_names

inflow_data_all = pd.DataFrame()

for run in runs:

    print(f"Working on run {run}")

    path_to_datafile = Path(
        f"p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-results/long/{run}.csv"
    )

    data = pd.read_csv(path_to_datafile, index_col=index_col, usecols=column_names)

    data.index = pd.to_datetime(data.index)
    data.columns = [f"Run {run}"]

    inflow_data_all = pd.concat([inflow_data_all, data], axis=1)

inflow_data_all.to_excel(writer, sheet_name="QWaal")

writer.close()