from pathlib import Path

import pandas as pd


def read_excel_sheet(path: Path, sheet_name: str):

    data = pd.read_excel(path, sheet_name=sheet_name, index_col=0)

    return data


if __name__ == "__main__":
    path_to_datafile = Path(
        "p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-input/demand.xlsx"
    )

    sheet_name = "BP18REF2017_slr0"

    data = read_excel_sheet(path_to_datafile, sheet_name)
