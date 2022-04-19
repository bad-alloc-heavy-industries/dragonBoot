Request Handlers
================

```{toctree}
:hidden:

dfu
windows
```

The gateware uses three request handlers to function:

* {py:class}`Standard Request Handler<luna.gateware.usb.request.standard.StandardRequestHandler>` (from the LUNA framework)
* [DFU Request Handler](dfu.md)
* [Windows Platform-Specific Request Handler](windows.md)

As DFU is handled entirely through endpoint 0 control requests, this along with the [descriptors](../descriptors.md) form the complete USB portion of the gateware
