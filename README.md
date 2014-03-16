# CSTBox extension for SOLEA ModBus products support

This repository contains the code for the extension adding the support
for SOLEA ModBus based products in the [CSTBox framework](http://cstbox.cstb.fr). 

SOLEA products are industrial modules for electrical measures. More details can be found
on their [Web site](http://solea-webshop.com/fr/).

The support comes in two forms :

  * product drivers generating CSTBox events from registers map readings
  * products definition files (aka metadata) driving the associated Web configuration editor
    pages

## Currently supported products

  * **AJ12**
      * single phase AC multi-measures module
      * outputs : U, I, P, Q, F, cosphi, active W, reactive W
  * **AJ42**
      * tri-phase AC multi-measures module
      * outputs : U, I, P, Q, F, cosphi, active W, reactive W
  * **AD12**
      * DC multi-measures module
      * outputs : U, I, P, W

## Runtime dependencies

This extension requires the CSTBox core and ModBus support extension to be already installed.
