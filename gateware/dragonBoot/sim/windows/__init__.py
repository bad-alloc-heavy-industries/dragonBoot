# SPDX-License-Identifier: BSD-3-Clause
from torii.test import ToriiTestCase
from usb_construct.types import USBRequestType, USBRequestRecipient
from usb_construct.types.descriptors.microsoft import MicrosoftRequests

from ...windows import WindowsRequestHandler
from .descriptorSet import platformDescriptors

descriptors = platformDescriptors.descriptors

class WindowsRequestHandlerTestCase(ToriiTestCase):
	dut : WindowsRequestHandler = WindowsRequestHandler
	dut_args = {
		'descriptors': platformDescriptors
	}
	domains = (('usb', 60e6),)

	def setupReceived(self):
		yield from self.pulse(self.setup.received)
		yield from self.settle(0)
		yield

	def sendSetup(self, *, type : USBRequestType, retrieve : bool, request,
		value : tuple[int, int] | int, index : tuple[int, int] | int, length : int,
		recipient: USBRequestRecipient = USBRequestRecipient.DEVICE):
		yield self.setup.recipient.eq(recipient)
		yield self.setup.type.eq(type)
		yield self.setup.is_in_request.eq(1 if retrieve else 0)
		yield self.setup.request.eq(request)
		if isinstance(value, int):
			yield self.setup.value.eq(value)
		else:
			yield self.setup.value[0:8].eq(value[0]) # This specifies the interface
			yield self.setup.value[8:16].eq(value[1])
		if isinstance(index, int):
			yield self.setup.index.eq(index)
		else:
			yield self.setup.index[0:8].eq(index[0])
			yield self.setup.index[8:16].eq(index[1])
		yield self.setup.length.eq(length)
		yield from self.setupReceived()

	def sendGetDescriptorSet(self, *, vendorCode, length):
		yield from self.sendSetup(
			recipient = USBRequestRecipient.DEVICE, type = USBRequestType.VENDOR, retrieve = True,
			request = vendorCode, value = 0, index = MicrosoftRequests.GET_DESCRIPTOR_SET, length = length
		)

	def receiveData(self, *, data : tuple[int, ...] | bytes):
		yield self.tx.ready.eq(1)
		yield self.interface.data_requested.eq(1)
		yield from self.settle()
		yield self.interface.data_requested.eq(0)
		self.assertEqual((yield self.tx.valid), 0)
		self.assertEqual((yield self.tx.payload), 0)
		while (yield self.tx.first) == 0:
			yield
		for idx, value in enumerate(data):
			self.assertEqual((yield self.tx.first), (1 if idx == 0 else 0))
			self.assertEqual((yield self.tx.last), (1 if idx == len(data) - 1 else 0))
			self.assertEqual((yield self.tx.valid), 1)
			self.assertEqual((yield self.tx.payload), value)
			self.assertEqual((yield self.interface.handshakes_out.ack), 0)
			if idx == len(data) - 1:
				yield self.tx.ready.eq(0)
				yield self.interface.status_requested.eq(1)
			yield
		self.assertEqual((yield self.tx.valid), 0)
		self.assertEqual((yield self.tx.payload), 0)
		self.assertEqual((yield self.interface.handshakes_out.ack), 1)
		yield self.interface.status_requested.eq(0)
		yield
		self.assertEqual((yield self.interface.handshakes_out.ack), 0)

	def ensureStall(self):
		yield self.tx.ready.eq(1)
		yield self.interface.data_requested.eq(1)
		yield
		yield self.interface.data_requested.eq(0)
		attempts = 0
		while (yield self.interface.handshakes_out.stall) == 0:
			self.assertEqual((yield self.tx.valid), 0)
			attempts += 1
			if attempts > 10:
				raise AssertionError('Stall took too long to assert')
			yield
		yield from self.settle()

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'usb')
	def testWindowsRequestHandler(self):
		self.interface = self.dut.interface
		self.setup = self.interface.setup
		self.tx = self.interface.tx
		self.rx = self.interface.rx

		yield
		yield from self.sendGetDescriptorSet(vendorCode = 1, length = 46)
		yield from self.receiveData(data = descriptors[1])
		yield from self.sendGetDescriptorSet(vendorCode = 0, length = 46)
		yield from self.ensureStall()
		yield from self.sendGetDescriptorSet(vendorCode = 2, length = 46)
		yield from self.ensureStall()
		yield from self.sendSetup(type = USBRequestType.VENDOR, retrieve = False, request = 1,
			value = 0, index = MicrosoftRequests.GET_DESCRIPTOR_SET, length = 0)
		yield from self.ensureStall()
		yield from self.sendSetup(type = USBRequestType.VENDOR, retrieve = True, request = 1,
			value = 1, index = MicrosoftRequests.GET_DESCRIPTOR_SET, length = 0)
		yield from self.ensureStall()
