from deltaverkenner_dashboard.deltapolder.visualisation.map_config import REGIONS

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1 import make_axes_locatable

POINT_STYLE = {
    "markercolor": "red",
    "edgecolor": "black",
    "label": "Waterbron",
    "markersize": 30,
}


def get_region_colors(gdf, region_type):
    column = REGIONS[region_type]["column"]
    color_dict = REGIONS[region_type]["colors"]

    colors = gdf[column].map(color_dict)

    missing = sorted(gdf.loc[colors.isna(), column].dropna().unique())

    if missing:
        raise ValueError(
            f"Missing colour definitions for {region_type}: " f"{', '.join(missing)}"
        )

    return colors


def add_count_box(ax, count, x, y, title="Aantal waterbronnen"):
    ax.text(
        x,
        y,
        f"{title}:\n{count}",
        fontsize=10,
    )


def plot_waterbronnen(
    data, region_shapefile, figpath, region_type="hoofdregios", axis_title=""
):
    # idea for another name: plot_point_map

    region_config = REGIONS[region_type]

    fig, ax = plt.subplots(figsize=(8.27, 11.69))

    ax.tick_params(
        axis="both",
        which="both",
        labelbottom=False,
        labelleft=False,
        bottom=False,
        left=False,
    )

    fill = region_config["fill"]

    plot_kwargs = {
        "ax": ax,
        "lw": 0.5,
        "edgecolor": region_config["edgecolor"],
    }

    if fill:
        plot_kwargs["color"] = get_region_colors(
            region_shapefile,
            region_type,
        )
    else:
        plot_kwargs["facecolor"] = "none"

    region_shapefile.plot(**plot_kwargs)

    data.plot(
        ax=ax,
        color=POINT_STYLE["markercolor"],
        edgecolor=POINT_STYLE["edgecolor"],
        markersize=POINT_STYLE["markersize"],
    )

    xmin, ymin, xmax, ymax = region_shapefile.total_bounds

    xtext = xmin - 0.0135 * (xmax - xmin)
    ytext = ymax - 0.02 * (ymax - ymin)

    add_count_box(ax, len(data), xtext, ytext)

    legend_markersize = POINT_STYLE["markersize"] ** 0.5

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=POINT_STYLE["label"],
            markerfacecolor=POINT_STYLE["markercolor"],
            markeredgecolor=POINT_STYLE["edgecolor"],
            markersize=legend_markersize,
        )
    ]

    legend = ax.legend(
        handles=legend_elements,
        bbox_to_anchor=(0.225, 0.90),
        frameon=False,
        title="Legenda:",
    )

    legend._legend_box.align = "left"

    if axis_title:
        ax.set_title(axis_title, fontsize=14)

    plt.savefig(figpath, bbox_inches="tight", dpi=300)

    plt.close()


def plot_distance_map(waterbronnen, lsw, figpath, axis_title=""):

    fig, ax = plt.subplots(figsize=(8.27, 11.69))

    ax.tick_params(
        axis="both",
        which="both",
        labelbottom=False,
        labelleft=False,
        bottom=False,
        left=False,
    )

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="4%", pad=0.1)

    lsw.plot(
        ax=ax,
        column="afstand_tot_waterbron_m",
        cmap="RdYlBu_r",
        legend=True,
        legend_kwds={
            "label": "m",
        },
        cax=cax,
    )

    waterbronnen.plot(
        ax=ax,
        color=POINT_STYLE["markercolor"],
        edgecolor=POINT_STYLE["edgecolor"],
        markersize=POINT_STYLE["markersize"],
    )

    xmin, ymin, xmax, ymax = lsw.total_bounds

    xtext = xmin - 0.0135 * (xmax - xmin)
    ytext = ymax - 0.02 * (ymax - ymin)

    add_count_box(ax, len(waterbronnen), xtext, ytext)

    legend_markersize = POINT_STYLE["markersize"] ** 0.5

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=POINT_STYLE["label"],
            markerfacecolor=POINT_STYLE["markercolor"],
            markeredgecolor=POINT_STYLE["edgecolor"],
            markersize=legend_markersize,
        )
    ]

    legend = ax.legend(
        handles=legend_elements,
        bbox_to_anchor=(0.235, 0.90),
        frameon=False,
        title="Legenda:",
    )

    legend._legend_box.align = "left"

    if axis_title:
        ax.set_title(axis_title, fontsize=14)

    plt.savefig(figpath, bbox_inches="tight", dpi=300)

    plt.close()
