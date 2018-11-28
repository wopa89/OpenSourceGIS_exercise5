#!/usr/bin/env python

import grass.script as gscript
import subprocess
import os


def main():

    # Path to the folder containing that data sets
    path_data = "/Users/chludwig/Development/git/OpenSourceGIS_exercise5/data/"

    # 0. Adjust the region of the mapset to your city ---------------------------

    # Create new layer containting the selected district
    gscript.run_command('v.extract', input='cities@PERMANENT', where="name='AK27'", output='studyarea')
    
    # Adjust GRASS GIS region to the study area
    gscript.run_command('g.region', vect='studyarea', align='rainfall@PERMANENT')

    # 1. Calculate average rainfall within the study area 
    # ----------------------------------------------------
    gscript.run_command('v.rast.stats', flags='c', map='studyarea', raster='rainfall@PERMANENT', column_prefix='rf', method='average,minimum')
    
    # Read and print value of column "rf_average"
    rf_average = gscript.read_command('v.db.select', map='studyarea', columns='rf_average')
    print("Average rainfall: " + rf_average.split("\n")[1])
    # Read and print value of column "rf_minimum" 
    rf_minimum = gscript.read_command('v.db.select', map='studyarea', columns='rf_minimum')
    print("Minimum rainfall: " + rf_minimum.split("\n")[1])


    # 2. Calculate number of hostels in Auckland 
    #---------------------------------------------

    # The data set 'osm_hostels.geojson' includes ways and their nodes. We only want to import the ways with the tag tourism=hostel
    # This can be done using v.in.ogr and the 'where' parameter. But in order to use this tool we need 
    # to reproject the data set first to EPSG:32760 using ogr2ogr.

    # Path to data set containing hostels
    path_hostels = os.path.join(path_data, 'nz_hostels.geojson')

    # Reproject the data set
    path_hostels_reprojected = os.path.join(path_data, 'nz_hostels_reprojected.geojson')
    subprocess.call(['ogr2ogr', '-f', 'geojson', '-t_srs', 'EPSG:32760', path_hostels_reprojected, path_hostels])
    
    # Importing the reprojected data set using v.in.ogr to be able to set the "where" parameter
    gscript.run_command('v.in.ogr', input =path_hostels_reprojected, layer='nz_hostels', output='hostels', where="tourism='hostel'")
    
    # Count the hostels within the study area
    NumberOfHostels = gscript.read_command('v.vect.stats', flags='p', points='hostels', areas='studyarea', type='point,centroid')
    print("Number of hostels: " + NumberOfHostels.split('|')[2])

    # 2.1 Calculate number of Pubs in Auckland using osm_pubs.geojson
    #-----------------------------------------------------------------

    # add code here ....


    # 4. Calculate total length of cycleways 
    # ----------------------------------------

    # Import data set with cycleways 
    path_cycleways = os.path.join(path_data, "osm_cycleways.geojson")
    gscript.run_command('v.import', input =path_cycleways, layer='osm_cycleways', output='cycleways')

    # Select cycleways within the study area and save them in new layer 'cyclewaysInStudyarea'
    gscript.run_command('v.select', ainput='cycleways', atype='line', binput='studyarea', btype='area', output='cyclewaysInStudyarea', operator='within')

    # Add a new column 'length' to the layer 'cyclewaysInStudyarea' 
    gscript.run_command('v.db.addcolumn', map='cyclewaysInStudyarea', columns='length double precision')

    # Calculate the length of each cycleway and store the result in the column 'length'
    gscript.run_command('v.to.db', map='cyclewaysInStudyarea', type='line', option='length', columns='length', units='kilometers')

    # Print the summary statistics for the column 'length'
    cyclewaysStatistics = gscript.read_command('v.db.univar', map='cyclewaysInStudyarea', column='length')
    print("Total length of cycleways: " + cyclewaysStatistics.split("\n")[9] + " km")


    # 3. Find the nearby airports 
    # ----------------------------

    # Calculate distances to all airports (calculation of distance in meters)
    # Not working --> gscript.run_command("v.distance", from="studyarea@Auckland", to="airports@PERMANENT", output="airport_distances", upload="dist,to_attr", column="airport,airport_distance", to_column="str_1", table="airport_distances", flags="a")
    # gscript.run_command('v.distance') does not work in this case due to a bug. Therefore we use subprocess.call() instead
    subprocess.call(["v.distance", '-a', 'from=studyarea', "to=airports@PERMANENT", "output=airport_distances", "upload=dist,to_attr", "column=airport_distance,airport", "from_type=centroid", "to_column=str_1", "table=airport_distances"])

    # Select and print airports that are within a 100 km radius (calculation of distance in meters)
    nearbyAirports = gscript.read_command('v.db.select', map='airport_distances', columns='airport,airport_distance', where='airport_distance <= 100000')
    print("Nearby airports (<100km): \n" + nearbyAirports)

    # Export airport distances to file 
    path_out_airportdistances = os.path.join(path_data, 'airport_distances.shp')
    gscript.run_command('v.out.ogr', input='airport_distances', output=path_out_airportdistances, format='ESRI_Shapefile')


if __name__ == '__main__':
    main()
