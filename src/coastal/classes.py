"""MapBiomas classes present in AULINOR, grouped for the analysis and the figures.

Groups and colors follow the brand palette (see style.py). Class names in English
come from the MapBiomas legend.
"""

# class_id: (name, group)
CLASSES = {
    3: ("Forest Formation", "Forest"),
    9: ("Forest Plantation", "Forestry"),
    11: ("Wetland", "Wetland and grassland"),
    12: ("Grassland", "Wetland and grassland"),
    15: ("Pasture", "Pasture, crops and mosaic"),
    21: ("Mosaic of Uses", "Pasture, crops and mosaic"),
    23: ("Beach, Dune and Sand Spot", "Beach and dune"),
    24: ("Urban Area", "Urban"),
    25: ("Other non Vegetated Areas", "Other non-vegetated"),
    33: ("River, Lake and Ocean", "Water"),
    39: ("Soybean", "Pasture, crops and mosaic"),
    40: ("Rice", "Pasture, crops and mosaic"),
    41: ("Other Temporary Crops", "Pasture, crops and mosaic"),
    49: ("Wooded Sandbank Vegetation", "Restinga"),
    50: ("Herbaceous Sandbank Vegetation", "Restinga"),
}
URBAN = 24

# Stacking order, bottom to top (urban on top), and brand colors
GROUPS = {
    "Water": "#DAD2CC",
    "Wetland and grassland": "#CDD7C5",
    "Forest": "#5C704C",
    "Restinga": "#93A97E",
    "Beach and dune": "#FDD34A",
    "Pasture, crops and mosaic": "#FED2BF",
    "Forestry": "#7B2405",
    "Other non-vegetated": "#9C9A8C",
    "Urban": "#D94400",
}

# Ecosystems that protect the coast and are hard to recover once built over
SENSITIVE = ["Wetland and grassland", "Restinga", "Beach and dune"]
