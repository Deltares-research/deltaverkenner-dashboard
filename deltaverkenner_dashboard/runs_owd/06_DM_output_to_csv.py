"""
Janneke Pouwels, 12-10-2023
Project: Waterbalans

Vervolg:
Jesse Reusen, 19-05-2026
Project: Deltaverkenner

Doel script: De DM uitvoer (mpx) samenvoegen voor alle jaren

Opmerkingen
    - Een eerdere versie van dit script is te vinden op de volgende locatie: p:/11211541-005-dpzw-pragmaanpak/waterbalances/src/1-prepare/06_DM_uitvoer_samenvoegen_jesse.py
"""

import os

import pandas as pd

# %%
##-------------------------------------------
## 1. INVOER, PARAMETERS en UITVOER
##-------------------------------------------

# os.chdir(r"p:\11210323-005-herijkingrisicos")
# os.chdir(r"p:\11211541-005-dpzw-pragmaanpak\waterbalances")
os.chdir(r"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard")

## PARAMETERS
variables = [
    "Tekort peilbeheer",
    "Tekort onttrekkingen DIW",
    "Watervraag peilbeheer",
    "Vraag doorspoeling netwerk",
    "Vraag onttrekkingen DIW",
    "Netto neerslag",
    "Tekort doorspoeling netwerk",
]

## PARAMETERS
# scenarios = ["S2050owd"]
scenarios = ["S2100"]  # "REF2017"] #] #, ]
jaren = [range(1972, 2003 + 1)]  # [range(1911, 2011 + 1)]

## UITVOER
loc_output = "data/nl2120/runs_deelregios/2-interim/"

##-------------------------------------------
## 2. FUNCTIES
##-------------------------------------------


def read(mpxfile):
    """Read a mpxfile to a Pandas DataFrame with extra attributes."""
    from struct import unpack, pack
    import numpy as np
    from datetime import datetime, timedelta
    from os.path import getsize
    import pandas as pd

    filesize = getsize(mpxfile)
    with open(mpxfile, "rb") as f:
        _ = f.read(8)
        mapname = f.read(8).rstrip()  # => "lnks"
        timestepkind = f.read(8).rstrip()  # => "decade"

        # if timestepkind == 'decade':
        #     timestep_size_in_seconds = 10 * 86400
        # else:
        #     # just porting from fortran, we can probably support this
        #     raise ValueError('only decade timesteps supported')

        nlocs, steps, series = unpack("hhh", f.read(6))  # => 329, 36, 1
        _ = f.read(10)
        quantity = f.read(40).rstrip()  # => "Debieten in het netwerk"
        unit = f.read(8).rstrip()  # => "m3/s"
        _ = f.read(32)

        nparam = series
        param_ids = []
        for i in range(nparam):
            # ignoring Fortran's UseMpxQuantity
            param_id = f.read(40).rstrip()
            param_ids.append(param_id)

        # read scale definitions and other dummy stuff from MPX header
        _ = f.read(26)  # 13 int16
        _ = f.read(14)  # 14 char
        _ = f.read(40)  # 10 float32
        _ = f.read(8)  # 2 float32
        _ = f.read(32)  # 32 char

        ndone = 240 + series * 40
        nrecsize = 2 + (4 * nlocs)
        nrecnr = 2 + 40 * (7 + series) // nrecsize - 1
        nbytes = nrecnr * nrecsize
        assert ndone == f.tell(), "ndone: {} f.tell() {}".format(ndone, f.tell())
        _ = f.read(nbytes - ndone)
        ndone = nbytes

        # read location ids (numbers)
        loc_ids = []
        for j in range(nlocs):
            k = unpack("h", f.read(2))[0]
            # possible overflow correction
            if k < 0:
                k += 65536
            loc_ids.append(str(k))
        ndone += nlocs * 2
        vara = f.tell()
        assert ndone == f.tell(), "ndone: {} f.tell() {}".format(ndone, f.tell())
        nrecnr = 2 + 40 * (7 + series) // nrecsize
        nbytes = nrecnr * nrecsize
        _ = f.read(nbytes - ndone)

        # read the data
        data = np.zeros((steps, nlocs), np.float32)
        for ts in range(steps):
            _ = f.read(2)  # index (i2) starting as 1, no need to use
            # date = startdate + timedelta(seconds=ts * dt)
            data[ts] = np.fromfile(f, np.float32, nlocs)

        assert filesize - f.tell() == 0

        df = pd.DataFrame(
            data,
            index=range(1, steps + 1),
            columns=loc_ids,
            dtype=np.float32,
            copy=True,
        )
        return df


# %%
##-------------------------------------------
## 3. MAIN CODE
##-------------------------------------------

# ## MPX FILES
for variable in variables:
    print(f"Analysing {variable}")
    for sc, jaar_range in zip(scenarios, jaren):

        # for ens in ensemble:
        for j in jaar_range:
            # Inlezen
            # data = read(
            #     rf"p:\11211541-005-dpzw-pragmaanpak\waterbalances\data\1-external\Modeloutput\{sc}\DM\output\{variable}_{j}.mpx"
            # )
            data = read(
                rf"p:\11212687-deltaverkenner2026\Zoetwater\Dashboard\data\nl2120\runs_deelregios\1-input\{sc}\DM\output\{variable}_{j}.mpx"
            )
            # Datum toevoegen
            data["Datum"] = [
                f"{j}-01-01",
                f"{j}-01-11",
                f"{j}-01-21",
                f"{j}-02-01",
                f"{j}-02-11",
                f"{j}-02-21",
                f"{j}-03-01",
                f"{j}-03-11",
                f"{j}-03-21",
                f"{j}-04-01",
                f"{j}-04-11",
                f"{j}-04-21",
                f"{j}-05-01",
                f"{j}-05-11",
                f"{j}-05-21",
                f"{j}-06-01",
                f"{j}-06-11",
                f"{j}-06-21",
                f"{j}-07-01",
                f"{j}-07-11",
                f"{j}-07-21",
                f"{j}-08-01",
                f"{j}-08-11",
                f"{j}-08-21",
                f"{j}-09-01",
                f"{j}-09-11",
                f"{j}-09-21",
                f"{j}-10-01",
                f"{j}-10-11",
                f"{j}-10-21",
                f"{j}-11-01",
                f"{j}-11-11",
                f"{j}-11-21",
                f"{j}-12-01",
                f"{j}-12-11",
                f"{j}-12-21",
            ]

            # print(data)
            data = data.set_index("Datum")
            # print(data)

            # samenvoegen
            if j == jaar_range[0]:
                combined = data.copy()
            else:
                combined = pd.concat([combined, data])
                # combined = combined.append(peilen)

        # combined = combined.reset_index(drop=True)

        # print(combined.index)

        ## Opslaan
        if not os.path.exists(f"{loc_output}/{sc}/DM/output"):
            os.makedirs(f"{loc_output}/{sc}/DM/output")
        combined.to_csv(f"{loc_output}/{sc}/DM/output/{variable}.csv")  # , index=None
        # )

    # ## Opslaan
    # if not os.path.exists(f"{loc_output}/DM/output"):
    #     os.makedirs(f"{loc_output}/DM/output")

    # data.to_csv(f"{loc_output}/DM/output/{variable}.csv")
