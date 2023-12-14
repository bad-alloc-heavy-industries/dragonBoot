# SPDX-License-Identifier: BSD-3-Clause
from torii import Elaboratable, Module, Signal
from torii.build import Platform

__all__ = (
	'ConnectTimeout'
)

class ConnectTimeout(Elaboratable):
	""" A USB connection timeout block for bootloaders that need to always be recoverable and don't mind a wait.

	This :py:class:`amaranth.hdl.ir.Elaoratable` waits for either `timeout` seconds, or until the LUNA USB
	device reports a USB bus reset condition has been seen, which indicates we're connected to a host.

	If we reach the timeout condition, we assert the `triggerReboot` signal. If we detect a connection before then,
	that automoatically aborts the timeout timer.
	"""
	def __init__(self, *, timeout: float, clockFreq: float):
		""" Constructs a new timeout block

		Parameters
		----------
		timeout
			The amount of time to wait, in seconds, before automatically rebooting into slot 1
		clockFreq
			Frequency of the USB clock domain in Hz

		Attributes
		----------
		triggerReboot: output
			When asserted, indicates that the timeout was hit and the FPGA should be rebooted
		stop: input
			When asserted, tells this block to halt and become idle
		"""
		self.timeout = timeout
		self.clockFreq = clockFreq

		self.triggerReboot = Signal()
		self.stop = Signal()

	def elaborate(self, platform: Platform) -> Module:
		m = Module()
		# Figure out the maximum counter value that represents the required timeout
		timeoutValue = int(self.timeout * self.clockFreq)
		counter = Signal(range(timeoutValue))

		m.d.comb += self.triggerReboot.eq(0)

		# This doesn't _need_ to be a state machine, but it's much simpler for it to be..
		with m.FSM(domain = 'usb'):
			# Start out in the counting state, going up from 0 to the timeout value
			with m.State('COUNT'):
				m.d.usb += counter.eq(counter + 1)
				# If we hit the timeout, trigger the reboot
				with m.If(counter == timeoutValue - 1):
					m.next = 'TIMEOUT'
				# If we're asked to stop for any reason, permanently idle
				with m.Elif(self.stop):
					m.next = 'IDLE'

			with m.State('TIMEOUT'):
				m.d.comb += self.triggerReboot.eq(1)

			with m.State('IDLE'):
				pass

		return m
