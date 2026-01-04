#!/usr/bin/env python3

import asyncio
import datetime
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import huawei_solar.register_names as rn
from huawei_solar import HuaweiSUN2000Bridge, create_tcp_bridge

bug_data = {
    rn.MODEL_NAME: None,
    rn.SERIAL_NUMBER: None,
    rn.PN: None,
    rn.MODEL_ID: None,
    rn.NB_PV_STRINGS: None,
    rn.NB_MPP_TRACKS: None,
    rn.CPLD_VERSION: None,
    rn.AFCI_VERSION: None,
    rn.STATE_1: None,
    rn.STATE_2: None,
    rn.STATE_3: None,
    rn.CAPBANK_RUNNING_TIME: None,
    rn.INTERNAL_FAN_1_RUNNING_TIME: None,
    rn.INV_MODULE_A_TEMP: None,
    rn.INV_MODULE_B_TEMP: None,
}

battery_fix_data = {  # unused rn.STORAGE_UNIT_1_DCDC_VERSION,
    # unused rn.STORAGE_UNIT_1_BMS_VERSION,
    rn.STORAGE_UNIT_1_SERIAL_NUMBER: None,
    rn.STORAGE_RATED_CAPACITY: None,
    rn.STORAGE_UNIT_1_BATTERY_PACK_1_SERIAL_NUMBER: None,
    rn.STORAGE_UNIT_1_BATTERY_PACK_2_SERIAL_NUMBER: None,
}

battery_base_data = {
    rn.STORAGE_TOTAL_CHARGE: "HuaweiSolar_Battery_TotalCharge",
    rn.STORAGE_TOTAL_DISCHARGE: "HuaweiSolar_Battery_TotalDisCharge",
    # not supported rn.STORAGE_UNIT_1_WORKING_MODE_B,
    # not supported rn.STORAGE_UNIT_1_SOFTWARE_VERSION,
    rn.STORAGE_UNIT_1_BATTERY_PACK_1_FIRMWARE_VERSION: "HuaweiSolar_Battery_Unit1_Firmware",
    rn.STORAGE_UNIT_1_BATTERY_PACK_2_FIRMWARE_VERSION: "HuaweiSolar_Battery_Unit2_Firmware",
    rn.STORAGE_CHARGING_CUTOFF_CAPACITY: "HuaweiSolar_Battery_Charge_Cutoff_Capacity",
    rn.STORAGE_DISCHARGING_CUTOFF_CAPACITY: "HuaweiSolar_Battery_Discharge_Cutoff_Capacity",
}

battery_current_data = {  # not supported rn.STORAGE_UNIT_1_RUNNING_STATUS,
    # not supported rn.STORAGE_UNIT_1_CHARGE_DISCHARGE_POWER,
    # not supported rn.STORAGE_UNIT_1_STATE_OF_CAPACITY,
    # not supported rn.STORAGE_UNIT_1_RATED_CHARGE_POWER,
    # not supported rn.STORAGE_UNIT_1_RATED_DISCHARGE_POWER,
    # not supported rn.STORAGE_UNIT_1_FAULT_ID,
    # not supported rn.STORAGE_UNIT_1_BUS_CURRENT,
    rn.STORAGE_UNIT_1_BATTERY_TEMPERATURE:"HuaweiSolar_Battery_Temperature",
    # not supported rn.STORAGE_UNIT_1_REMAINING_CHARGE_DIS_CHARGE_TIME,
    # not supported rn.STORAGE_UNIT_1_BATTERY_PACK_1_MAXIMUM_TEMPERATURE,
    # not supported rn.STORAGE_UNIT_1_BATTERY_PACK_1_MINIMUM_TEMPERATURE,
    # not supported rn.STORAGE_UNIT_1_BATTERY_PACK_2_MAXIMUM_TEMPERATURE,
    # not supported rn.STORAGE_UNIT_1_BATTERY_PACK_2_MINIMUM_TEMPERATURE,
    rn.STORAGE_BUS_CURRENT: "HuaweiSolar_Battery_ChargeCurrent",
    rn.STORAGE_CHARGE_DISCHARGE_POWER: "HuaweiSolar_Battery_ChargeDischargePower",
    rn.BACKUP_SWITCH_TO_OFF_GRID: "HuaweiSolar_Battery_Switch_To_Off_Grid",
}

