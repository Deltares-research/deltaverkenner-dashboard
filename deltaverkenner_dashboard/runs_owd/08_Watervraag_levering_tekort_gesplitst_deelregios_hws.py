"""
Janneke Pouwels, 19-10-2023
Project: Waterbalans

Vervolg:
Jesse Reusen, 19-05-2026
Project: Deltaverkenner

Doel script: Watervraag, levering, tekort per scenario uit het algemene-dashboard halen


Opmerkingen
    - Een eerdere versie van dit script is te vinden op de volgende locatie: p:/11211541-005-dpzw-pragmaanpak/waterbalances/src/1-prepare/08_Watervraag_levering_tekort_gesplitst_hoofdregios.py
"""

# %%

import os
from pathlib import Path
from itertools import product
import datetime as datetime

# import mpxToDataframe as mpx
import pandas as pd
import numpy as np
import configparser
from mozart import read_mzbalance

# time the code execution
start_time = datetime.datetime.now()

# %%
##-------------------------------------------
## 1. INVOER, PARAMETERS en UITVOER
##-------------------------------------------

# os.chdir(r"p:/11210323-005-herijkingrisicos")
# os.chdir(r"p:\11211541-005-dpzw-pragmaanpak\waterbalances")
os.chdir(r"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard")

loc_input = "data/nl2120/runs_deelregios/2-interim"
# loc_input = r"p:/11211541-005-dpzw-pragmaanpak/waterbalances/data/2-interim/Modeloutput/"


## PARAMETERS
# scenarios = ["S2050owd"]
scenarios = ["S2100"]  # "S2050"] # "REF2017"] #] #, ]


jaren = {
    "S2050owd": range(1911, 2011 + 1),
    "REF2017": range(1911, 2011 + 1),
    "S2050": range(1911, 2011 + 1),
    "S2100": range(1972, 2003 + 1),
}

## UITVOER
# loc_output = Path(r"p:/11211541-005-dpzw-pragmaanpak/waterbalances/data/3-input")
loc_output = "data/nl2120/runs_deelregios/3-output"

##-------------------------------------------
## 2. FUNCTIES
##-------------------------------------------


# %%
##-------------------------------------------
## 3. MAIN CODE
##-------------------------------------------

# CONFIGURATION INI FILE
config = configparser.ConfigParser()
config.read(
    r"p:\11212687-deltaverkenner2026\Zoetwater\Dashboard\data\runs_2018\1-input\RegioIndeling_HL_fixed_deelregios_2025.ini"
)
# config.read("data/runs_2018/1-input/RegioIndeling_HL_fixed_deelregios_2025.ini")

# hier mozart districten inlezen
mozart_districts = pd.read_csv(
    r"p:/archivedprojects/11211541-005-dpzw-pragmaanpak/waterbalances/data/2-interim/koppeltabel_districten_(deel)regios_2025.csv"
)
# mozart_districts = pd.read_csv(
# "data/runs_2018/1-input/koppeltabel_districten_(deel)regios_2025.csv"
# )

# %%

# combs = list(product(*[scenarios, ensembles]))

# for s, ens in tqdm(combs):
# for s, ens in combs:
# for sc in scenarios:
# print(f"Scenario is {sc}")

#############
## INLEZEN ##
#############

