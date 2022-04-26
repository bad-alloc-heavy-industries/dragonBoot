The SPI Flash controller
========================

```{toctree}
:hidden:
```

The Flash controller is comprised of two major parts - the underlying
{py:class}`SPI bus <dragonBoot.spi.SPIBus>` engine, and the
{py:class}`Flash controller <dragonBoot.flash.SPIFlash>` itself.

```{eval-rst}
.. automodule:: dragonBoot.spi
  :members:

.. autoclass:: dragonBoot.flash.SPIFlash
  :members:

.. autoclass:: dragonBoot.flash.SPIFlashCmd
  :members:

.. autoclass:: dragonBoot.flash.SPIFlashOp
  :members:
```

Additionaly there is also a configuration class used by platforms to define their configuration Flash to the bootloader.

```{eval-rst}
.. autoclass:: dragonBoot.platform.Flash
  :members:
```
