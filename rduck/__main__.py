import argparse
import os
from datetime import datetime

from halo import Halo

from .audio import VADAudio
from .speech import Recognizer

DEFAULT_SAMPLE_RATE = 16000

parser = argparse.ArgumentParser(
    description="Stream from microphone to DeepSpeech using VAD")

parser.add_argument('-v', '--vad_aggressiveness', type=int, default=3,
                    help="Set aggressiveness of VAD: an integer between 0 " +
                    "and 3, 0 being the least aggressive about filtering out " +
                    "non-speech, 3 the most aggressive. Default: 3")
parser.add_argument('-p', '--vad_padding', type=int, default=0.75,
                    help="Set padding ratio for VAD: an float between 0.0 " +
                    "and 1.0, 0.0 being the least padding, 1.0 being the most. Default: 0.75")
parser.add_argument('--nospinner', action='store_true',
                    help="Disable spinner")
parser.add_argument('-w', '--savewav',
                    help="Save .wav files of utterences to given directory")
parser.add_argument('-f', '--file',
                    help="Read from .wav file instead of microphone")

parser.add_argument('-m', '--model', required=True,
                    help="Path to the model (protocol buffer binary file, " +
                    "or entire directory containing all standard-named files for model)")
parser.add_argument('-s', '--scorer',
                    help="Path to the external scorer file.")
parser.add_argument('-d', '--device', type=int, default=None,
                    help="Device input index (Int) as listed by " +
                    "pyaudio.PyAudio.get_device_info_by_index(). " +
                    "If not provided, falls back to PyAudio.get_default_device().")
parser.add_argument('-r', '--rate', type=int, default=DEFAULT_SAMPLE_RATE,
                    help=f"Input device sample rate. Default: {DEFAULT_SAMPLE_RATE}." +
                    " Your device may require 44100.")

ARGS = parser.parse_args()
if ARGS.savewav:
    os.makedirs(ARGS.savewav, exist_ok=True)

# Load DeepSpeech model
if os.path.isdir(ARGS.model):
    model_dir = ARGS.model
    ARGS.model = os.path.join(model_dir, 'output_graph.pb')
    ARGS.scorer = os.path.join(model_dir, ARGS.scorer)

print('Initializing model...')
recognizer = Recognizer(ARGS.model, ARGS.scorer)

# Start audio with VAD
vad_audio = VADAudio(aggressiveness=ARGS.vad_aggressiveness,
                     device=ARGS.device,
                     input_rate=ARGS.rate,
                     file=ARGS.file)
print("Listening (ctrl-C to exit)...")
frames = vad_audio.vad_collector(ratio=ARGS.vad_padding)

# Stream from microphone to DeepSpeech using VAD
spinner = None
if not ARGS.nospinner:
    spinner = Halo(spinner='line')
wav_data = bytearray()

for frame in frames:
    if frame is not None:
        if spinner:
            spinner.start()
        recognizer.process_frame(frame)

        if ARGS.savewav:
            wav_data.extend(frame)
    else:
        if spinner:
            spinner.stop()

        if ARGS.savewav:
            filename = datetime.now().strftime("rec_%Y-%m-%d_%H-%M-%S_%f.wav")
            vad_audio.write_wav(os.path.join(ARGS.savewav, filename), wav_data)
            wav_data = bytearray()

        text = recognizer.get_results()
        print("Recognized: %s" % text)
