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

watertypes_english = {
    "Vraag": "Demand",
    "Levering": "Allocation",
    "Tekort": "Shortage"
}

priorities = {
    "verdamping": "p1",
    "peilbeheer": "p2",
    "doorspoeling hws" : "p3",
    "doorspoeling": "p4",
    "beregening": "p5",
}

# scenarios = ["S2050owd"]
scenarios = ["REF2017", "S2050", "S2050owd"] # ["S2100"] #] "S2050"# ] #] #, ]


jaren = {
    "S2050owd": range(1911, 2011+1),
    "REF2017": range(1911, 2011+1),
    "S2050": range(1911, 2011+1),
    "S2100": range(1972, 2003+1)
}

regions = {f"Region{i}": f"r{i}" for i in range(1, 9)}

exclude_names = ["totaal", "doorspoeling_boezem", "doorspoeling_polders"]

for sc in scenarios:
    print(f"Working on {sc} scenario")

    filedir = Path(f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/runs_veengebieden/3-output/{sc}/waterbalans_per_jaar/")

    total_df = pd.DataFrame()

    jaar_range = jaren[sc]
    for jaar in jaar_range:
        print(f"Working on {jaar} year")

        files = filedir.glob(f"*{jaar}*.csv")

        df = pd.DataFrame()

        for file in files:
            # print(file.stem)

            if not any(x in file.stem for x in exclude_names):
                # print("in if")
                data = pd.read_csv(file, index_col=0, parse_dates=True)
                priority = file.stem.split("_")[1]
                watertype = file.stem.split("_")[0]

                data.name = file.stem.replace(
                    watertype, watertypes_english[watertype]
                ).replace(priority, priorities[priority]).replace(f"_{sc}_{jaar}_deelregios_hws", "")

                for region in regions:
                    series = data[region]
                    series.name = data.name + '_' + regions[region]

                    if df.empty:
                        df = series.to_frame()
                    else:
                        df = pd.concat([df, series], axis=1, join="inner")

        if total_df.empty:
            total_df = df
        else:
            total_df = pd.concat([total_df, df])

    total_df.columns = [rename_col(c) for c in total_df.columns]

    output_path = Path(f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/runs_veengebieden/4-final/output_{sc}.csv")
    total_df.to_csv(output_path, index_label="time")

end_time = datetime.datetime.now()

elapsed_time = end_time - start_time
print("Script done, elapsed time: ", elapsed_time.seconds, "Seconds")
