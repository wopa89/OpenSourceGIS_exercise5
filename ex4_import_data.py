#!/usr/bin/env python

import grass.script as gscript

# subprocess is a Python module that lets you execute processes in the command
# line from within your python script e.g. gdal_transform. 
import subprocess

def main():

    # Path to the folder containing all data to be imported
    path_data = '/Users/chludwig/Data/ex04/'

    # 0. Import cities (survey capture areas)
    path_cities = path_data + '/nz_cities/nz-survey-capture-areas-sca.shp'
    gscript.run_command('v.in.ogr', input=path_cities, output='cities')

    # 1. Importing railways (nz_railway.shp) ---------------------------------
    path_railways = path_data + '/nz_railway/nz_railway.shp'
    gscript.run_command('v.in.ogr', input=path_railways, output='railways')

    # 2. Importing rainfall data (avg_annual_rainfall.tif) -------------------
    path_rainfall = path_data + '/avg_annual_rainfall.tif'
    path_rainfall_corrected = '/Users/chludwig/Data/ex04/avg_annual_rainfall_corrected.tif'

    # Use gdal_translate to assign the correct crs to the avg_annual_rainfall.tif
    subprocess.call(['gdal_translate', '-a_srs', 'EPSG:4326', path_rainfall, path_rainfall_corrected])

    # Import the corrected avg_annual_rainfall_corrected.tif into GRASS 
    gscript.run_command('r.import', input=path_rainfall_corrected, output='rainfall')
    
    # 3. Importing sealed roads (nz_road.shp) --------------------------------
    path_roads = path_data + '/nz_road/nz_road.shp'
    path_roads_reprojected = '/Users/chludwig/Data/ex04/nz_road/nz_road_reprojected.shp'

    # Repoject nz_roads.shp using OGR2OGR
    subprocess.call(['ogr2ogr', '-f', 'ESRI Shapefile', '-t_srs', 'EPSG:32760', path_roads_reprojected, path_roads])

    # Import the reprojected roads file into GRASS GIS
    gscript.run_command('v.in.ogr', input=path_roads_reprojected, layer='nz_road_reprojected', output='sealed_roads', where="surface='sealed'")

    # 4. Importing airports (nz_airports.csv) --------------------------------
    path_airports = path_data + '/nz_airport.csv'
    gscript.run_command('v.in.ascii', input=path_airports, output='airports', separator='comma', skip=1, x=4, y=5)

    # 5. Set region to match rainfall dataset --------------------------------
    gscript.run_command('g.region', rast='rainfall@PERMANENT')

    # Print some information about the mapset to check if everything worked 
    # Print projection of mapset 
    gscript.run_command('g.proj', flags='p')
    # Print extent of region 
    gscript.run_command('g.region', flags='p')
    # List all raster and vector layers 
    gscript.run_command('g.list', type='vector')
    gscript.run_command('g.list', type='raster')

    print('Importing data done.')

if __name__ == '__main__':
    main()
