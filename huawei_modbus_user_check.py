#!/usr/bin/env python3

import asyncio
import logging
import os
import time
from logging.handlers import RotatingFileHandler

from huawei_solar import SUN2000Device, create_device_instance, create_tcp_client
from huawei_solar.registers import REGISTERS

LOGGER = logging.getLogger(__name__)
IP_ADDRESS = "192.168.178.34"


async def get_data(register_name: str, huawei_solar_bridge: SUN2000Device) -> None:
    """Get data from the inverter and wait"""
    LOGGER.info("%20s - Starting", register_name)
    LOGGER.info("%20s - Getting values", register_name)
    register_list = [register_name]
    try:
        responses = await huawei_solar_bridge.batch_update(register_list)
        for register_name, response in responses.items():
            LOGGER.info("%20s - %35s: %s", register_name, register_name, response)
            print(f"{register_name} - {response}")
    except Exception as err:
        LOGGER.error("%20s - Error getting values: %s", register_name, err)

    LOGGER.info("%20s - stopping", register_name)


async def main():
    """Main function to test asyncio."""
    print("Starting main")

    connected = False
    connect_count = 0
    while not connected:
        try:
            connect_count += 1
            client = create_tcp_client(host=IP_ADDRESS, port=502)
            hsb = await create_device_instance(client)
            assert isinstance(hsb, SUN2000Device)

            connected = True
        except Exception as err:
            LOGGER.exception("Connection Error: %s - Retry %s", err, connect_count)

    print("Connected to Huawei")

    register_request = input("Enter register name (None to stop): ")
    while register_request != "None" and register_request != "":
        if register_request in REGISTERS:
            await get_data(register_name=register_request, huawei_solar_bridge=hsb)
        else:
            print(f"Register name {register_request} not found")
            print("Valid register names are: ")
            for key in dict(sorted(REGISTERS.items())):
                if register_request.lower() in key:
                    print(f"-- {key}")
        try:
            register_request = input("Enter register name (None to stop): ")
        except KeyboardInterrupt:
            LOGGER.info("Program interrupted by user.")
    await hsb.stop()
    print("Ending main")


if __name__ == "__main__":
    FORMAT = "%(asctime)s %(name)10s %(levelname)s : %(message)s"
    FILENAME = "/mnt/EAD1-0E0A/huawei_modbus_user_check.log"

    if os.name == "nt":
        FILENAME = "huawei_modbus_user_check.log"

    my_handler = RotatingFileHandler(
        FILENAME,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding="UTF-8",
        delay=False,
    )
    logging.basicConfig(
        format=FORMAT,
        level=logging.INFO,
        datefmt="%A: %y-%m-%d %H:%M:%S",
        handlers=[my_handler],
    )
    LOGGER = logging.getLogger(__name__)
    print("Logging to file: ", FILENAME)

    start = time.perf_counter()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Program interrupted by user.")

    elapsed = time.perf_counter() - start
    LOGGER.info("Program completed in %.5f seconds.", elapsed)