battery_rare_data = {
    rn.STORAGE_STATE_OF_CAPACITY: "HuaweiSolar_Battery_ChargeLevel",
    rn.STORAGE_RUNNING_STATUS: None,
    rn.STORAGE_CURRENT_DAY_CHARGE_CAPACITY: "HuaweiSolar_Battery_DayChargeCapacity",
    rn.STORAGE_CURRENT_DAY_DISCHARGE_CAPACITY: "HuaweiSolar_Battery_DayDisChargeCapacity",
}

inverter_fix_data = {
    rn.MODEL_NAME: None,
    rn.SERIAL_NUMBER: None,
    rn.PN: None,
    rn.MODEL_ID: None,
    rn.NB_PV_STRINGS: None,
    rn.NB_MPP_TRACKS: None,
    rn.HARDWARE_VERSION: None,
    rn.MONITORING_SOFTWARE_VERSION: None,
    rn.MASTER_DSP_VERSION: None,
    # not used "slave_dsp_version": None,
    rn.CPLD_VERSION: None,
    rn.AFCI_VERSION: None,
    rn.NB_OPTIMIZERS: None,
}

inverter_base_data = {
    rn.FIRMWARE_VERSION: "HuaweiSolar_Inverter_Firmware",
    rn.SOFTWARE_VERSION: "HuaweiSolar_Inverter_Software",
    rn.PROTOCOL_VERSION_MODBUS: "HuaweiSolar_Inverter_ModbusVersion",
    rn.NUMBER_OF_PACKAGES_TO_BE_UPGRADED: "HuaweiSolar_Inverter_PackageToBeUpgraded",
    rn.NB_OPTIMIZERS: "HuaweiSolar_Inverter_NumberOfOptimizers",
    rn.NB_ONLINE_OPTIMIZERS: "HuaweiSolar_Inverter_NumberOfOptimizersOnline",
}

inverter_current_data = {
    rn.INPUT_POWER: "HuaweiSolar_Inverter_InputPower",
    rn.ACTIVE_POWER: "HuaweiSolar_Inverter_ActivePower",
    rn.REACTIVE_POWER: "HuaweiSolar_Inverter_ReactivePower",
}

inverter_rare_data = {
    rn.PV_01_CURRENT: "HuaweiSolar_Inverter_PV1_Current",
    rn.PHASE_A_CURRENT: "HuaweiSolar_Inverter_PhaseACurrent",
    rn.PHASE_B_CURRENT: "HuaweiSolar_Inverter_PhaseBCurrent",
    rn.PHASE_C_CURRENT: "HuaweiSolar_Inverter_PhaseCCurrent",
    rn.PV_01_VOLTAGE: "HuaweiSolar_Inverter_PV1_Voltage",
    rn.GRID_VOLTAGE: "HuaweiSolar_Inverter_GridVoltage",
    rn.PHASE_A_VOLTAGE: "HuaweiSolar_Inverter_PhaseAVoltage",
    rn.PHASE_B_VOLTAGE: "HuaweiSolar_Inverter_PhaseBVoltage",
    rn.PHASE_C_VOLTAGE: "HuaweiSolar_Inverter_PhaseCVoltage",
    rn.GRID_FREQUENCY: "HuaweiSolar_Inverter_GridFrequency",
    rn.DAY_ACTIVE_POWER_PEAK: "HuaweiSolar_Inverter_DayActivePowerPeak",
    rn.INTERNAL_TEMPERATURE: "HuaweiSolar_Inverter_InternalTemperature",
    rn.FAULT_CODE: "HuaweiSolar_Inverter_FaultCode",
}

meter_fix_data = {
    rn.METER_TYPE: None,
}

