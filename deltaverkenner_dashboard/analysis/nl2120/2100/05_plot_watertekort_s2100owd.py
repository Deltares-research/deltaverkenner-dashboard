from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib as mpl
import numpy as np
import cmocean
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

my_path_effect = define_path_effect(linewidth=6, foreground="white", alpha=0.4)

run_nrs = {"BP18REF2017_slr0": "1", "BP18STOOM2050_slr0.5": "5"}

run1 = "REF2017"
run2 = "S2100"

runs = [run1, run2]
s2100owds = [False, True]

watervraag_types = ["Totaal"]  # "Beregening"]#, "Peilbeheer", "Doorspoeling", "Totaal"]

selected_months = ["July"]  # , "August"]

path_to_deelregios = r"n:/Projects/11209000/11209259/F. Other information/00 Scripts en GISbestanden/Gisbestanden/ZW_regios/ZW_deelregios.shp"
deelregios = gpd.read_file(path_to_deelregios)

# bounds van Nederland
xmin, ymin, xmax, ymax = (0.0, 300000.0, 281000.0, 625000.0)

cmap = matplotlib.colormaps.get_cmap("OrRd").copy()
cmap.set_under("#add8e6")

bounds = [0, 10, 20, 30, 40, 50]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N, extend="max")  # , clip=True)

for watervraag_type in watervraag_types:
    for selected_month in selected_months:

        data_dict = {}

        for run, s2100owd in zip(runs, s2100owds):
            print(f"Reading data for {run}, {watervraag_type}, and {selected_month}")
            path_to_datafile = Path(
                f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/runs_owd/4-final/output_{run}.csv"
            )

            data = read_watervraag(
                path_to_datafile,
                watervraag_type=watervraag_type,
                selected_months=selected_month,
                S2100_owd=s2100owd
            )

            deelregios_with_watervraag = deelregios.merge(data, on="Nummer")

            deelregios_with_watervraag["Nummer"] = pd.to_numeric(
                deelregios_with_watervraag["Nummer"]
            )
            deelregios_with_watervraag = deelregios_with_watervraag.sort_values(
                by=["Nummer"]
            )

            if run in ["REF2017"]:
                deelregios_with_watervraag["Watervraag gecorrigeerd"] = (
                    1 - 0.27
                ) * deelregios_with_watervraag["Watervraag"]

            data_dict[run] = deelregios_with_watervraag

        diff = data_dict[run2]
        diff[f"Difference with {run1}"] = (
            data_dict[run2]["Watervraag"] - data_dict[run1]["Watervraag gecorrigeerd"]
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

        # First line (centered)
        ax.text(
            0.7,
            1.04,
            f"Watertekort in {run2}",
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=14,
        )

        cs = diff.plot(
            ax=ax,
            column=f"Difference with {run1}",
            zorder=2,
            cmap=cmap,
            norm=norm,
            legend=False,
        )

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

        cbar = plt.colorbar(
            sm,
            ax=ax,
            extend="both",
            shrink=0.65,
            label=r"m$^{3}$/s",
        )

        diff.boundary.plot(ax=ax, lw=0.3, color="black")

        ax.set_xlim([xmin, xmax])
        ax.set_ylim([ymin, ymax])

        xtext = -100_000
        ytext = 620_000

        for x, y, label, deelregio, deelregio_legenda, nummer in zip(
            diff.centroid.x,
            diff.centroid.y,
            diff[f"Difference with {run1}"],
            diff["Naam"],
            diff["deelregio"],
            diff["Nummer"],
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
                # s=f"<{label:.0f}>",
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
        ax_image.axis("off")  # Remove axis of the image

        ax.axis("off")

        figpath = Path(
            f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/figuren/2100/Figuren Dimmie/05_watertekort_{run2}owd_deelregios_{selected_month}_1976.png"
        )

        plt.savefig(figpath, bbox_inches="tight", dpi=300)

        plt.close()

        deelregios_with_watervraag = deelregios_with_watervraag.drop(
            columns=["geometry", "Watervraag"]
        )

        deelregios_with_watervraag = deelregios_with_watervraag.rename(
            columns={"Difference with REF2017": "Watertekort (m3/s)"}
        )

        outputpath = f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/figuren/2100/csv's Dimmie/05_watertekort_{run2}owd_deelregios_{selected_month}_1976.csv"

        deelregios_with_watervraag.to_csv(outputpath, index=False)
