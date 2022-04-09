# SPDX-License-Identifier: BSD-3-Clause
from arachne.core.sim import sim_case
from amaranth.sim import Simulator, Settle
from usb_protocol.types import USBRequestType, USBRequestRecipient
from usb_protocol.types.descriptors.microsoft import MicrosoftRequests
from typing import Tuple, Union

from ...windows import WindowsRequestHandler
from .descriptorSet import platformDescriptors

descriptors = platformDescriptors.descriptors

@sim_case(
	domains = (('usb', 60e6),),
	dut = WindowsRequestHandler(platformDescriptors)
)
def windowsRequestHandler(sim : Simulator, dut : WindowsRequestHandler):
	interface = dut.interface
	setup = interface.setup
	tx = interface.tx
	rx = interface.rx

	def setupReceived():
		yield setup.received.eq(1)
		yield Settle()
		yield
		yield setup.received.eq(0)
		yield Settle()
		yield
		yield

	def sendSetup(*, type : USBRequestType, retrieve : bool, request,
		value : Union[Tuple[int, int], int], index : Union[Tuple[int, int], int], length : int):
		yield setup.recipient.eq(USBRequestRecipient.DEVICE)
		yield setup.type.eq(type)
		yield setup.is_in_request.eq(1 if retrieve else 0)
		yield setup.request.eq(request)
		if isinstance(value, int):
			yield setup.value.eq(value)
		else:
			yield setup.value[0:8].eq(value[0]) # This specifies the interface
			yield setup.value[8:16].eq(value[1])
		if isinstance(index, int):
			yield setup.index.eq(index)
		else:
			yield setup.index[0:8].eq(index[0])
			yield setup.index[8:16].eq(index[1])
		yield setup.length.eq(length)
		yield from setupReceived()

	def sendGetDescriptorSet(*, vendorCode, length):
		yield from sendSetup(type = USBRequestType.VENDOR, retrieve = True,
			request = vendorCode, value = 0, index = MicrosoftRequests.GET_DESCRIPTOR_SET, length = length)

	def receiveData(*, data : Union[Tuple[int],bytes]):
		yield tx.ready.eq(1)
		yield interface.data_requested.eq(1)
		yield Settle()
		yield
		yield interface.data_requested.eq(0)
		assert (yield tx.valid) == 0
		assert (yield tx.payload) == 0
		while (yield tx.first) == 0:
			yield Settle()
			yield
		for idx, value in enumerate(data):
			assert (yield tx.valid) == 1
			assert (yield tx.payload) == value
			assert (yield interface.handshakes_out.ack) == 0
			if idx == len(data) - 1:
				yield tx.ready.eq(0)
				yield interface.status_requested.eq(1)
			yield Settle()
			yield
		assert (yield tx.valid) == 0
		assert (yield tx.payload) == 0
		assert (yield interface.handshakes_out.ack) == 1
		yield interface.status_requested.eq(0)
		yield Settle()
		yield
		assert (yield interface.handshakes_out.ack) == 0

	def ensureStall():
		yield tx.ready.eq(1)
		yield interface.data_requested.eq(1)
		yield Settle()
		yield
		yield interface.data_requested.eq(0)
		attempts = 0
		while (yield interface.handshakes_out.stall) == 0:
			assert (yield tx.valid) == 0
			attempts += 1
			if attempts > 10:
				raise AssertionError('Stall took too long to assert')
			yield Settle()
			yield
		yield Settle()
		yield

	def domainUSB():
		yield
		yield from sendGetDescriptorSet(vendorCode = 1, length = 46)
		yield from receiveData(data = descriptors[1])
		yield from sendGetDescriptorSet(vendorCode = 0, length = 46)
		yield from ensureStall()
		yield from sendGetDescriptorSet(vendorCode = 2, length = 46)
		yield from ensureStall()
		yield from sendSetup(type = USBRequestType.VENDOR, retrieve = False, request = 1,
			value = 0, index = MicrosoftRequests.GET_DESCRIPTOR_SET, length = 0)
		yield from ensureStall()
		yield from sendSetup(type = USBRequestType.VENDOR, retrieve = True, request = 1,
			value = 1, index = MicrosoftRequests.GET_DESCRIPTOR_SET, length = 0)
		yield from ensureStall()
	yield domainUSB, 'usb'
