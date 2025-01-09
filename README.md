# Burlington Tiny Home Parcel Calculation Project

We're trying to figure out how many parcels in the NNE of Burlington VT have backyards large enough to fit a minimum size 350 sqft tiny home on them, taking into account setbacks, and the fact that parcels are not always rectangular (they can sometimes be more complex polygons). We will use this information to argue with the Planning Commission that zoning needs to be changed to allow tiny homes in the NNE and beyond.

## The Data

`Tax_Parcels.geojson` is downloaded from [data.burlingtonvt.gov](https://data.burlingtonvt.gov/maps/8f26c016d0ba4fb6af7688668a4b6e81/about) and holds the geometries of land parcels in Burlington Vermont. `Vermont.geojson` is downloaded from Microsoft's [USBuildingFootprint](https://github.com/microsoft/USBuildingFootprints) and holds the geometries of buildings in Burlington.

## Setup

Note, this project was developed on a Mac, and I'm not sure how well it will work on Windows.

Also note you will need [`gdal`](https://formulae.brew.sh/formula/gdal) and [`docker`](https://docs.docker.com/engine/install/)

```bash
# make your virtual environment and install dependencies
python -m venv ~/path/to/virtualenvs/burlington_tiny_home_lots
source ~/path/to/virtualenvs/burlington_tiny_home_lots/bin/activate
pip install -r requirements.txt

# setup the postgis docker container, transform the raw data,
# load it into postgres, and build the appropriate tables
./setup.sh

# finally, run the analysis
python main.py
```
