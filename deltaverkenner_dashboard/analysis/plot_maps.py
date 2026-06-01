from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib as mpl
import cmocean
from highlight_text import ax_text

from read_dashboard import read_watervraag


# bron voor gehighlighte text: https://python-graph-gallery.com/advanced-custom-annotations-matplotlib/
def define_path_effect(**kwargs):
    return [path_effects.Stroke(**kwargs), path_effects.Normal()]


my_path_effect = define_path_effect(linewidth=6, foreground="white", alpha=0.4)

runs = {"BP18REF2017_slr0": "1", "BP18STOOM2050_slr0.5": "5"}

run = "BP18STOOM2050_slr0.5"  # "BP18REF2017_slr0"

path_to_datafile = Path(
    f"p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-results/long/{runs[run]}.csv"
)

watervraag_types = ["Beregening", "Peilbeheer", "Doorspoeling", "Totaal"]

selected_months = ["July", "August"]

for watervraag_type in watervraag_types:

    for selected_month in selected_months:
        print(f"reading and plotting {watervraag_type} for {run} in {selected_month}")

        data = read_watervraag(
            path_to_datafile,
            watervraag_type=watervraag_type,
            selected_months=selected_month,
        )

        path_to_deelregios = r"n:\Projects\11209000\11209259\F. Other information\00 Scripts en GISbestanden\Gisbestanden\ZW_regios\ZW_deelregios.shp"
        deelregios = gpd.read_file(path_to_deelregios)

        deelregios_with_watervraag = deelregios.merge(data, on="Nummer")

        deelregios_with_watervraag["Nummer"] = pd.to_numeric(
            deelregios_with_watervraag["Nummer"]
        )
        deelregios_with_watervraag = deelregios_with_watervraag.sort_values(
            by=["Nummer"]
        )

        # bounds van Nederland
        xmin, ymin, xmax, ymax = (0.0, 300000.0, 281000.0, 625000.0)

        # cmap = matplotlib.colormaps.get_cmap("winter_r")
        # newcmap = cmocean.tools.crop_by_percent(cmap, 40, which="max", N=None)

        cmap = matplotlib.colormaps.get_cmap("RdYlBu_r")
        # newcmap = cmocean.tools.crop_by_percent(cmap, 40, which="max", N=None)

        if (runs[run] in ["1", "5"]) and (
            watervraag_type in ["Beregening", "Doorspoeling", "Peilbeheer"]
        ):
            bounds = [0, 10, 20, 30, 40, 50]
        elif (runs[run] in ["1", "5"]) and (watervraag_type in ["Totaal"]):
            bounds = [0, 20, 40, 60, 80, 100]

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

        ax.set_title(
            f"{run} - watervraag, {watervraag_type.lower()}", fontsize=14, loc="right"
        )

        deelregios_with_watervraag.plot(
            ax=ax,
            column="Watervraag",
            zorder=2,
            cmap=cmap,
            norm=norm,
            legend=True,
            legend_kwds={"shrink": 0.65, "label": r"m$^{3}$/s"},
        )

        deelregios_with_watervraag.boundary.plot(ax=ax, lw=0.3, color="black")

        ax.set_xlim([xmin, xmax])
        ax.set_ylim([ymin, ymax])

        xtext = -80_000
        ytext = 620_000

        for x, y, label, deelregio, deelregio_legenda, nummer in zip(
            deelregios_with_watervraag.centroid.x,
            deelregios_with_watervraag.centroid.y,
            deelregios_with_watervraag["Watervraag"],
            deelregios_with_watervraag["Naam"],
            deelregios_with_watervraag["deelregio"],
            deelregios_with_watervraag["Nummer"],
        ):
            # ax.annotate(
            #     f"{label:.2f}",
            #     xy=(x, y),
            #     xycoords="data",
            #     zorder=3,
            # )

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
                s=deelregio_legenda,
                fontsize=7,
            )

            ytext -= 10_000

        ax.axis("off")
        # cbax = fig.add_axes([0.95, 0.3, 0.03, 0.39])
        # cbax.set_title('Population')
        # fig.colorbar(cs, ax=cbax)

        figpath = Path(
            f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/2-output/figuren/{run}_watervraag_{watervraag_type.lower()}_deelregios_{selected_month}_1976.png"
        )

        # plt.show()

        plt.savefig(figpath, bbox_inches="tight", dpi=300)

        plt.close()
