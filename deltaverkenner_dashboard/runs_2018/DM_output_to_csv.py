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

## UITVOER
loc_output = "data/runs_2018/2-interim"


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

for variable in variables:
    print(f"Analysing {variable}")

    data = read(f"data/runs_2018/1-input/DM/{variable}.mpx")
    # data = read(
    #     rf"p:\11211541-005-dpzw-pragmaanpak\waterbalances\data\1-external\Modeloutput\REF2017VP\DM\output\{variable}_1912.mpx"
    # )

    # Datum toevoegen
    data["Datum"] = [
        "2018-01-01",
        "2018-01-11",
        "2018-01-21",
        "2018-02-01",
        "2018-02-11",
        "2018-02-21",
        "2018-03-01",
        "2018-03-11",
        "2018-03-21",
        "2018-04-01",
        "2018-04-11",
        "2018-04-21",
        "2018-05-01",
        "2018-05-11",
        "2018-05-21",
        "2018-06-01",
        "2018-06-11",
        "2018-06-21",
        "2018-07-01",
        "2018-07-11",
        "2018-07-21",
        "2018-08-01",
        "2018-08-11",
        "2018-08-21",
        "2018-09-01",
        "2018-09-11",
        "2018-09-21",
        "2018-10-01",
        "2018-10-11",
        "2018-10-21",
        "2018-11-01",
        "2018-11-11",
        "2018-11-21",
        "2018-12-01",
        "2018-12-11",
        "2018-12-21",
    ]

    data = data.set_index("Datum")

    ## Opslaan
    if not os.path.exists(f"{loc_output}/DM/output"):
        os.makedirs(f"{loc_output}/DM/output")

    data.to_csv(f"{loc_output}/DM/output/{variable}.csv")
