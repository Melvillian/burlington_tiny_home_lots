# Burlington Tiny Home Parcel Calculation Project

We're trying to figure out how many parcels in the NNE of Burlington VT have backyards large enough to fit a minimum size 350 sqft tiny home on them, taking into account setbacks, and the fact that parcels are not always rectangular (they can sometimes be more complex polygons). We will use this information to argue with the Planning Commission that zoning needs to be changed to allow tiny homes in the NNE and beyond.

## The Data

`Tax_Parcels.geojson` is downloaded from [data.burlingtonvt.gov](https://data.burlingtonvt.gov/maps/8f26c016d0ba4fb6af7688668a4b6e81/about) and holds the geometries of land parcels in Burlington Vermont. `Vermont.geojson` is downloaded from Microsoft's [USBuildingFootprint](https://github.com/microsoft/USBuildingFootprints) and holds the geometries of buildings in Burlington.

## Setup and Running the Analysis

Note, this project was developed on a Mac, and I'm not sure how well it will work on Windows.

Also note you will need [`gdal`](https://formulae.brew.sh/formula/gdal) and [`docker`](https://docs.docker.com/engine/install/)

```bash
# make your virtual environment and install dependencies
python -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt

# setup the postgis docker container, transform the raw data,
# load it into postgres, and build the appropriate tables
./setup.sh

# finally, run the analysis, this will take many hours (sorry!)
python main.py
```

## Visualization

Once you've completed the analysis above, the `tiny_home_structure` column of the `buildable_parcel_areas` table will be populated with a non-empty string geometry value iff the a 350 sqft home can be built on that parcel. You can then run

`python visualize_buildable_parcels.py`

and it will plot 10 of the parcels in blue along with each parcel's 350 sqft rectangular home in red. Keep closing each plot to have the script generate the next one

## Initial Findings (note, don't use this, I have found bugs in the rectangle-finding algorithm that says it's found a rectangle that fits when really it doesnt. More work must be done!)

Found 3712 parcels out of 8000 that could fit a 350 sq ft tiny home

Found 3356 parcels out of 8000 that could NOT fit a 350 sq ft tiny home

Found 932 parcels out of 8000 that where something went wrong and we didn't process them correctly
