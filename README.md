README.md

This project is an exploration of creating MIDI sounds with Python and pygame.


## Directory layout

(Copied/adapted from https://build-system.fman.io/manual/)

- src/                  Root directory for your source files
    - venv              Python virtual environment for developing/running application
    - build/            Files for the build process
        - (various scripts)
        - settings/     Build settings
            - base.json
            - (mac.json)
            - (...etc)
    - main/             Application code
        - icons/
        - python/       Python source code
        - resources/    Data files, images etc.
        - (...etc)
    - (freeze/)         Files for freezing your app
    - (installer/)      Installer source files
        - (mac/)
        - ...etc)
- (requirements/)       Application Python dependencies
    - (base.txt)        All platforms
    - (linux.txt)       All Linux distributions
    - (...etc)


## Setup notes (tested on my MacBook)

<!--
- installed xcode (can skip this?)

- installed command line tools (`xcode-select --install`)
-->

- install python-3.11 (from .pkg file at https://www.python.org/ftp/python/3.11.4/python-3.11.4-macos11.pkg).  Installs to `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11`.

Then:

    $(which python3.11) -m venv venv
    . venv/bin/activate

    pip install --upgrade pip
    pip install --upgrade certifi
    pip install pygame
<!--
    pip install numpy
    pip install opencv-python
-->


## References

https://github.com/pygame/pygame/blob/1a5fa4bb8d0220b3d657bd423981ef199dad8e40/examples/midi.py#L25 - starting point for experiments.

