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

import pycstbox.hal.device as haldev
import pycstbox.solea.aj12b as aj12b
import pycstbox.solea.aj42 as aj42
import pycstbox.solea.ad12b as ad12b
import pycstbox.solea.scs as scs
from pycstbox.hal import hal_device

_logger = logging.getLogger('solea')

DEFAULT_PRECISION = 3


@hal_device(device_type="solea.ad12b", coordinator_type="modbus")
class AD12B(haldev.PolledDevice):
    """ HAL device modeling the Solea AD12B module.

    DC multi-parameters module.

    The extension adds the support of polling requests and CSTBox events
    publishing on D-Bus.
    """
    def __init__(self, coord, cfg):
        super(AD12B, self).__init__(coord, cfg)
        self._hwdev = ad12b.AD12BInstrument(
            coord.port, cfg.address, cfg.U_range, cfg.I_range
        )


@hal_device(device_type="solea.aj12b", coordinator_type="modbus")
class AJ12B(haldev.PolledDevice):
    """ HAL device modeling the Solea AJ12B module.

    Single phase AC multi-parameters module.

    The extension adds the support of polling requests and CSTBox events
    publishing on D-Bus.
    """
    def __init__(self, coord, cfg):
        super(AJ12B, self).__init__(coord, cfg)
        self._hwdev = aj12b.AJ12BInstrument(
            coord.port, cfg.address, cfg.U_range, cfg.I_range
        )


@hal_device(device_type="solea.aj42b", coordinator_type="modbus")
class AJ42B(haldev.PolledDevice):
    """ HAL device modeling the Solea AJ42B module.

    Three phases AC multi-parameters module.

    The extension adds the support of polling requests and CSTBox events
    publishing on D-Bus.
    """
    def __init__(self, coord, cfg):
        super(AJ42B, self).__init__(coord, cfg)
        self._hwdev = aj42.AJ42BInstrument(
            coord.port, cfg.address, cfg.U_range, cfg.I_range
        )


@hal_device(device_type="solea.scs", coordinator_type="modbus")
class SCS(haldev.PolledDevice):
    """ HAL device modeling the Solea SCS photo-voltaic module.

    The extension adds the support of polling requests and CSTBox events
    publishing on D-Bus.
    """
    def __init__(self, coord, cfg):
        super(SCS, self).__init__(coord, cfg)
        self._hwdev = scs.SCSInstrument(coord.port, cfg.address)
