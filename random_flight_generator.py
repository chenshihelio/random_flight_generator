import pandas as pd
import os
import numpy as np
from sys import exit

earth_radius = 6371
nm_to_km = 1.852

def calc_distance(lat1,lon1,lat2,lon2):
    return 2 * earth_radius * np.arcsin(np.sqrt( (np.sin((lat2-lat1)/2))**2 + 
                    np.cos(lat1)*np.cos(lat2)*(np.sin((lon2-lon1)/2))**2))

# read and pre-process data
if not os.path.exists('./airport_large.csv'):
    if not os.path.exists('./airport.csv'):
        data =pd.read_csv("https://davidmegginson.github.io/ourairports-data/airports.csv")
    else:
        data = pd.read_csv('./airport.csv')

    data_small = data.loc[data['type']=='small_airport']
    data_medium = data.loc[data['type']=='medium_airport']
    data_large = data.loc[data['type']=='large_airport']

    data_small.to_csv('./airport_small.csv')
    data_medium.to_csv('./airport_medium.csv')
    data_large.to_csv('./airport_large.csv')


min_distance = int(input(" Minimum distance (nm): "))
max_distance = int(input(" Maximum distance (nm): "))

if max_distance<=min_distance:
    print('Maximum distance should be larger than minimum distance!! Swapping them...')
    tmp = max_distance
    max_distance = min_distance
    min_distance = tmp


success = False 

while success==False:
    # read data
    data_medium = pd.read_csv('./airport_medium.csv')
    data_large = pd.read_csv('./airport_large.csv')

    data = pd.concat([data_medium,data_large],ignore_index=True)

    data_medium = -1
    data_large = -1

    data['latitude'] = data['latitude_deg'] * np.pi / 180
    data['longitude'] = data['longitude_deg'] * np.pi / 180


    nrec = len(data)

    # generate a random number
    rand0 = np.random.randint(nrec)

    airport0 = data.loc[rand0]

    lat0 = data.loc[rand0]['latitude']
    lon0 = data.loc[rand0]['longitude']


    # calculate distances to this airport
    lat = data['latitude'].to_numpy()
    lon = data['longitude'].to_numpy()

    distance = np.zeros(nrec)
    for i in range(nrec):
        distance[i] = calc_distance(lat[i],lon[i],lat0,lon0)/nm_to_km

    data['distance'] = distance


    # extract airports that fall into the distance range
    data_sub = data.loc[(data['distance']>=min_distance) & (data['distance']<=max_distance)].reset_index()

    if len(data_sub)==0:
        continue

    # random another number
    rand1 = np.random.randint(len(data_sub))
    airport1 = data_sub.loc[rand1]



    #if len(airport1['ident'])!=4 or len(airport0['ident'])!=4:
    if len(airport1['gps_code'])!=4 or len(airport0['gps_code'])!=4:
        continue 


    success = True




print('Departure: ', airport0['gps_code'], '   ------------   Arrival: ', 
      airport1['gps_code'], '    Distance (nm): {:.3f}'.format(airport1['distance']))


print('----------------------------------------')
print('Departure airport info:')
print(airport0)

print('----------------------------------------')
print('Arrival airport info:')
print(airport1)
print('----------------------------------------')