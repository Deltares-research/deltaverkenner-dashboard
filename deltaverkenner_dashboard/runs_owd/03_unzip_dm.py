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

# extract_folder = Path(r"p:\11210323-005-herijkingrisicos\data\1-external\Modeloutput")
# extract_folder = Path(r"p:\11211541-005-dpzw-pragmaanpak\waterbalances\data\1-external\Modeloutput")
extract_folder = Path(
    r"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/runs_owd/1-input/"
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

scenarios = ['S2050owd']

for sc in tqdm(scenarios):
    print(f"Extracting data for scenario {sc}")

    i = 0

    # if sc in ['REF2017VP', 'S2050VP']:
    #     path_zips = Path(
    #         rf"p:\archivedprojects\11205271-kpp-dp-zoetwater\NWM\2020_NWM_productieomgeving\archief\2020_voorkeurs&economischpakket\modeldata\download"
    #     )
    # else:
    #     path_zips = Path(
    #         rf"p:\archivedprojects\11202240-kpp-dp-zoetwater\NWM_BP2018_en_historie\2018_BP2018_productieomgeving\Modelzips_Productieomgeving_NWM_Z1\{sc}BP18"
    #     )

    path_zips = Path(r'p:\archivedprojects\11205271-kpp-dp-zoetwater\NWM\2020_NWM_testomgeving\Gevoeligheidsanalyse_OWD')

    for z in path_zips.iterdir():
        z_name = z.stem

        if (("LHM" in z_name) and (f"{sc}" in z_name)):
            # realyear = z_name.split("_")[2][:4]
            realyear = int(z_name.split("_")[2][:4]) - 1

            print(f"Folder {z_name} contains LHM data")

            i+=1

            output_folder = extract_folder / z_name.split("_")[-1]

            myzip = zipfile2.ZipFile(z, mode="r")
            files = myzip.namelist()

            for fname in files_to_extract:
                fnames = [
                    f
                    for f in files
                    if re.search(str(fname).replace("\\", "/"), f)
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

    print(f'There are {i} output folders with LHM data')
