// SPDX-License-Identifier: BSD-3-Clause
#ifndef ATXMEGA256A3U___HXX
#define ATXMEGA256A3U___HXX

extern "C"
{
	[[gnu::used, gnu::signal]] void irqUSB() noexcept;
	[[gnu::used, gnu::signal]] void irqOSCFailure() noexcept;
}

#endif /*ATXMEGA256A3U___HXX*/
