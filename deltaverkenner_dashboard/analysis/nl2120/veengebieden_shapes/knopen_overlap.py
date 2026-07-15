from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


# Open an image from a computer
def open_image_local(path_to_image):
    image = Image.open(path_to_image)  # Open the image
    width_px, height_px = image.size
    aspect_ratio = width_px / height_px
    image_array = np.array(image)  # Convert to a numpy array
    return (width_px, height_px, aspect_ratio, image_array)  # Output)


# Open the image from my computer
width_px, height_px, aspect_ratio, image = open_image_local(
    r"c:/Users/reusen/OneDrive - Stichting Deltares/Documents/Deltares Huisstijl/Deltares_logo_D-blauw_RGB/Deltares_logo_D-blauw_RGB/Deltares_logo_D-blauw_RGB.png"
)

# Define the position and size parameters
image_xaxis = 0.145
image_yaxis = 0.18
image_width = 0.15
image_height = image_width / aspect_ratio  # Same as width since our logo is a square

#################################################################
# provinces (for plot)
#################################################################

path_to_provinces_shapefile = "p:/11207812-somers-ontwikkeling/1-data/1-external/Bestuurlijke_grenzen/provincial_boundaries_2025.shp"
provinces = gpd.read_file(path_to_provinces_shapefile)

#################################################################
# DM links
#################################################################

# path_mz_districts = Path(
#     "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/Districten_knopen_takken/regios_districten.shp"
# )

# districts = gpd.read_file(path_mz_districts)

# districts = districts.drop_duplicates(subset="DWRN")

path_dm_nodes = Path(
    "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/Districten_knopen_takken/nodes_gekoppeld_v2.shp"
)

nodes = gpd.read_file(path_dm_nodes)

#################################################################
# veengebieden shapes
#################################################################

path_veengebieden_shapes = "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/shapes_veengebieden/shapes_deelgebieden_veen.shp"

veengebieden = gpd.read_file(path_veengebieden_shapes)

################################################################
# intersection between the polygons
################################################################

# district_points = districts.copy()
# district_points["geometry"] = district_points.geometry.representative_point()


# centroid_overlap = gpd.sjoin(
#     district_points, veengebieden, predicate="within", how="inner"
# )

# districts_in_veen = districts[districts["DWRN"].isin(centroid_overlap["DWRN"])]


# # intersection = gpd.overlay(districts, veengebieden, keep_geom_type=False)

# # intersection["overlap_area"] = intersection.area


# # district_area = districts.set_index("DWRN").area

# # intersection["pct_district"] = (
# #     intersection["overlap_area"] / intersection["DWRN"].map(district_area) * 100
# # )

# # districts_in_veengebieden = districts[districts["DWRN"].isin(intersection.drop_duplicates(subset="DWRN")["DWRN"])]

print("Done!")

#########
# make a simple plot
#########

xmin, ymin, xmax, ymax = (0.0, 300000.0, 281000.0, 625000.0)

fig, ax = plt.subplots(figsize=(8.27, 11.69))

ax.tick_params(
    axis="both",
    which="both",
    labelbottom=False,
    labelleft=False,
    bottom=False,
    left=False,
)

nodes.plot(ax=ax, markersize=5)

# # districts.boundary.plot(ax=ax, lw=0.3, color="grey")


# # districts.plot(ax=ax, color="orange")
# # centroid_overlap.plot(ax=ax, markersize=5, facecolor="green", edgecolor="black")

# districts.plot(ax=ax, facecolor="lightblue", edgecolor="grey", linewidth=0.3)

# # intersection.plot(ax=ax)
# districts_in_veen.plot(ax=ax, facecolor="green", edgecolor="grey", linewidth=0.3)
# district_points.plot(
#     ax=ax, markersize=5, facecolor="lightblue", edgecolor="black", linewidth=0.3
# )
# centroid_overlap.plot(ax=ax, markersize=5, facecolor="green", edgecolor="black")

veengebieden.plot(ax=ax, facecolor="orange", alpha=0.5)

veengebieden.boundary.plot(ax=ax, lw=1, color="black", alpha=1)

provinces.boundary.plot(ax=ax, lw=0.5, color="black")

ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])

# Define the position for the image axes
ax_image = fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])

# Display the image
ax_image.imshow(image)
ax_image.axis("off")  # Remove axis of the image

ax.axis("off")

figpath = Path(
    "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/figuren/shapes_veengebieden/dm_knopen_in_veengebieden.png"
)

plt.savefig(figpath, bbox_inches="tight", dpi=300)

plt.close()
