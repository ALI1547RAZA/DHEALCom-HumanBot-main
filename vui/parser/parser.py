import os
import csv
import sys

# Calcola il path assoluto della root del progetto (due livelli sopra questo file)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import utils

SAVE_FOLDER = os.path.abspath(".")


def crea_paziente(result_json):
    paziente = result_json.get("paziente")
    peso = result_json.get("peso")
    u2ss = result_json.get("u2ss")
    print(f"[CREA PAZIENTE] Nome: {paziente.split('_')[0]} {paziente.split('_')[1]}, Peso: {peso}kg, U2SS: {u2ss}")
    #     # Crea cartella se non esiste
    #     base_dir = "../patient_data"
    #     os.makedirs(base_dir, exist_ok=True)
    #     # Normalizza il nome: minuscolo, spazi sostituiti con underscore
    #     nome_file = paziente.strip().lower().replace(" ", "_") + ".csv"
    #     csv_path = os.path.join(base_dir, nome_file)
    #     if os.path.exists(csv_path):
    #         print(f"[CSV ESISTE] Il file {csv_path} esiste già, non verrà sovrascritto.")
    #         return
    #     # Scrive il CSV con le colonne richieste
    #     with open(csv_path, mode="w", newline="") as csvfile:
    #         writer = csv.DictWriter(csvfile, fieldnames=["patient", "u2ss", "bw"])
    #         writer.writeheader()
    #         writer.writerow({
    #             "patient": 1,
    #             "u2ss": u2ss,
    #             "bw": peso
    #         })
    #     print(f"[CSV CREATO] File salvato in: {csv_path}")

def crea_dt(result_json):
    paziente = result_json.get("paziente")
    data = result_json.get("data")
    if not paziente:
        return {"state": "error", "error": "Campo 'paziente' mancante nel JSON.", "messaggio": "Errore! Non hai indicato il paziente."}
    if not data:
        return {"state": "error", "error": "Campo 'data' mancante nel JSON.", "messaggio": "Errore! Non hai indicato la data."}
    #Log
    print(f"[CREA DIGITAL TWIN] Paziente: {paziente.split('_')[0]} {paziente.split('_')[1]}, Data: {utils.formatta_data(data)}")

    # Carica informazioni del paziente
    patient_info_path = f"patient_data/{paziente}.csv"
    try:
        patient_info = utils.load_patient_info(patient_info_path)
    except FileNotFoundError:
        print(f"[ERRORE] Paziente {paziente.split('_')[0]} {paziente.split('_')[1]} non trovato ({patient_info_path}).")
        return {"state": "error", "error": f"Paziente {paziente.split('_')[0]} {paziente.split('_')[1]} non trovato.", "messaggio": f"Errore! Il paziente {paziente.split('_')[0]} {paziente.split('_')[1]} non esiste. Crea prima il paziente o prova con qualcun altro."}

    # Carica dati giornalieri
    day_data_path = f"patient_data/{paziente}_{data}.csv"
    try:
        day_data = utils.load_test_data(day_data_path)
    except FileNotFoundError:
        print(f"[ERRORE] Dati per il giorno {utils.formatta_data(data)} non trovati ({day_data_path}).")
        return {"state": "error", "error": f"Dati per il giorno {utils.formatta_data(data)} non trovati.", "messaggio": f"Errore! I dati per il giorno {utils.formatta_data(data)} non esistono. Carica prima i dati o prova con un altro giorno."}
   

    save_name = f"{paziente}_{data}"
    map_file_name = f"map_{save_name}.pkl"
    file_path = os.path.join(SAVE_FOLDER, "results", "map", map_file_name)

    if os.path.exists(file_path):
        print(f"[ERRORE] Il twin per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)} esiste già: {file_path}")
        return {"state": "error", "error": f"Il twin per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)} esiste già.", "messaggio": f"Errore! Il twin per il paziente {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)} esiste già."}
    
    print(f"[OK] Creazione del twin in corso...")
    # il messaggio da dare al t2s
    # print(f"Creazione del twin per {paziente} per il giorno {data} in corso")
    twin_results = utils.twin(patient_info, day_data, save_name, SAVE_FOLDER)
    if not twin_results:
        print(f"[ERRORE] Creazione del twin fallita per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)}.")
        return {"state": "error", "error": f"Creazione del twin fallita per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)}.", "messaggio": f"Errore! Creazione del twin fallita per il paziente {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)}."}
    print(f"[OK] Twin creato e salvato in {file_path}")
    return {
        "state": "success",
        "error": None,
        "messaggio": f"Twin creato con successo.",
    }

