"""
Janneke Pouwels, 12-10-2023
Project: Waterbalans

Vervolg:
Jesse Reusen, 19-05-2026
Project: Deltaverkenner

Doel script: De DM uitvoer (mpx) samenvoegen voor alle jaren


Opmerkingen
    - Een eerdere versie van dit script is te vinden op de volgende locatie: p:/11211541-005-dpzw-pragmaanpak/waterbalances/src/1-prepare/07_Mozart_uitvoer_samenvoegen_jesse.py
"""

import os
import pandas as pd
from mozart import read_mzbalance


# %%
##-------------------------------------------
## 1. INVOER, PARAMETERS en UITVOER
##-------------------------------------------

# os.chdir(r"p:\11210323-005-herijkingrisicos")
# os.chdir(r"p:\11211541-005-dpzw-pragmaanpak\waterbalances")
os.chdir(r"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard")

## PARAMETERS
variables = ["lswwaterbalans"]

## PARAMETERS
scenarios = ["S2050owd"]
jaren = [range(1911, 2011 + 1)]

## UITVOER
loc_output = "data/nl2120/runs_owd/2-interim/"

# %%
##-------------------------------------------
## 3. MAIN CODE
##-------------------------------------------

# ## MPX FILES
# ## MPX FILES
for variable in variables:
    print(f"Analysing {variable}")
    for sc, jaar_range in zip(scenarios, jaren):

        # for ens in ensemble:
        for j in jaar_range:
            print(j)
            data = read_mzbalance(
                f"data/nl2120/runs_owd/1-input/{sc}/Mozart/{variable}_{j}.out"
            )

            if j == jaar_range[0]:
                combined = data.copy()
            else:
                combined = pd.concat([combined, data])

        # this is to reset the index in the pandas dataframe
        combined = combined.reset_index(drop=True)

        # Opslaan
        if not os.path.exists(f"{loc_output}/{sc}/Mozart"):
            os.makedirs(f"{loc_output}/{sc}/Mozart")

        data.to_csv(f"{loc_output}/{sc}/Mozart/{variable}.csv", index=None)

# print("end of script")
