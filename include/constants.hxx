#ifndef CONSTANTS___HXX
#define CONSTANTS___HXX

#include <cstdint>

constexpr static uint16_t vid{0x1209};
// TODO: Get a new PID for the bootloader so we don't steal SPIFP's
constexpr static uint16_t pid{0xAB0C};

#endif /*CONSTANTS___HXX*/