def simula_dt(result_json):
    paziente = result_json.get("paziente")
    terapia = result_json.get("terapia")
    data = result_json.get("data")
    print(f"[SIMULA DT] Paziente: {paziente.split('_')[0]} {paziente.split('_')[1]}, Terapia: {terapia}, Data: {utils.formatta_data(data)}")
    # Controlla se il paziente è specificato
    if not paziente:
        print("[ERRORE] Campo 'paziente' mancante nel JSON.")
        return {"state": "error", "error": "Campo 'paziente' mancante nel JSON.", "messaggio": "Errore! Non hai indicato il paziente."}
    if not data:
        print("[ERRORE] Campo 'data' mancante nel JSON.")
        return {"state": "error", "error": "Campo 'data' mancante nel JSON.", "messaggio": "Errore! Non hai indicato la data."}
    # Carica informazioni del paziente
    patient_info_path = f"patient_data/{paziente}.csv"
    try:
        patient_info = utils.load_patient_info(patient_info_path)
    except FileNotFoundError:
        print(f"[ERRORE] Paziente {paziente.split('_')[0]} {paziente.split('_')[1]} non trovato ({patient_info_path}).")
        return {"state": "error", "error": f"Paziente {paziente.split('_')[0]} {paziente.split('_')[1]} non trovato.", "messaggio": f"Errore! Il paziente {paziente.split('_')[0]} {paziente.split('_')[1]} non esiste. Crea prima il paziente o prova con qualcun altro."}

    # Carica dati giornalieri
    day_data_path = f"patient_data/{paziente}_{data}.csv"
    try:
        day_data = utils.load_test_data(day_data_path)
    except FileNotFoundError:
        print(f"[ERRORE] Dati per il giorno {utils.formatta_data(data)} non trovati ({day_data_path}).")
        return {"state": "error", "error": f"Dati per il giorno {utils.formatta_data(data)} non trovati.", "messaggio": f"Errore! I dati per il giorno {utils.formatta_data(data)} non esistono. Carica prima i dati o prova con un altro giorno."}
    
    #Esiste il dt del paziente?
    save_name = f"{paziente}_{data}"
    map_file_name = f"map_{save_name}.pkl"
    file_path = os.path.join(SAVE_FOLDER, "results", "map", map_file_name)

    if not os.path.exists(file_path):
        print(f"[ERRORE] Il twin per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)} non esiste: {file_path}")
        return {"state": "error", "error": f"Il twin per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)} non esiste.", "messaggio": f"Errore! Il twin per il paziente {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)} non esiste. Crea prima il twin o prova con un altro giorno."}
    print(f"[OK] Twin trovato: {file_path}")
    
    #Se la terapia è false o null, non applicare alcuna terapia
    if not terapia or terapia == "base" or terapia == "nessuna":
        print("[INFO] Terapia base o nessuna. Nessuna modifica applicata.")
        suffix_name = ""
    else:
        print(f"[OK] Terapia trovata: {terapia}")
        if not utils.verifica_terapia(terapia):
            print(f"[ERRORE] Terapia non valida: {terapia}")
            return {"state": "error", "error": f"Terapia non valida: {terapia}", "messaggio": f"Errore! La terapia fornita non è valida."}
        try:
            day_data = utils.applica_terapia(day_data, terapia)
        except Exception as e:
            print(f"[ERRORE] Applicazione della terapia fallita: {e}")
            return {"state": "error", "error": f"Applicazione della terapia fallita: {e}", "messaggio": f"Errore! Applicazione della terapia fallita."}
        suffix_name = f"{terapia['text']}" 

    replay_results = utils.replay(patient_info, day_data, save_name, suffix_name, SAVE_FOLDER)
    if not replay_results:
       print(f"[ERRORE] Replay fallito per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)}.")
       return {"state": "error", "error": f"Replay fallito per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)}.", "messaggio": f"Errore! Simulazione fallita per il paziente {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)}."}
    #Log
    print(f"[OK] Replay della terapia completato per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)}.")
    return {
        "state": "success",
        "error": None,
        "messaggio": f"Simulazione della terapia completata per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)}.",
    }

