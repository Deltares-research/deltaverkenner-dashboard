from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib as mpl
import numpy as np
from highlight_text import ax_text
from PIL import Image

from deltaverkenner_dashboard.analysis.read_dashboard import read_watervraag


# Open an image from a computer
def open_image_local(path_to_image):
    image = Image.open(path_to_image)  # Open the image
    width_px, height_px = image.size
    aspect_ratio = width_px / height_px
    image_array = np.array(image)  # Convert to a numpy array
    return (width_px, height_px, aspect_ratio, image_array)  # Output)


# bron voor gehighlighte text: https://python-graph-gallery.com/advanced-custom-annotations-matplotlib/
def define_path_effect(**kwargs):
    return [path_effects.Stroke(**kwargs), path_effects.Normal()]


# Open the image from my computer
width_px, height_px, aspect_ratio, image = open_image_local(
    r"c:/Users/reusen/OneDrive - Stichting Deltares/Documents/Deltares Huisstijl/Deltares_logo_D-blauw_RGB/Deltares_logo_D-blauw_RGB/Deltares_logo_D-blauw_RGB.png"
)

# Define the position and size parameters
image_xaxis = -0.1
image_yaxis = 0.235
image_width = 0.15
image_height = image_width / aspect_ratio  # Same as width since our logo is a square

#################################################################
# provinces (for plot)
#################################################################

path_to_provinces_shapefile = "p:/11207812-somers-ontwikkeling/1-data/1-external/Bestuurlijke_grenzen/provincial_boundaries_2025.shp"
provinces = gpd.read_file(path_to_provinces_shapefile)

#################################################################
# veengebieden shapes
#################################################################

path_veengebieden_shapes = "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/shapes_veengebieden/shapes_deelgebieden_veen.shp"

veengebieden = gpd.read_file(path_veengebieden_shapes)

veengebieden = veengebieden.rename(columns={"naam": "deelgebied"})

#################################################################

mapping = pd.DataFrame(
    {
        "deelgebied": [
            "1. Friesland-Groningen",
            "1. Friesland-Groningen",
            "1. Friesland-Groningen",
            "1. Friesland-Groningen",
            "2. Wieden-Weerribben",
            "3.1 Veluwe/Utrechtse heuvelrug",
            "3.1 Veluwe/Utrechtse heuvelrug",
            "3.1 Veluwe/Utrechtse heuvelrug",
            "3.2 Veluwe/Utrechtse heuvelrug",
            "3.3 Veluwe/Utrechtse heuvelrug",
            "4. Noord-Holland",
            "5. Randstad-Groene Hart",
            "5. Randstad-Groene Hart",
            "6. Rivierengebied",
            "6. Rivierengebied",
            "6. Rivierengebied",
        ],
        "deelregio": [12, 7, 8, 9, 2, 1, 2, 3, 1, 18, 10, 17, 18, 14, 17, 18],
        "pct": [8, 16, 66, 10, 99, 18, 48, 33, 97, 100, 94, 50, 50, 34, 38, 28],
    }
)

mapping["pct"] /= 100

my_path_effect = define_path_effect(linewidth=6, foreground="white", alpha=0.4)

run = "REF2017"

path_to_datafile = Path(
    f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/runs_owd/4-final/output_{run}.csv"
)

watervraag_types = ["Totaal"]  # "Beregening"]#, "Peilbeheer", "Doorspoeling", "Totaal"]

selected_months = ["July"]  # , "August"]

# bounds van Nederland
xmin, ymin, xmax, ymax = (0.0, 300000.0, 281000.0, 625000.0)

cmap = matplotlib.colormaps.get_cmap("RdYlBu_r")

