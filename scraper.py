import csv
import os
import os.path
import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from os import path
from difflib import SequenceMatcher  # to compare strings
from tkinter import messagebox
filename = ''

try:
    import BusinessMapInfo
    import pandas as pd  # Used for csv editing

except ModuleNotFoundError:
    print("Installing missing modules")
    os.system("pip install googlemaps pandas pyyaml requests")
    import BusinessMapInfo
    import pandas as pd  # Used for csv editing


def main():
    # Name of origional CSV file that will be fed in.
    createGUI()
    # Initializaion Functions
    if (filename == ''):
        showError()
        return 0

    if (testAPI("largo", "Taco Bell", "9999999999")):  # Testing APIs, info can be whatever

        # Main working function
        importCSV(filename)
    # Place Functions for more scrape data below...
    else:
        return 0
# Function that creates our temp file Directory, that will be used to merge with main CSV file.


def showError():
    root = Tk()
    root.withdraw()
    messagebox.showerror("Error", "Before staring parse, select input file...")


def createGUI():

    root = Tk()
    frame = tk.Frame(root)
    root.geometry("500x500")
    pathlabel = Label(root)
    frame.pack()
    root.title("Synapse Data Scraper")
    button = tk.Button(frame,
                       text="QUIT PROGRAM",
                       fg="red",
                       command=quit)
    button.pack(side=tk.LEFT)

    guifilename = tk.Button(frame,
                            text="Select Input File",
                            command=getFilename
                            )
    guifilename.pack(side=tk.LEFT)

    start = tk.Button(frame,
                      text="Start parse",
                      command=root.destroy
                      )
    start.pack(side=tk.LEFT)

    root.mainloop()


def getFilename():
    global filename
    filename = filedialog.askopenfilename(initialdir=os.getcwd(
    ), title="Select file", filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))


def importCSV(filename):
    # Arrays to populate the temp files

    print("WORKING....")
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', skipinitialspace=True)

        # Get titles of the rows.
        names = csv_reader.__next__()

        # pandas data of the read csv file
        df = pd.read_csv(filename, error_bad_lines=False)

        if(len(df.columns) == 27):
            df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
            df.to_csv(filename, index=False)

        df = pd.read_csv(filename, error_bad_lines=False)

        if(len(df.columns) == 26):
            df["Address"] = ""
            df["Lat/Long"] = ""
            df["Phone"] = ""
            df["Website"] = ""
            df["Verified"] = ""
            df.to_csv(filename, index=False)

        checkDate(filename, df)


def checkDate(filename, df):

    # current date in MM-DD-YYYY format
    scanTime = datetime.date.today()
    line_count = 1

    for row in df.itertuples(index=True, name='Pandas'):
        # sets crated_at with current date if this is the first scan
        if isinstance(getattr(row, "created_at"), str) == False:
            print("\nFirst time scanning %s, scan on %s: " %
                  (getattr(row, "name"), str(scanTime.strftime('%m/%d/%Y'))))

            df.loc[df['id'] == line_count, ['created_at']
                   ] = scanTime.strftime('%m/%d/%Y')

            df.loc[df['id'] == line_count, ['updated_at']
                   ] = scanTime.strftime('%m/%d/%Y')

            try:
                createmaplistCSV(row,  df, line_count)

            except:
                print("error scanning company")

        # if 'updated_at' is not blank
        else:
            # last time this company was scanned
            try:
                oldTime = datetime.datetime.strptime(
                    getattr(row, "updated_at"), '%m/%d/%Y').date()
            except:
                oldTime = "01/01/2020"
                oldTime = datetime.datetime.strptime(
                    oldTime, '%m/%d/%Y').date()

            # todays date - last scan date
            lastUpdate = scanTime-oldTime

            # if 'updated_at' is not blank and is not 30 days old
            if lastUpdate < datetime.timedelta(days=30):
                print("Skipping " + getattr(row, "name") +
                      ", last updated on " + getattr(row, "updated_at"))

            # if 'updated_at' is blank or is over 30 days old
            elif lastUpdate > datetime.timedelta(days=30):
                print("\nUpdating scan of " + getattr(row, "name"))
                df.loc[df['id'] == line_count, ['updated_at']
                       ] = scanTime.strftime('%m/%d/%Y')

                try:
                    createmaplistCSV(row,  df, line_count)

                except:
                    print("error scanning company")

        line_count += 1
        df.to_csv(filename, index=False)


def getaddressField(companyName, location):
    # This function will allow us to populate address, and lat/long
    # First param will be company name followed by location
    return(BusinessMapInfo.getAddress(companyName, location))


