[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![GitHub all releases](https://img.shields.io/github/downloads/andyb2000/HACS-husqvarna_automower_ble/total)
![GitHub issues by-label](https://img.shields.io/github/issues/andyb2000/HACS-husqvarna_automower_ble)
![GitHub contributors](https://img.shields.io/github/contributors/andyb2000/HACS-husqvarna_automower_ble)

# HACS-husqvarna_automower_ble - Custom integration for Husqvarna Bluetooth automowers

This is the home-assistant integration based on @alistair23 BLE implementation of Husqvarna bluetooth mowers
https://github.com/alistair23/AutoMower-BLE

## Installation
Install via HACS

# Installation
Just add this repo to the custom repos in HACS (https://hacs.xyz/docs/faq/custom_repositories/).

You can do this by going to your HACS menu on the left of Home Assistant, go into INTEGRATIONS.
At the top right you should have the 3 dots, click and choose CUSTOM REPOSITORIES.

In the "Repository" input box, paste this git folder:
https://github.com/andyb2000/HACS-husqvarna_automower_ble
Choose "Integration" from category and click ADD.
It should add and you can close the Repository input box.

You should now see the integration in HACS where you can download the latest version, or search for "Husqvarna Automower BLE".
Restart home assistant to load the new integration

# Usage

BEFORE you add the new integration, you need to have your bluetooth proxy setup.
In ESPHome setup an ESP32 BLE proxy, the config in ESPHome should look like:

```yaml
esphome:
  name: mower-ble

esp32:
  board: esp32dev
  framework:
    type: esp-idf

# Enable logging
logger:

# Enable Home Assistant API
api:

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

esp32_ble_tracker:
  scan_parameters:
    active: false
    continuous: false
    duration: 50sec

bluetooth_proxy:
  active: true
  cache_services: true

time:
  - platform: homeassistant
    on_time:
      - seconds: 0
        minutes: '*'
        then:
          esp32_ble_tracker.start_scan:
# create a button to reboot the esp32
button:
  - platform: restart
    name: "Mower ESP Restart"

```

Once you have done this, deploy it to an ESP32 that is within range of your automower.
You need the MAC address of your automower. Get this from your existing app.

Now add your custom integration in Home Assistant.
SETTINGS > INTEGRATIONS
Add Integration
Search for "Husqvarna Automower BLE"

BEFORE you enter the MAC address, power off your mower. Then power it back on and enter the physical
PIN (if required). The mower goes into bluetooth pairing mode for up to 2 minutes which you need
for this initial connection.
Now enter the MAC address for your mower. Wait for it to add/search.

You may need to repeat this several times as the bluetooth pairing does not always work correctly.

