import glob
from pathlib import Path
import datetime as datetime

import pandas as pd


def rename_col(col):
    parts = col.split("_")
    if len(parts) == 3:
        return f"{parts[1]}_{parts[0]}_{parts[2]}"
    return col

start_time = datetime.datetime.now()

filedir = Path("p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/runs_2018/3-output/")
files = filedir.glob("*.csv")

watertypes_english = {
    "Vraag": "Demand",
    "Levering": "Allocation",
    "Tekort": "Shortage"
}

priorities = {
    "verdamping": "p1",
    "peilbeheer": "p2",
    "doorspoeling" : "p3",
    "doorspoeling regionaal": "p4",
    "beregening": "p5",
}

regions = {f"Region{i}": f"r{i}" for i in range(1, 22)}

exclude_names = ["totaal", "doorspoeling_boezem", "doorspoeling_polders"]

df = pd.DataFrame()

for file in files:
    print(file.stem)

    if not any(x in file.stem for x in exclude_names):
        print("in if")
        data = pd.read_csv(file, index_col=0, parse_dates=True)
        priority = file.stem.split("_")[1]
        watertype = file.stem.split("_")[0]

        data.name = file.stem.replace(
            watertype, watertypes_english[watertype]
        ).replace(priority, priorities[priority]).replace("_deelregios_hws", "")

        for region in regions:
            series = data[region]
            series.name = data.name + '_' + regions[region]

            if df.empty:
                df = series.to_frame()
            else:
                df = pd.concat([df, series], axis=1, join="inner")

df.columns = [rename_col(c) for c in df.columns]

output_path = Path("p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/runs_2018/4-final/output_2018_run.csv")
df.to_csv(output_path, index_label="time")

end_time = datetime.datetime.now()

elapsed_time = end_time - start_time
print("Script done, elapsed time: ", elapsed_time.seconds, "Seconds")
