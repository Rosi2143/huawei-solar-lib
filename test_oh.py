#!/usr/bin/env python3

import datetime
import logging

from openhab import OpenHAB

LOGGER = logging.getLogger(__name__)
IP_ADDRESS = "192.168.178.48"
base_url = "http://openhabianpi:8080/rest"

print("Starting main")

openhab = OpenHAB(base_url)
# fetch all items
items = openhab.fetch_all_items()

sunset = items.get("HuaweiSolar_Statistic_CurrentElectricityGenerationStatisticsTime")
print(f"Time: {sunset.state}")
sunset.command(datetime.datetime.strptime("2024-04-20T19:37:54", "%Y-%m-%dT%H:%M:%S"))
print(f"Time: {sunset.state}")
