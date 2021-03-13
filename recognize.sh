#!/bin/sh
python -m rduck.cli -m models/deepspeech.pbmm -s models/deepspeech.scorer -w audio $@