meter_base_data = {
    rn.GRID_EXPORTED_ENERGY: "HuaweiSolar_Meter_GridExportedEnergy",
    rn.GRID_ACCUMULATED_ENERGY: "HuaweiSolar_Meter_GridAccumulatedEnergy",
    rn.METER_TYPE_CHECK: None,
}

meter_current_data = {
    rn.POWER_METER_ACTIVE_POWER: "HuaweiSolar_Meter_ActivePower",
    rn.POWER_METER_REACTIVE_POWER: "HuaweiSolar_Meter_ReactivePower",
}

meter_rare_data = {
    rn.METER_STATUS: "HuaweiSolar_Meter_Status",
    rn.ACTIVE_GRID_A_POWER: "HuaweiSolar_Meter_GridAPower",
    rn.ACTIVE_GRID_B_POWER: "HuaweiSolar_Meter_GridBPower",
    rn.ACTIVE_GRID_C_POWER: "HuaweiSolar_Meter_GridCPower",
}

statistic_base_data = {
    rn.MONTHLY_YIELD_ENERGY: "HuaweiSolar_Statistic_MonthlyYieldEnergy",
    rn.YEARLY_YIELD_ENERGY: "HuaweiSolar_Statistic_YearlyYieldEnergy",
    rn.ELECTRICITY_STATISTICS_TIME_IN_THE_PREVIOUS_DAY: "HuaweiSolar_Statistic_ElectricityStatisticsTimeInThePreviousDay",
    rn.ELECTRICITY_GENERATED_TIME_IN_THE_PREVIOUS_DAY: "HuaweiSolar_Statistic_ElectricityGeneratedTimeInThePreviousDay",
    rn.ELECTRICITY_STATISTICS_TIME_IN_THE_PREVIOUS_MONTH: "HuaweiSolar_Statistic_ElectricityStatisticsTimeInThePreviousMonth",
    rn.ELECTRICITY_GENERATED_TIME_IN_THE_PREVIOUS_MONTH: "HuaweiSolar_Statistic_ElectricityGeneratedTimeInThePreviousMonth",
    rn.ELECTRICITY_STATISTICS_TIME_IN_THE_PREVIOUS_YEAR: "HuaweiSolar_Statistic_ElectricityStatisticsTimeInThePreviousYear",
    rn.ELECTRICITY_GENERATED_TIME_IN_THE_PREVIOUS_YEAR: "HuaweiSolar_Statistic_ElectricityGeneratedTimeInThePreviousYear",
}

statistic_hour_data = {
    rn.DAILY_YIELD_ENERGY: "HuaweiSolar_Statistic_DailyYieldEnergy",
}

statistic_rare_data = {
    rn.ACCUMULATED_YIELD_ENERGY: "HuaweiSolar_Statistic_AccumulatedYieldEnergy",
    rn.TOTAL_DC_INPUT_POWER: "HuaweiSolar_Statistic_TotalDCInputPower",
    rn.CURRENT_ELECTRICITY_GENERATION_STATISTICS_TIME: "HuaweiSolar_Statistic_CurrentElectricityGenerationStatisticsTime",
    rn.HOURLY_YIELD_ENERGY: "HuaweiSolar_Statistic_HourlyYieldEnergy",
    rn.NUMBER_OF_CRITICAL_ALARMS: "HuaweiSolar_Statistic_NumberOfCriticalAlarms",
    rn.NUMBER_OF_MAJOR_ALARMS: "HuaweiSolar_Statistic_NumberOfMajorAlarms",
    rn.NUMBER_OF_MINOR_ALARMS: "HuaweiSolar_Statistic_NumberOfMinorAlarms",
    rn.NUMBER_OF_WARNING_ALARMS: "HuaweiSolar_Statistic_NumberOfWarningAlarms",
    rn.ALARM_CLEARANCE_SERIAL_NUMBER: "HuaweiSolar_Statistic_AlarmClearanceSerialNumber",
    rn.ELECTRICITY_STATISTICS_TIME_IN_THE_PREVIOUS_HOUR: "HuaweiSolar_Statistic_ElectricityStatisticsTimeInThePreviousHour",
    rn.ELECTRICITY_GENERATED_TIME_IN_THE_PREVIOUS_HOUR: "HuaweiSolar_Statistic_ElectricityGeneratedTimeInThePreviousHour",
}

