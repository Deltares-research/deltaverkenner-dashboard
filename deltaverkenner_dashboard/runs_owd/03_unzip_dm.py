# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 11:18:45 2024

@author: woerkom

Vervolg:
Jesse Reusen, 19-05-2026
Project: Deltaverkenner

Doel script: De neerslag en verdamping unzippen en elders opslaan

Opmerkingen
    - Een eerdere versie van dit script is te vinden op de volgende locatie: p:/11211541-005-dpzw-pragmaanpak/waterbalances/src/0-setup/03_unzip_dm_jesse.py
"""

import zipfile2
from pathlib import Path
import re
from itertools import product
from tqdm import tqdm

# extract_folder = Path(
#     r"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/runs_owd/1-input/"
# )
extract_folder = Path(
    r"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/runs_REF2017owd/1-input/"
)

files_to_extract = [
    Path("DM/output/Tekort peilbeheer.mpx"),
    Path("DM/output/Tekort onttrekkingen DIW.mpx"),
    Path("DM/output/Watervraag peilbeheer.mpx"),
    Path("DM/output/Vraag doorspoeling netwerk.mpx"),
    Path("DM/output/Vraag onttrekkingen DIW.mpx"),
    Path("DM/output/Netto neerslag.mpx"),
    Path("DM/output/Tekort doorspoeling netwerk.mpx"),
]

# scenarios = ['S2050owd']
# scenarios = ["S2085"] #"REF2017", ]
scenarios = ["REF2017owd"]

# jaren = {
#     "REF2017": range(1912, 2012+1),
#     "S2050": range(1912, 2012+1),
# }

for sc in tqdm(scenarios):
    print(f"Extracting data for scenario {sc}")

    i = 0

    if sc in ["REF2017owd","S2050owd"]:
        path_zips = Path(r'p:\archivedprojects\11205271-kpp-dp-zoetwater\NWM\2020_NWM_testomgeving\Gevoeligheidsanalyse_OWD')
    elif sc in ["REF2017", "S2050", "S2085"]:
        path_zips = Path(
            rf"p:\archivedprojects\11202240-kpp-dp-zoetwater\NWM_BP2018_en_historie\2018_BP2018_productieomgeving\Modelzips_Productieomgeving_NWM_Z1\{sc}BP18"
        )

    for z in path_zips.iterdir():
        z_name = z.stem

        if ("LHM" in z_name) and (f"{sc}" in z_name):
            # realyear = z_name.split("_")[2][:4]
            realyear = int(z_name.split("_")[2][:4]) - 1

            print(f"Folder {z_name} contains LHM data")

            i += 1

            if "2085" in str(z_name):
                z_name = z_name.replace("2085", "2100")

            if "BP18" in z_name.split("_")[-1]:
                output_folder = extract_folder / z_name.split("_")[-1].replace(
                    "BP18", ""
                )
            else:
                output_folder = extract_folder / z_name.split("_")[-1]

            myzip = zipfile2.ZipFile(z, mode="r")
            files = myzip.namelist()

            for fname in files_to_extract:
                fnames = [
                    f for f in files if re.search(str(fname).replace("\\", "/"), f)
                ]

                for fn in fnames:

                    if not (output_folder / fn).is_file():
                        myzip.extract(fn, path=output_folder)

                    fn = Path(fn)
                    new_name = (
                        output_folder / Path(fn).parent / f"{fn.stem}_{realyear}.mpx"
                    )

                    if not new_name.is_file():
                        (output_folder / fn).rename(new_name)

        # jaar_range = jaren[sc]
        # # # jaar_range = [1976]
        # # # jaar_range = [1911]
        # for jaar in jaar_range:
        #     realyear = jaar-1

        #     path_zip = path_zips.joinpath(jaar, "01", "zoetwater", "01", "simulated")

    print(f"There are {i} output folders with LHM data")
