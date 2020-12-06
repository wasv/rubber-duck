import logging

import deepspeech
import numpy as np


class Recognizer:

    _log = logging.getLogger("speech")

    def __init__(self, model_path, scorer_path=None):
        self._log.info("Model: %s", model_path)
        self._model = deepspeech.Model(model_path)
        if scorer_path:
            self._log.info("Scorer: %s", model_path)
            self._model.enableExternalScorer(scorer_path)

        self._context = self._model.createStream()

    def get_results(self):
        text_result = self._context.finishStream()
        self._log.info("Got: %s", text_result)
        self._context = self._model.createStream()
        return text_result

    def process_frame(self, frame):
        self._log.debug("Got new frame")
        self._context.feedAudioContent(np.frombuffer(frame, np.int16))
