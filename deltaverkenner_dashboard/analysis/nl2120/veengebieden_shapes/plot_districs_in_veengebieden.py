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
# mz districts
#################################################################

path_mz_districts = Path(
    "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/Districten_knopen_takken/regios_districten.shp"
)

districts = gpd.read_file(path_mz_districts)

districts = districts.drop_duplicates(subset="DWRN")
#################################################################
# veengebieden shapes
#################################################################

path_veengebieden_shapes = "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/shapes_veengebieden/shapes_deelgebieden_veen.shp"

veengebieden = gpd.read_file(path_veengebieden_shapes)

################################################################
# intersection between the polygons
################################################################

districtnrs_in_veengebieden = {
    "1": [508, 503, 507, 502, 504, 505, 4, 5, 144, 6, 607],
    "2": [13],
    "3.1": [105, 106, 15],
    "3.2": [282],
    "3.3": [401, 402, 403, 404],
    "4": [361, 351, 353, 341, 352, 821],
    "5": [
        954,
        980,
        979,
        981,
        371,
        391,
        810,
        971,
        392,
        395,
        396,
        394,
        393,
        43,
        969,
        968,
        967,
        972,
        955,
        956,
        42,
        957,
        970,
        984,
        974,
    ],
    "6": [
        53,
        55,
        44,
        42,
        43,
        45,
        965,
        463,
        464,
        462,
        461,
        471,
        472,
        959,
        983,
        961,
        962,
        213,
        966,
        475,
        92,
        963,
        964,
        84,
    ],
}

districtnrs_in_veengebieden_list = [
    value for values in districtnrs_in_veengebieden.values() for value in values
]

districts_in_veengebied = districts[
    districts["DWRN"].isin(districtnrs_in_veengebieden_list)
]

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

districts.plot(ax=ax, facecolor="lightblue", edgecolor="grey", linewidth=0.3)

districts_in_veengebied.plot(ax=ax, facecolor="green")

veengebieden.plot(ax=ax, facecolor="orange", alpha=0.5)

veengebieden.boundary.plot(ax=ax, lw=1, color="black", alpha=1)

ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])

# Define the position for the image axes
ax_image = fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])

# Display the image
ax_image.imshow(image)
ax_image.axis("off")  # Remove axis of the image

ax.axis("off")

figpath = Path(
    "p:/11212687-deltaverkenner2026/Zoetwater/Dashboard/data/nl2120/figuren/shapes_veengebieden/mz_districts_in_veengebieden_26-07-31.png"
)

plt.savefig(figpath, bbox_inches="tight", dpi=300)

plt.close()
