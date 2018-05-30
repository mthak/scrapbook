import datetime
import json
import logging
import sys
import argparse
import requests


class GeoJsondata():
    ''' Class to get earthquake data by state for a week'''

    def __init__(self):
        ''' init method '''

        # adding this constant as the data has wrangling issues
        # some of the state data is in both full name and abbrevation e.g. CA & california
        self.states = {
            "Alabama": "AL",
            "Alaska": "AK",
            "American Samoa": "AS",
            "Arizona": "AZ",
            "Arkansas": "AR",
            "California": "CA",
            "Colorado": "CO",
            "Connecticut": "CT",
            "Delaware": "DE",
            "District of Columbia": "DC",
            "Florida": "FL",
            "Georgia": "GA",
            "Guam": "GU",
            "Hawaii": "HI",
            "Idaho": "ID",
            "Illinois": "IL",
            "Indiana": "IN",
            "Iowa": "IA",
            "Kansas": "KS",
            "Kentucky": "KY",
            "Louisiana": "LA",
            "Maine": "ME",
            "Maryland": "MD",
            "Massachusetts": "MA",
            "Michigan": "MI",
            "Mexico": "Mexico",
            "Minnesota": "MN",
            "Mississippi": "MS",
            "Missouri": "MO",
            "Montana": "MT",
            "National": "NA",
            "Nebraska": "NE",
            "Nevada": "NV",
            "New Hampshire": "NH",
            "New Jersey": "NJ",
            "New Mexico": "NM",
            "New York": "NY",
            "North Carolina": "NC",
            "North Dakota": "ND",
            "Northern Mariana Islands": "MP",
            "Ohio": "OH",
            "Oklahoma": "OK",
            "Oregon": "OR",
            "Pennsylvania": "PA",
            "Puerto Rico": "PR",
            "Rhode Island": "RI",
            "South Carolina": "SC",
            "South Dakota": "SD",
            "Tennessee": "TN",
            "Texas": "TX",
            "Utah": "UT",
            "Vermont": "VT",
            "Virgin Islands": "VI",
            "Virginia": "VA",
            "Washington": "WA",
            "West Virginia": "WV",
            "Wisconsin": "WI",
            "Wyoming": "WY"}
        self.geojson = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson"

    def _get_geo_data(self):
        ''' get geo data as dict '''
        try:
            geodata = requests.get(self.geojson)
        except requests.exceptions.RequestException as e:
            raise Exception("Could not connect Error: %s", e)
        geodict = geodata.json()
        logging.debug("json values are {}".format(geodict))
        return geodict

    def get_geo_json_properties(self, payload=None):
        ''' get geo fetatures properties i.e. all data as dict for all states '''
        properties = []
        geodata = self._get_geo_data()
        features = geodata['features']
        for feature in features:
            propdata = feature['properties']
            properties.append(propdata)
        return properties

    def get_geotime(self, properties):
        ''' get time in epoch and datetime format for a given property '''

        geotime = properties['time']
        realtime = geotime / 1000
        realtime = datetime.datetime.fromtimestamp(
            realtime).strftime('%Y-%m-%dT%H:%M:%S')
        return geotime, realtime

    def get_geostate(self, properties):
        ''' get state information for a give property '''
        stateinfo = properties['place']
        try:
            state = stateinfo.split(',')[1].strip()
        except IndexError:
            state = stateinfo
        state = self.states.get(state, state)
        return state, stateinfo

    def get_geomagnitude(self, properties):
        ''' get magnitude for a give property '''
        magnitude = properties['mag']
        return magnitude


def create_data_struct(geoinstance):
    ''' method to parse all properties and create the data structure as ::
        "state": [{"epoch": {"time": time, "mag": magnitude, "info": info}}]
    '''
    # Disclaimair :: We can handle all these much more cleanly and efficienly using pandas dataframe
    # Assuming we don't want to use a third party library like pandas here.
    geoinfo = {}
    g = geoinstance
    properties = g.get_geo_json_properties()
    for data in properties:
        geotime, realtime = g.get_geotime(data)
        state, stateinfo = g.get_geostate(data)
        state = state.rstrip()
        magnitude = g.get_geomagnitude(data)
        geodata = {}
        geodata[geotime] = {}
        geodata[geotime]['magnitude'] = str(magnitude)
        geodata[geotime]['time'] = realtime
        geodata[geotime]['stateinfo'] = stateinfo
        if state in geoinfo:
            geoinfo[state].append(dict(geodata))
        else:
            geoinfo[state] = []
            geoinfo[state].append(dict(geodata))

    logging.debug("geodata is {}".format(json.dumps(geoinfo, indent=4)))
    return geoinfo


def main():
    ''' main method to parse and display output in chronogical order for a given state
        Sicne the data is for a week only so not adding the logic to check if date is > 7 days old '''
    parser = argparse.ArgumentParser(
        description="Get Eweekly earthquake data for a given state")
    parser.add_argument(
        "--state",
        dest="state",
        help="Name of the state in two letter abbreviated format for US, Some data has sates like 'Fiji Region'")
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    state = args.state
    g = GeoJsondata()
    geoinfo = create_data_struct(g)
    data = geoinfo.get(state, None)
    if data:
        for info in sorted(data):
            for k, v in info.items():
                print "{} | {} | magnitude: {}".format(
                    v['time'], v['stateinfo'], v['magnitude'])

    else:
        raise Exception("Data not found for the state")


if __name__ == "__main__":
    main()
