import os
import datetime as datetime
import pandas as pd

# time the code execution
start_time = datetime.datetime.now()

# os.chdir(r"p:/11211541-005-dpzw-pragmaanpak/waterbalances")
os.chdir(r"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard")

loc_input = "data/runs_REF2017owd/3-output/"
loc_output = "data/runs_REF2017owd/4-final-pragmaanpak-dashboards/"

scenarios = ["REF2017owd"]
# scenarios = ['REF2017', 'S2050', 'S2100', 'REF2017VP', 'S2050VP']

years = {
    "S2050owd": range(1911, 2011 + 1),
    "REF2017owd": range(1911, 2011 + 1),
    "REF2017": range(1911, 2011+1),
    "S2050": range(1911, 2011+1),
    "S2100": range(1972, 2003+1),
    "REF2017VP": range(1911, 2011+1),
    "S2050VP": range(1911, 2011+1),
}

waterbalances = ["Tekort", "Vraag", "Levering"]
waterbalance_types = [
    "doorspoeling",
    "doorspoeling_polders",
    "doorspoeling_boezem",
    "peilbeheer",
    "beregening",
    "totaal",
]

regiotype = "deelregios"  # 'hoofdregios'

nr_of_regions = 21  # 6 (is the number for the amount of regios)

for sc in scenarios:

    print(f"Creating dashboard for {sc}")

    dashboard = None

    ## Locatie modelrun opzoeken
    loc_run = f"{loc_input}/{sc}"

    year_range = years[sc]

    for waterbalance in waterbalances:
        for waterbalance_type in waterbalance_types:

            dashboard_wb_type = None

            for year in year_range:

                data = pd.read_csv(
                    rf"{loc_run}/Waterbalans_per_jaar/{waterbalance}_{waterbalance_type}_{sc}_{year}_{regiotype}_hws.csv",
                    index_col=0,
                )

                for nr in range(1, nr_of_regions + 1):
                    data = data.rename(
                        columns={
                            f"Region{nr}": f"{waterbalance}_{waterbalance_type}_{nr}"
                        }
                    )

                if dashboard_wb_type is None:
                    dashboard_wb_type = data
                else:
                    dashboard_wb_type = pd.concat([dashboard_wb_type, data])

            dashboard_wb_type[f"{waterbalance}_{waterbalance_type}_total"] = (
                dashboard_wb_type.sum(axis=1)
            )

            if dashboard is None:
                dashboard = dashboard_wb_type
            else:
                dashboard = pd.concat([dashboard, dashboard_wb_type], axis="columns")

    dashboard.index = pd.to_datetime(dashboard.index, format="mixed")

    dashboard.to_csv(rf"{loc_output}/{sc}/dashboard_{regiotype}_hws.csv")

# %%

end_time = datetime.datetime.now()

elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time.seconds, "Seconds")