LOGGER = logging.getLogger(__name__)
IP_ADDRESS = "192.168.178.29"
BASE_URL = "http://192.168.178.26:8080/rest"
OH_ITEM_MAP = {}
OH_EXTRA_ITEM_MAP = {}
OH_SWITCH_ITEMS = ["HuaweiSolar_Battery_Switch_To_Off_Grid"]
OH_SWITCH_ITEMS_MAP = {"0": "OFF", "1": "ON"}

USE_MAX = False
USE_MIN = True


def sum_up(oh_item_name: str, oh_state: float, time_value: int) -> None:
    """Add new value to sum of old values"""
    reset = False
    result = 0
    if oh_item_name in OH_EXTRA_ITEM_MAP:
        if time_value < OH_EXTRA_ITEM_MAP[oh_item_name]["time"]:
            reset = True
    else:
        OH_EXTRA_ITEM_MAP.update({oh_item_name: {"time": 0, "value": 0}})
        reset = True

    if reset:
        OH_EXTRA_ITEM_MAP[oh_item_name]["time"] = 0
        result = oh_item_command(oh_item_name=oh_item_name, oh_state=str(oh_state))
        OH_EXTRA_ITEM_MAP[oh_item_name]["value"] = 0
        if result != 0:
            LOGGER.error("Error sending value: %s", oh_state)
            OH_EXTRA_ITEM_MAP[oh_item_name]["value"] = 0

    OH_EXTRA_ITEM_MAP[oh_item_name]["time"] = time_value
    OH_EXTRA_ITEM_MAP[oh_item_name]["value"] += oh_state


def check_min_max(oh_item_name: str, oh_state: float, time_value: int, min_max: int) -> None:
    """Check if the value is the minimum or maximum"""
    new_time_line = False
    if oh_item_name in OH_EXTRA_ITEM_MAP:
        if time_value < OH_EXTRA_ITEM_MAP[oh_item_name]["time"]:
            LOGGER.info(
                "New time line for %s (%s -> %s)",
                oh_item_name,
                OH_EXTRA_ITEM_MAP[oh_item_name]["time"],
                time_value,
            )
            new_time_line = True
    else:
        OH_EXTRA_ITEM_MAP.update({oh_item_name: {"time": 0, "value": 0}})
        LOGGER.info("Adding new element %s", oh_item_name)
        if min_max == USE_MAX:
            OH_EXTRA_ITEM_MAP[oh_item_name]["value"] = -sys.maxsize - 1
        else:
            OH_EXTRA_ITEM_MAP[oh_item_name]["value"] = sys.maxsize
        LOGGER.info("Set value %s for oh_item %s", OH_EXTRA_ITEM_MAP[oh_item_name]["value"], oh_item_name)
        new_time_line = True

    current_min_max_value = OH_EXTRA_ITEM_MAP[oh_item_name]["value"]
    if min_max == USE_MAX:
        current_min_max_value = max(current_min_max_value, oh_state)
    else:
        current_min_max_value = min(current_min_max_value, oh_state)

    if new_time_line:
        LOGGER.info("Setting value %s for oh_item %s", current_min_max_value, oh_item_name)
        result = oh_item_command(oh_item_name=oh_item_name, oh_state=str(current_min_max_value))
        if result != 0:
            LOGGER.error("Error sending value: %s", current_min_max_value)
        if min_max == USE_MAX:
            OH_EXTRA_ITEM_MAP[oh_item_name]["value"] = -sys.maxsize + 1
        else:
            OH_EXTRA_ITEM_MAP[oh_item_name]["value"] = sys.maxsize
        current_min_max_value = OH_EXTRA_ITEM_MAP[oh_item_name]["value"]

    OH_EXTRA_ITEM_MAP[oh_item_name]["time"] = time_value
    if OH_EXTRA_ITEM_MAP[oh_item_name]["value"] != current_min_max_value:
        LOGGER.info("Storing new value (%s) for %s", current_min_max_value, oh_item_name)
        OH_EXTRA_ITEM_MAP[oh_item_name]["value"] = current_min_max_value


