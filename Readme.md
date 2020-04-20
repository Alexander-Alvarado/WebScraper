# Synapse Connect Program 
<img src="https://github.com/Web-Cam/WebScraper/blob/master/synapse.jpg" alt="synapse" width="400" height="400">

## Installation

### Prerequsite Downloads
* [google maps](https://pypi.org/project/googlemaps/)
* [PYYAML](https://pypi.org/project/PyYAML/)
* [pandas](https://pypi.org/project/pandas/)
* [Requests](https://pypi.org/project/requests/)
### API Keys Needed
* [Google Maps Places](https://developers.google.com/places/web-service/get-api-key)
* [YELP](https://www.yelp.com/developers)

## Running The Program
1. Double click the scraper.py file
2. Place API keys in the [KEYS.YAML](keys.yaml)
*Should look like googlemaps: EXAMPLE_KEY With a space after :
3. Open the project, and select the import file (Should be Cunchbaseview.CSV)
4. Click begin to start scraping the data!

## Possible Errors:
1. No API keys/Invalid Keys: Make sure to exit the keys.yaml file!
2. No file selected : Make sure file is selected from the GUI
3. Import errors : Ensure all above files are imported

## Output
* Output will be in the Crunchbaseview.CSV file, all extra information will be shown here
* Extra Fields: Address, Lat/LONG, Phone, Website, Verified
* Verified shows if Google maps Matches YELP data, if yelp data does not match/exist value will be false
