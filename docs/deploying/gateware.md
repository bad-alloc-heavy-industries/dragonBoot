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

First install `python`, `pip` and `virtualenv` for your platform:

```{eval-rst}
.. platform-picker::
  .. platform-choice:: arch
    :title: Arch Linux

    .. code-block:: console

      $ sudo pacman -S python python-pip python-virtualenv

  .. platform-choice:: debian
    :title: Debian/Ubuntu Linux

    .. code-block:: console

      $ sudo apt install python3 python3-pip python3-virtualenv

  .. platform-choice:: linux
    :title: Other Linux

    .. todo::

      Using your distro package manager, install :code:`python3`, :code:`python3-pip` and
      :code:`python3-virtualenv` or equivalent packages that satisfy the minimum version
      requirement of Python 3.8.

  .. platform-choice:: macos
    :title: macOS

    .. code-block:: console

      $ brew install python
      $ pip3 install virtualenv

  .. platform-choice:: windows
    :title: Windows

    Download the latest installer from `the Python downloads page <https://www.python.org/downloads/>`_
    and follow the instructions in the installer to have Python end up on :code:`%PATH%`.

```

Once you have completed the platform-specific steps, please create a virtual environment and activate it
for all further steps:

```{code-block} console

$ virtualenv env
created virtual environment CPython3.10.4.final.0-64 in 100ms
  creator CPython3Posix(dest=/tmp/env, clear=False, no_vcs_ignore=False, global=False)
  seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=/home/dx-mon/.local/share/virtualenv)
    added seed packages: pip==22.0.4, setuptools==61.1.1, wheel==0.37.1
  activators BashActivator,CShellActivator,FishActivator,NushellActivator,PowerShellActivator,PythonActivator
$ . env/bin/activate
```

```{note}

Windows users will need to either use MSYS2, WSL2 and follow the Linux instructions, or substitute
`. env/bin/activate` for `call env/bin/activate.bat` if using the Windows command line.
We recomend using Windows Terminal for a better experience doing this.
```

Once you have python you will then need Yosys and nextpnr.
There are two ways to get these requirements - [natively](#native-yosys-and-nextpnr) or
[via YoWASP](#yowasp-yosys-and-nextpnr), details below.

Native Yosys and nextpnr
------------------------

```{eval-rst}
.. platform-picker::
  .. platform-choice:: arch
    :title: Arch Linux

    Yosys can be installed from the community repos with:

    .. code-block:: console

      $ sudo pacman -S yosys

    However, it is preferred due to some features dragonBoot needs for the toolchain to be installed from the
    `AUR <https://aur.archlinux.org/>`_. nextpnr is not available in repos, so must be installed from the AUR.

    To install Yosys from the AUR, install the :code:`yosys-nightly` package with your favourite AUR helper,
    or run:

    .. code-block:: console

      $ git clone https://aur.archlinux.org/yosys-nightly.git
      $ cd yosys-nightly
      $ makepkg -sic yosys-nightly

    Once installed you must then pick a nextpnr to install suitable for your target.
    For the Lattice iCE40 parts, install :code:`nextpnr-ice40-nightly` with your favourite AUR helper, or run:

    .. code-block:: console

      $ git clone https://aur.archlinux.org/nextpnr-ice40-nightly.git
      $ cd nextpnr-ice40-nightly
      $ makepkg -sic nextpnr-ice40-nightly

    For the Lattice ECP5 parts, install :code:`nextpnr-ecp5-nightly` with your favourite AUR helper, or run:

    .. code-block:: console

      $ git clone https://aur.archlinux.org/nextpnr-ecp5-nightly.git
      $ cd nextpnr-ecp5-nightly
      $ makepkg -sic nextpnr-ecp5-nightly

  .. platform-choice:: debian
    :title: Debian/Ubuntu Linux

    The Debian versions of Yosys and nextpnr are too old, so you must use the
    `YoWASP <#yowasp-yosys-and-nextpnr>`_ versions. dragonBoot requires features from Yosys
    0.10 and newer, and will not place and route with nextpnr older than 0.4.

  .. platform-choice:: linux
    :title: Other Linux

    .. todo::

      Write this section

  .. platform-choice:: macos
    :title: macOS

    Given Homebrew doesn't have nextpnr, for the native tools please use
    `oss-cad-suite-builder <https://github.com/YosysHQ/oss-cad-suite-build/releases>`_. Extract
    the latest tarball for :code:`darwin-x64`, and stick the :code:`oss-cad-suite/bin` directory from
    the extracted tarball in to your environment's :code:`$PATH`.

  .. platform-choice:: windows
    :title: Windows

    The easiest way to get started on Windows if not using the `YoWASP <#yowasp-yosys-and-nextpnr>`_ versions
    of the tools, is to use `oss-cad-suite-builder <https://github.com/YosysHQ/oss-cad-suite-build/releases>`_.
    Run the latest installer for :code:`windows-x64`, and stick the :code:`oss-cad-suite/bin` directory from
    the installation in to your environment's :code:`%PATH%`.

    .. note::

        If you do not wish to edit your environment block to do this permanently, please run:

        .. code-block:: console

          $ call <extracted_location>\oss-cad-suite\environment.bat

