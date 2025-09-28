# SPDX-License-Identifier: BSD-3-Clause
from torii.hdl import Record
from torii.hdl.rec import Direction
from torii.build import Clock
from torii.test import ToriiTestCase
from usb_construct.types import USBRequestType, USBRequestRecipient, USBStandardRequests
from usb_construct.types.descriptors.dfu import DFURequests
from typing import Tuple, Union

from ..platform import Flash
from ..dfu import DFURequestHandler, DFUState

bus = Record((
	('clk', [
		('o', 1, Direction.FANOUT),
	]),
	('cs', [
		('o', 1, Direction.FANOUT),
	]),
	('copi', [
		('o', 1, Direction.FANOUT),
	]),
	('cipo', [
		('i', 1, Direction.FANIN),
	]),
))

class Platform:
	flash = Flash(
		size = 512 * 1024,
		pageSize = 64,
		erasePageSize = 256,
		eraseCommand = 0x20
	)

	flash.slots = 4
	flash.slotSize = 2 ** 18

	default_clk_constraint = Clock(12e6)

	def request(self, name, number):
		assert name == 'flash'
		assert number == 0
		return bus

dfuData = (
	0xff, 0x00, 0x00, 0xff, 0x7e, 0xaa, 0x99, 0x7e, 0x51, 0x00, 0x01, 0x05, 0x92, 0x00, 0x20, 0x62,
	0x03, 0x67, 0x72, 0x01, 0x10, 0x82, 0x00, 0x00, 0x11, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
)

class DFURequestHandlerTestCase(ToriiTestCase):
	dut : DFURequestHandler = DFURequestHandler
	dut_args = {
		'configuration': 1,
		'interface': 0,
		'resource': ('flash', 0),
	}
	domains = (('usb', 60e6),)
	platform = Platform()

	def setupReceived(self):
		yield self.setup.received.eq(1)
		yield from self.settle()
		yield self.setup.received.eq(0)
		yield from self.settle()
		yield

	def sendSetup(self, *, type : USBRequestType, retrieve : bool, request,
		value : Union[Tuple[int, int], int], index : Union[Tuple[int, int], int], length : int
	):
		yield self.setup.recipient.eq(USBRequestRecipient.INTERFACE)
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

	def sendSetupSetInterface(self):
		# setup packet for interface 0
		yield from self.sendSetup(type = USBRequestType.STANDARD, retrieve = False,
			request = USBStandardRequests.SET_INTERFACE, value = (1, 0), index = (0, 0), length = 0)

	def sendDFUDetach(self):
		yield from self.sendSetup(type = USBRequestType.CLASS, retrieve = False,
			request = DFURequests.DETACH, value = 1000, index = 0, length = 0)

	def sendDFUDownload(self):
		yield from self.sendSetup(type = USBRequestType.CLASS, retrieve = False,
			request = DFURequests.DOWNLOAD, value = 0, index = 0, length = 256)

	def sendDFUGetStatus(self):
		yield from self.sendSetup(type = USBRequestType.CLASS, retrieve = True,
			request = DFURequests.GET_STATUS, value = 0, index = 0, length = 6)

	def sendDFUGetState(self):
		yield from self.sendSetup(type = USBRequestType.CLASS, retrieve = True,
			request = DFURequests.GET_STATE, value = 0, index = 0, length = 1)

	def sendData(self, *, data : tuple[int, ...]):
		yield self.rx.valid.eq(1)
		for value in data:
			yield from self.settle()
			yield self.rx.data.eq(value)
			yield self.rx.next.eq(1)
			yield from self.settle()
			yield self.rx.next.eq(0)
		yield self.rx.valid.eq(0)
		yield self.interface.rx_ready_for_response.eq(1)
		yield from self.settle()
		yield self.interface.rx_ready_for_response.eq(0)
		yield self.interface.status_requested.eq(1)
		yield from self.settle()
		yield self.interface.status_requested.eq(0)
		yield self.interface.handshakes_in.ack.eq(1)
		yield from self.settle()
		yield self.interface.handshakes_in.ack.eq(0)
		yield from self.settle()

	def receiveData(self, *, data : tuple[int, ...] | bytes, check = True):
		result = True
		yield self.tx.ready.eq(1)
		yield self.interface.data_requested.eq(1)
		yield
		yield self.interface.data_requested.eq(0)
		assert (yield self.tx.valid) == 0
		assert (yield self.tx.data) == 0
		while (yield self.tx.first) == 0:
			yield
		for idx, value in enumerate(data):
			assert (yield self.tx.first) == (1 if idx == 0 else 0)
			assert (yield self.tx.last) == (1 if idx == len(data) - 1 else 0)
			assert (yield self.tx.valid) == 1
			if check:
				assert (yield self.tx.data) == value
			if (yield self.tx.data) != value:
				result = False
			assert (yield self.interface.handshakes_out.ack) == 0
			if idx == len(data) - 1:
				yield self.tx.ready.eq(0)
				yield self.interface.status_requested.eq(1)
			yield
		assert (yield self.tx.valid) == 0
		assert (yield self.tx.data) == 0
		assert (yield self.interface.handshakes_out.ack) == 1
		yield self.interface.status_requested.eq(0)
		yield
		assert (yield self.interface.handshakes_out.ack) == 0
		return result

	def receiveZLP(self):
		assert (yield self.tx.valid) == 0
		assert (yield self.tx.last) == 0
		yield self.interface.status_requested.eq(1)
		yield
		assert (yield self.tx.valid) == 1
		assert (yield self.tx.last) == 1
		yield self.interface.status_requested.eq(0)
		yield self.interface.handshakes_in.ack.eq(1)
		yield
		assert (yield self.tx.valid) == 0
		assert (yield self.tx.last) == 0
		yield self.interface.handshakes_in.ack.eq(0)
		yield

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'usb')
	def testDFURequestHandler(self):
		self.interface = self.dut.interface
		self.setup = self.interface.setup
		self.tx = self.interface.tx
		self.rx = self.interface.rx

		yield self.interface.active_config.eq(1)
		yield from self.settle()
		yield
		yield from self.wait_until_low(bus.cs.o)
		yield from self.wait_for(20e-6)
		yield from self.step(2)
		yield from self.sendDFUGetStatus()
		yield from self.receiveData(data = (0, 0, 0, 0, DFUState.dfuIdle, 0))
		yield from self.sendSetupSetInterface()
		yield from self.receiveZLP()
		yield from self.step(3)
		yield from self.sendDFUDownload()
		yield from self.sendData(data = dfuData)
		yield from self.sendDFUGetStatus()
		yield from self.receiveData(data = (0, 0, 0, 0, DFUState.downloadBusy, 0))
		yield from self.sendDFUGetState()
		yield from self.receiveData(data = (DFUState.downloadBusy,))
		yield from self.step(6)
		yield from self.sendDFUGetState()
		while (yield from self.receiveData(data = (DFUState.downloadBusy,), check = False)):
			yield from self.sendDFUGetState()
		yield from self.sendDFUGetState()
		yield from self.receiveData(data = (DFUState.downloadSync,))
		yield from self.sendDFUGetStatus()
		yield from self.receiveData(data = (0, 0, 0, 0, DFUState.downloadSync, 0))
		yield from self.sendDFUGetState()
		yield from self.receiveData(data = (DFUState.downloadIdle,))
		yield
		yield from self.sendDFUDetach()
		yield from self.receiveZLP()
		assert (yield self.dut.triggerReboot) == 1
		yield from self.settle()
		assert (yield self.dut.triggerReboot) == 1
		yield