def check_max_day(oh_item_name: str, oh_state: str) -> None:
    """Check if the value is the maximum for the day"""
    hour = datetime.datetime.now().hour
    oh_item_max_day_name = oh_item_name + "_Max_Day"

    check_min_max(oh_item_max_day_name, float(oh_state), hour, USE_MAX)


def check_min_day(oh_item_name: str, oh_state: str) -> None:
    """Check if the value is the minimum for the day"""
    hour = datetime.datetime.now().hour
    oh_item_min_day_name = oh_item_name + "_Min_Day"

    check_min_max(oh_item_min_day_name, float(oh_state), hour, USE_MIN)


def check_max_month(oh_item_name: str, oh_state: str) -> None:
    """Check if the value is the maximum for the month"""
    day = datetime.datetime.now().day
    oh_item_max_month_name = oh_item_name + "_Max_Month"

    check_min_max(oh_item_max_month_name, float(oh_state), day, USE_MAX)


def check_min_month(oh_item_name: str, oh_state: str) -> None:
    """Check if the value is the minimum for the month"""
    day = datetime.datetime.now().day
    oh_item_min_month_name = oh_item_name + "_Min_Month"

    check_min_max(oh_item_min_month_name, float(oh_state), day, USE_MIN)


def sum_up_day(oh_item_name: str, oh_state: str) -> None:
    """Create sum of values for the whole day"""
    hour = datetime.datetime.now().hour
    oh_item_min_month_name = oh_item_name + "_Sum_Day"

    sum_up(oh_item_min_month_name, float(oh_state), hour)


def sum_up_month(oh_item_name: str, oh_state: str) -> None:
    """Create sum of values for the whole month"""
    day = datetime.datetime.now().day
    oh_item_min_month_name = oh_item_name + "_Sum_Month"

    sum_up(oh_item_min_month_name, float(oh_state), day)


def check_special_handling(oh_item_name: str, oh_state: str) -> None:
    """Check if special handling is needed for the item"""
    if (
        oh_item_name == "HuaweiSolar_Battery_ChargeLevel"
        or (oh_item_name == "HuaweiSolar_Battery_ChargeDischargePower")
        or (oh_item_name == "HuaweiSolar_Inverter_ActivePower")
        or (oh_item_name == "HuaweiSolar_Inverter_InputPower")
        or (oh_item_name == "HuaweiSolar_Inverter_InternalTemperature")
        or (oh_item_name == "HuaweiSolar_Meter_ActivePower")
    ):
        check_max_day(oh_item_name, oh_state)
        check_min_day(oh_item_name, oh_state)
        check_max_month(oh_item_name, oh_state)
        check_min_month(oh_item_name, oh_state)

    if oh_item_name == "HuaweiSolar_Battery_DayChargeCapacity" or (
        oh_item_name == "HuaweiSolar_Battery_DayDisChargeCapacity"
    ):
        check_max_month(oh_item_name, oh_state)
        check_min_month(oh_item_name, oh_state)


def oh_item_command(oh_item_name: str, oh_state: str) -> int:
    """Send the item to openHAB"""
    if oh_item_name in OH_SWITCH_ITEMS:
        oh_state = OH_SWITCH_ITEMS_MAP[oh_state]
    command = f"curl -X POST --header 'Content-Type: text/plain' --header 'Accept: application/json' \
        -d '{oh_state}' '{BASE_URL}/items/{oh_item_name}'"

    return os.system(command)


