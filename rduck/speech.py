import logging

import deepspeech
import numpy as np


class Recognizer:
    def __init__(self, model_path, scorer_path=None):
        logging.info("Model: %s", model_path)
        self._model = deepspeech.Model(model_path)
        if scorer_path:
            logging.info("Scorer: %s", model_path)
            self._model.enableExternalScorer(scorer_path)

        self._context = self._model.createStream()

    def get_results(self):
        text_result = self._context.finishStream()
        logging.info("Got: %s", text_result)
        self._context = self._model.createStream()
        return text_result

    def process_frame(self, frame):
        logging.debug("Got new frame")
        self._context.feedAudioContent(np.frombuffer(frame, np.int16))
