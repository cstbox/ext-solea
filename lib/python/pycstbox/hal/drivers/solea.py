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

""" HAL interface classes for SOLEA supported products. """

import logging

import pycstbox.solea.aj12b as aj12b
import pycstbox.solea.aj42 as aj42
import pycstbox.solea.ad12b as ad12b
import pycstbox.solea.scs as scs

from pycstbox.hal import hal_device
from pycstbox.modbus import RTUModbusHALDevice

_logger = logging.getLogger('solea')

DEFAULT_PRECISION = 3


@hal_device(device_type="solea.ad12b", coordinator_type="modbus")
class AD12B(RTUModbusHALDevice):
    """ HAL device modeling the Solea AD12B module.

    DC multi-parameters module.

    The extension adds the support of polling requests and CSTBox events
    publishing on D-Bus.
    """
    def __init__(self, coord_cfg, dev_cfg):
        super(AD12B, self).__init__(coord_cfg, dev_cfg)
        self._hwdev = ad12b.AD12BInstrument(
            coord_cfg.port, dev_cfg.address, dev_cfg.U_range, dev_cfg.I_range
        )


@hal_device(device_type="solea.aj12b", coordinator_type="modbus")
class AJ12B(RTUModbusHALDevice):
    """ HAL device modeling the Solea AJ12B module.

    Single phase AC multi-parameters module.

    The extension adds the support of polling requests and CSTBox events
    publishing on D-Bus.
    """
    def __init__(self, coord_cfg, dev_cfg):
        super(AJ12B, self).__init__(coord_cfg, dev_cfg)
        self._hwdev = aj12b.AJ12BInstrument(
            coord_cfg.port, dev_cfg.address, dev_cfg.U_range, dev_cfg.I_range
        )


@hal_device(device_type="solea.aj42b", coordinator_type="modbus")
class AJ42B(RTUModbusHALDevice):
    """ HAL device modeling the Solea AJ42B module.

    Three phases AC multi-parameters module.

    The extension adds the support of polling requests and CSTBox events
    publishing on D-Bus.
    """
    def __init__(self, coord_cfg, dev_cfg):
        super(AJ42B, self).__init__(coord_cfg, dev_cfg)
        self._hwdev = aj42.AJ42BInstrument(
            coord_cfg.port, dev_cfg.address, dev_cfg.U_range, dev_cfg.I_range
        )


@hal_device(device_type="solea.scs", coordinator_type="modbus")
class SCS(RTUModbusHALDevice):
    """ HAL device modeling the Solea SCS photo-voltaic module.

    The extension adds the support of polling requests and CSTBox events
    publishing on D-Bus.
    """
    def __init__(self, coord_cfg, dev_cfg):
        super(SCS, self).__init__(coord_cfg, dev_cfg)
        self._hwdev = scs.SCSInstrument(coord_cfg.port, dev_cfg.address)