async def get_data(data_set_name: str, delay_sec: int, huawei_solar_bridge: HuaweiSUN2000Bridge) -> None:
    """Get data from the inverter and wait"""
    LOGGER.info("%20s - Starting", data_set_name)
    connected = True
    if data_set_name not in globals():
        LOGGER.error("%20s - Data set not found", data_set_name)
        raise ValueError(f"Data set {data_set_name} not found")
    data_set = globals()[data_set_name]
    while connected:
        try:
            LOGGER.info("%20s - Getting values", data_set_name)
            register_names = data_set.keys()
            try:
                responses = await huawei_solar_bridge.batch_update(register_names)
            except Exception as err:
                LOGGER.error("%20s - Error getting values: %s", data_set_name, err)
                continue

            for register_name, response in responses.items():
                LOGGER.info("%20s - %35s: %s", data_set_name, register_name, response)
                if response.value is not None:
                    oh_item_name = data_set[register_name]
                    if oh_item_name is not None:
                        if isinstance(response.value, datetime.datetime):
                            time_format = "%Y-%m-%dT%H:%M:%S"
                            oh_state = datetime.datetime.strptime(response.value.strftime(time_format), time_format)
                        else:
                            oh_state = str(response.value)
                        send = True
                        if oh_item_name in OH_ITEM_MAP:
                            if OH_ITEM_MAP[oh_item_name]["value"] != oh_state:
                                LOGGER.info(
                                    "%20s - Sending value %s to %s",
                                    data_set_name,
                                    oh_state,
                                    data_set[register_name],
                                )
                            else:
                                LOGGER.info("%20s - Value %s not changed", data_set_name, oh_state)
                                send = False
                        else:
                            LOGGER.info(
                                "%20s - Sending value %s to %s",
                                data_set_name,
                                oh_state,
                                data_set[register_name],
                            )

                        if send:
                            try:
                                oh_item_command(oh_item_name=oh_item_name, oh_state=oh_state)
                            except Exception as err:
                                LOGGER.error("Error sending value: %s", err)
                            OH_ITEM_MAP[oh_item_name] = {"value": oh_state}
                        check_special_handling(oh_item_name, oh_state)
        except Exception as err:
            LOGGER.error("Error accessing values: %s", err)
            connected = False

        if delay_sec == 0:
            break
        LOGGER.info("%20s - waiting %s seconds", data_set_name, delay_sec)
        await asyncio.sleep(delay=delay_sec)

    LOGGER.info("%20s - stopping", data_set_name)


async def main():
    """Main function to test asyncio."""
    print("Starting main")

    connected = False
    connect_count = 0
    while not connected:
        try:
            connect_count += 1
            hsb = await create_tcp_bridge(host=IP_ADDRESS, port=502, slave_id=1)

            connected = True
        except Exception as err:
            LOGGER.exception("Connection Error: %s - Retry %s", err, connect_count)

    print("Connected to Huawei")
    check_once_a_day = 60 * 60 * 24
    check_once_a_hour = 60 * 60
    check_rare = 5 * 60
    check_normal = 20
    await asyncio.gather(  # get_data("bug_data", 0, hsb),
        get_data("battery_fix_data", 0, hsb),
        get_data("inverter_fix_data", 0, hsb),
        get_data("meter_fix_data", 0, hsb),
        get_data("battery_base_data", check_once_a_day, hsb),
        get_data("inverter_base_data", check_once_a_day, hsb),
        get_data("meter_base_data", check_once_a_day, hsb),
        get_data("statistic_base_data", check_once_a_day, hsb),
        get_data("statistic_hour_data", check_once_a_hour, hsb),
        get_data("battery_rare_data", check_rare, hsb),
        get_data("inverter_rare_data", check_rare, hsb),
        get_data("meter_rare_data", check_rare, hsb),
        get_data("statistic_rare_data", check_rare, hsb),
        get_data("battery_current_data", check_normal, hsb),
        get_data("inverter_current_data", check_normal, hsb),
        get_data("meter_current_data", check_normal, hsb),
    )

    await hsb.stop()
    print("Ending main")


if __name__ == "__main__":
    FORMAT = "%(asctime)s %(name)10s %(levelname)s : %(message)s"
    FILENAME = "/mnt/EAD1-0E0A/huawei_modbus_to_openHab.log"

    if os.name == "nt":
        FILENAME = "huawei_modbus_to_openHab.log"

    my_handler = RotatingFileHandler(
        FILENAME,
        mode="a",
        maxBytes=50 * 1024 * 1024,
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
