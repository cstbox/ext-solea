#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of CSTBox.
#
# CSTBox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CSTBox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with CSTBox.  If not, see <http://www.gnu.org/licenses/>.

""" Solea SCS photo-voltaic panel monitoring module.

This modules provides a sub-class of  minimalmodbus.Instrument which
is specialized in talking to the SCS module.

Depends on Jonas Berg's minimalmodbus Python library :
    https://pypi.python.org/pypi/MinimalModbus/
    Version in date of writing: 0.4
"""

import struct
from collections import namedtuple

from pycstbox.modbus import ModbusRegister
from pycstbox.solea.shared import SoleaInstrument

__author__ = 'Eric PASCUAL - CSTB (eric.pascual@cstb.fr)'
__copyright__ = 'Copyright (c) 2013 CSTB'
__vcs_id__ = '$Id$'
__version__ = '1.0.0'


REG_UNIT_ID = ModbusRegister(0x00)
REG_VOLTAGE = ModbusRegister(0x01)
REG_INTENSITY = ModbusRegister(0x02)
REG_TEMPERATURE = ModbusRegister(0x03)
REG_SECURITY = ModbusRegister(0x04)
REG_POWER = ModbusRegister(0x05)
REG_ENERGY = ModbusRegister(0x06)

REG_AUTO_NUMBERING = ModbusRegister(0x0A)
REG_SET_SECURITY = ModbusRegister(0x0B)

ALL_PARMS_SIZE = reduce(lambda sztot, sz : sztot + sz,
                        [reg.size for reg in [  #pylint: disable=E1103
                            REG_VOLTAGE,
                            REG_INTENSITY,
                            REG_TEMPERATURE,
                            REG_SECURITY,
                            REG_POWER,
                            REG_ENERGY,
                        ]])


class SCSInstrument(SoleaInstrument):
    """ Solea SCS multi-parameters module Modbus instrument model.

    The supported model is the RTU RS485 one, the RS485 bus being connected
    via a USB.RS485 interface.
    """

    # Definition of the type of the poll() method result

    # VERY IMPORTANT :
    # The name of its items MUST match with the name of the outputs described
    # in the metadata stored in devcfg.d directory, since the notification
    # events generation process
    # (see pycstbox.hal.device.PolledDevice.poll() method for details)
    OutputValues = namedtuple('OutputValues', [
        'U',        # instant voltage (V)
        'I',        # instant intensity (A)
        'temp',     # temperature (degC)
        'P',        # instant active power (W)
        'W',        # accumulated active energy over 10 minutes (Wh)
    ])

    # raw to real readings conversion ratios
    _Raw_to_real = namedtuple('Raw_to_real', 'U I temp P W')

    class RawValues(object):
        def __init__(self, U=0, I=0, temp=0, P=0, W=0):
            self.U, self.I, self.temp, self.P, self.W = U, I, temp, P, W

    def __init__(self, port, unit_id):
        """ Constructor

        Parameters:
            port:
                serial port on which the RS485 interface is connected
            unit_id:
                the address of the device
        """
        SoleaInstrument.__init__(self, port=port, unit_id=unit_id)

        self.RAW_TO_REAL = self._Raw_to_real(
            0.1,    # U
            0.001,  # I
            0.1,    # temp
            1.,     # P
            1.      # Q
        )

        # initializes the last known good values for filtering out weird
        # measurements, such as crazy temperature when the panel votage is 0
        self._last_rawvalues = self.RawValues()

    @property
    def unit_id(self):
        """ The id of the device """
        return self.address

    def poll(self):
        """ Reads the registers holding the polled parameters and returns the
        values as a named tuple.
        """

        raw_u, raw_i, raw_temp, _raw_relay, raw_p, raw_w = struct.unpack(
            '>HHHHHH',
            self.read_string(REG_VOLTAGE.addr, ALL_PARMS_SIZE)
        )

        # filter out weird temperatures when voltage is 0 (let's say the
        # temperature cannot go above 200 degC (ie 2000 tenth of degC)
        # in normal situation)
        if raw_temp > 2000.0:
            raw_temp = self._last_rawvalues.temp
        self._last_rawvalues = self.RawValues(
            raw_u, raw_i, raw_temp, raw_p, raw_w
        )

        outputs = self.OutputValues(
            U = float(raw_u) * self.RAW_TO_REAL.U,
            I = float(raw_i) * self.RAW_TO_REAL.I,
            temp = float(raw_temp) * self.RAW_TO_REAL.temp,
            P = float(raw_p) * self.RAW_TO_REAL.P,
            W = float(raw_w) * self.RAW_TO_REAL.W
        )
        return outputs

    def security_is_activated(self):
        """ Tells if the security is activated (ie relay opened). """
        state = struct.unpack(
            '>H',
            self.read_string(REG_SECURITY.addr, REG_SECURITY.size)
        )
        return state == 1

    def set_security_relay(self, activated):
        """ Sets the security relay state.

        Parameters:
            state:
                new state (True = security activated => relay opened)
        """
        self.write_register(REG_SET_SECURITY, 1 if activated else 0)
