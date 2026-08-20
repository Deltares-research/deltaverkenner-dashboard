from pathlib import Path

import geopandas as gpd

from deltaverkenner_dashboard.deltapolder.io.read import (
    read_drinkwaterbronnen,
    read_lsw,
)

from deltaverkenner_dashboard.deltapolder.visualisation.plotting import (
    plot_distance_map,
)

if __name__ == "__main__":

    path_drinkwaterbronnen = Path(
        "C:/Users/reusen/OneDrive - Stichting Deltares/SHORTC~1/112127~1/WERKPA~1/VISIEL~1/DATADR~1/DRINKW~1.SHP"
    )

    waterbronnen = read_drinkwaterbronnen(path_drinkwaterbronnen)

    #################################################################
    # LSW's
    #################################################################

    path_lsws = Path(
        "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/Districten_knopen_takken/lsws.shp"
    )

    lsws = read_lsw(path_lsws)

    lsws_points = lsws.copy()
    lsws_points["geometry"] = lsws_points.geometry.representative_point()

    print("Done reading data")

    lsws_nearest = lsws_points.sjoin_nearest(
        waterbronnen, how="left", distance_col="afstand_tot_waterbron_m"
    )

    lsws_nearest = lsws_nearest[["LSWFINAL", "Onttrek", "afstand_tot_waterbron_m"]]

    lsws_nearest["geometry"] = lsws["geometry"]

    lsws_nearest = gpd.GeoDataFrame(lsws_nearest, geometry="geometry", crs="EPSG:28992")

    print("Done calculating the shortest distances")

    #### plot a map #####

    figpath = "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/deltapolder/2-visualisation/kaart_afstand_tot_waterbron_opp_grondwater_Vewin_KWR.png"

    plot_distance_map(
        waterbronnen,
        lsws_nearest,
        figpath,
        axis_title="Afstand tot dichtstbijzijnde waterbron",
    )
