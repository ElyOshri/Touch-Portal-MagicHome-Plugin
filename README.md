# Touch-Portal-MagicHome-Plugin
A Magic-Home Plugin For Touch Portal

[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/ElyOshri/Touch-Portal-MagicHome-Plugin?include_prereleases&label=Release)](https://github.com/ElyOshri/Touch-Portal-MagicHome-Plugin/releases/tag/v1.2.1)
[![Downloads](https://img.shields.io/github/downloads/ElyOshri/Touch-Portal-MagicHome-Plugin/total?label=Downloads)](https://github.com/ElyOshri/Touch-Portal-MagicHome-Plugin/releases)
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.me/ElyOshri1)

## Overview

This plugin is for controlling MagicHome devices in your local network

## Features

* Discovers devices in the network automatically.
* Changing device state, color, brightness and mode through buttons.
* Allows button state and event changes in real time from the device.

## Installation Guide

Go to the releases:
https://github.com/ElyOshri/Touch-Portal-MagicHome-Plugin/releases

Get the latest version and there will be a TPP file you can download. From Touch Portal go to Import Plugin. Once you have done that restart Touch Portal. After that you will have a list of new actions you can choose from. Also "Dynamic Text" variables are available. You can see them from the Dynamic Text Updater, or you can add an option for "On Plugin State Change" then select the corresponding state and "Changes to". 

For Device ON or OFF state you need to use "On" or "Off".

For RGB background color change or text color change you can use "When Plug-in State changes" and set it to "does not change to" and it the text you need to put "0" for it to work.

• Note: If White Led Is Enabled, You Can't Change The Color Of The Light! So, You Need To Turn Off The White Led Before Changing The Color.

## Plugin Settings
* State Update Delay: The Time It Takes For States To Update.
* Discover Devices Delay: The Time It Takes To Discover New Devices.
* Enable Disconnected Devices: If Your Devices Have A Low Connection This Would Keep Them Connected At All Time("On" or "Off").
* Enable Log: If You Want To Troubleshoot This Would Create A Log("On" or "Off") .
* Enable Auto Update: If You Want The Plugin To Search For A New Version Every Time It Starts("On" or "Off")

## Permanent Devices Tutorial
* To Use Permanent Devices You Will Need To Enable The UI Through The Plugin Settings And Add Your Device Ip In The UI
* To Find Your Device IP Go To Your MagicHome-Pro Phone App Then Click On `Settings-->Device Manager-->Your Device-->Device Information-->IP address` (Make Sure `Local Network` Is Online) Then Copy The Ip Address To The UI Of The Plugin And Add It




Any Donations are welcome at www.paypal.me/ElyOshri1 
