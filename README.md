# Burlington Tiny Home Parcel Calculation Project

We're trying to figure out how many parcels in the NNE of Burlington VT have backyards small enough to fit a minimum size 350 sqft tiny home on them, taking into account setbacks, and the fact that parcels are not always rectangular. We will use this information to argue with the Planning Commission that zoning needs to be changed to allow tiny homes in the NNE and beyond.

## What Has Alex Done So Far?

He's downloaded the parcel data (`Tax_Parcels.geojson`) from data.burlingtonvt.gov and verified that his parcel exists. He's also downloaded Vermont building structure geometry data (`Vermont.geojson`) and found that the `162116` index of the `features` array contains his home. So this verifies that these two geojson's together can help us figure out how parcels and how size of backyards.

## Work To Do

[ ] Determine the boundaries for the NNE (i.e. a set of coordinates) and bound the parcel data to that area.
[ ] Write a function that, given a parcel and its coordinates from `Tax_Parcels.geojson`, returns the building structure in `Vermont.geojson` that is on that parcel. This will allow us to determine the size of the backyard for that parcel by subtracking out the structure, and using the placement of the structure to determine what the frontyard is, and remove that.
[ ] Write a function that, given a backyard size, returns whether or not it is large enough to fit a 350 sqft tiny home.
[ ] Finally, iterate through all of the parcels in `Tax_Parcels.geojson` and determine how many of them have backyards large enough to fit a 350 sqft tiny home. Also include what percentage of the total number of parcels have backyards large enough to fit a 350 sqft tiny home.