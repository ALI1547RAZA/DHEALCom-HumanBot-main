from pydoc import text
from bottle import request, response, route, run, hook, template, static_file, default_app
import io
import tempfile
from vui.s2t.audio_transcriber import AudioTranscriber
from bpml import motore

# import vui.s2t.remote.audio_transcriber as transcriber
from vui.parser.agent_factory import create_agent
import vui.parser.parser as parser
import json
import os

# import utils
from dotenv import load_dotenv

CONFIG_PATH = "app_config.json"
DEFAULT_CONFIG = {
    "paziente": "John Doe",
    "data": "21 ottobre 2025",
    "indice_prompt": 0,
    "porta": 8086
}
def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                return {**DEFAULT_CONFIG, **config_data}  # merge con default
        except Exception as e:
            print(f"Errore nel caricamento del file di configurazione: {e}")
    return DEFAULT_CONFIG

config = load_config()
paziente = config["paziente"]
data = config["data"]
indice_prompt = config["indice_prompt"]
porta = config["porta"]

prompt_data = [
    {
        "scenario": "crea_dt",
        "prompt": f"Crea il twin di {paziente} per la data {data}",
    },
    {
        "scenario": "simula_terapia",
        "prompt": f"Simula per {paziente} per il giorno {data} la terapia base",
    },
    {
        "scenario": "simula_terapia_errore",
        "prompt": f"Simula per {paziente} per il giorno {data} la terapia con 200gr di carboidrati",
    },
    {
        "scenario": "analizza_terapia_errore",
        "prompt": f"Analizza per {paziente} per il giorno {data} la terapia con 200gr di carboidrati",
    },
    {
        "scenario": "simula_terapia_alternativa",
        "prompt": f"Simula per {paziente} per il giorno {data} la terapia con 200gr di carboidrati in più a cena",
    },
    {
        "scenario": "analizza_terapia_alternativa",
        "prompt": f"Analizza per {paziente} per il giorno {data} la terapia con 200gr di carboidrati in più a cena",
    },
    {
        "scenario": "confronta_terapie",
        "prompt": f"Confronta per {paziente} per il giorno {data} la terapia con 200gr di carboidrati in più a cena con la terapia base",
    },
    {
        "scenario": "analizza_terapia_con_prompt_alternativo",
        "prompt": f"Vorrei sapere cosa succede a {paziente} per il giorno {data} se mangia 200gr di carboidrati in meno a cena",
    },
    {
        "scenario": "analizza_terapia_con_prompt_alternativo_2",
        "prompt": f"Analizza cosa succede a {paziente} per il giorno {data} se mangia 200gr di carboidrati in meno a cena",
    },
]

agent = create_agent("default")
medicalAgent = create_agent("medical")
textTransformerAgent = create_agent("text_transformer")
agentPOD = create_agent("pod_manager")


@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

@route("/")
def index():
    return template("index.tpl")

# @route('/to_result_0', method=['POST'])
# def get_0():
#     response.content_type = 'application/json'
#     return {
#         "stato": 0,
#         "messaggio": "Risultato 0 per l'attività",
#         "risultato": False
#     }
    

@route("/esegui_processo", method=["POST"])
def esegui_processo():
    print("[POST] /esegui_processo")

    utente = request.forms.get("utente")  # 'medico' o 'paziente'
    audio_file = request.files.get("audio")
    peso = request.forms.get("peso")

    if not audio_file or not utente:
        return {
            "stato": 0,
            "messaggio": "Audio o tipo utente mancante",
            "risultato": False,
        }

    # Converti audio in BytesIO
    audio_bytes = io.BytesIO(audio_file.file.read())

    # Determina quale file BPML usare
    nome_file_xml = f"{utente.lower()}.xml"
    percorso_file_xml = os.path.join(
        "bpml", nome_file_xml
    )  # cartella dove metti i tuoi .xml

    if not os.path.exists(percorso_file_xml):
        return {
            "stato": 0,
            "messaggio": f"File BPML non trovato: {nome_file_xml}",
            "risultato": False,
        }

    # Costruisci il context iniziale
    context = {"audioBlob": audio_bytes, "peso": peso}

    # Esegui il processo
    risultato = motore.run_bpml_process(percorso_file_xml, context)

    return risultato


