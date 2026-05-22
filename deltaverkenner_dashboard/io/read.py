from pathlib import Path
import re

import pandas as pd
import numpy as np


def read_excel_sheet(path: Path, sheet_name: str):

    data = pd.read_excel(path, sheet_name=sheet_name, index_col=0)

    return data


def replace_region(col):
    match = re.search(r"(r\d+)$", col)
    if match:
        r = match.group(1)
        return col.replace(r, regiokoppeling.get(r, r))
    return col


if __name__ == "__main__":
    # path_to_datafile = Path(
    #     "p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-input/demand.xlsx"
    # )

    # sheet_name = "BP18REF2017_slr0"

    # data = read_excel_sheet(path_to_datafile, sheet_name)

    # runs = [1, 2]
    runs = np.linspace(1, 21, 21).astype(int)

    regiokoppeling = {
        "r10": "h1",
        "r11": "h1",
        "r12": "h1",
        "r13": "h1",
        "r14": "h3",
        "r15": "h3",
        "r16": "h2",
        "r17": "h2",
        "r18": "h2",
        "r19": "h6",
        "r20": "h4",
        "r21": "h4",
        "r1": "h5",
        "r2": "h5",
        "r3": "h5",
        "r4": "h5",
        "r5": "h6",
        "r6": "h6",
        "r7": "h1",
        "r8": "h1",
        "r9": "h1",
    }

    index_col = 0

    nr_of_deelregios = 21
    priorities = np.linspace(2, 5, 4).astype(int)
    # priorities = np.linspace(1, 4, 4).astype(int)
    types = ["Demand", "Allocation", "Shortage"]

    selected_years = [1976, 2003]
    selected_months = [4, 5, 6, 7, 8, 9]

    column_names = []

    for p in priorities:
        for t in types:
            for i in range(nr_of_deelregios):
                column_names.append(f"p{p}_{t}_r{i+1}")

    extra_takken = ["afsluitdijk", "ark", "hij", "lek", "volkerak"]
    # hier ook even iets als column_names.append([""])

    for t in types:
        for extra in extra_takken:
            column_names.append(f"p3_{t}_{extra}")

    # add the unnamed index column name to the list of column names
    column_names = ["time"] + column_names

    writer = pd.ExcelWriter(
        Path(
            "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/2-output/dashboard_2026_data_runs_from_python.xlsx"
        )
    )

    for run in runs:

        print(f"Working on run {run}")

        path_to_datafile = Path(
            f"p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-results/long/{run}.csv"
        )

        data = pd.read_csv(path_to_datafile, index_col=index_col, usecols=column_names)

        data.index = pd.to_datetime(data.index)

        data_year = data[data.index.year.isin(selected_years)]

        selected_data = data_year[data_year.index.month.isin(selected_months)]

        # this needs to be changed to new names
        # replace the deelregio name with the hoofdregio name
        # selected_data.columns = selected_data.columns.str.replace(regiokoppeling)
        # vermoedelijk staat in de regel hieronder het (algemene) AI antwoord ;)
        selected_data.columns = selected_data.columns.map(replace_region)
        # selected_data.columns = pd.Index(
        #     [
        #         "_".join(col.split("_")[:-1]) + "_" + regiokoppeling[col.split("_")[-1]]
        #         for col in selected_data.columns
        #     ]
        # )

        selected_data_grouped = (
            selected_data.T.groupby(by=selected_data.columns).sum().T
        )

        # sheet = writer.sheets[f"Run {run}"]

        # add a column with national values (totals):
        new_cols = {}

        for col in selected_data_grouped.columns:
            parts = col.split("_")
            p = parts[0]  # p1, p2, ...
            metric = parts[1]  # Allocation, Demand, Shortage

            key = f"{p}_{metric}_total"

            new_cols.setdefault(key, []).append(col)

        # Create the aggregated dataframe
        selected_data_grouped_totals = pd.DataFrame(
            {
                new_col: selected_data_grouped[cols].sum(axis=1)
                for new_col, cols in new_cols.items()
            }
        )

        # Optional: merge back into original selected_data_grouped
        selected_data_grouped = pd.concat(
            [selected_data_grouped, selected_data_grouped_totals], axis=1
        )

        selected_data_grouped.to_excel(writer, sheet_name=f"Run {run}")

    ######################################################################
    # the inflow door de Rijn
    ######################################################################

    print("Working on inflow Rijn")

    inflows = ["bovenrijn"]
    # hier ook even iets als column_names.append([""])

    column_names = []

    for inflow in inflows:
        column_names.append(f"P0_Inflow_{inflow}")

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

    inflow_data_all.to_excel(writer, sheet_name="QRijn")

    ######################################################################
    # the inflow door de Maas
    ######################################################################

    print("Working on inflow Maas")

    inflows = ["maas"]
    # hier ook even iets als column_names.append([""])

    column_names = []

    for inflow in inflows:
        column_names.append(f"P0_Inflow_{inflow}")

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

    inflow_data_all.to_excel(writer, sheet_name="QMaas")

    writer.close()
