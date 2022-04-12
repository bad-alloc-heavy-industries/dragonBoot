# SPDX-License-Identifier: BSD-3-Clause
from arachne.core.sim import sim_case
from amaranth import Record
from amaranth.hdl.rec import DIR_FANOUT, DIR_FANIN
from amaranth.sim import Simulator, Settle
from usb_protocol.types import USBRequestType, USBRequestRecipient, USBStandardRequests
from usb_protocol.types.descriptors.dfu import DFURequests
from typing import Tuple, Union

from ..platform import Flash
from ..dfu import DFURequestHandler, DFUState

bus = Record((
	('clk', [
		('o0', 1, DIR_FANOUT),
		('o1', 1, DIR_FANOUT),
		('o_clk', 1, DIR_FANOUT),
	]),
	('cs', [
		('o', 1, DIR_FANOUT),
	]),
	('copi', [
		('o', 1, DIR_FANOUT),
	]),
	('cipo', [
		('i', 1, DIR_FANIN),
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

	def request(self, name, number, xdr = None):
		assert name == 'flash'
		assert number == 0
		assert xdr is not None
		assert xdr['clk'] == 2
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

@sim_case(
	domains = (('usb', 60e6),),
	platform = Platform(),
	dut = DFURequestHandler(interface = 0, resource = ('flash', 0))
)
def dfuRequestHandler(sim : Simulator, dut : DFURequestHandler):
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
		yield setup.recipient.eq(USBRequestRecipient.INTERFACE)
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

	def sendSetupSetInterface():
		# setup packet for interface 0
		yield from sendSetup(type = USBRequestType.STANDARD, retrieve = False,
			request = USBStandardRequests.SET_INTERFACE, value = (1, 0), index = (0, 0), length = 0)

	def sendDFUDetach():
		yield from sendSetup(type = USBRequestType.CLASS, retrieve = False,
			request = DFURequests.DETACH, value = 1000, index = 0, length = 0)

	def sendDFUDownload():
		yield from sendSetup(type = USBRequestType.CLASS, retrieve = False,
			request = DFURequests.DOWNLOAD, value = 0, index = 0, length = 256)

	def sendDFUGetStatus():
		yield from sendSetup(type = USBRequestType.CLASS, retrieve = True,
			request = DFURequests.GET_STATUS, value = 0, index = 0, length = 6)

	def sendDFUGetState():
		yield from sendSetup(type = USBRequestType.CLASS, retrieve = True,
			request = DFURequests.GET_STATE, value = 0, index = 0, length = 1)

	def sendData(*, data : Tuple):
		yield rx.valid.eq(1)
		for value in data:
			yield Settle()
			yield
			yield rx.payload.eq(value)
			yield rx.next.eq(1)
			yield Settle()
			yield
			yield rx.next.eq(0)
		yield rx.valid.eq(0)
		yield interface.rx_ready_for_response.eq(1)
		yield Settle()
		yield
		yield interface.rx_ready_for_response.eq(0)
		yield interface.status_requested.eq(1)
		yield Settle()
		yield
		yield interface.status_requested.eq(0)
		yield interface.handshakes_in.ack.eq(1)
		yield Settle()
		yield
		yield interface.handshakes_in.ack.eq(0)
		yield Settle()
		yield

	def receiveData(*, data : Union[Tuple[int],bytes], check = True):
		result = True
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
			assert (yield tx.first) == (1 if idx == 0 else 0)
			assert (yield tx.last) == (1 if idx == len(data) - 1 else 0)
			assert (yield tx.valid) == 1
			if check:
				assert (yield tx.payload) == value
			if (yield tx.payload) != value:
				result = False
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
		return result

	def receiveZLP():
		assert (yield tx.valid) == 0
		assert (yield tx.last) == 0
		yield interface.status_requested.eq(1)
		yield Settle()
		yield
		assert (yield tx.valid) == 1
		assert (yield tx.last) == 1
		yield interface.status_requested.eq(0)
		yield interface.handshakes_in.ack.eq(1)
		yield Settle()
		yield
		assert (yield tx.valid) == 0
		assert (yield tx.last) == 0
		yield interface.handshakes_in.ack.eq(0)
		yield Settle()
		yield

	def domainUSB():
		yield
		yield
		yield
		yield
		yield from sendDFUGetStatus()
		yield from receiveData(data = (0, 0, 0, 0, DFUState.dfuIdle, 0))
		yield from sendSetupSetInterface()
		yield from receiveZLP()
		yield
		yield
		yield
		yield from sendDFUDownload()
		yield from sendData(data = dfuData)
		yield from sendDFUGetStatus()
		yield from receiveData(data = (0, 0, 0, 0, DFUState.downloadBusy, 0))
		yield from sendDFUGetState()
		yield from receiveData(data = (DFUState.downloadBusy,))
		for _ in range(6):
			yield
		yield from sendDFUGetState()
		while (yield from receiveData(data = (DFUState.downloadBusy,), check = False)):
			yield from sendDFUGetState()
		yield from sendDFUGetState()
		yield from receiveData(data = (DFUState.downloadSync,))
		yield from sendDFUGetStatus()
		yield from receiveData(data = (0, 0, 0, 0, DFUState.downloadSync, 0))
		yield
		yield from sendDFUDetach()
		assert (yield dut.triggerReboot) == 1
		yield Settle()
		yield
		assert (yield dut.triggerReboot) == 1
		yield

	yield domainUSB, 'usb'