@route("/get_prompt", method=["POST"])
def get_prompt():
    response.content_type = "application/json"
    #Decommentare per testare con prompt predefiniti
    # transcribed_text = prompt_data[indice_prompt]["prompt"]
    # print(f"Transcribed text: {transcribed_text}")
    # return {
    #     "stato": 1,
    #     "messaggio": "Conversione in testo effettuata.",
    #     "risultato": transcribed_text,
    # }
    
    audio_file = request.files.get(
        "audioBlob"
    )  # <-- questa è la chiave usata in formData.append()
    if audio_file:
        audio_file_bytes = io.BytesIO(audio_file.file.read())
        print("quaa")
        with tempfile.NamedTemporaryFile(suffix=".ogg") as temp_file:
            temp_file.write(audio_file_bytes.getbuffer())
            temp_file.flush()
            print("quiii")
            transcriber = AudioTranscriber()
            print("qui")
            print(temp_file.name)
            transcribed_text = transcriber.transcribe_text_only(temp_file.name)
            print("qui")
            print(transcribed_text)
            risultato = {
                "stato": 1,
                "messaggio": "Conversione in testo effettuata.",
                "risultato": transcribed_text,
            }
    else:
        risultato = {
            "stato": 0,
            "messaggio": "Errore, riprova ad inviare il prompt.",
            "risultato": False,
        }
    print(f"route /get_prompt: {risultato}")
    return risultato


@route("/to_json", method=["POST"])
def to_json():
    response.content_type = "application/json"
    # prompt = request.params.get('promptText')
    print("Sono in /to_json")
    prompt = request.json.get("promptText")
    print(f"Prendo in input: {prompt}")
    if not prompt:
        risultato = {
            "stato": 0,
            "messaggio": "Nessun prompt passato in input",
            "risultato": False,
        }
    else:
        #agent_response = agent.ask(prompt)
        agent_response = agentPOD.ask(prompt)
        risultato = {
            "stato": 1,
            "messaggio": "Risposta dell'agent ottenuta.",
            "risultato": agent_response,
        }
    print(f"Risultato di to_json: {risultato}")
    return risultato


@route("/parse_output", method=["POST"])
def parse_output():
    """Parse the intent JSON coming from the LLM and route to the BPML parser.

    Accepts either:
    - a JSON *string* in request.json["intentJson"] (possibly with a leading "<s>"), or
    - a JSON *object* (dict) already parsed.

    This makes the endpoint robust to how the agent returns data (string vs dict)
    and avoids NoneType errors when the field is missing.
    """
    response.content_type = "application/json"

    body = request.json or {}
    raw_intent = body.get("intentJson")

    if raw_intent is None:
        risultato = {
            "stato": 0,
            "messaggio": "Nessun output passato in input (intentJson mancante)",
            "risultato": False,
        }
        return risultato

    # Normalize to a Python dict
    if isinstance(raw_intent, str):
        output = raw_intent.replace("<s>", "").strip()
        if not output:
            risultato = {
                "stato": 0,
                "messaggio": "intentJson vuoto dopo la pulizia",
                "risultato": False,
            }
            return risultato
        try:
            parsedOutput = json.loads(output)
        except Exception as e:
            risultato = {
                "stato": 0,
                "messaggio": f"intentJson non è un JSON valido: {e}",
                "risultato": False,
            }
            return risultato
    elif isinstance(raw_intent, dict):
        parsedOutput = raw_intent
        output = json.dumps(parsedOutput, ensure_ascii=False)
    else:
        risultato = {
            "stato": 0,
            "messaggio": f"Tipo di intentJson non supportato: {type(raw_intent)}",
            "risultato": False,
        }
        return risultato

    print(f"Input raw: {output}")

    # parsedOutput now *must* be a dict
    parsed_output = parser.parse_output(parsedOutput)
    print(f"parsed output 1: {parsed_output}")
    print(type(parsedOutput))

    if not parsed_output:
        risultato = {
            "stato": 0,
            "messaggio": "Errore durante il parsing dell'output",
            "risultato": False,
        }
        return risultato

    if parsed_output.get("state") == "error":
        risultato = {
            "stato": 0,
            "messaggio": parsed_output.get("messaggio", "Errore generico"),
            "risultato": False,
        }
        return risultato

    print(f"parsed_output 2: {parsed_output}")

    # If we are in an analysis/comparison intent, call the medical agent
    if parsedOutput.get("intent") is not None and parsedOutput.get("intent") in ["analizza", "confronta"]:
        med_answer = medicalAgent.ask(parsed_output)
        if not med_answer:
            risultato = {
                "stato": 0,
                "messaggio": "Errore durante la chiamata all'agent medico",
                "risultato": False,
            }
        else:
            risultato = {
                "stato": 1,
                "messaggio": "Output parsato correttamente.",
                "risultato": med_answer,
            }
    else:
        risultato = {
            "stato": 1,
            "messaggio": "Output parsato correttamente.",
            "risultato": parsed_output,
        }

    # print(f"Risultato: {risultato}")
    return risultato


