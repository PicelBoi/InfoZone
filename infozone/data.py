'''
    Copyright (C) 2025  PicelBoi

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

import urllib
import json
import urllib.request
import logging
import datetime
from .config import config

logger = logging.getLogger("InfoZone Data Generator")

pages = []
lb_line = []
useragent = "PicelBoi InfoZone, problems? contact picelboi@picelboi.xyz"
locationdata = {}

grabDonePages = False
grabDoneLB = False

# Helper function to just directly get the JSON.
def grabJSON(url: str):
    request = urllib.request.Request(
            url,
            None,
            {
                "User-Agent": useragent
            }
            )
    
    data = json.loads((urllib.request.urlopen(request).read()))
    return data

# Taken from https://gist.github.com/RobertSudwarts/acf8df23a16afdb5837f
def degrees_to_cardinal(d):
    '''
    note: this is highly approximate...
    '''
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((d + 11.25)/22.5 - 0.02)
    return dirs[ix % 16]

def meters_to_miles(m):
    mile = m * 0.000621
    return(int(mile))

def kph_to_mph(kph):
    mph = kph * 0.621371
    return(int(mph))

def getLocData(locations):
    global locationdata
    for x in locations:
        locationdata[f"{x["geocode"][0]}{x["geocode"][1]}"] = {}

        data = grabJSON(f"https://api.weather.gov/points/{x["geocode"][0]},{x["geocode"][1]}")
        locationdata[f"{x["geocode"][0]}{x["geocode"][1]}"]["loc"] = data
        
        data = grabJSON(data["properties"]["observationStations"])
        locationdata[f"{x["geocode"][0]}{x["geocode"][1]}"]["obs"] = data["observationStations"][0]

def grabMainCC(x:dict):
    global pages
    page = {
        "title": f"{x["display_name"]}'s Conditions",
        "footer": "",
        "bgcolor": "main_default_color",
        "align": "center",
        "duration": 10000,
        "lines": [
            "",
            "",
            "",
            "No",
            "Data",
            "",
            "",
            ""
        ]
    }
    try:
        data = grabJSON(locationdata[f"{x["geocode"][0]}{x["geocode"][1]}"]["obs"] + "/observations/latest")
        try:
            wind = f"Wind: {kph_to_mph(data["properties"]["windSpeed"]["value"])} MPH {degrees_to_cardinal(data["properties"]["windDirection"]["value"])}"
            precip = "Precipitation: "

            if data["properties"]["precipitationLastHour"]["value"] != None:
                precip += f"{data["properties"]["precipitationLastHour"]["value"]} mm"
            else:
                precip += "0 mm"

            if data["properties"]["windGust"]["value"] != None:
                wind += f" (Gusts: {kph_to_mph(data["properties"]["windGust"]["value"])} MPH)"
            page = {
                "title": f"{x["display_name"]}'s Conditions",
                "footer": "",
                "bgcolor": "main_default_color",
                "align": "left",
                "duration": 10000,
                "lines": [
                    f"Temperature: {int(data["properties"]["temperature"]["value"])}°C",
                    data["properties"]["textDescription"],
                    f"Dew Point: {int(data["properties"]["dewpoint"]["value"])}°C",
                    wind,
                    f"Barometric Pressure: {int(data["properties"]["barometricPressure"]["value"] / 100)} hPa",
                    f"Relative Humidity: {int(data["properties"]["relativeHumidity"]["value"])} %",
                    f"Visibility: {meters_to_miles(data["properties"]["visibility"]["value"])} miles",
                    precip
                ]
            }

            lb_line.append(f"{x["display_name"]}'s Conditions")
            lb_line.append(f"Temperature: {int(data["properties"]["temperature"]["value"])}°C")
            lb_line.append(data["properties"]["textDescription"])
            lb_line.append(f"Dew Point: {int(data["properties"]["dewpoint"]["value"])}°C")
            lb_line.append(wind)
            lb_line.append(f"Barometric Pressure: {int(data["properties"]["barometricPressure"]["value"] / 100)} hPa")
            lb_line.append(f"Relative Humidity: {int(data["properties"]["relativeHumidity"]["value"])} %")
            lb_line.append(f"Visibility: {meters_to_miles(data["properties"]["visibility"]["value"])} miles")
            lb_line.append(precip)

        except Exception as e:
            logger.error(f"Could not generate the Current Condtions for {x["display_name"]}.")
            logger.error(e)

    except Exception as e:
        logger.error(f"Could not grab the Current Condtions for {x["display_name"]}.")
        logger.error(e)

    pages.append(page)

def getNearCond():
    global pages
    page = {
        "title": f"Nearby Conditions",
        "footer": "",
        "bgcolor": "main_default_color",
        "align": "center",
        "duration": 10000,
        "lines": [
            "",
            "",
            "",
            "No",
            "Data",
            "",
            "",
            ""
        ]
    }
    try:
        page = {
            "title": f"Nearby Conditions",
            "footer": "",
            "bgcolor": "main_default_color",
            "align": "center",
            "duration": 10000,
            "lines": [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                ""
            ]
        }

        lineindex = 0
        for location in config["locations"]["nearbyLocs"]:
            try:
                data = grabJSON(locationdata[f"{location["geocode"][0]}{location["geocode"][1]}"]["obs"] + "/observations/latest")
                try:
                    page["lines"][lineindex] = f"{location["display_name"]}: {int(data["properties"]["temperature"]["value"])}°C {data["properties"]["textDescription"]}"
                    lineindex += 1
                except Exception as e:
                    logger.error(f"Could not generate the current condtions for nearby locations.")
                    logger.error(e)

                
            except Exception as e:
                logger.error(f"Could not grab the current condtions for {location["display_name"]}.")
                logger.error(e)
        


        

    except Exception as e:
        logger.error(f"Could not grab the current conditions for nearby locations.")
        logger.error(e)

    pages.append(page)

def IntroPage():
    page = {
                "title": f"Hello!",
                "footer": "",
                "bgcolor": "main_default_color",
                "align": "center",
                "duration": 10000,
                "lines": [
                    "",
                    "",
                    "Hello,",
                    f"{config["locations"]["main"]["display_name"]}!",
                    "",
                    "('ᴗ')",
                    "",
                    "",
                ]
            }
    try:
        hour = datetime.datetime.now().hour
        if hour >= 6 and hour < 12:
            page["lines"][2] = "Good morning,"
        elif hour >= 12 and hour < 20:
            page["lines"][2] = "Good afternoon,"
        else:
            page["lines"][2] = "Good night,"
    except Exception as e:
        logger.error(f"Could not correctly set phrase for Intro based on time!")
        logger.error(e)

    pages.append(page)

def ChannelID():
    page = {
            "title": f"PicelBoi InfoZone is provided to you by",
            "footer": "",
            "bgcolor": "main_default_color",
            "align": "center",
            "duration": 10000,
            "lines": [
                config["affiliate"]["name"],
                "on",
                config["affiliate"]["channel"],
                "",
                "",
                "",
                "",
                "",
            ]
            }

    try:
        page["lines"][5] = "- " +config["affiliate"]["platforms"][0]
        page["lines"][4] = "You may watch this channel on:"
    except IndexError:
        pass

    try:
        page["lines"][6] = "- " + config["affiliate"]["platforms"][1]
        page["lines"][4] = "You may watch this channel on:"
    except IndexError:
        pass

    try:
        page["lines"][7] = "- " +config["affiliate"]["platforms"][2]
        page["lines"][4] = "You may watch this channel on:"
    except IndexError:
        pass

    pages.append(page)

# First-time preparations for data grabbing.
def dataSetUp():
    locations = [config["locations"]["main"]] + config["locations"]["nearbyLocs"]
    getLocData(locations)

# The boss of data.
def dataGrabber():
    global grabDonePages, grabDoneLB
    lb_line.append("Welcome to PicelBoi InfoZone! ('ᴗ')")
    IntroPage()
    pages.append(
        {
          "title": f"Up Next",
                "footer": "",
                "bgcolor": "main_default_color",
                "align": "left",
                "duration": 10000,
                "lines": [
                    "- Weather",
                    "- Headlines",
                    "- Rankings",
                    "- Statuses",
                    "- Daily Somethings",
                    "- Holidays",
                    "- Special Message",
                    "",
                ]  
        })
    grabMainCC(config["locations"]["main"])
    getNearCond()
    ChannelID()

    grabDonePages = True
    grabDoneLB = True
    grabDone = True