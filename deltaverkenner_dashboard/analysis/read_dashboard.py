from pathlib import Path

import pandas as pd
import numpy as np

watervraag_types = {
    "Peilbeheer": ["p2"],
    "Doorspoeling": ["p4"],
    "Beregening": ["p5"],
    "Totaal": ["p2", "p4", "p5"],
}
months = {
    "April": [4],
    "May": [5],
    "June": [6],
    "July": [7],
    "August": [8],
    "September": [9],
    "October": [10],
    "Summer_half-year": [4, 5, 6, 7, 8, 9],
}


def read_watervraag(
    path, watervraag_type, selected_year=[2003], selected_months="Summer_half-year"
):
    index_col = 0
    nr_of_deelregios = 21

    column_names = []

    for t in watervraag_types[watervraag_type]:
        for i in range(nr_of_deelregios):
            column_names.append(f"{t}_Demand_r{i+1}")

    # add the unnamed index column name to the list of column names
    column_names = ["time"] + column_names

    data = pd.read_csv(path, index_col=index_col, usecols=column_names)

    data.index = pd.to_datetime(data.index)

    data_year = data[data.index.year.isin(selected_year)]

    selected_data = data_year[data_year.index.month.isin(months[selected_months])]

    # average over the time
    selected_data_averages = selected_data.mean(axis=0)

    selected_data_averages = selected_data_averages.to_frame()
    selected_data_averages.columns = ["Watervraag"]

    selected_data_averages["Nummer"] = (
        selected_data_averages.index.str.split("_").str[-1].str.lstrip("r")
    )  # .astype(int)

    if watervraag_type == "Totaal":
        # Extract the shared part (Demand_rX)
        group_key = selected_data_averages.index.str.split("_", n=1).str[1]

        # Group and sum
        result = selected_data_averages.groupby(group_key)["Watervraag"].sum()
        result = result.to_frame()
        result["Nummer"] = (
            result.index.str.split("_").str[-1].str.lstrip("r")
        )  # .astype(int)
        return result

    else:
        return selected_data_averages


if __name__ == "__main__":

    path_to_datafile = Path(
        "p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-results/long/1.csv"
    )

    data = read_watervraag(path_to_datafile, watervraag_type="Peilbeheer")
    # # path_to_datafile = Path(
    # #     "p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-input/demand.xlsx"
    # # )

    # # sheet_name = "BP18REF2017_slr0"

    # # data = read_excel_sheet(path_to_datafile, sheet_name)

    # runs = [1]
    # # runs = np.linspace(1, 21, 21).astype(int)

    # index_col = 0

    # nr_of_deelregios = 21
    # priorities = np.linspace(2, 4, 3).astype(int)
    # # priorities = np.linspace(1, 4, 4).astype(int)
    # types = ["Demand"]  # , "Allocation", "Shortage"]

    # # selected_years = [1976, 2003]
    # selected_year = [2003]
    # selected_months = [4, 5, 6, 7, 8, 9]

    # watervraag_type = "Peilbeheer"

    # column_names = []

    # for t in types:
    #     for i in range(nr_of_deelregios):
    #         column_names.append(f"{watervraag_types[watervraag_type]}_{t}_r{i+1}")

    # # add the unnamed index column name to the list of column names
    # column_names = ["time"] + column_names

    # for run in runs[:2]:

    #     print(f"Working on run {run}")

    #     path_to_datafile = Path(
    #         f"p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-results/long/{run}.csv"
    #     )

    #     data = pd.read_csv(path_to_datafile, index_col=index_col, usecols=column_names)

    #     data.index = pd.to_datetime(data.index)

    #     data_year = data[data.index.year.isin(selected_year)]

    #     selected_data = data_year[data_year.index.month.isin(selected_months)]

    #     # average over the time
    #     selected_data_averages = selected_data.mean(axis=0)

# print("Done!")
