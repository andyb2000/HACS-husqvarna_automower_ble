[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![GitHub all releases](https://img.shields.io/github/downloads/andyb2000/HACS-husqvarna_automower_ble/total)
![GitHub issues by-label](https://img.shields.io/github/issues/andyb2000/HACS-husqvarna_automower_ble)
![GitHub contributors](https://img.shields.io/github/contributors/andyb2000/HACS-husqvarna_automower_ble)

# HACS-husqvarna_automower_ble - Custom integration for Husqvarna Bluetooth automowers

This is the home-assistant integration based on @alistair23 BLE implementation of Husqvarna bluetooth mowers
https://github.com/alistair23/AutoMower-BLE

** THIS IS DEVELOPMENTAL/DEBUG HACS integration so expect errors! **

NOTE - It is recommended to use the python library direct from the source tree, rather than pypi/pip libraries. This is due to the library being behind on pypi for legacy applications.
I have included in this HACS repo manifest for Home Assistant/Python/PIP to install from the main repo above, so this should happen.
If not, you need to manually update the library on your home assistant installation, in the location:
  /usr/local/lib/python3.12/site-packages/automower_ble/
(The newer version should NOT have request.py as a file so you can check if you are using the correct version)

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

# PIN codes with Flymo or similar

These devices (Easilife Go and other brands that use Husqvarna internal boards) don't have an option to disable PIN.
They accept the pin by pressing the sequence of buttons on the mower and on the app when setting up the pairing.
The PIN sequence is translated to digits like this:

On/OFF Power button = 1

Go/Schedule button = 2

Go button = 3

Park button = 4

See below image from operators manual. Which indicates the default pin would be 1234

![image](https://github.com/user-attachments/assets/10c75863-a634-4686-bc4c-15bb128dcad9)


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

Bluetooth discovery may now discover your mower, if so you can go to SETTINGS > INTEGRATIONS
and CONFIGURE. It will ask for the MAC and PIN.
If autodiscovered the MAC will be filled in for you, otherwise you need to enter it manually.
If the MAC is not discovered, you need to find this from your existing app.

If you need to manually add it, do it by going into:
SETTINGS > INTEGRATIONS
Add Integration
Search for "Husqvarna Automower BLE"

BEFORE you enter the MAC address, power off your mower. Then power it back on and enter the physical
PIN (if required). The mower goes into bluetooth pairing mode for up to 2 minutes which you need
for this initial connection.
During the configuration stage for the integration it will show a blank box with SUBMIT, click this when your mower
is powered on and in bluetooth pairing mode.

You may need to repeat this several times as the bluetooth pairing does not always work correctly.

# Sensors and dashboard

An automower entity is created that allows for the main control of the mower, start mowing, return to dock, etc.

![image](https://github.com/user-attachments/assets/82929c73-4b91-4249-a8b2-bdc493078a31)

In addition to that, extra sensors are created that allow you to monitor battery status, next mowing time and overall cutting details:

![image](https://github.com/user-attachments/assets/ae4c2d43-8ec3-4cb3-8f61-beb5dd3442f5)

# Release notes/updates

| Release Date | Changes |
|-----:|-----------|
| 25/Oct/24 | - Added new return to dock status as implement in HA, so bumping required release for HA up to 2024.9
 - Hassfest validation still fails due to formatting of the requirements in custom_components, see https://github.com/home-assistant/actions/issues/92 |
| 7/Apr/24 | - Updated README
 - 

