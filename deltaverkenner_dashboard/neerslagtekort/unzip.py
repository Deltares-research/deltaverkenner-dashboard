# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 11:18:45 2024

@author: woerkom

Vervolg:
Jesse Reusen, 19-05-2026
Project: Deltaverkenner

Doel script: De neerslag en verdamping unzippen en elders opslaan

Opmerkingen
    - Een eerdere versie van dit script is te vinden op de volgende locatie: p:/11211541-005-dpzw-pragmaanpak/waterbalances/src/1-prepare/06_DM_uitvoer_samenvoegen_jesse.py
"""

from pathlib import Path

import re
# from itertools import product
from tqdm import tqdm
import zipfile2

# extract_folder = Path(r"p:\11210323-005-herijkingrisicos\data\1-external\Modeloutput")
extract_folder = Path(
    r"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/neerslagtekort"
)

files_to_extract = [
    # Path("DM/output/Tekort peilbeheer.mpx"),
    Path("meteo/prec"),
    Path("meteo/evap"),
]

exclude = ["prec0365", "prec0366", "evap0366", "evap0365"]

# ## PARAMETERS
scenarios = ["REF2017", "S2050", "S2085"]

for sc in tqdm(scenarios):
    print(f"Extracting data for scenario {sc}")

    i = 0

    path_zips = Path(
        f"p:/archivedprojects/11202240-kpp-dp-zoetwater/NWM_BP2018_en_historie/2018_BP2018_productieomgeving/Modelzips_Productieomgeving_NWM_Z1/{sc}BP18"
    )

    for z in path_zips.iterdir():
        z_name = z.stem

        if "LHM" in z_name:
            # realyear = z_name.split("_")[2][:4]
            realyear = int(z_name.split("_")[2][:4]) - 1

            print(f"Folder {z_name} contains LHM data")

            i += 1

            output_folder = extract_folder / z_name.split("_")[-1]

            myzip = zipfile2.ZipFile(z, mode="r")
            files = myzip.namelist()

            for fname in files_to_extract:
                fnames = [
                    f
                    for f in files
                    if re.search(str(fname).replace("\\", "/"), f)
                    and not any(re.search(ex, f) for ex in exclude)
                ]

                for fn in fnames:
                    if not (output_folder / fn).is_file():
                        myzip.extract(fn, path=output_folder)

                    else:
                        fn = Path(fn)
                        new_name = (
                            output_folder
                            / Path(fn).parent
                            / f"{fn.stem}.asc"
                        )
                        if not new_name.is_file():
                            (output_folder / fn).rename(new_name)

    print(f"There are {i} output folders with LHM data")