@route("/transform_text", method=["POST"])
def transform_text():
    response.content_type = "application/json"
    parsed_result = request.json.get("parsedResult")
    if not parsed_result:
        risultato = {
            "stato": 0,
            "messaggio": "Nessun testo parsato passato in input",
            "risultato": False,
        }
    else:
        # Esegui la trasformazione del testo
        if (parsed_result.get('intent') == "inserimento"):
            # Only in case of insert, answer with succesful insert.
            transformed_text = "Inserimento di " + str(parsed_result.get('glucosio')) + " milligrammi effettuato con successo"
            risultato = {
                "stato": 1,
                "messaggio": "Testo trasformato correttamente.",
                "risultato": transformed_text,
            }
        else:
            transformed_text = textTransformerAgent.ask(parsed_result)
        if not transformed_text:
            risultato = {
                "stato": 0,
                "messaggio": "Errore durante la trasformazione del testo",
                "risultato": False,
            }
        else:
            risultato = {
                "stato": 1,
                "messaggio": "Testo trasformato correttamente.",
                "risultato": transformed_text,
            }
    # print(f"Risultato: {risultato}")
    return risultato


@route("/to_speech", method=["POST"])
def to_speech():
    """Text-to-speech helper.

    Accepts:
    - JSON body with one of:
      - { "parsedResult": {...} }
      - { "transformedText": "..." }
      - { "text": "..." }
    - Or form / query parameter:
      - text=<plain text>

    Always returns JSON with base64 MP3 in `risultato` so it can be played
    on any page (including the measurement page).
    """
    from gtts import gTTS
    from io import BytesIO
    import base64

    response.content_type = "application/json"

    # Safely read JSON body, if present
    body = None
    try:
        body = request.json
    except Exception:
        body = None

    data = None
    if isinstance(body, dict):
        if body.get("parsedResult") is not None:
            print("Using parsedResult for TTS")
            data = body.get("parsedResult")
        elif body.get("transformedText") is not None:
            print("Using transformedText for TTS")
            data = body.get("transformedText")
        elif body.get("text") is not None:
            print("Using raw text for TTS")
            data = body.get("text")

    # Fallback: support classic form/query parameter `text`
    if data is None:
        text_param = request.forms.get("text") or request.params.get("text")
        if text_param:
            print("Using form/query text for TTS")
            data = text_param

    print("data: ", data)

    # Normalize to plain text
    if isinstance(data, dict):
        stato = data.get("stato", 1)
        if stato == 0:
            # In caso di errore, leggi il messaggio
            text = data.get("messaggio") or str(data.get("risultato"))
        else:
            # In caso di successo, leggi il risultato
            text = data.get("risultato") or data.get("messaggio")
    elif isinstance(data, str):
        text = data  # già testo diretto
    else:
        text = None

    if not text:
        risultato = {
            "stato": 0,
            "messaggio": "Nessun testo fornito.",
            "risultato": False,
        }
    else:
        try:
            tts = gTTS(text=text, lang="it", tld="it")
            mp3_fp = BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)

            audio_base64 = base64.b64encode(mp3_fp.read()).decode("utf-8")

            risultato = {
                "stato": 1,
                "messaggio": "Audio generato con successo.",
                "risultato": audio_base64,
            }

        except Exception as e:
            risultato = {
                "stato": 0,
                "messaggio": f"Errore durante la conversione: {str(e)}",
                "risultato": False,
            }
    # print(f"Risultato: {risultato}")
    return risultato

@route("/static/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root="static")


def start():
    try:
        run(host="localhost", port=porta, server="paste", reloader=True)
    except OSError as e:
        print(f"Errore durante l'avvio del server sulla porta {porta}: {e}")
        run(host="localhost", port=porta + 1, server="paste", reloader=True)

if __name__ == "__main__":
    start()

app = default_app()
