iCE40 Platform Helper
=====================

```{toctree}
:hidden:
```

To reduce boilerplate and aid platform implementation, an iCE40 platform helper type has been defined.

```{eval-rst}
.. autoclass:: dragonBoot.platform.DragonICE40Platform
  :members:
```

iCE40 slots system
------------------

Because of the iCE40 warmboot block, dragonBoot also defines a set of types and construct structures for building the slots configuration for a given target platform

```{eval-rst}
.. autoclass:: dragonBoot.ice40.Slots
  :members:
  :private-members:

.. autoclass:: dragonBoot.ice40.Opcodes
  :members:

.. autoclass:: dragonBoot.ice40.SpecialOpcodes
  :members:

.. autoclass:: dragonBoot.ice40.BootModes
  :members:

.. autosubconstruct:: dragonBoot.ice40.Special
.. autosubconstruct:: dragonBoot.ice40.BootMode
.. autosubconstruct:: dragonBoot.ice40.BankOffset
.. autosubconstruct:: dragonBoot.ice40.BootAddress
.. autosubconstruct:: dragonBoot.ice40.Payload
.. autosubconstruct:: dragonBoot.ice40.Instruction
.. autosubconstruct:: dragonBoot.ice40.Slot
```
