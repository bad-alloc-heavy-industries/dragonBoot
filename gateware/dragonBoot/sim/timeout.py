# SPDX-License-Identifier: BSD-3-Clause
from torii.sim import Settle
from torii.test import ToriiTestCase

from ..timeout import ConnectTimeout

class ConnectTimeoutTestCase(ToriiTestCase):
	dut = ConnectTimeout
	dut_args = {
		'timeout': (1 / 12) * 10e-6,
		'clockFreq': 12e6,
	}
	domains = (('usb', 12e6), )

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'usb')
	def testTimeout(self):
		self.assertEqual((yield self.dut.triggerReboot), 0)
		yield from self.step(7)
		yield Settle()
		self.assertEqual((yield self.dut.triggerReboot), 0)
		yield
		yield Settle()
		self.assertEqual((yield self.dut.triggerReboot), 1)
		yield
		yield Settle()
		self.assertEqual((yield self.dut.triggerReboot), 1)

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'usb')
	def testConnected(self):
		self.assertEqual((yield self.dut.triggerReboot), 0)
		yield from self.step(5)
		yield Settle()
		self.assertEqual((yield self.dut.triggerReboot), 0)
		yield self.dut.stop.eq(1)
		yield
		yield Settle()
		self.assertEqual((yield self.dut.triggerReboot), 0)
		yield self.dut.stop.eq(0)
		yield
		yield Settle()
		self.assertEqual((yield self.dut.triggerReboot), 0)
		yield from self.step(10)
		yield Settle()
		self.assertEqual((yield self.dut.triggerReboot), 0)
