# SPDX-License-Identifier: BSD-3-Clause
from ..framework import sim_case
from torii.sim import Simulator, Settle
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

@sim_case(
	domains = (('usb', 60e6),),
	dut = GetDescriptorSetHandler(platformDescriptors)
)
def getDescriptorSetHandler(sim : Simulator, dut : GetDescriptorSetHandler):
	tx = dut.tx

	def domainUSB():
		# Make sure we're in a known state
		yield tx.ready.eq(0)
		yield Settle()
		yield
		# Set up the request
		yield dut.request.eq(1)
		yield dut.length.eq(46)
		yield dut.startPosition.eq(0)
		yield tx.ready.eq(1)
		yield dut.start.eq(1)
		yield Settle()
		yield
		yield dut.start.eq(0)
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
			assert (yield dut.stall) == 0
			yield
			yield Settle()
		assert (yield tx.valid) == 0
		yield

		# Test the first stall-able condition
		yield tx.ready.eq(0)
		yield Settle()
		yield
		yield dut.request.eq(0)
		yield dut.length.eq(0)
		yield dut.startPosition.eq(0)
		yield tx.ready.eq(1)
		yield dut.start.eq(1)
		yield Settle()
		yield
		yield dut.start.eq(0)
		yield Settle()
		attempts = 0
		while not (yield dut.stall):
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
		yield dut.request.eq(2)
		yield dut.length.eq(1)
		yield dut.startPosition.eq(0)
		yield tx.ready.eq(1)
		yield dut.start.eq(1)
		yield Settle()
		yield
		yield dut.start.eq(0)
		yield Settle()
		attempts = 0
		while not (yield dut.stall):
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

	yield domainUSB, 'usb'
