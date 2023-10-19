# SPDX-License-Identifier: BSD-3-Clause
from torii.sim import Settle
from torii.test import ToriiTestCase
from usb_construct.emitters.descriptors.microsoft import SetHeaderDescriptorEmitter, PlatformDescriptorCollection

from ...windows.descriptorSet import GetDescriptorSetHandler

platformDescriptors = PlatformDescriptorCollection()
setHeader = SetHeaderDescriptorEmitter()
with setHeader.SubsetHeaderConfiguration() as subsetConfig:
	subsetConfig.bConfigurationValue = 1

	with subsetConfig.SubsetHeaderFunction() as subsetFunc:
		subsetFunc.bFirstInterface = 0

		with subsetFunc.FeatureCompatibleID() as compatID:
			compatID.CompatibleID = 'WINUSB'
			compatID.SubCompatibleID = ''
platformDescriptors.add_descriptor(setHeader, 1)

descriptors = platformDescriptors.descriptors

class GetDescriptorSetHandlerTestCase(ToriiTestCase):
	dut: GetDescriptorSetHandler = GetDescriptorSetHandler
	dut_args = {
		'descriptorCollection': platformDescriptors
	}
	domains = (('usb', 60e6),)

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'usb')
	def testGetDescriptorSetHandler(self):
		tx = self.dut.tx

		# Make sure we're in a known state
		yield tx.ready.eq(0)
		yield Settle()
		yield
		# Set up the request
		yield self.dut.request.eq(1)
		yield self.dut.length.eq(46)
		yield self.dut.startPosition.eq(0)
		yield tx.ready.eq(1)
		yield self.dut.start.eq(1)
		yield Settle()
		yield
		yield self.dut.start.eq(0)
		yield Settle()
		while (yield tx.valid) == 0:
			yield
			yield Settle()
		descriptor = descriptors[1]
		bytes = len(descriptor)
		lastByte = bytes - 1
		# And read back the result, validating state along the way
		for byte in range(bytes):
			assert (yield tx.first) == (1 if byte == 0 else 0)
			assert (yield tx.last) == (1 if byte == lastByte else 0)
			assert (yield tx.valid) == 1
			assert (yield tx.payload) == descriptor[byte]
			assert (yield self.dut.stall) == 0
			yield
			yield Settle()
		assert (yield tx.valid) == 0
		yield

		# Test the first stall-able condition
		yield tx.ready.eq(0)
		yield Settle()
		yield
		yield self.dut.request.eq(0)
		yield self.dut.length.eq(0)
		yield self.dut.startPosition.eq(0)
		yield tx.ready.eq(1)
		yield self.dut.start.eq(1)
		yield Settle()
		yield
		yield self.dut.start.eq(0)
		yield Settle()
		attempts = 0
		while not (yield self.dut.stall):
			assert (yield tx.valid) == 0
			attempts += 1
			if attempts > 10:
				raise AssertionError('Stall took too long to assert')
			yield
			yield Settle()
		yield

		# Test the second stall-able condition
		yield tx.ready.eq(0)
		yield Settle()
		yield
		yield self.dut.request.eq(2)
		yield self.dut.length.eq(1)
		yield self.dut.startPosition.eq(0)
		yield tx.ready.eq(1)
		yield self.dut.start.eq(1)
		yield Settle()
		yield
		yield self.dut.start.eq(0)
		yield Settle()
		attempts = 0
		while not (yield self.dut.stall):
			assert (yield tx.valid) == 0
			attempts += 1
			if attempts > 10:
				raise AssertionError('Stall took too long to assert')
			yield
			yield Settle()
		yield

		# Cleanup
		yield tx.ready.eq(0)
		yield Settle()
		yield
		yield Settle()
		yield
