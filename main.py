import tkinter as tk
from tkinter import ttk,Checkbutton
import pandas as pd
import os
import numpy as np
from sys import exit
import random

earth_radius = 6371
nm_to_km = 1.852
def calc_distance(lat1,lon1,lat2,lon2):
    return 2 * earth_radius * np.arcsin(np.sqrt( (np.sin((lat2-lat1)/2))**2 + 
                    np.cos(lat1)*np.cos(lat2)*(np.sin((lon2-lon1)/2))**2))

# Function to execute when the button is clicked
def calculate():
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




    # Get values from input boxes
    min_distance = int(entry1.get())
    max_distance = int(entry2.get())

    if min_distance*nm_to_km>=earth_radius*np.pi:
        result_label.config(text="Minimum distance is too large!! Input a new value.")
        return


    if max_distance<min_distance:
        print('Maximum distance should be larger than minimum distance!! Swapping them...')
        tmp = max_distance
        max_distance = min_distance
        min_distance = tmp

        entry1.delete(0, tk.END)
        entry1.insert(0,'{:d}'.format(int(min_distance)))

        entry2.delete(0, tk.END)
        entry2.insert(0,'{:d}'.format(int(max_distance)))


    if min_distance*nm_to_km>=earth_radius*np.pi:
        result_label.config(text="Minimum distance is too large!! Input a new value.")
        for i in tree1.get_children():
            tree1.delete(i)

        for i in tree2.get_children():
            tree2.delete(i)
        return


    success = False 
    num_try = 0
    while success==False:
        if num_try>100:
            result_label.config(text="Fail to find a result!!!")

            for i in tree1.get_children():
                tree1.delete(i)

            for i in tree2.get_children():
                tree2.delete(i)

            return
        
        num_try = num_try + 1
        # read data
        if not (airportType_large.get() or airportType_medium.get()
                 or airportType_small.get()):
            result_label.config(text="No airport type is selected!!")

            for i in tree1.get_children():
                tree1.delete(i)

            for i in tree2.get_children():
                tree2.delete(i)
            return

        airportTypes = [airportType_small,airportType_medium,airportType_large]
        airportFiles = ['./airport_small.csv','./airport_medium.csv','./airport_large.csv']
        data = []
        for i in range(len(airportTypes)):
            if not airportTypes[i].get():
                continue 
            # print('Read ' + airportFiles[i])

            data_tmp = pd.read_csv(airportFiles[i])
            if len(data)==0:
                data = data_tmp.copy()
            else:
                data = pd.concat([data,data_tmp],ignore_index=True)
            del data_tmp

        # data_medium = pd.read_csv('./airport_medium.csv')
        # data_large = pd.read_csv('./airport_large.csv')

        # data = pd.concat([data_medium,data_large],ignore_index=True)

        # del data_medium
        # del data_large 
        
        data['latitude'] = data['latitude_deg'] * np.pi / 180
        data['longitude'] = data['longitude_deg'] * np.pi / 180


        nrec = len(data)


        if rand_option.get() == "airports":
            # print('Directly get random airports...')
            # generate a random number
            rand0 = np.random.randint(nrec)

            airport0 = data.loc[rand0]

        elif rand_option.get() == "latitude-longitude":
            # print('Random a spatial location and then find airports...')

            # generate a random number
            lat_rand = random.uniform(-90,90) * np.pi/180
            lon_rand = random.uniform(-180,180) * np.pi/180

            # calculate distances to this random location
            lat = data['latitude'].to_numpy()
            lon = data['longitude'].to_numpy()

            distance = np.zeros(nrec)
            for i in range(nrec):
                distance[i] = calc_distance(lat[i],lon[i],lat_rand,lon_rand)/nm_to_km

            # find the airport closest to this random location 
            ind0 = distance.argmin()
            print('ind0 = ', ind0)
            airport0 = data.loc[ind0]

        # get latitude and longitude of airport0
        lat0 = airport0['latitude']
        lon0 = airport0['longitude']

        # calculate distances to this airport
        lat = data['latitude'].to_numpy()
        lon = data['longitude'].to_numpy()

        distance = np.zeros(nrec)
        for i in range(nrec):
            distance[i] = calc_distance(lat[i],lon[i],lat0,lon0)/nm_to_km

        data['distance'] = distance


        # extract airports that fall into the distance range
        data_sub = data.loc[(data['distance']>=min_distance) & (data['distance']<=max_distance)].reset_index()
        data_sub.drop(data_sub.loc[data_sub['ident'] == airport0['ident']].index, inplace=True)

        data_sub.reset_index()
        if len(data_sub)==0:
            continue

        # random another number
        rand1 = np.random.randint(len(data_sub))
        airport1 = data_sub.loc[rand1]



        #if len(airport1['ident'])!=4 or len(airport0['ident'])!=4:
        if len(str(airport1['gps_code']))!=4 or len(str(airport0['gps_code']))!=4:
            continue 


        success = True


    result_label.config(text='Departure: ' + airport0['gps_code'] + '   ---   Arrival: ' + 
            airport1['gps_code'] + '    Distance (nm): {:.1f}'.format(airport1['distance']))


    for i in tree1.get_children():
        tree1.delete(i)

    for i in tree2.get_children():
        tree2.delete(i)
        

    tree1.insert("", "end", values=(airport0['gps_code']))
    tree1.insert("", "end", values=(airport0['name'],""))
    tree1.insert("", "end", values=('{:.3f}'.format(float(airport0['latitude_deg']))))
    tree1.insert("", "end", values=('{:.3f}'.format(float(airport0['longitude_deg']))))

    tree2.insert("", "end", values=(airport1['gps_code']))
    tree2.insert("", "end", values=(airport1['name'],""))
    tree2.insert("", "end", values=('{:.3f}'.format(float(airport1['latitude_deg']))))
    tree2.insert("", "end", values=('{:.3f}'.format(float(airport1['longitude_deg']))))




