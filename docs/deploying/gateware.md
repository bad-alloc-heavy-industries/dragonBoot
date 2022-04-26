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

The next few steps are considerably easier, and consist of a couple of simple `pip` commands and
running the bootloader builder.

First we preinstall the LUNA framework to resovle a dependency issue:

```{code-block} console

$ pip3 install git+https://github.com/shrine-maiden-heavy-industries/luna@main#egg=luna
Collecting luna
  Cloning https://github.com/shrine-maiden-heavy-industries/luna (to revision main) to /tmp/pip-install-21jaa3jl/luna_d8cb58b30cf84ad5a38f6517eeb86922
  Running command git clone --filter=blob:none --quiet https://github.com/shrine-maiden-heavy-industries/luna /tmp/pip-install-21jaa3jl/luna_d8cb58b30cf84ad5a38f6517eeb86922
  Resolved https://github.com/shrine-maiden-heavy-industries/luna to commit 1d88d4272e763397dcc824659a322782992c9db0
  Running command git submodule update --init --recursive -q
  Preparing metadata (setup.py) ... done
Collecting usb_protocol@ git+https://github.com/shrine-maiden-heavy-industries/python-usb-protocol@main
  Cloning https://github.com/shrine-maiden-heavy-industries/python-usb-protocol (to revision main) to /tmp/pip-install-21jaa3jl/usb-protocol_7c85d4eaaaff4e61beb52a6fa8eed1e2
  Running command git clone --filter=blob:none --quiet https://github.com/shrine-maiden-heavy-industries/python-usb-protocol /tmp/pip-install-21jaa3jl/usb-protocol_7c85d4eaaaff4e61beb52a6fa8eed1e2
  Resolved https://github.com/shrine-maiden-heavy-industries/python-usb-protocol to commit ce0649683ee6a0839a3be8d2776b85fb1ec10dd6
  Preparing metadata (setup.py) ... done
Collecting amaranth@ git+https://github.com/amaranth-lang/amaranth.git@main
  Cloning https://github.com/amaranth-lang/amaranth.git (to revision main) to /tmp/pip-install-21jaa3jl/amaranth_5cd8546b83f64ed4b1dac3c949a3c754
  Running command git clone --filter=blob:none --quiet https://github.com/amaranth-lang/amaranth.git /tmp/pip-install-21jaa3jl/amaranth_5cd8546b83f64ed4b1dac3c949a3c754
  Resolved https://github.com/amaranth-lang/amaranth.git to commit 8b85afa72e09b334b29c28565709cd50d8112d11
  Preparing metadata (setup.py) ... done
Collecting amaranth-boards@ git+https://github.com/amaranth-lang/amaranth-boards.git@main
  Cloning https://github.com/amaranth-lang/amaranth-boards.git (to revision main) to /tmp/pip-install-21jaa3jl/amaranth-boards_9ab0a8652b924697ac0881d0d5224462
  Running command git clone --filter=blob:none --quiet https://github.com/amaranth-lang/amaranth-boards.git /tmp/pip-install-21jaa3jl/amaranth-boards_9ab0a8652b924697ac0881d0d5224462
  Resolved https://github.com/amaranth-lang/amaranth-boards.git to commit 2d0a23b75ebb769874719297dec65ff07ca9e79f
  Preparing metadata (setup.py) ... done
Collecting amaranth-soc@ git+https://github.com/amaranth-lang/amaranth-soc.git@main
  Cloning https://github.com/amaranth-lang/amaranth-soc.git (to revision main) to /tmp/pip-install-21jaa3jl/amaranth-soc_be060f48ee744611ba50b88833e38e56
  Running command git clone --filter=blob:none --quiet https://github.com/amaranth-lang/amaranth-soc.git /tmp/pip-install-21jaa3jl/amaranth-soc_be060f48ee744611ba50b88833e38e56
  Resolved https://github.com/amaranth-lang/amaranth-soc.git to commit 217d4ea76ad3b3bbf146980d168bc7b3b9d95a18
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting amaranth-stdio@ git+https://github.com/amaranth-lang/amaranth-stdio.git@main
  Cloning https://github.com/amaranth-lang/amaranth-stdio.git (to revision main) to /tmp/pip-install-21jaa3jl/amaranth-stdio_f3eff8333bfc499a9ba0832c12a4b11e
  Running command git clone --filter=blob:none --quiet https://github.com/amaranth-lang/amaranth-stdio.git /tmp/pip-install-21jaa3jl/amaranth-stdio_f3eff8333bfc499a9ba0832c12a4b11e
  Resolved https://github.com/amaranth-lang/amaranth-stdio.git to commit ae74f176b6ca32b24ab08325159a19318711a5a9
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pyserial~=3.5
  Using cached pyserial-3.5-py2.py3-none-any.whl (90 kB)
Collecting pyvcd<0.4,>=0.2.2
  Using cached pyvcd-0.3.0-py2.py3-none-any.whl (23 kB)
Collecting Jinja2~=3.0
  Using cached Jinja2-3.1.1-py3-none-any.whl (132 kB)
Collecting construct
  Using cached construct-2.10.68-py3-none-any.whl
Collecting MarkupSafe>=2.0
  Using cached MarkupSafe-2.1.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (25 kB)
Building wheels for collected packages: luna, amaranth, amaranth-boards, amaranth-soc, amaranth-stdio, usb_protocol
  Building wheel for luna (setup.py) ... done
  Created wheel for luna: filename=luna-0.1.0-py3-none-any.whl size=442478 sha256=8c2f90aaf7485d3c2b6b2a7fcc9254c32887628a4a10463f802eca838fe75a14
  Stored in directory: /tmp/pip-ephem-wheel-cache-tjjqkdfm/wheels/9c/54/2e/da68220833cbe4ba2ed7140c021a732401dde6791b31a664f3
  Building wheel for amaranth (setup.py) ... done
  Created wheel for amaranth: filename=amaranth-0.4.dev19+g8b85afa-py3-none-any.whl size=169157 sha256=ceff2d9438e0a515490eabb78f987bc45855a7810455a13f2ba2fb50f7be2724
  Stored in directory: /tmp/pip-ephem-wheel-cache-tjjqkdfm/wheels/a4/89/54/0a9ba686a13223ad1faf99fc73a31441da9fa7ecaea6fd7028
  Building wheel for amaranth-boards (setup.py) ... done
  Created wheel for amaranth-boards: filename=amaranth_boards-0.1.dev208+g2d0a23b-py3-none-any.whl size=110356 sha256=2118ecd4645dd6b07b524d9bfa904056870ca5ed46fc88cb5359634ce4f11f54
  Stored in directory: /tmp/pip-ephem-wheel-cache-tjjqkdfm/wheels/72/99/c0/f370d869eeec5baae2251393f257a7ec8605b28066f4f21fe7
  Building wheel for amaranth-soc (pyproject.toml) ... done
  Created wheel for amaranth-soc: filename=amaranth_soc-0.1.dev49+g217d4ea-py3-none-any.whl size=38202 sha256=61c8ebafef421bf829914e0262782f6dd9e216803fcab823d8c6106cc61141ce
  Stored in directory: /tmp/pip-ephem-wheel-cache-tjjqkdfm/wheels/21/9c/53/1a6ef18f68ac76d54f136cbb72a06cfed374e3d2ee7d4b8167
  Building wheel for amaranth-stdio (pyproject.toml) ... done
  Created wheel for amaranth-stdio: filename=amaranth_stdio-0.1.dev11+gae74f17-py3-none-any.whl size=6697 sha256=a9669acae7d8eb84834eaf68fb4fede07adf7d24bdbcb8ff00da338bd4e7653f
  Stored in directory: /tmp/pip-ephem-wheel-cache-tjjqkdfm/wheels/05/e2/ab/86bf051eb0ebefdedac1af65e25536176562ed531d2981cd86
  Building wheel for usb_protocol (setup.py) ... done
  Created wheel for usb_protocol: filename=usb_protocol-0.0-py3-none-any.whl size=57694 sha256=ff61ee2dba9dabb8e2d0ef0532ca27fd8400a5d160afa6f157b3a284f653d78a
  Stored in directory: /tmp/pip-ephem-wheel-cache-tjjqkdfm/wheels/be/ae/5e/3959cc346afc0a482f59d83cb9630bdabb16fad378dacd8341
Successfully built luna amaranth amaranth-boards amaranth-soc amaranth-stdio usb_protocol
Installing collected packages: pyserial, pyvcd, MarkupSafe, construct, usb_protocol, Jinja2, amaranth, amaranth-stdio, amaranth-soc, amaranth-boards, luna
Successfully installed Jinja2-3.1.1 MarkupSafe-2.1.1 amaranth-0.4.dev19+g8b85afa amaranth-boards-0.1.dev208+g2d0a23b amaranth-soc-0.1.dev49+g217d4ea amaranth-stdio-0.1.dev11+gae74f17 construct-2.10.68 luna-0.1.0 pyserial-3.5 pyvcd-0.3.0 usb_protocol-0.0
```

