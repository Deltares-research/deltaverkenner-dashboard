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

## UITVOER
loc_output = "data/runs_2018/2-interim/"

# %%
##-------------------------------------------
## 3. MAIN CODE
##-------------------------------------------

# ## MPX FILES
for variable in variables:
    data = read_mzbalance(f"data/runs_2018/1-input/Mozart/{variable}.out")

    # this is to reset the index in the pandas dataframe
    data = data.reset_index(drop=True)

    # Opslaan
    if not os.path.exists(f"{loc_output}/Mozart"):
        os.makedirs(f"{loc_output}/Mozart")

    data.to_csv(f"{loc_output}/Mozart/{variable}.csv", index=None)

print("end of script")