for sc in scenarios:
    print(f"Scenario is {sc}")
    ## Locatie modelrun opzoeken
    loc_run = f"{loc_input}/{sc}"

    # print(loc_run)

    tekort_doorspoeling = pd.read_csv(
        rf"{loc_run}/DM/output/Tekort doorspoeling netwerk.csv", index_col="Datum"
    )
    tekort_peilbeheer = pd.read_csv(
        rf"{loc_run}/DM/output/Tekort peilbeheer.csv", index_col="Datum"
    )
    tekort_ontrekking_DIW = pd.read_csv(
        rf"{loc_run}/DM/output/Tekort onttrekkingen DIW.csv", index_col="Datum"
    )
    vraag_doorspoeling = pd.read_csv(
        rf"{loc_run}/DM/output/Vraag doorspoeling netwerk.csv", index_col="Datum"
    )
    vraag_peilbeheer = pd.read_csv(
        rf"{loc_run}/DM/output/Watervraag peilbeheer.csv", index_col="Datum"
    )
    vraag_onttrekking_DIW = pd.read_csv(
        rf"{loc_run}/DM/output/Vraag onttrekkingen DIW.csv", index_col="Datum"
    )
    netto_neerslag = pd.read_csv(
        rf"{loc_run}/DM/output/Netto neerslag.csv", index_col="Datum"
    )

    # de code hieronder kan pas wanneer we een lswwaterbalans.out hebben
    # MozartFile = read_mzbalance(rf"{loc_run}/mozart/lswwaterbalans.out")
    MozartFile = pd.read_csv(rf"{loc_run}/Mozart/lswwaterbalans.csv")
    MozartFile["TIMESTART"] = pd.to_datetime(MozartFile["TIMESTART"], format="%Y%m%d")
    MozartFile["TIMEEND"] = pd.to_datetime(MozartFile["TIMEEND"], format="%Y%m%d")
    MozartFile["year"] = MozartFile["TIMESTART"].dt.year

    #################################
    ## KOPPELING PER REGIO INLEZEN ##
    #################################

    ## Nummers van districts, links, nodes krijgen per regio
    regios = {}

    config.sections()
    for key in config:
        regios[key] = {}
        for key2 in config[key]:
            regios[key][key2] = config[key][key2]

    del [regios["DEFAULT"]]

    for regio in regios:
        # print(regio[6:])
        globals()[regio + "_node"] = [
            v
            for k, v in regios[regio].items()
            if (("dmnode" in k) & ("dmnodeids" not in k))
        ]
        globals()[regio + "_link"] = [
            v
            for k, v in regios[regio].items()
            if ("dmlink" in k) & ("dmlinkids" not in k)
        ]
        # globals()[regio + "_district"] = [
        #     v for k, v in regios[regio].items() if ("mzdistrict" in k)
        # ]  # hier kan overruled worden met info uit district

        # hier mozart districten toevoegen

        # mz_districts = mozart_districts[mozart_districts['Zoetwaterregio naam'] == int(regio[6:])].Districtnummer.values
        mz_districts = mozart_districts[
            mozart_districts["Zoetwater deelregio naam"]
            == regios[regio]["regionname"][10:].replace("_", " ")
        ].Districtnummer.values
        mz_districts = mz_districts.tolist()
        mz_districts_strings = [str(dist) for dist in mz_districts]

        globals()[regio + "_district"] = mz_districts_strings

    ## Check of alle nodes, links en districten wel bestaan
    nodes_all = list(set(sum([globals()[r + "_node"] for r in regios], [])))
    links_all = list(set(sum([globals()[r + "_link"] for r in regios], [])))
    dists_all = list(set(sum([globals()[r + "_district"] for r in regios], [])))
    nodes_dm = list(vraag_peilbeheer.columns)
    links_dm = list(vraag_doorspoeling.columns)
    dists_mz = [str(i) for i in list(set(list(MozartFile["DW"])))]
    missing_nodes = list(set(nodes_all) - set(nodes_dm))
    missing_links = list(set(links_all) - set(links_dm))
    missing_dists = list(set(dists_all) - set(dists_mz))

    ## En verwijder deze uit de lijstjes als die niet bestaat
    for regio in regios:

        for i in missing_nodes:
            if i in globals()[regio + "_node"]:
                globals()[regio + "_node"].remove(i)

        for i in missing_links:
            if i in globals()[regio + "_link"]:
                globals()[regio + "_link"].remove(i)

        for i in missing_dists:
            if i in globals()[regio + "_district"]:
                globals()[regio + "_district"].remove(i)

    ################################
    ## WATERVRAGEN EN TEKORTEN DM ##
    ################################

    ## Watervragen en tekorten per regio in [m3/s], let op, omrekenen naar decade-waarden

    DM_tekort_doorspoel = pd.DataFrame(columns=regios)
    DM_tekort_peilbeheer = pd.DataFrame(columns=regios)
    DM_tekort_onttrekking_DIW = pd.DataFrame(columns=regios)
    DM_vraag_doorspoel = pd.DataFrame(columns=regios)
    DM_vraag_peilbeheer = pd.DataFrame(columns=regios)
    DM_vraag_onttrekking_DIW = pd.DataFrame(columns=regios)
    DM_netto_neerslag = pd.DataFrame(columns=regios)

    for regio in regios:
        DM_tekort_doorspoel[regio] = tekort_doorspoeling[
            globals()[regio + "_link"]
        ].sum(axis=1)

        DM_tekort_peilbeheer[regio] = tekort_peilbeheer[globals()[regio + "_node"]].sum(
            axis=1
        )

        DM_tekort_onttrekking_DIW[regio] = tekort_ontrekking_DIW[
            globals()[regio + "_node"]
        ].sum(axis=1)

        DM_vraag_doorspoel[regio] = vraag_doorspoeling[globals()[regio + "_link"]].sum(
            axis=1
        )
        DM_vraag_peilbeheer[regio] = vraag_peilbeheer[globals()[regio + "_node"]].sum(
            axis=1
        )
        DM_vraag_onttrekking_DIW[regio] = vraag_onttrekking_DIW[
            globals()[regio + "_node"]
        ].sum(axis=1)
        DM_netto_neerslag[regio] = netto_neerslag[globals()[regio + "_node"]].sum(
            axis=1
        )
    ####################################
    ## WATERVRAGEN EN TEKORTEN MOZART ##
    ####################################

    ## Mozart data uitlezen in [m3/decade]

    jaar_range = jaren[sc]
    # # jaar_range = [1976]
    # # jaar_range = [1911]
    for jaar in jaar_range:
        print(f"Jaar is {jaar}")

        # ## Eerst specifieke jaar selecteren
        MozartFile_jaar = MozartFile[MozartFile["year"] == jaar]

        ## De specifieke vragen en allocaties uit de balansfile halen via pivot table
        MZ_demand_flush2 = pd.pivot_table(
            MozartFile_jaar,
            index=["TIMESTART"],
            columns=["DW"],
            values="DEM_FLUSH",
            aggfunc="sum",
        )
        MZ_demand_flush2.columns = MZ_demand_flush2.columns.map(str)
        MZ_demand_WMtot2 = pd.pivot_table(
            MozartFile_jaar,
            index=["TIMESTART"],
            columns=["DW"],
            values="DEM_WMTOTAL",
            aggfunc="sum",
        )
        MZ_demand_WMtot2.columns = MZ_demand_WMtot2.columns.map(str)
        MZ_demand_WMdw2 = pd.pivot_table(
            MozartFile_jaar,
            index=["TIMESTART"],
            columns=["DW"],
            values="DEM_WM_TODW",
            aggfunc="sum",
        )
        MZ_demand_WMdw2.columns = MZ_demand_WMdw2.columns.map(str)
        MZ_demand_agric2 = pd.pivot_table(
            MozartFile_jaar,
            index=["TIMESTART"],
            columns=["DW"],
            values="DEM_AGRIC",
            aggfunc="sum",
        )
        MZ_demand_agric2.columns = MZ_demand_agric2.columns.map(str)

        MZ_alloc_flush2 = pd.pivot_table(
            MozartFile_jaar,
            index=["TIMESTART"],
            columns=["DW"],
            values="ALLOC_FLUSH",
            aggfunc="sum",
        )
        MZ_alloc_flush2.columns = MZ_alloc_flush2.columns.map(str)
        MZ_alloc_WMdw2 = pd.pivot_table(
            MozartFile_jaar,
            index=["TIMESTART"],
            columns=["DW"],
            values="ALLOC_WM_DW",
            aggfunc="sum",
        )
        MZ_alloc_WMdw2.columns = MZ_alloc_WMdw2.columns.map(str)
        MZ_alloc_agric2 = pd.pivot_table(
            MozartFile_jaar,
            index=["TIMESTART"],
            columns=["DW"],
            values="ALLOC_AGRIC",
            aggfunc="sum",
        )
        MZ_alloc_agric2.columns = MZ_alloc_agric2.columns.map(str)

        ## En omzetten naar pandas dataframe
        MZ_demand_flush = pd.DataFrame(
            index=np.unique(MozartFile_jaar.TIMESTART), columns=regios
        )
        MZ_demand_WMtot = pd.DataFrame(
            index=np.unique(MozartFile_jaar.TIMESTART), columns=regios
        )
        MZ_demand_WMdw = pd.DataFrame(
            index=np.unique(MozartFile_jaar.TIMESTART), columns=regios
        )
        MZ_demand_agric = pd.DataFrame(
            index=np.unique(MozartFile_jaar.TIMESTART), columns=regios
        )
        MZ_alloc_flush = pd.DataFrame(
            index=np.unique(MozartFile_jaar.TIMESTART), columns=regios
        )
        MZ_alloc_WMdw = pd.DataFrame(
            index=np.unique(MozartFile_jaar.TIMESTART), columns=regios
        )
        MZ_alloc_agric = pd.DataFrame(
            index=np.unique(MozartFile_jaar.TIMESTART), columns=regios
        )

        ## Groeperen per regio
        for regio in regios:
            MZ_demand_flush[regio] = MZ_demand_flush2[
                globals()[regio + "_district"]
            ].sum(axis=1)
            MZ_demand_WMtot[regio] = MZ_demand_WMtot2[
                globals()[regio + "_district"]
            ].sum(axis=1)
            MZ_demand_WMdw[regio] = MZ_demand_WMdw2[globals()[regio + "_district"]].sum(
                axis=1
            )
            MZ_demand_agric[regio] = MZ_demand_agric2[
                globals()[regio + "_district"]
            ].sum(axis=1)
            MZ_alloc_flush[regio] = MZ_alloc_flush2[globals()[regio + "_district"]].sum(
                axis=1
            )
            MZ_alloc_WMdw[regio] = MZ_alloc_WMdw2[globals()[regio + "_district"]].sum(
                axis=1
            )
            MZ_alloc_agric[regio] = MZ_alloc_agric2[globals()[regio + "_district"]].sum(
                axis=1
            )

        ####
        # hier kan de Mozart selectie geplaatst worden op LSW niveau.
        ####

        # iets van: mozartfile_jaar[mozartfile_jaar["LSWNR"].isin(selection of LSWNR)]

        # selecteer jaar in DM dataframe
        DM_tekort_doorspoel_jaar = DM_tekort_doorspoel[
            DM_tekort_doorspoel.index.str.contains(str(jaar))
        ]
        DM_tekort_onttrekking_DIW_jaar = DM_tekort_onttrekking_DIW[
            DM_tekort_onttrekking_DIW.index.str.contains(str(jaar))
        ]
        DM_tekort_peilbeheer_jaar = DM_tekort_peilbeheer[
            DM_tekort_peilbeheer.index.str.contains(str(jaar))
        ]

        DM_vraag_doorspoel_jaar = DM_vraag_doorspoel[
            DM_vraag_doorspoel.index.str.contains(str(jaar))
        ]
        DM_vraag_onttrekking_DIW_jaar = DM_vraag_onttrekking_DIW[
            DM_vraag_onttrekking_DIW.index.str.contains(str(jaar))
        ]
        DM_vraag_peilbeheer_jaar = DM_vraag_peilbeheer[
            DM_vraag_peilbeheer.index.str.contains(str(jaar))
        ]
        DM_netto_neerslag_jaar = DM_netto_neerslag[
            DM_netto_neerslag.index.str.contains(str(jaar))
        ]

        DM_tekort_doorspoel_jaar.index = pd.to_datetime(DM_tekort_doorspoel_jaar.index)
        DM_tekort_onttrekking_DIW_jaar.index = pd.to_datetime(
            DM_tekort_onttrekking_DIW_jaar.index
        )
        DM_tekort_peilbeheer_jaar.index = pd.to_datetime(
            DM_tekort_peilbeheer_jaar.index
        )

        DM_vraag_doorspoel_jaar.index = pd.to_datetime(DM_vraag_doorspoel_jaar.index)
        DM_vraag_onttrekking_DIW_jaar.index = pd.to_datetime(
            DM_vraag_onttrekking_DIW_jaar.index
        )
        DM_vraag_peilbeheer_jaar.index = pd.to_datetime(DM_vraag_peilbeheer_jaar.index)

        DM_netto_neerslag_jaar.index = pd.to_datetime(DM_netto_neerslag_jaar.index)

        # convert mozart values from m3/decade naar m3/s
        # this gives the time difference between all the columns
        difference = DM_tekort_doorspoel_jaar.index.diff()
        # add 12 days to the end, and also remove the first value in the diff column
        difference = difference.delete(0)
        difference = difference.append([pd.TimedeltaIndex(data=["12 days"])])
        # conversion value in seconds:
        dt_in_seconds = difference.values.astype("timedelta64[s]")
        dt_in_seconds_floats = dt_in_seconds / np.timedelta64(1, "s")

        # divide mozart values by the time difference in seconds to
        # convert from m3/decade to m3/s
        MZ_alloc_flush = MZ_alloc_flush.T / dt_in_seconds_floats
        MZ_alloc_flush = MZ_alloc_flush.T

        MZ_demand_flush = MZ_demand_flush.T / dt_in_seconds_floats
        MZ_demand_flush = MZ_demand_flush.T

        MZ_demand_WMtot = MZ_demand_WMtot.T / dt_in_seconds_floats
        MZ_demand_WMtot = MZ_demand_WMtot.T

        MZ_alloc_WMdw = MZ_alloc_WMdw.T / dt_in_seconds_floats
        MZ_alloc_WMdw = MZ_alloc_WMdw.T

        MZ_demand_WMdw = MZ_demand_WMdw.T / dt_in_seconds_floats
        MZ_demand_WMdw = MZ_demand_WMdw.T

        MZ_alloc_agric = MZ_alloc_agric.T / dt_in_seconds_floats
        MZ_alloc_agric = MZ_alloc_agric.T

        MZ_demand_agric = MZ_demand_agric.T / dt_in_seconds_floats
        MZ_demand_agric = MZ_demand_agric.T

        # totale_waardes = pd.DataFrame()

        # totale waardes per categorie

        # beregening
        totale_vraag_beregening = MZ_demand_agric * -1
        totale_levering_beregening = MZ_alloc_agric * -1
        totale_tekort_beregening = (
            totale_vraag_beregening - totale_levering_beregening
        )  # MZ_demand_agric - MZ_alloc_agric

        # peilbeheer
        totale_vraag_peilbeheer = MZ_demand_WMdw + DM_netto_neerslag_jaar * -1
        totale_tekort_peilbeheer = MZ_demand_WMdw - MZ_alloc_WMdw
        totale_levering_peilbeheer = totale_vraag_peilbeheer - totale_tekort_peilbeheer

        # doorspoeling
        # Tekort doorspoeling                = [MZ: demand_flush] - [MZ: alloc_flush] + [DM: TekortDoorspoeling]
        totale_vraag_doorspoeling = MZ_demand_flush * -1 + DM_vraag_doorspoel_jaar
        totale_tekort_doorspoeling = (
            MZ_demand_flush * -1 - MZ_alloc_flush * -1 + DM_tekort_doorspoel_jaar
        )
        totale_levering_doorspoeling = (
            totale_vraag_doorspoeling - totale_tekort_doorspoeling
        )

        # doorspoeling - polders
        totale_vraag_doorspoeling_polders = MZ_demand_flush * -1
        totale_tekort_doorspoeling_polders = MZ_demand_flush * -1 - MZ_alloc_flush * -1
        totale_levering_doorspoeling_polders = (
            totale_vraag_doorspoeling_polders - totale_tekort_doorspoeling_polders
        )

        # doorspoeling - boezems
        totale_vraag_doorspoeling_boezem = DM_vraag_doorspoel_jaar
        totale_tekort_doorspoeling_boezem = DM_tekort_doorspoel_jaar
        totale_levering_doorspoeling_boezem = (
            totale_vraag_doorspoeling_boezem - totale_tekort_doorspoeling_boezem
        )

        # totale waarrdes
        totale_tekort = (
            totale_tekort_doorspoeling
            + totale_tekort_peilbeheer
            + totale_tekort_beregening
        )

        totale_vraag = (
            totale_vraag_doorspoeling
            + totale_vraag_peilbeheer
            + totale_vraag_beregening
        )

        totale_levering = (
            totale_levering_doorspoeling
            + totale_levering_peilbeheer
            + totale_levering_beregening
        )

        totale_tekort_doorspoeling.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Tekort_doorspoeling_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_tekort_doorspoeling_polders.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Tekort_doorspoeling_polders_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_tekort_doorspoeling_boezem.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Tekort_doorspoeling_boezem_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_tekort_peilbeheer.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Tekort_peilbeheer_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_tekort_beregening.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Tekort_beregening_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_tekort.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Tekort_totaal_{sc}_{jaar}_deelregios_hws.csv"
        )

        totale_vraag_doorspoeling.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Vraag_doorspoeling_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_vraag_doorspoeling_polders.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Vraag_doorspoeling_polders_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_vraag_doorspoeling_boezem.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Vraag_doorspoeling_boezem_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_vraag_peilbeheer.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Vraag_peilbeheer_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_vraag_beregening.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Vraag_beregening_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_vraag.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Vraag_totaal_{sc}_{jaar}_deelregios_hws.csv"
        )

        totale_levering_doorspoeling.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Levering_doorspoeling_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_levering_doorspoeling_polders.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Levering_doorspoeling_polders_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_levering_doorspoeling_boezem.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Levering_doorspoeling_boezem_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_levering_peilbeheer.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Levering_peilbeheer_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_levering_beregening.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Levering_beregening_{sc}_{jaar}_deelregios_hws.csv"
        )
        totale_levering.to_csv(
            f"{loc_output}/{sc}/waterbalans_per_jaar/Levering_totaal_{sc}_{jaar}_deelregios_hws.csv"
        )

# %%

end_time = datetime.datetime.now()

elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time.seconds, "Seconds")