```

Once done, continue setup with [setting up dragonBoot](#setting-up-dragonboot).

YoWASP Yosys and nextpnr
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

Finally, install `nextpnr` for your target:

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

Once done, continue setup with [setting up dragonBoot](#setting-up-dragonboot).

Setting up dragonBoot
---------------------

The next few steps are considerably easier, and consist of a simple `pip` command and running the bootloader builder.

First we install the project's requirements:

```{code-block} console

$ pip3 install -r requirements.txt
Collecting torii
  Cloning https://github.com/shrine-maiden-heavy-industries/torii-hdl.git (to revision main) to /tmp/pip-install-esl2f2gm/torii_dbbd76ad2ecf4fada3e2a39ac8a4bd27
  Running command git clone --filter=blob:none --quiet https://github.com/shrine-maiden-heavy-industries/torii-hdl.git /tmp/pip-install-esl2f2gm/torii_dbbd76ad2ecf4fada3e2a39ac8a4bd27
  Resolved https://github.com/shrine-maiden-heavy-industries/torii-hdl.git to commit f8716fe8ca652844faf83b6ebeaa6d2f32110510
  Preparing metadata (setup.py) ... done
Collecting sol-usb
  Cloning https://github.com/shrine-maiden-heavy-industries/sol (to revision main) to /tmp/pip-install-esl2f2gm/sol-usb_256334e4182a41b59be038754cdf8b07
  Running command git clone --filter=blob:none --quiet https://github.com/shrine-maiden-heavy-industries/sol /tmp/pip-install-esl2f2gm/sol-usb_256334e4182a41b59be038754cdf8b07
  Resolved https://github.com/shrine-maiden-heavy-industries/sol to commit 9a6fa95114806e9d65ff18a77024a8ac3d7ddff0
  Preparing metadata (setup.py) ... done
Collecting usb-construct
  Cloning https://github.com/shrine-maiden-heavy-industries/usb-construct (to revision main) to /tmp/pip-install-esl2f2gm/usb-construct_cd6ae5caac0c465387ae67b89acfafd5
  Running command git clone --filter=blob:none --quiet https://github.com/shrine-maiden-heavy-industries/usb-construct /tmp/pip-install-esl2f2gm/usb-construct_cd6ae5caac0c465387ae67b89acfafd5
  Resolved https://github.com/shrine-maiden-heavy-industries/usb-construct to commit 9a046d9f947e782de102fb3262c051ed5eb5e758
  Preparing metadata (setup.py) ... done
Collecting Jinja2~=3.0
  Using cached jinja2-3.1.5-py3-none-any.whl (134 kB)
Collecting pyvcd>=0.2.2
  Using cached pyvcd-0.4.1-py2.py3-none-any.whl (23 kB)
Collecting rich
  Using cached rich-13.9.4-py3-none-any.whl (242 kB)
Requirement already satisfied: setuptools in ./.env/lib/python3.11/site-packages (from torii->-r ../../requirements.txt (line 1)) (66.1.1)
Collecting typing-extensions
  Using cached typing_extensions-4.12.2-py3-none-any.whl (37 kB)
Collecting pyserial~=3.5
  Using cached pyserial-3.5-py2.py3-none-any.whl (90 kB)
Collecting pyvcd>=0.2.2
  Using cached pyvcd-0.3.0-py2.py3-none-any.whl (23 kB)
Collecting construct
  Using cached construct-2.10.70-py3-none-any.whl (63 kB)
Collecting MarkupSafe>=2.0
  Using cached MarkupSafe-3.0.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (23 kB)
Collecting markdown-it-py>=2.2.0
  Using cached markdown_it_py-3.0.0-py3-none-any.whl (87 kB)
Collecting pygments<3.0.0,>=2.13.0
  Using cached pygments-2.19.1-py3-none-any.whl (1.2 MB)
Collecting mdurl~=0.1
  Using cached mdurl-0.1.2-py3-none-any.whl (10.0 kB)
