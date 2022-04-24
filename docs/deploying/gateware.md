Deploying the gateware
======================

System Requirements
-------------------

The dragonBoot gateware requires the following:

* Python 3.8 or newer
* [Yosys](https://github.com/YosysHQ/yosys) 0.10 or newer
* [nextpnr](https://github.com/YosysHQ/nextpnr) 0.4 or newer

Installing Python
-----------------

First install python + pip for your platform:

```{eval-rst}
.. platform-picker::
  .. platform-choice:: arch
    :title: Arch Linux

    .. code-block:: console

      $ sudo pacman -S python python-pip

  .. platform-choice:: debian
    :title: Debian/Ubuntu Linux

    .. code-block:: console

      $ sudo apt install python3 python3-pip

  .. platform-choice:: linux
    :title: Other Linux

    .. todo::

      Write this section

  .. platform-choice:: macos
    :title: macOS

    .. code-block:: console

      $ brew install python

  .. platform-choice:: windows
    :title: Windows

    Download the latest installer from `the Python downloads page <https://www.python.org/downloads/>`_
    and follow the instructions in the installer to have Python end up on %PATH%

```

Once you have python you will then need Yosys and nextpnr.
There are two ways to get these requirements - [natively](#native-yosys-and-nextpnr) or
[via YoWASP](#yowasp-yosys-and-nextpnr), details below.

Native yosys and nextpnr
------------------------

```{eval-rst}
.. platform-picker::
  .. platform-choice:: arch
    :title: Arch Linux

    .. code-block:: console

      $ sudo pacman -S python python-pip

```

YoWASP yosys and nextpnr
------------------------

Then install Yosys:

```{code-block} console

$ pip3 install yowasp-yosys
Collecting yowasp-yosys
  Downloading yowasp_yosys-0.16.post31.dev334-py3-none-any.whl (6.8 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.8/6.8 MB 10.5 MB/s eta 0:00:00
Collecting appdirs~=1.4
  Using cached appdirs-1.4.4-py2.py3-none-any.whl (9.6 kB)
Collecting wasmtime<0.31,>=0.30
  Downloading wasmtime-0.30.0-py3-none-manylinux1_x86_64.whl (5.6 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.6/5.6 MB 20.9 MB/s eta 0:00:00
Installing collected packages: appdirs, wasmtime, yowasp-yosys
Successfully installed appdirs-1.4.4 wasmtime-0.30.0 yowasp-yosys-0.16.post31.dev334
```

Finally, install nextpnr for your target:

```{eval-rst}
.. platform-picker::
  .. platform-choice:: ice40
    :title: Lattice iCE40

    .. code-block:: console

      $ pip3 install yowasp-nextpnr-ice40
      Collecting yowasp-nextpnr-ice40
        Downloading yowasp_nextpnr_ice40-0.3.dev303-py3-none-any.whl (71.9 MB)
          ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 71.9/71.9 MB 8.9 MB/s eta 0:00:00
      Requirement already satisfied: appdirs~=1.4 in ./env/lib/python3.10/site-packages (from yowasp-nextpnr-ice40) (1.4.4)
      Requirement already satisfied: wasmtime<0.31,>=0.30 in ./env/lib/python3.10/site-packages (from yowasp-nextpnr-ice40) (0.30.0)
      Installing collected packages: yowasp-nextpnr-ice40
      Successfully installed yowasp-nextpnr-ice40-0.3.dev303

  .. platform-choice:: ecp5
    :title: Lattice ECP5

    .. code-block:: console

      $ pip3 install yowasp-nextpnr-ecp5
      Collecting yowasp-nextpnr-ecp5
        Downloading yowasp_nextpnr_ecp5-0.3.dev303-py3-none-any.whl (30.1 MB)
          ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 30.1/30.1 MB 14.3 MB/s eta 0:00:00
      Requirement already satisfied: appdirs~=1.4 in ./env/lib/python3.10/site-packages (from yowasp-nextpnr-ecp5) (1.4.4)
      Requirement already satisfied: wasmtime<0.31,>=0.30 in ./env/lib/python3.10/site-packages (from yowasp-nextpnr-ecp5) (0.30.0)
      Installing collected packages: yowasp-nextpnr-ecp5
      Successfully installed yowasp-nextpnr-ecp5-0.3.dev303
```