def show_selection():
    selected_option = rand_option.get()
    print(f"Selected Option: {selected_option}")




if __name__== "__main__" :
    # Create the main window
    root = tk.Tk()
    root.title("Random Flight Generator")

    # Calculate the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the x and y coordinates for the center of the screen
    x = (screen_width - 1200) // 2  # 400 is the width of the GUI
    y = (screen_height - 400) // 2  # 300 is the height of the GUI

    root.geometry(f"1200x400+{x}+{y}")

    # Create input boxes
    label1 = tk.Label(root, text="Minimum Distance (NM):")
    entry1 = tk.Entry(root)
    label2 = tk.Label(root, text="Maximum Distance (NM):")
    entry2 = tk.Entry(root)

    # Check boxes for airport types
    airportType_small =  tk.BooleanVar(value=False) 
    airportType_medium = tk.BooleanVar(value=True) 
    airportType_large = tk.BooleanVar(value=True)

    checkBox_small = Checkbutton(root, text = "Small airports", variable = airportType_small,
        onvalue = True, offvalue = False,width=15)
    checkBox_medium = Checkbutton(root, text = "Medium airports", variable = airportType_medium, 
        onvalue = True, offvalue = False,width=15)
    checkBox_large = Checkbutton(root, text = "Large airports", variable = airportType_large, 
        onvalue = True, offvalue = False,width=15)
    
    checkBox_small.grid(row=0, column=2)
    checkBox_medium.grid(row=1, column=2)
    checkBox_large.grid(row=2, column=2)


    # drop down menu for the random algorithms:---------
    # Define options for the drop-down menu
    options = ["latitude-longitude", "airports"]

    # Create a Tkinter variable to hold the selected option
    rand_option = tk.StringVar(root)
    rand_option.set(options[0])  # Set the default value

    # Create the OptionMenu widget
    option_menu = tk.OptionMenu(root, rand_option, *options)
    option_menu.grid(row=2, column=0)

    # # Create a button to display the selected option
    # show_button = tk.Button(root, text="random_method", command=show_selection)
    # show_button.grid(row=3,column=0)
    #----------------


    # Create a button
    calculate_button = tk.Button(root, text="Calculate", command=calculate)

    # Create a label to display the result
    result_label = tk.Label(root, text="")

    # # Create a table using the ttk.Treeview widget (two horizontally-aligned tables)
    # tree = ttk.Treeview(root, columns=("Departure", "Arrival"))
    # tree.heading("#1", text="Departure")
    # tree.heading("#2", text="Arrival")

    # Create tables using the ttk.Treeview widget (two horizontally-aligned tables)
    tree0 = ttk.Treeview(root, columns=("Info"),show="headings")
    tree0.heading("#0", text="Info")

    tree0.insert("", "end", values=("ICAO Code",""), tags=("centered",))
    tree0.insert("", "end", values=("Name",""), tags=("centered",))
    tree0.insert("", "end", values=("Latitude",""), tags=("centered",))
    tree0.insert("", "end", values=("Longitude",""), tags=("centered",))


    tree1 = ttk.Treeview(root, columns=("Departure"),show="headings")
    tree1.heading("#1", text="Departure")

    tree2 = ttk.Treeview(root, columns=("Arrival"),show="headings")
    tree2.heading("#1", text="Arrival")


    # Configure row and column expansion
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(4, weight=1)


    # Place widgets on the grid
    label1.grid(row=0, column=0, sticky="nsew")
    entry1.grid(row=0, column=1)
    label2.grid(row=1, column=0, sticky="nsew")
    entry2.grid(row=1, column=1)


    calculate_button.grid(row=2, column=1, columnspan=1)
    result_label.grid(row=3, column=1, columnspan=1)
    # tree.grid(row=4, column=0, columnspan=2, sticky="nsew")

    tree0.grid(row=4, column=0, columnspan=1, sticky="nsew")
    tree1.grid(row=4, column=1, columnspan=1, sticky="nsew")
    tree2.grid(row=4, column=2, columnspan=1, sticky="nsew")


    # Start the main loop
    root.mainloop()