def getadditionalInfo(ID):
    # Function returns more data based on ID
    return (BusinessMapInfo.getadditionalInfo(ID))


def testAPI(location, name, phone):
    try:
        print("Testing google MAPS API")
        getaddressField(name, location)
    except:
        print("GOOGLE MAPS API ERROR")
        return False

    try:
        print("Testing YELP API")
        BusinessMapInfo.getYelpInfo("9999999999")
    except:
        print("YELP API ERROR")
        return False

    print("BOTH APIs Valid...")
    return True


def createmaplistCSV(row,  df, line_count):
    businessName = str(getattr(row, "name"))
    location = str(getattr(row, "headquarters_location"))

    locationData = getaddressField(businessName, location)

    # API call to google maps, if this check passes means that the company matches.
    if (locationData['status'] == 'OK'):
        # Grab the first canidate, since it will be the closest match.
        placeid = str(locationData['candidates'][0]['place_id'])
        address = str(locationData['candidates'][0]['formatted_address'])
        geometry = str(locationData['candidates'][0]['geometry'])

        # Make another API call to get additional info about the company.
        additionalInfo = getadditionalInfo(placeid)
        phoneNumber = getPhoneNumber(additionalInfo)
        website = getWebsite(additionalInfo)
        # Add all this new info to our array, which we use to populate map info.
        # Any additional info from a maps API call should go here.

        print("Found on Google Maps")

        df.loc[df['id'] == line_count, ['Address']
               ] = address

        df.loc[df['id'] == line_count, ['Lat/Long']
               ] = geometry

        df.loc[df['id'] == line_count, ['Phone']
               ] = phoneNumber

        df.loc[df['id'] == line_count, ['Website']
               ] = website

        if (phoneNumber != 'NULL' or phoneNumber != ""):

            yelpResponse = BusinessMapInfo.getYelpInfo(phoneNumber)

            # If no response with phone number, it will throw a keyerror
            try:
                total = yelpResponse["total"]
            except KeyError:
                total = 0

            if (total > 0):
                print("Comparing Yelp To GMAPS data")
                # Check to see if Yelp data matches google maps
                yelpReturn = comparison(
                    address, businessName, phoneNumber, yelpResponse)

                if (yelpReturn):
                    print("Yelp data matches Google maps\n")
                    df.loc[df['id'] == line_count, ['Verified']
                           ] = "True"
                    return

                else:
                    print("no match ON YELP")
                    df.loc[df['id'] == line_count, ['Verified']
                           ] = "False"
                    return

            else:
                print("no match ON YELP")
                df.loc[df['id'] == line_count, ['Verified']
                       ] = "False"
                return

        else:
            print("no match ON YELP")
            df.loc[df['id'] == line_count, ['Verified']
                   ] = "False"
            return

    # This means the company was not found
    elif (locationData['status'] == 'ZERO_RESULTS'):
        print("No results on google maps")
        return

    else:  # Some kind of other error occured.
        print("GMAP ERROR RETRY...")
        return


def comparison(Gmaps, googlebusinessName, gmapPhone, yelp):

    gmapAddress = Gmaps  # str(Gmaps['candidates'][0]['formatted_address'])
    gmapCompanyName = str(googlebusinessName)

    print("Comparing against %s, %s, %s" %
          (gmapCompanyName, gmapAddress, gmapPhone))

    for i in range(0, len(yelp["businesses"])):
        yelpAddress = str(yelp["businesses"][i]["location"]["display_address"])
        yelpAddress += ", United States"
        yelpCompanyName = str(yelp["businesses"][i]["name"])
        yelpPhone = str(yelp["businesses"][i]["phone"])

        print("Comparing: %s, %s, %s" %
              (yelpCompanyName, yelpAddress, yelpPhone))
        # address is formateed differently, than Gmaps
        yelpAddresslength = len(yelpAddress)
        # next, we cut down the google map sting to correct length
        gmapAddress = gmapAddress[:yelpAddresslength]

        addressScore = SequenceMatcher(a=yelpAddress, b=gmapAddress).ratio()
        nameScore = SequenceMatcher(
            a=yelpCompanyName, b=gmapCompanyName).ratio()
        if(addressScore >= .75 and nameScore >= .60):
            yelpReturn = [yelpCompanyName, yelpAddress, yelpPhone]
            return yelpReturn

    return False


def getPhoneNumber(additionalInfo):
    try:
        return(additionalInfo['result']['formatted_phone_number'])

    except KeyError:
        return("")


def getWebsite(additionalInfo):
    try:
        return(additionalInfo['result']['website'])

    except KeyError:
        return("")


if __name__ == "__main__":
    main()
