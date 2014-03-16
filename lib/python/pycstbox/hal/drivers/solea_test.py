#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from pycstbox.hal.drivers import solea

def _tohex(s):
    return ' '.join(['%02x' % ord(b) for b in s])

class MockupCoordinator(object):
    def __init__(self, cfg):
        self.cfg = cfg

class MockupConfig(object):
    pass

class _BaseTestCase(unittest.TestCase):
    _hal_device = None

    def setUp(self):
        self._simulated_reply = None

    def simulated_read_string(self, addr, reg_cnt):
        """ Simulated modbus.Instrumment read_string.

        Original method is pacthed with this one to simulate a physical read
        and return a simulated reply for the tests.

        The reply to be return must have been set in the attribute _simulated_reply
        before activating the device read query. For conveniency's sake, the
        value is adjusted to the requested read size, padding it with 0's if
        needed.

        Parameters:
            addr:
                address of the first register to read
            reg_cnt:
                number of 16 bits registers to read
        """
        self.assertIsNotNone(self._simulated_reply, 'simulated reply not set')
        reply = self._simulated_reply
        l = len(reply)
        size = 2 * reg_cnt
        if l < size:
            reply = reply.ljust(size, r'\00')
        elif l > size:
            reply = reply[:size]

        print('simulating read of %d regs starting from address %d' % (reg_cnt, addr))
        print('--> reply : %s (%d bytes)' % (_tohex(reply), size))
        return reply

    def simulate_reply(self, data):
        self._simulated_reply = ''.join(chr(b) for b in data)

    def set_hal_device(self, dev):
        self._hal_device = dev
        self._hal_device._hwdev.read_string = self.simulated_read_string    #pylint: disable=W0212

    def get_hw_device(self):
        return self._hal_device._hwdev          #pylint: disable=W0212


class TestAJ12BHalDriver(_BaseTestCase):
    def setUp(self):
        _BaseTestCase.setUp(self)

        cfg_coord = MockupConfig()
        # just put here an existing port so that the coordinator constructor
        # will not complain. Remember we do no real serial I/O.
        cfg_coord.port = '/dev/ttyS0'
        coord = MockupCoordinator(cfg_coord)

        cfg_dev = MockupConfig()
        cfg_dev.address = 1
        cfg_dev.outputs = {
            'U' : {
                'varname' : 'voltage_test',
                'enabled' : True
            },
            'I' : {
                'varname' : 'current_office',
                'enabled' : True
            }
        }

        self.set_hal_device(solea.AJ12B(coord=coord, cfg=cfg_dev))

    def test_poll(self):
        simulated_vars = {
            'voltage': 230.,
            'current': 10.
        }

        aj12 = self.get_hw_device()

        raw_U = int(simulated_vars['voltage'] * aj12.FULL_RANGE / aj12.VOLTAGE_RANGE)
        raw_I = int(simulated_vars['current'] * aj12.FULL_RANGE / aj12.INTENSITY_RANGE)
        data = [
            (raw_U >> 8) & 0xff, raw_U & 0xff,
            (raw_I >> 8) & 0xff, raw_I & 0xff
        ]
        self.simulate_reply(data)

        events = self._hal_device.poll()

        print(events)
        self.assertEqual(len(events), len(simulated_vars), 'event count mismatch')

        for evt in events:
            value = evt.data['value']
            print('var_type=%s value=%s' % (evt.var_type, value))
            try:
                expected_value = simulated_vars[evt.var_type]
                self.assertEqual(value, expected_value, 'wrong %s value' % evt.var_type)
            except KeyError:
                self.fail('wrong var type (%s)' % evt.var_type)


class TestSCSHalDriver(_BaseTestCase):
    def setUp(self):
        _BaseTestCase.setUp(self)

        cfg_coord = MockupConfig()
        cfg_coord.port = '/dev/ttyS0'
        coord = MockupCoordinator(cfg_coord)

        cfg_dev = MockupConfig()
        cfg_dev.address = 1
        cfg_dev.outputs = {
            'U' : {
                'varname' : 'panel_voltage',
                'enabled' : True
            },
            'I' : {
                'varname' : 'current',
                'enabled' : True
            },
            'temp' : {
                'varname' : 'temperature',
                'enabled' : True
            }
        }

        self.set_hal_device(solea.SCS(coord=coord, cfg=cfg_dev))

    def test_poll(self):
        simulated_vars = {
            'voltage': 230.,
            'current': 10.,
            'temperature': 27.5
        }

        raw_U = int(simulated_vars['voltage'] * 10)
        raw_I = int(simulated_vars['current'] * 1000)
        raw_temp = int(simulated_vars['temperature'] * 10)
        data = [
            (raw_U >> 8) & 0xff, raw_U & 0xff,
            (raw_I >> 8) & 0xff, raw_I & 0xff,
            (raw_temp >> 8) & 0xff, raw_temp & 0xff,
        ]
        self.simulate_reply(data)

        events = self._hal_device.poll()

        print(events)
        self.assertEqual(len(events), len(simulated_vars), 'event count mismatch')

        for evt in events:
            value = evt.data['value']
            print('var_type=%s value=%s' % (evt.var_type, value))
            try:
                expected_value = simulated_vars[evt.var_type]
                self.assertEqual(value, expected_value, 'wrong %s value' % evt.var_type)
            except KeyError:
                self.fail('wrong var type (%s)' % evt.var_type)

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
