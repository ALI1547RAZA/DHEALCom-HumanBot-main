import xml.etree.ElementTree as ET
import requests
import json
from io import BytesIO

NAMESPACE = {"bpml": "http://www.bpmi.org/2002/03/bpml"}
BASE_URL = "http://localhost:8086"

# # Mappatura partner/operation → path REST
# SERVICE_MAP = {
#     ("SpeechService", "getPrompt"): "/get_prompt",
#     ("JsonService", "toJson"): "/to_json",
#     ("ParserService", "parseOutput"): "/parse_output",
#     ("SpeechService", "toSpeech"): "/to_speech",
# }
# Mappatura partner/operation → path REST
SERVICE_MAP = {
    ("SpeechService", "getPrompt"): "/get_prompt",
    ("JsonService", "toJson"): "/to_json",
    ("ParserService", "parseOutput"): "/parse_output",
    ("SpeechService", "toSpeech"): "/to_speech",
    ("TransformService", "transformText"): "/transform_text",
}


def run_bpml_process(bpml_file_path, initial_context):
    tree = ET.parse(bpml_file_path)
    root = tree.getroot()

    contesto = initial_context.copy()
    contesto["errore"] = None
    ultimo_messaggio = "Processo completato con successo."
    print("Prima di ogni attività, il contesto è il seguente: ", contesto)
    # Stampa tutto l'xml dal root a scendere
    # for child in root.iter():
    # print(f"[Motore] Trovato elemento: {child.tag} con attributi {child.attrib}")
    # Trova la sequenza principale
    sequenza_tag = root.find(".//bpml:sequence", NAMESPACE)
    if sequenza_tag is None:
        risultato = {
            "stato": 0,
            "messaggio": "Sequenza principale non trovata nel processo.",
            "risultato": False,
        }
        ultimo_messaggio = risultato["messaggio"]
    else:
        # Cerca le attività
        attivita_tag = [act for act in sequenza_tag]
        # attivita = [act for act in sequenza.findall(".//bpml:activity", NAMESPACE) if act.attrib.get("name") != "fallbackToSpeech"]
        for act in attivita_tag:
            nome_attivita = act.attrib.get("name")
            print(f"[Motore] Avvio attività: {nome_attivita}")

            childs = [child for child in act]
            input_attivita_tag = [c for c in childs if c.tag.endswith("input")]
            invoke_tag = [c for c in childs if c.tag.endswith("invoke")]
            assegna_tag = [c for c in childs if c.tag.endswith("assign")]

            if not input_attivita_tag:
                risultato = {
                    "stato": 0,
                    "messaggio": f"Nessun input trovato per l'attività {nome_attivita}.",
                    "risultato": False,
                }
            else:
                print(
                    f"[Motore] Input per {nome_attivita}: {[inp.attrib.get('property') for inp in input_attivita_tag]}"
                )
                payload = {}
                # Prepara il payload con gli input
                for input_attivita in input_attivita_tag:
                    print(
                        f"[Motore] Aggiungo {input_attivita.attrib.get('property')} = {contesto[input_attivita.attrib.get('property')]} al payload di {nome_attivita}"
                    )
                    payload[input_attivita.attrib.get("property")] = contesto[
                        input_attivita.attrib.get("property")
                    ]
                if not invoke_tag:
                    risultato = {
                        "stato": 0,
                        "messaggio": f"Nessun invoke trovato per l'attività {nome_attivita}.",
                        "risultato": False,
                    }
                else:
                    for invoke in invoke_tag:
                        # partner e operation servono unicamente a prendere il path corrispondente
                        partner = invoke.attrib.get("partner")
                        operation = invoke.attrib.get("operation")
                        print(f"Partner {partner}, operation: {operation}", partner, operation);
                        path = SERVICE_MAP.get((partner, operation))
                        print(
                            f"[Motore] Invoke per {nome_attivita}: path = {path} con payload {payload}"
                        )

                        url = BASE_URL + path
                        metodo = "POST"
                        # Special case per file audio
                        if nome_attivita == "toText":
                            files = {"audioBlob": contesto["audioBlob"]}
                            risposta = requests.post(url, files=files)
                        else:
                            risposta = requests.request(
                                metodo, url, json=payload)
                        risposta.raise_for_status()
                        dati = risposta.json()
                        print("dati ricevuti:", dati)
                        if dati.get("stato") == 0:
                            contesto["errore"] = dati.get("messaggio")
                            payload = {}
                            # Prendi catchAll
                            catch_all_tag = act.find(
                                ".//bpml:catchAll", NAMESPACE)
                            assign_tag = catch_all_tag.find(
                                ".//bpml:assign", NAMESPACE)
                            prop = assign_tag.attrib.get("property")
                            exp = assign_tag.attrib.get("expression")
                            if exp == "errore" and prop:
                                contesto[prop] = contesto.get(
                                    "errore", "Errore generico")
                            activity_tag = catch_all_tag.find(
                                ".//bpml:activity", NAMESPACE)
                            activity_input = activity_tag.find(
                                ".//bpml:input", NAMESPACE)
                            input_property = activity_input.attrib.get(
                                "property")
                            payload[input_property] = contesto.get(
                                input_property)
                            invoke_tag = activity_tag.find(
                                ".//bpml:invoke", NAMESPACE)
                            partner = invoke_tag.attrib.get("partner")
                            operation = invoke_tag.attrib.get("operation")
                            path = SERVICE_MAP.get((partner, operation))
                            url = BASE_URL + path
                            fallback_response = requests.request(
                                "POST", url, json=payload)
                            fallback_response.raise_for_status()
                            fallback_response_json = fallback_response.json()
                            assign_tag = activity_tag.find(
                                ".//bpml:assign", NAMESPACE)
                            prop = assign_tag.attrib.get("property")
                            exp = assign_tag.attrib.get("expression")
                            if exp == "response.result" and prop:
                                contesto[prop] = fallback_response_json.get(
                                    "risultato")
                            return {
                                "stato": 0,
                                "messaggio": contesto.get("errore"),
                                "risultato": contesto.get("outputAudio", False),
                            }
                        # Processa <assign> per salvare output nel contesto
                        for assegna in assegna_tag:
                            var = assegna.attrib.get("property")
                            expr = assegna.attrib.get("expression")
                            # Per semplicità: supportiamo solo "response.result"
                            if expr == "response.result" and var:
                                contesto[var] = dati.get("risultato")
                                print(
                                    f"[Motore] Assegnato {var} = {dati.get('risultato')}"
                                )
                        print("Contesto dopo l'attività: ", contesto)
    return {
        "stato": 1,
        "messaggio": "Processo completato con successo.",
        "risultato": contesto.get("outputAudio", True),
        "context": contesto.get("parsedResult", {})
    }