def analizza(result_json):
    from py_replay_bg.analyzer import Analyzer
    import pickle
    print(f"[ANALIZZA] Intent: {result_json.get('intent')}")
    paziente = result_json.get("paziente")
    data = result_json.get("data")
    terapia = result_json.get("terapia")
    print(terapia)
    # Controlla se il paziente è specificato
    if not paziente:
        print("[ERRORE] Campo 'paziente' mancante nel JSON.")
        return {"state": "error", "error": "Campo 'paziente' mancante nel JSON.", "messaggio": "Errore! Non hai indicato il paziente."}
    if not data:
        print("[ERRORE] Campo 'data' mancante nel JSON.")
        return {"state": "error", "error": "Campo 'data' mancante nel JSON.", "messaggio": "Errore! Non hai indicato la data."}
    if terapia:
        if not utils.verifica_terapia(terapia):
            print(f"[ERRORE] Terapia non valida: {terapia}")
            return {"state": "error", "error": f"Terapia non valida: {terapia}", "messaggio": f"Errore! La terapia fornita non è valida."}   
        text = terapia.get("text")
        filename = f"{paziente}_{data}{text}"
    else:
        filename = f"{paziente}_{data}"
        text = "base"
    filepath = os.path.join(SAVE_FOLDER, 'results', 'workspaces', f'{filename}.pkl')
    
    if not os.path.exists(filepath):
        print(f"[ERRORE] Simulazione {filename}.pkl non esistente")
        return {"state": "error", "error": f"Simulazione {filename}.pkl non esistente", "messaggio": f"Errore! Devi prima simulare la terapia."}
    
    with open(filepath, 'rb') as file:
        replay_results = pickle.load(file)
    analysis = Analyzer.analyze_replay_results(replay_results)
    print(f"[ANALISI] Completata per  per {paziente.split('_')[0]} {paziente.split('_')[1]} per il giorno {utils.formatta_data(data)} con terapia {text}.")
    return utils.stampa_analisi(analysis,text)

def confronta(result_json):
    print(f"[CONFRONTA] Intent: {result_json.get('intent')}")

    paziente = result_json.get("paziente")
    if not paziente:
        print("[ERRORE] Campo 'paziente' mancante nel JSON.")
        return {"state": "error", "error": "Campo 'paziente' mancante nel JSON.", "messaggio": "Errore! Non hai indicato il paziente."}
    data = result_json.get("data")
    if not data:
        print("[ERRORE] Campo 'data' mancante nel JSON.")
        return {"state": "error", "error": "Campo 'data' mancante nel JSON.", "messaggio": "Errore! Non hai indicato la data."}
    
    terapie = result_json.get("terapia")  # Lista di 2 terapie

    if not isinstance(terapie, list) or len(terapie) < 2:
        print(f"[ERRORE] Devi fornire almeno due terapie nel campo 'terapia'. Ricevuto: {terapie}")
        return {"state":"error","error":"Devi fornire almeno due terapie nel campo 'terapia","messaggio":"Le terapia devono essere almeno due per essere confrontate"}

    risultati = []

    for terapia in terapie:
        if not terapia:
            nome_terapia = "Base"
        else:
            nome_terapia = terapia["text"]
            if not utils.verifica_terapia(terapia):
                print(f"[ERRORE] Terapia non valida: {terapia}")
                return {"state": "error", "error": f"Terapia non valida: {terapia}", "messaggio": f"Errore! La terapia fornita non è valida."}   

        input_singolo = {
            "intent": "analizza",
            "paziente": paziente,
            "data": data,
            "terapia": terapia
        }

        # print(f"Input singolo: {input_singolo}")
        risultato = analizza(input_singolo)
        if risultato["state"]:
            if risultato["state"] in ["error"]:
                return risultato
        testo = utils.formatta_analisi_testo(risultato)
        # print(testo)
        risultati.append(testo)
    print(risultati)
    return "\n\n".join(risultati)


def inserimento(result_json):
    print(f"[INSERIMENTO] Operazione in corso")
    return result_json

def cancellazione(result_json):
    print(f"[CANCELLAZIONE] Operazione in corso")
    return result_json


def parse_output(result_json):
    intent = result_json.get("intent")
    print(f"Intent: {intent}")
    if intent == "crea_utente":
        return crea_paziente(result_json)
    elif intent == "crea_dt":
        return crea_dt(result_json)
    elif intent == "simula_dt":
        return simula_dt(result_json)
    elif intent == "analizza":
        return analizza(result_json)
    elif intent == "confronta":
        return confronta(result_json)
    elif intent == "inserimento":
        return inserimento(result_json)
    elif intent == "cancellazione":
        return cancellazione(result_json)
    else:
        #Log
        print(f"[ERRORE] Intent sconosciuto: {intent}")
        return {"state": "error", "error": f"Intent sconosciuto", "messaggio": f"Errore! Azione sconosciuta."}   