Building wheels for collected packages: torii, sol-usb, usb-construct
  Building wheel for torii (setup.py) ... done
  Created wheel for torii: filename=torii-0.7.1-py3-none-any.whl size=197953 sha256=63c632cc6a9914c56a1f90429541c8c6310151991c24dbc9cbdca73df094c371
  Stored in directory: /tmp/pip-ephem-wheel-cache-fxe1urst/wheels/ba/a1/49/e35527bc80007f98e1d3b18ba38c3c5fff10858bf072ed5d04
  Building wheel for sol-usb (setup.py) ... done
  Created wheel for sol-usb: filename=sol_usb-0.4.1-py3-none-any.whl size=364559 sha256=76ef02dff8d5a4f17dd835caa590c5ceedd4a468ed8870958c3742c7c3cb97a5
  Stored in directory: /tmp/pip-ephem-wheel-cache-fxe1urst/wheels/07/47/51/72a39aa82d4f966bcd1e07f0eaed502dc7623acd7a9a2e6c3f
  Building wheel for usb-construct (setup.py) ... done
  Created wheel for usb-construct: filename=usb_construct-0.2.2.dev1+g9a046d9-py3-none-any.whl size=68152 sha256=80be4086d26508b375581f74e51a7e361718955aa96ce3a77b55b6957ad8a84e
  Stored in directory: /tmp/pip-ephem-wheel-cache-fxe1urst/wheels/7b/2d/80/971ec1e3366716382c069f792fbdb6d96a4e3cf7dd9bb8df18
Successfully built torii sol-usb usb-construct
Installing collected packages: pyserial, typing-extensions, pyvcd, pygments, mdurl, MarkupSafe, construct, usb-construct, markdown-it-py, Jinja2, rich, torii, sol-usb
Successfully installed Jinja2-3.1.5 MarkupSafe-3.0.2 construct-2.10.70 markdown-it-py-3.0.0 mdurl-0.1.2 pygments-2.19.1 pyserial-3.5 pyvcd-0.3.0 rich-13.9.4 sol-usb-0.4.1 torii-0.7.1 typing-extensions-4.12.2 usb-construct-0.2.2.dev1+g9a046d9
```

This will install all of the Python dependencies needed.

Using dragonBoot
----------------

The gateware builder is run from in the gateware subdirectory of your clone of dragonBoot.
For example, to build the bootloader for the [HeadphoneAmp audio interface](https://github.com/dragonmux/HeadphoneAmp),
it is invoked as follows:

```{code-block} console

$ ./dragonBoot.py build --target audioInterface
[~] (LUNA) SoC framework components could not be imported; some functionality will be unavailable.
[~] (LUNA) No module named 'lambdasoc'
[~] Building for a 512.0kiB Flash with 2 boot slots
[~] Boot slot 0 starts at 0x001000 and finishes at 0x040000
[~] Boot slot 1 starts at 0x040000 and finishes at 0x080000
[~] Serialising 160 bytes of slot data
```

This will generate a build directory where it is invoked containing the following important files:

* `dragonBoot.bin` - this is the upgrade bitstream for the device
* `dragonBoot.multi.bin` - this is the Flash image to be programed to the start of the configuration Flash
  on the device when bringing new hardware up and doing initial programming

To upgrade a device's bootloader, one need only execute the following command (adjusted for the device's primary VID:PID):

```{code-block} console

$ dfu-util -d 1209:badc,:badb -a 0 -D build/dragonBoot.bin
dfu-util 0.11

Copyright 2005-2009 Weston Schmidt, Harald Welte and OpenMoko Inc.
Copyright 2010-2021 Tormod Volden and Stefan Schmidt
This program is Free Software and has ABSOLUTELY NO WARRANTY
Please report bugs to http://sourceforge.net/p/dfu-util/tickets/

dfu-util: Warning: Invalid DFU suffix signature
dfu-util: A valid DFU suffix will be required in a future dfu-util release
Opening DFU capable USB device...
Device ID 1209:badc
Run-Time device DFU version 0110
Claiming USB DFU (Run-Time) Interface...
Setting Alternate Interface zero...
Determining device status...
DFU state(0) = appIDLE, status(0) = No error condition is present
Device really in Run-Time Mode, send DFU detach request...
dfu-util: error detaching
Device will detach and reattach...
Opening DFU USB Device...
Claiming USB DFU Interface...
Setting Alternate Interface #0 ...
Determining device status...
DFU state(2) = dfuIDLE, status(0) = No error condition is present
DFU mode device DFU version 0110
Device returned transfer size 4096
Copying data from PC to DFU device
Download        [=========================] 100%       135100 bytes
Download done.
DFU state(2) = dfuIDLE, status(0) = No error condition is present
Done!
```
