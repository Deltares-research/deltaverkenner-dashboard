from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import cmocean
from highlight_text import ax_text

from read_dashboard import read_watervraag


# bron voor gehighlighte text: https://python-graph-gallery.com/advanced-custom-annotations-matplotlib/
def define_path_effect(**kwargs):
    return [path_effects.Stroke(**kwargs), path_effects.Normal()]


my_path_effect = define_path_effect(linewidth=6, foreground="white", alpha=0.4)

runs = {"BP18REF2017_slr0_afvoer2018": "1", "BP18STOOM2050_slr0.5_afvoer2018": "5"}

run = "BP18STOOM2050_slr0.5_afvoer2018"

path_to_datafile = Path(
    f"p:/11212687-deltaverkenner2026/Zoetwater/deltaverkenner-data/data/3-results/long/{runs[run]}.csv"
)

watervraag_types = ["Beregening", "Peilbeheer", "Doorspoeling", "Totaal"]

# selected_month = "July"
selected_months = ["July", "August"]

for watervraag_type in watervraag_types:
    for selected_month in selected_months:
        print(f"reading and plotting {watervraag_type} for {run} in {selected_month}")

        data = read_watervraag(
            path_to_datafile, watervraag_type=watervraag_type, selected_months=selected_month
        )

        path_to_deelregios = r"n:\Projects\11209000\11209259\F. Other information\00 Scripts en GISbestanden\Gisbestanden\ZW_regios\ZW_deelregios.shp"
        deelregios = gpd.read_file(path_to_deelregios)

        deelregios_with_watervraag = deelregios.merge(data, on="Nummer")
        # bounds van Nederland
        xmin, ymin, xmax, ymax = (0.0, 300000.0, 281000.0, 625000.0)

        cmap = matplotlib.colormaps.get_cmap("winter_r")
        newcmap = cmocean.tools.crop_by_percent(cmap, 40, which="max", N=None)

        fig, ax = plt.subplots(figsize=(8.27, 11.69))

        ax.tick_params(
            axis="both",
            which="both",
            labelbottom=False,
            labelleft=False,
            bottom=False,
            left=False,
        )

        ax.set_title(f"{run} - watervraag, {watervraag_type.lower()}", fontsize=14)

        # provinces.boundary.plot(ax=ax, lw=0.5, color="black")
        deelregios_with_watervraag.plot(ax=ax, column="Watervraag", zorder=2, cmap=newcmap)
        deelregios_with_watervraag.boundary.plot(ax=ax, lw=0.3, color="black")

        ax.set_xlim([xmin, xmax])
        ax.set_ylim([ymin, ymax])

        for x, y, label, deelregio in zip(
            deelregios_with_watervraag.centroid.x,
            deelregios_with_watervraag.centroid.y,
            deelregios_with_watervraag["Watervraag"],
            deelregios_with_watervraag["Naam"],
        ):
            # ax.annotate(
            #     f"{label:.2f}",
            #     xy=(x, y),
            #     xycoords="data",
            #     zorder=3,
            # )

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

            ax_text(
                x=x,
                y=y,
                s=f"<{label:.2f}>",
                fontsize=9,
                ax=ax,
                highlight_textprops=[{"path_effects": my_path_effect, "color": "black"}],
            )

        figpath = Path(
            f"p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/2-output/figuren/{run}_watervraag_{watervraag_type.lower()}_deelregios_{selected_month}_1976.png"
        )

        # plt.show()

        plt.savefig(figpath, bbox_inches="tight", dpi=300)

        plt.close()
