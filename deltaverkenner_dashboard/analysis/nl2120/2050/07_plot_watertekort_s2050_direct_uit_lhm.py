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

from deltaverkenner_dashboard.analysis.read_dashboard import read_watertekort


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

my_path_effect = define_path_effect(linewidth=6, foreground="white", alpha=0.4)

run = "S2050"

path_to_datafile = Path(
    f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/runs_deelregios/4-final/output_{run}.csv"
)

watervraag_types = ["Totaal"]

selected_months = ["July"]  # , "August"]

path_to_deelregios = r"n:/Projects/11209000/11209259/F. Other information/00 Scripts en GISbestanden/Gisbestanden/ZW_regios/ZW_deelregios.shp"
deelregios = gpd.read_file(path_to_deelregios)

# bounds van Nederland
xmin, ymin, xmax, ymax = (0.0, 300000.0, 281000.0, 625000.0)

cmap = matplotlib.colormaps.get_cmap("OrRd").copy()
cmap.set_under("#add8e6")

bounds = [0, 10, 20, 30, 40, 50]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend="max")

for watervraag_type in watervraag_types:

    for selected_month in selected_months:
        print(f"reading and plotting {watervraag_type} for {run} in {selected_month}")

        data = read_watertekort(
            path_to_datafile,
            watervraag_type=watervraag_type,
            selected_months=selected_month,
        )

        deelregios_with_watervraag = deelregios.merge(data, on="Nummer")

        deelregios_with_watervraag["Nummer"] = pd.to_numeric(
            deelregios_with_watervraag["Nummer"]
        )
        deelregios_with_watervraag = deelregios_with_watervraag.sort_values(
            by=["Nummer"]
        )

        fig, ax = plt.subplots(figsize=(8.27, 11.69))

        ax.tick_params(
            axis="both",
            which="both",
            labelbottom=False,
            labelleft=False,
            bottom=False,
            left=False,
        )

        ax.set_title(
            f"{run} - watertekort, {watervraag_type.lower()}", fontsize=14, loc="right"
        )

        deelregios_with_watervraag.plot(
            ax=ax,
            column="Watervraag",
            zorder=2,
            cmap=cmap,
            norm=norm,
            legend=False,
            # legend_kwds={"shrink": 0.65, "label": r"m$^{3}$/s"},
        )

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

        cbar = plt.colorbar(
            sm,
            ax=ax,
            extend="max",
            shrink=0.65,
            label=r"m$^{3}$/s",
        )

        deelregios_with_watervraag.boundary.plot(ax=ax, lw=0.3, color="black")

        ax.set_xlim([xmin, xmax])
        ax.set_ylim([ymin, ymax])

        xtext = -100_000
        ytext = 620_000

        for x, y, label, deelregio, deelregio_legenda, nummer in zip(
            deelregios_with_watervraag.centroid.x,
            deelregios_with_watervraag.centroid.y,
            deelregios_with_watervraag["Watervraag"],
            deelregios_with_watervraag["Naam"],
            deelregios_with_watervraag["deelregio"],
            deelregios_with_watervraag["Nummer"],
        ):

            fontsize = 9

            if deelregio == "Rivierengebied Noord":
                x -= 15_000
            elif deelregio == "Rivierengebied Zuid":
                x += 22_500
                y += 3_000
            elif deelregio == "Zuidwestelijke Delta zonder aanvoer":
                x -= 6_000
                y += 5_000
            elif deelregio == "Noord Holland Noord":
                x -= 12_000
            elif deelregio == "Noord Drenths plateau":
                y += 8_000
            elif deelregio == "West met bovenregionale aanvoer":
                x -= 8_000
            elif deelregio == "Hoge Zandgronden Oost met aanvoer":
                x -= 8_000
            elif deelregio == "Noord Aanvoergebied voor Gaarkeuken":
                x -= 10_000
            elif deelregio == "Noord Waddeneilanden":
                y -= 18_500
                x -= 32_000
                fontsize = 8.5

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
                s=rf"{deelregio_legenda} ({label:.0f} m$^3$/s)",
                fontsize=7,
            )

            ytext -= 10_000

        # Define the position for the image axes
        ax_image = fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])

        # Display the image
        ax_image.imshow(image)

        # Remove axis of the image
        ax_image.axis("off")

        ax.axis("off")

        figpath = Path(
            f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/figuren/2050/Voor Dimmie 2026_08_28/Figuren Dimmie/07_{run}_watertekort_{watervraag_type.lower()}_deelregios_{selected_month}_1976.png"
        )

        plt.savefig(figpath, bbox_inches="tight", dpi=300)

        plt.close()

        deelregios_with_watervraag = deelregios_with_watervraag.drop(
            columns=["geometry"]
        )

        deelregios_with_watervraag = deelregios_with_watervraag.rename(
            columns={"Watervraag": "Watertekort (m3/s)"}
        )

        outputpath = f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/figuren/2050/Voor Dimmie 2026_08_28/csv's Dimmie/07_{run}_watertekort_{watervraag_type.lower()}_deelregios_{selected_month}_1976.csv"

        deelregios_with_watervraag.to_csv(outputpath, index=False)
