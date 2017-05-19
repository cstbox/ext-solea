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

""" ModBus version of the Solea AJ42 multi-parameters sensor.
"""

import struct
from collections import namedtuple

from pycstbox.modbus import ModbusRegister
from pycstbox.solea.shared import SoleaHWDevice, FULL_RANGE

__author__ = 'Eric PASCUAL - CSTB (eric.pascual@cstb.fr)'
__copyright__ = 'Copyright (c) 2013 CSTB'


REG_VOLTAGE_A = ModbusRegister(0x10)
REG_INTENSITY_A = ModbusRegister(0x11)
REG_VOLTAGE_B = ModbusRegister(0x12)
REG_INTENSITY_B = ModbusRegister(0x13)
REG_VOLTAGE_C = ModbusRegister(0x14)
REG_INTENSITY_C = ModbusRegister(0x15)
REG_ACTIVE_POWER = ModbusRegister(0x16)
REG_REACTIVE_POWER = ModbusRegister(0x17)
REG_COS_PHI = ModbusRegister(0x18)
REG_FREQUENCY = ModbusRegister(0x19)
REG_ACTIVE_ENERGY = ModbusRegister(0x1A, 2)
REG_REACTIVE_ENERGY = ModbusRegister(0x1C, 2)

ALL_PARMS_SIZE = reduce(lambda sztot, sz: sztot + sz,
                        [reg.size for reg in [      #pylint: disable=E1103
                            REG_VOLTAGE_A,
                            REG_INTENSITY_A,
                            REG_VOLTAGE_B,
                            REG_INTENSITY_B,
                            REG_VOLTAGE_C,
                            REG_INTENSITY_C,
                            REG_ACTIVE_POWER,
                            REG_REACTIVE_POWER,
                            REG_COS_PHI,
                            REG_FREQUENCY,
                            REG_ACTIVE_ENERGY,
                            REG_REACTIVE_ENERGY
                        ]])

REG_RESET_ENERGY_COUNTERS = ModbusRegister(0xa7, cfgreg=True)
REG_ADDR_BAUDRATE = ModbusRegister(0x20, cfgreg=True)


class AJ42BHWDevice(SoleaHWDevice):
    """ Solea AJ42 tri-phases multi-parameters module Modbus instrument model.

    The supported model is the RTU RS485 one, the RS485 bus being connected
    via a USB.RS485 interface.
    """

    # transducer name, as stored in the corresponding register
    TRANSDUCER_NAME = 'J523'

    REG_TRANSDUCER_NAME = ModbusRegister(0x21, size=2, cfgreg=True)

    # change ranges above depending on the options of your specific model
    VOLTAGE_RANGE = 380
    INTENSITY_RANGE = 25

    UI_RANGE = VOLTAGE_RANGE * INTENSITY_RANGE

    # Definition of the type of the poll() method result

    # VERY IMPORTANT :
    # The names of its items MUST match the names of the outputs described
    # in the metadata stored in devcfg.d directory, since the notification
    # events generation process uses this key to map them.
    # (see pycstbox.hyal.device.PolledDevice.poll() method for details)
    OutputValues = namedtuple('OutputValues', [
        'U_a',      # instant voltage phase A (V)
        'I_a',      # instant intensity phase A (A)
        'U_b',      # instant voltage phase B (V)
        'I_b',      # instant intensity phase B (A)
        'U_c',      # instant voltage phase C (V)
        'I_c',      # instant intensity phase C (A)
        'P',        # instant active power (W)
        'Q',        # instant reactive power (VAr)
        'cos_phi',  # instant phase
        'F',        # instant frequency (Hz)
        'Wa',       # accumulated active energy (kWh)
        'Wr'        # accumulated reactive energy (kVArh)
    ])

    # raw to real readings conversion ratios
    RawToReal = namedtuple('Raw_to_real', 'U I P_Q cos_phi F Wa_Wr')

    def __init__(self, port, unit_id, u_range, i_range, ti_loops=1):
        """ Constructor

        Parameters:
            port:
                serial port on which the RS485 interface is connected
            unit_id:
                the address of the device
            u_range:
                real values range for voltage
            i_range:
                real values range for intensity
            ti_loops:
                number of wiring loops in TI (acts as current
                amplification factor)
        """
        SoleaHWDevice.__init__(self, port=port, unit_id=unit_id, logname='aj42')

        u_range = float(u_range)
        i_range = float(i_range) / ti_loops

        self.raw_to_real = self.RawToReal(
            u_range / FULL_RANGE,               # U
            i_range / FULL_RANGE,               # I
            u_range * i_range / FULL_RANGE,     # P, Q
            1. / FULL_RANGE,                    # cos phi
            1. / 1000.,                         # F
            u_range * i_range / 3600000.        # Wa, Wr
        )

        self.i_range = i_range
        self.u_range = u_range

    def poll(self):
        """ Reads the registers holding the polled parameters and returns the
        values as a named tuple.
        """

        raw_u_a, raw_i_a, raw_u_b, raw_i_b, raw_u_c, raw_i_c, raw_p, raw_q, raw_cosphi, raw_f, \
            raw_wa, raw_wr = struct.unpack(
                '>HHHHHHHHHHII',
                self.read_string(REG_VOLTAGE_A.addr, ALL_PARMS_SIZE)
            )

        outputs = self.OutputValues(
            U_a=float(raw_u_a) * self.raw_to_real.U,
            I_a=float(raw_i_a) * self.raw_to_real.I,
            U_b=float(raw_u_b) * self.raw_to_real.U,
            I_b=float(raw_i_b) * self.raw_to_real.I,
            U_c=float(raw_u_c) * self.raw_to_real.U,
            I_c=float(raw_i_c) * self.raw_to_real.I,
            P=float(raw_p) * self.raw_to_real.P_Q,
            Q=float(raw_q) * self.raw_to_real.P_Q,
            cos_phi=float(raw_cosphi) * self.raw_to_real.cos_phi,
            F=float(raw_f) * self.raw_to_real.F,
            Wa=float(raw_wa) * self.raw_to_real.Wa_Wr,
            Wr=float(raw_wr) * self.raw_to_real.Wa_Wr,
        )
        return outputs

    def reset_energy_counters(self):
        """ Resets all the energy counters."""
        self.write_register(REG_RESET_ENERGY_COUNTERS.addr, 0)
