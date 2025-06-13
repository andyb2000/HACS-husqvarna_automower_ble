"""Constants for the Husqvarna Automower Bluetooth integration."""

NAME = "Automower BLE component for HASS"
DOMAIN = "husqvarna_automower_ble"
MANUFACTURER = "Husqvarna"
SERIAL = "serialNumber"
MODEL = "model"
CONF_ADDRESS = "address"
CONF_PIN = "pin"
CONF_CLIENT_ID = "client_id"
STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Custom component by @andyb2000
-------------------------------------------------------------------
"""
ERROR_CODES = {
    0: "No error",
    1: "Outside working area",
    2: "No loop signal",
    3: "Wrong loop signal",
    4: "Loop sensor problem, front",
    5: "Loop sensor problem, rear",
    8: "PIN code is incorrect",
    9: "Trapped",
    10: "Mower is upside down",
    11: "Mower has low battery",
    12: "Battery has been exhausted",
    13: "No drive",
    14: "Mower has been lifted",
    15: "Mower has been lifted",
    16: "Mower is stuck in charger",
    17: "Charger is blocked",
    25: "Cutting system is blocked",
    29: "Slope is too steep",
    62: "Frost Protection Mode",
    78: "Wheel slip",
    255: "Unknown error"
}
