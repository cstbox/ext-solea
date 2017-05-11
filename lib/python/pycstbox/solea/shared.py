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

from pycstbox.modbus import RTUModbusHWDevice

# DEFAULT_BAUDRATE = 9600

FULL_RANGE = 10000.


class SoleaInstrument(RTUModbusHWDevice):
    """ Base class for implementing models of SOLEA Modbus devices. """

    TRANSDUCER_NAME = None
    REG_TRANSDUCER_NAME = None

    def __init__(self, port, unit_id, logname):
        """
        :param str port: serial port on which the RS485 interface is connected
        :param int unit_id: the device unit id (aka address)
        :param str logname: the root name of the device logger 
        """
        super(SoleaInstrument, self).__init__(port=port, unit_id=int(unit_id), logname=logname)

    @property
    def unit_id(self):
        """ The id of the device """
        return self.address

    def get_transducer_name(self):
        """ Return the transducer name register.

        Used mainly for checking that communications are ok and that we are
        dealing with the right guy.
        """
        if self.REG_TRANSDUCER_NAME:
            return self.read_string(
                self.REG_TRANSDUCER_NAME.addr, self.REG_TRANSDUCER_NAME.size
            )
        else:
            return None

    def check(self):
        """ Checks we are talking to the right guy.

        :returns: True if the device name matches ours, or if we don't know our name
        """
        if self.TRANSDUCER_NAME and self.REG_TRANSDUCER_NAME:
            return self.get_transducer_name() == self.TRANSDUCER_NAME
        else:
            return True
