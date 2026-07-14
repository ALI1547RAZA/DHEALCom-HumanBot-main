import os
import json
from faster_whisper import WhisperModel
import logging

class AudioTranscriber:
    def __init__(self, config_path=None, model_size="turbo", device="cpu", compute_type="int8"):
        """
        Inizializza il modello WhisperModel.
        Se viene passato un file di configurazione JSON, prende i parametri da lì.
        Altrimenti usa i valori di default o quelli passati esplicitamente.
        """
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                model_size = config.get("model_size", model_size)
                device = config.get("device", device)
                compute_type = config.get("compute_type", compute_type)
        logging.basicConfig()
        logging.getLogger("faster_whisper").setLevel(logging.DEBUG)
        self.model = WhisperModel("medium", device="cpu", compute_type="int8")
        print("hereeea")

    def transcribe_detailed(self, audio_path, beam_size=1):
        """
        Ritorna la trascrizione completa con timestamp e testo.
        Utile per leggere con riferimento temporale.
        """
        segments, _ = self.model.transcribe(audio_path, beam_size=beam_size)
        return "\n".join("[%.2fs -> %.2fs] %s" % (s.start, s.end, s.text) for s in segments)

    def transcribe_text_only(self, audio_path, beam_size=1):
        """
        Ritorna solo il testo continuo, senza timestamp.
        Utile per elaborazione con LLM o analisi del contenuto.
        """
        segments, _ = self.model.transcribe(audio_path, beam_size=beam_size)
        return " ".join(s.text.strip() for s in segments)

    def detect_language(self, audio_path, beam_size=1):
        """
        Ritorna la lingua rilevata e la sua probabilità sotto forma di tupla.
        """
        _, info = self.model.transcribe(audio_path, beam_size=beam_size)
        return info.language, info.language_probability

    def to_json(self, audio_path, beam_size=1):
        """
        Ritorna un oggetto JSON con:
        - lingua
        - probabilità della lingua
        - lista di segmenti (inizio, fine, testo)
        """
        segments, info = self.model.transcribe(audio_path, beam_size=beam_size)
        data = {
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": [
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                }
                for segment in segments
            ]
        }
        return data
