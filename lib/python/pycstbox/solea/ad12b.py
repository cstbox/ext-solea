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

""" ModBus version of the Solea AD12B multi-parameters sensor.
"""

import struct
from collections import namedtuple

from pycstbox.modbus import ModbusRegister
from pycstbox.solea.shared import SoleaHWDevice, FULL_RANGE

__author__ = 'Eric PASCUAL - CSTB (eric.pascual@cstb.fr)'
__copyright__ = 'Copyright (c) 2013 CSTB'


REG_VOLTAGE = ModbusRegister(0x10)
REG_INTENSITY = ModbusRegister(0x11)
REG_POWER = ModbusRegister(0x12)
REG_ENERGY = ModbusRegister(0x13, 2)

ALL_PARMS_SIZE = reduce(lambda sztot, sz: sztot + sz,
                        [reg.size for reg in [  #pylint: disable=E1103
                            REG_VOLTAGE,
                            REG_INTENSITY,
                            REG_POWER,
                            REG_ENERGY
                        ]])

REG_RESET_ENERGY_COUNTERS = ModbusRegister(0xa7, cfgreg=True)
REG_ADDR_BAUDRATE = ModbusRegister(0x20, cfgreg=True)

DEFAULT_U_RANGE = 800
DEFAULT_I_RANGE = 60


class AD12BHWDevice(SoleaHWDevice):
    """ Solea AD12B multi-parameters module Modbus instrument model.

    The supported model is the RTU RS485 one, the RS485 bus being connected
    via a USB.RS485 interface.

    See : http://solea-webshop.com/fr/mesure-multi-parametres-ac-dc/1-solea-ad12-transducteur-mesure-electrique-dc.html
    """

    # transducer name, as stored in the corresponding register
    TRANSDUCER_NAME = 'D113'

    REG_TRANSDUCER_NAME = ModbusRegister(0x21, size=2, cfgreg=True)

    # Definition of the type of the poll() method result

    # VERY IMPORTANT :
    # The names of its items MUST match the names of the outputs described
    # in the metadata stored in devcfg.d directory, since the notification
    # events generation process uses this key to map them.
    # (see pycstbox.hyal.device.PolledDevice.poll() method for details)
    OutputValues = namedtuple('OutputValues', [
        'U',    # instant voltage (V)
        'I',    # instant intensity (A)
        'P',    # instant active power (W)
        'W'     # accumulated energy (kWh)
    ])

    # raw to real readings conversion ratios
    RawToReal = namedtuple('Raw_to_real', 'U I P W')

    _check_I = True

    def __init__(self, port, unit_id, u_range, i_range, ti_loops=1):
        """
        :param str port: serial port on which the RS485 interface is connected
        :param int unit_id: the address of the device
        :param float u_range: real values range for voltage
        :param float i_range: real values range for intensity
        :param int ti_loops: number of wiring loops in TI (acts as current amplification factor)
        """
        SoleaHWDevice.__init__(self, port=port, unit_id=unit_id, logname='ad12b')

        u_range = float(u_range)
        i_range = float(i_range) / ti_loops

        self.raw_to_real = self.RawToReal(
            u_range / FULL_RANGE,
            i_range / FULL_RANGE,
            u_range * i_range / FULL_RANGE,
            u_range * i_range / 3600000.
        )

        self.i_range = i_range
        self.u_range = u_range
        self._invalid_I_notified = False

    def poll(self):
        """ Reads the registers holding the polled parameters and returns the
        values as a named tuple.
        """

        raw_u, raw_i, raw_p, raw_w = struct.unpack(
            '>HHHI',
            self.read_string(REG_VOLTAGE.addr, ALL_PARMS_SIZE)
        )

        outputs = self.OutputValues(
            U=float(raw_u) * self.raw_to_real.U,
            I=float(raw_i) * self.raw_to_real.I,
            P=float(raw_p) * self.raw_to_real.P,
            W=float(raw_w) * self.raw_to_real.W
        )

        # filter out weird current value when real intensity is under the
        # sensitivity threshold
        if self._check_I and outputs.I > self.i_range:
            outputs = self.OutputValues(outputs.U, 0., 0., outputs.W)
            if not self._invalid_I_notified:
                self.logger.warn(
                    'under range current value replaced by 0 for AD12B id=%d',
                    self.unit_id
                )
                self._invalid_I_notified = True
            else:
                self._invalid_I_notified = False

        return outputs

    def reset_energy_counters(self):
        """ Resets all the energy counters."""
        self.write_register(REG_RESET_ENERGY_COUNTERS.addr, 0)
