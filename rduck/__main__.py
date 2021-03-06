import argparse
import os
import logging
from datetime import datetime

from .audio import Audio, VADetector
from .speech import Recognizer

parser = argparse.ArgumentParser(
    description="Stream from microphone to DeepSpeech using VAD"
)

parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Logging level, use -v for info, -vv for debug.",
)
parser.add_argument(
    "-a",
    "--vad_aggressiveness",
    type=int,
    default=3,
    help=(
        "Set aggressiveness of VAD: an integer between 0 "
        " and 3, 0 being the least aggressive about filtering out "
        "non-speech, 3 the most aggressive. Default: 3"
    )
)
parser.add_argument(
    "-p",
    "--vad_padding",
    type=int,
    default=300,
    help="Set padding time for VAD: an int in ms. Default: 300",
)
parser.add_argument("--nospinner", action="store_true", help="Disable spinner")
parser.add_argument(
    "-w", "--savewav", help="Save .wav files of utterences to given directory"
)
parser.add_argument(
    "-m",
    "--model",
    required=True,
    help=(
        "Path to the model (protocol buffer binary file, "
        "or entire directory containing all standard-named files for model)"
    )
)
parser.add_argument("-s", "--scorer", help="Path to the external scorer file.")
parser.add_argument(
    "-d",
    "--device",
    type=int,
    default=None,
    help=(
        "Device input index (Int) as listed by "
        "pyaudio.PyAudio.get_device_info_by_index(). "
        "If not provided, falls back to PyAudio.get_default_device().",
    )
)
parser.add_argument(
    "-r",
    "--rate",
    type=int,
    default=16000,
    help="Input device sample rate. Default: 16000.",
)

ARGS = parser.parse_args()

if ARGS.verbose == 1:
    logging.basicConfig(level=logging.INFO)
elif ARGS.verbose == 2:
    logging.basicConfig(level=logging.DEBUG)

if ARGS.savewav:
    os.makedirs(ARGS.savewav, exist_ok=True)

# Load DeepSpeech model
if os.path.isdir(ARGS.model):
    model_dir = ARGS.model
    ARGS.model = os.path.join(model_dir, "output_graph.pb")
    ARGS.scorer = os.path.join(model_dir, ARGS.scorer)

print("Initializing model...")
recognizer = Recognizer(ARGS.model, ARGS.scorer)

# Start audio with VAD
source = Audio(
    device=ARGS.device,
    input_rate=ARGS.rate
)
vad = VADetector(
    source,
    aggressiveness=ARGS.vad_aggressiveness,
)
print("Listening (ctrl-C to exit)...")
frames = vad.vad_collector(padding_ms=ARGS.vad_padding)

# Stream from microphone to DeepSpeech using VAD
spinner = None
wav_data = bytearray()

for frame in frames:
    if frame is not None:
        recognizer.process_frame(frame)

        if ARGS.savewav:
            wav_data.extend(frame)
    else:

        if ARGS.savewav:
            filename = datetime.now().strftime("rec_%Y-%m-%d_%H-%M-%S_%f.wav")
            source.write_wav(os.path.join(ARGS.savewav, filename), wav_data)
            wav_data = bytearray()

        text = recognizer.get_results()
        print("Recognized: %s" % text)