Then we install the rest of the requirements:

```{code-block} console

$ pip3 install -r requirements-ci.txt
Collecting amaranth
  Cloning https://github.com/amaranth-lang/amaranth.git (to revision main) to /tmp/pip-install-qk963uua/amaranth_fc7092b8b38d4eed93ff74f26847c9ca
  Running command git clone --filter=blob:none --quiet https://github.com/amaranth-lang/amaranth.git /tmp/pip-install-qk963uua/amaranth_fc7092b8b38d4eed93ff74f26847c9ca
  Resolved https://github.com/amaranth-lang/amaranth.git to commit 8b85afa72e09b334b29c28565709cd50d8112d11
  Preparing metadata (setup.py) ... done
Collecting amaranth-soc
  Cloning https://github.com/amaranth-lang/amaranth-soc (to revision main) to /tmp/pip-install-qk963uua/amaranth-soc_832c57e5eee64c96affa5d2f2a556817
  Running command git clone --filter=blob:none --quiet https://github.com/amaranth-lang/amaranth-soc /tmp/pip-install-qk963uua/amaranth-soc_832c57e5eee64c96affa5d2f2a556817
  Resolved https://github.com/amaranth-lang/amaranth-soc to commit 217d4ea76ad3b3bbf146980d168bc7b3b9d95a18
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting amaranth-boards
  Cloning https://github.com/dragonmux/amaranth-boards (to revision main) to /tmp/pip-install-qk963uua/amaranth-boards_644c2f7558a043989a7dcce7d5aa821f
  Running command git clone --filter=blob:none --quiet https://github.com/dragonmux/amaranth-boards /tmp/pip-install-qk963uua/amaranth-boards_644c2f7558a043989a7dcce7d5aa821f
  Resolved https://github.com/dragonmux/amaranth-boards to commit c2f5fd37f954a213ef176ba247addb8d6c966f9d
  Preparing metadata (setup.py) ... done
Collecting arachne
  Cloning https://github.com/shrine-maiden-heavy-industries/arachne (to revision main) to /tmp/pip-install-qk963uua/arachne_104c527196d2447fb94b96fcda2324f1
  Running command git clone --filter=blob:none --quiet https://github.com/shrine-maiden-heavy-industries/arachne /tmp/pip-install-qk963uua/arachne_104c527196d2447fb94b96fcda2324f1
  Resolved https://github.com/shrine-maiden-heavy-industries/arachne to commit 28a109e5263fd92a18efea3cec20ea1829c7baf1
  Preparing metadata (setup.py) ... done
Collecting usb-protocol
  Cloning https://github.com/shrine-maiden-heavy-industries/python-usb-protocol (to revision main) to /tmp/pip-install-qk963uua/usb-protocol_35a396f403f9431aaa48963803a3a511
  Running command git clone --filter=blob:none --quiet https://github.com/shrine-maiden-heavy-industries/python-usb-protocol /tmp/pip-install-qk963uua/usb-protocol_35a396f403f9431aaa48963803a3a511
  Resolved https://github.com/shrine-maiden-heavy-industries/python-usb-protocol to commit ce0649683ee6a0839a3be8d2776b85fb1ec10dd6
  Preparing metadata (setup.py) ... done
Requirement already satisfied: pyvcd<0.4,>=0.2.2 in /tmp/env/lib/python3.10/site-packages (from amaranth->-r requirements-ci.txt (line 1)) (0.3.0)
Requirement already satisfied: Jinja2~=3.0 in /tmp/env/lib/python3.10/site-packages (from amaranth->-r requirements-ci.txt (line 1)) (3.1.1)
Requirement already satisfied: construct in /tmp/env/lib/python3.10/site-packages (from usb-protocol->-r requirements-ci.txt (line 5)) (2.10.68)
Requirement already satisfied: MarkupSafe>=2.0 in /tmp/env/lib/python3.10/site-packages (from Jinja2~=3.0->amaranth->-r requirements-ci.txt (line 1)) (2.1.1)
Building wheels for collected packages: amaranth-boards, arachne
  Building wheel for amaranth-boards (setup.py) ... done
  Created wheel for amaranth-boards: filename=amaranth_boards-0.1.dev209+gc2f5fd3-py3-none-any.whl size=110462 sha256=57f476ac1359a9d8ddbc9e2ef1a69b0d788336923ab4872a69a5081dd3e5be30
  Stored in directory: /tmp/pip-ephem-wheel-cache-ytg_6dcc/wheels/19/46/3e/9dec9c575f28bfb6d38bdb4562f3448ec2155a7f7b65e0fdec
  Building wheel for arachne (setup.py) ... done
  Created wheel for arachne: filename=arachne-0.1.dev172+g28a109e-py3-none-any.whl size=103519 sha256=362be3dc234ef55609499c1b44dc5161fa604f74508d8abeb5615aa95b76cad6
  Stored in directory: /tmp/pip-ephem-wheel-cache-ytg_6dcc/wheels/1c/a3/4a/cbfa63d4de4a4895929567ff869e65498ab98433ca29d54e17
Successfully built amaranth-boards arachne
Installing collected packages: arachne, amaranth-boards
  Attempting uninstall: amaranth-boards
    Found existing installation: amaranth-boards 0.1.dev208+g2d0a23b
    Uninstalling amaranth-boards-0.1.dev208+g2d0a23b:
      Successfully uninstalled amaranth-boards-0.1.dev208+g2d0a23b
Successfully installed amaranth-boards-0.1.dev209+gc2f5fd3 arachne-0.1.dev172+g28a109e
```

This will install all Python dependencies needed.

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
