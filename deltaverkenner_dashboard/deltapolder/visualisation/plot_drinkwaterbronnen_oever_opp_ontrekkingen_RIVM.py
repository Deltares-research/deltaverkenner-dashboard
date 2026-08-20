from pathlib import Path

import matplotlib.pyplot as plt

from deltaverkenner_dashboard.deltapolder.io.read import (
    read_drinkwaterbronnen,
    read_region,
)

from deltaverkenner_dashboard.deltapolder.visualisation.plotting import (
    plot_waterbronnen,
)

if __name__ == "__main__":

    path_drinkwaterbronnen = Path(
        "C:/Users/reusen/OneDrive - Stichting Deltares/SHORTC~1/112127~1/WERKPA~1/VISIEL~1/DATADR~1/OEVER_~1.SHP"
    )
    path_hoofdregios = Path(
        "n:/Projects/11209000/11209259/F. Other information/00 Scripts en GISbestanden/Gisbestanden/ZW_regios/ZW_hoofdregios.shp"
    )

    waterbronnen = read_drinkwaterbronnen(path_drinkwaterbronnen)
    hoofdregios = read_region(path_hoofdregios)

    print("Done reading data")

    #### a simple plot #####

    figpath = "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/deltapolder/2-visualisation/kaart_drinkwaterbronnen_oever_opp_ontrekkingen_RIVM.png"

    plot_waterbronnen(
        waterbronnen,
        hoofdregios,
        figpath,
        axis_title="Drinkwaterbronnen oever opp ontrekkingen RIVM",
    )

    print("Done plotting data")

    ################# Write the amount of rows #######################
    n_waterbronnen = len(waterbronnen)

    out_file = Path(
        "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/deltapolder/1-output/aantal_drinkwaterbronnen_oever_opp_ontrekkingen_RIVM.txt"
    )

    with open(out_file, "w") as f:
        f.write(f"aantal_waterbronnen: {len(waterbronnen)}\n")

    print("Done writing data")
