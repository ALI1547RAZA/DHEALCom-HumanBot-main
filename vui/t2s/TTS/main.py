import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False).to(device)
# tts.tts_to_file("Errore! Il twin per il paziente mario rossi  per il giorno 2025-05-06 esiste già..", speaker_wav="clone.wav", language="it", file_path="output.wav")
tts = TTS("tts_models/it/mai_male/vits")
tts.tts_with_vc_to_file(
    "Errore! Il twin per il paziente mario rossi  per il giorno 2025-05-06 esiste già..",
    speaker_wav="clone.wav",
    file_path="output.wav"
)