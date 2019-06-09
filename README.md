# funfile
A toy project to demonstrate knowledge of:
* Object Oriented Programming
* Concurrency
* DSP

with the use of basic python libraries.

Funfile will scan the lib directory of a linux system.

It will use the file size of each file as the value of a hypothetical input signal.

This signal is then processed (only DCT at the moment) and plotted in the CLI.
    
Important constants (to be exposed as CLI parameters in the future):
* TotalBars: Horizontal size of CLI graph.
* MaxPix: Vertical size of CLI graph.
* MaxVal: Maximum file-size for graphs, in bytes. Fixed to 100MB
* RefreshRate: Number of plots per second.
* WorkDir: Directory where to scan from.

## Running
```sh
python3 funfile.py
```

## Requirements
Requires Python 3 (at least 3.6). Tested on Linux only (Ubuntu 18.04).