for watervraag_type in watervraag_types:

    for selected_month in selected_months:
        print(f"reading and plotting {watervraag_type} for {run} in {selected_month}")

        data = read_watervraag(
            path_to_datafile,
            watervraag_type=watervraag_type,
            selected_months=selected_month,
        )

        data = data.rename(columns={"Nummer": "deelregio"})

        data["deelregio"] = pd.to_numeric(data["deelregio"])

        data["Watervraag gecorrigeerd"] = (1 - 0.19) * data["Watervraag"]

        result_veengebieden = data.merge(mapping, on="deelregio")

        result_veengebieden["watervraag_deelgebied"] = (
            result_veengebieden["Watervraag gecorrigeerd"]
            * result_veengebieden["pct"]
        )

        veengebieden_with_watervraag = veengebieden.merge(
            result_veengebieden, on="deelgebied"
        )

        deelgebied_gdf = veengebieden_with_watervraag.groupby(
            "deelgebied", as_index=False
        ).agg(
            {"watervraag_deelgebied": "sum", "geometry": "first", "id_num": "first"}
        )

        deelgebied_gdf = gpd.GeoDataFrame(
            deelgebied_gdf,
            geometry="geometry",
            crs=veengebieden_with_watervraag.crs,
        )

        # deelregios_with_watervraag["Watervraag gecorrigeerd"] = (
        #     1 - 0.19
        # ) * deelregios_with_watervraag[
        #     "Watervraag"
        # ]  # 19% decrease in inflow from Rijn

        if watervraag_type in ["Beregening", "Doorspoeling", "Peilbeheer"]:
            bounds = [0, 10, 20, 30, 40, 50]
        elif watervraag_type in ["Totaal"]:
            bounds = [0, 15, 30, 45, 60, 75]

        norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend="max")

        fig, ax = plt.subplots(figsize=(8.27, 11.69))

        ax.tick_params(
            axis="both",
            which="both",
            labelbottom=False,
            labelleft=False,
            bottom=False,
            left=False,
        )

        ax.set_title("Waterbeschikbaarheid in 2050", fontsize=14, loc="right")

        deelgebied_gdf.plot(
            ax=ax,
            column="watervraag_deelgebied",
            zorder=2,
            cmap=cmap,
            norm=norm,
            legend=True,
            legend_kwds={"shrink": 0.65, "label": r"m$^{3}$/s"},
        )

        deelgebied_gdf.boundary.plot(ax=ax, lw=0.5, color="black")

        provinces.boundary.plot(ax=ax, lw=0.4, color="grey")

        ax.set_xlim([xmin, xmax])
        ax.set_ylim([ymin, ymax])

        xtext = -100_000
        ytext = 620_000

        for x, y, label, deelgebied, nummer in zip(
            deelgebied_gdf.representative_point().x,
            deelgebied_gdf.representative_point().y,
            deelgebied_gdf["watervraag_deelgebied"],
            deelgebied_gdf["deelgebied"],
            deelgebied_gdf["id_num"],
        ):

            fontsize = 9

            if deelgebied == "2. Wieden-Weerribben":
                x -= 5_000
            elif deelgebied == "3.2 Veluwe/Utrechtse heuvelrug":
                fontsize = 8
                x -= 3_000
                y += 3_000
            elif deelgebied == "3.3 Veluwe/Utrechtse heuvelrug":
                fontsize = 8
                x -= 4_000

            ax_text(
                x=x,
                y=y,
                s=f"<{nummer}>",
                fontsize=fontsize,
                ax=ax,
                highlight_textprops=[
                    {"path_effects": my_path_effect, "color": "black"}
                ],
            )

            ax.text(
                x=xtext,
                y=ytext,
                s=rf"{deelgebied} ({label:.0f} m$^3$/s)",
                fontsize=7,
            )

            ytext -= 10_000

        # Define the position for the image axes
        ax_image = fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])

        # Display the image
        ax_image.imshow(image)
        ax_image.axis("off")  # Remove axis of the image

        ax.axis("off")

        figpath = Path(
            f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/figuren/shapes_veengebieden/2050/waterbeschikbaarheid_2050_deelregios_{selected_month}_1976.png"
        )

        plt.savefig(figpath, bbox_inches="tight", dpi=300)

        plt.close()
