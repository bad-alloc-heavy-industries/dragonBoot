USB Descriptors
===============

```{toctree}
:hidden:
```

The descriptors for dragonBoot gateware work as follows:

* The device descriptor defines the class, subclass and protocol to be in the interfaces.
* It also defines the device to be USB 2.01 compliant to allow us to use Binary Object Storage (BOS) descriptors.
  * It is of particular note that even USB FS devices may be USB 2.01 compliant as physical protocol compliance is
    seperate from logical protocol compliance, and a device on an older physical protocol may choose to implement
    any newer logical protocol defined by the spec with the exception of USB 3.x support which requires USB HS as
    fallback.
* We define a single configuration which supports up to 100mA max draw with power required from the bus and no
  wake-up support - this keeps the implmentation simple as we have no need for wakeup support.
* In the configuration we then define one interface which is coded as being for DFU and already in DFU mode.
* This interface descriptor is then repeated for each slot with a unique alternate setting number per slot.
* The interface descriptors each sport a DFU functional descriptor that further defines:
  * That we can download, not upload, cannot be "manifested" (switched to application mode) in the way the
    standard defines and we control detaching from the bus when a DFU_DETACH request is received.
  * That we have the minimum viable timeout for detach to keep delays caused by tooling down as best as possible.
  * That sets the transfer size to equal the target Flash's erase page size
* We then define platform-specific Windows descriptors that ask Windows to bind WinUSB.sys to the DFU interface.
  * This is done to avoid the need for custom INF files and other drudgery so we get a "just works" solution out
    the box on all host platforms where this matters. Windows is the exception, not the rule.

The string descriptors are automatically generated from the strings assigned to their respective slots in the
various descriptors - this is done by
[python-usb-protocol](https://github.com/shrine-maiden-heavy-industries/python-usb-protocol).

We manually define the string dscriptors to be in American as part of the setup of the LUNA core. This is not
strictly required, but means that if any behaviour is required to change in the future, we will be immune.

The standard USB descriptors are handed off to the
{py:class}`LUNA standard descriptor handler <luna.gateware.usb.request.standard.StandardRequestHandler>` during
setup of the LUNA core, and the Windows ones to our {py:class}`dragonBoot.windows.WindowsRequestHandler`.
