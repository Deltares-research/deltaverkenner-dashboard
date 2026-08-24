from pathlib import Path

import geopandas as gpd


def read_drinkwaterbronnen(path):

    drinkwaterbronnen = gpd.read_file(path)

    return drinkwaterbronnen


def read_region(path):

    provinces = gpd.read_file(path)

    return provinces


def read_lsw(path):
    lsws = gpd.read_file(path)

    lsws_merged = lsws.dissolve(by=["ORIG_FID"], as_index=False)

    return lsws_merged


if __name__ == "__main__":

    path_drinkwaterbronnen = Path(
        "C:/Users/reusen/OneDrive - Stichting Deltares/SHORTC~1/112127~1/WERKPA~1/VISIEL~1/DATADR~1/OEVER_~1.SHP"
    )

    bron = read_drinkwaterbronnen(path_drinkwaterbronnen)

    print("Done")

    #### a simple plot #####

    import matplotlib.pyplot as plt

    path_to_provinces_shapefile = "p:/11207812-somers-ontwikkeling/1-data/1-external/Bestuurlijke_grenzen/provincial_boundaries_2025.shp"
    provinces = gpd.read_file(path_to_provinces_shapefile)

    fig, ax = plt.subplots(figsize=(8.27, 11.69))

    ax.tick_params(
        axis="both",
        which="both",
        labelbottom=False,
        labelleft=False,
        bottom=False,
        left=False,
    )

    provinces.boundary.plot(ax=ax, lw=0.5, color="grey")

    bron.plot(ax=ax)

    plt.show()
