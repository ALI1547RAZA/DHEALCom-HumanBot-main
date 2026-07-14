def transcribe(filename):
    import requests
    import os
    url = "https://7af2-34-53-8-25.ngrok-free.app/transcribe"
    audio_path = os.path.join("audio", filename)

    with open(audio_path, "rb") as f:
        # Specifica il tipo MIME corretto (es. audio/wav)
        files = {"audio": (filename, f, "audio/ogg")}
        response = requests.post(url, files=files)

    try:
        # print(filename, "=>", response.json())
        return response.json()["text"]
    except Exception as e:
        print(filename, "=> Errore nella risposta:", response.text, e)