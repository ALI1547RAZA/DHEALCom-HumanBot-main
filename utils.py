import pandas as pd
import os
import io
from py_replay_bg.py_replay_bg import ReplayBG

SAVE_FOLDER = os.path.abspath("..")


def replay(dati_paziente, dati_ottimizzazione_modello, save_name, suffix_name, save_folder=None):
    if not save_folder:
        save_folder = SAVE_FOLDER
    try:
        # Inizializza oggetto ReplayBG
        rbg = ReplayBG(
            save_folder=save_folder,
            blueprint="multi-meal",
            yts=5,
            exercise=False,
            seed=1,
            plot_mode=False,
            verbose=False,
        )

        # Estrai parametri paziente
        patient_row = dati_paziente[dati_paziente["patient"] == 1].iloc[0]
        bw = float(patient_row["bw"])  # Body weight

        # Esegui replay e restituisci l'output
        return rbg.replay(
            data=dati_ottimizzazione_modello,
            bw=bw,
            save_name=save_name,
            twinning_method="map",
            save_workspace=True,
            save_suffix=suffix_name,
        )

    except Exception as e:
        #print(f"[ERRORE] Replay fallito per {save_name}: {e}")
        return False # oppure False, a seconda di cosa ti aspetti a valle



def twin(dati_paziente, dati_ottimizzazione_modello, save_name, save_folder=None):
    if not save_folder:
        save_folder = SAVE_FOLDER

    try:
        # Inizializza oggetto ReplayBG
        rbg = ReplayBG(
            save_folder,
            blueprint="multi-meal",
            yts=5,
            exercise=False,
            seed=1,
            plot_mode=False,
            verbose=True,
        )

        # Estrai parametri paziente
        patient_row = dati_paziente[dati_paziente["patient"] == 1].iloc[0]
        bw = float(patient_row["bw"])     # Body weight
        u2ss = float(patient_row["u2ss"]) # Steady-state insulin

        # Generazione del twin
        rbg.twin(
            dati_ottimizzazione_modello,
            bw=bw,
            save_name=save_name,
            twinning_method="map",
            parallelize=True,
            u2ss=u2ss,
        )
        return True

    except Exception as e:
        print(f"[ERRORE] Twin fallito per {save_name}: {e}")
        return False



def load_patient_info(file):
    df = pd.read_csv(file)
    return df


def load_test_data(file):
    df = pd.read_csv(file)
    df.t = pd.to_datetime(df["t"])
    return df


def show_data(data):
    for row in data.itertuples(index=True):
        print(
            f"i: {row.Index}, t: {row.t}, bolus: {row.bolus}, meal: {row.meal}, basal: {row.basal}, exercise: {row.exercise}, bg: {row.bg}"
        )

#Funziona che mostra solo i primi 5 record del DataFrame
def show_data_head(data, n=5):
    if isinstance(data, pd.DataFrame):
        print(data.head(n))
    else:
        print("Il dato fornito non è un DataFrame di pandas.")

def verifica_terapia(terapia: dict) -> bool:
    """
    Controlla se una terapia è valida secondo il formato richiesto dal prompt.
    """
    if not isinstance(terapia, dict):
        return False

    required_fields = ["quantita", "unita", "operazione", "parametro", "text"]
    
    # Tutti i campi base devono essere presenti e non nulli
    for field in required_fields:
        if field not in terapia or terapia[field] is None:
            print(f"[VALIDAZIONE] Campo mancante o nullo: '{field}'")
            return False

    parametro = terapia["parametro"]

    # Se il parametro è 'cho', 'pasto' deve essere presente e non nullo
    if parametro == "cho":
        if "pasto" not in terapia or terapia["pasto"] is None:
            print("[VALIDAZIONE] 'pasto' obbligatorio per parametro 'cho'")
            return False

    return True

def applica_terapia(df: pd.DataFrame, terapia: dict) -> pd.DataFrame:
    
    if not verifica_terapia(terapia):
        raise ValueError(f"[ERRORE] Terapia non valida o incompleta: {terapia}")
    
    valore = float(terapia["quantita"])
    unita = terapia.get("unita", "g")
    operazione = terapia["operazione"]
    parametro = terapia["parametro"]
    pasto = terapia.get("pasto")  # viene dal dizionario, non dal DataFrame

    if parametro not in df.columns:
        raise ValueError(f"[ERRORE] Colonna '{parametro}' non trovata nel DataFrame")

    # Caso specifico per 'cho'
    if parametro == "cho":
        if not pasto:
            raise ValueError("[ERRORE] Campo 'pasto' mancante o nullo nella terapia per parametro 'cho'")

        if "cho_label" not in df.columns:
            raise ValueError("[ERRORE] Colonna 'cho_label' non presente nel DataFrame")

        # Maschera: cho_label uguale al pasto fornito
        maschera = df["cho_label"] == pasto
        if not maschera.any():
            raise ValueError(f"[ERRORE] Nessuna riga con cho_label = '{pasto}'")

        sottoinsieme = df.loc[maschera, parametro].astype(float)
        delta = (valore / 100.0) * sottoinsieme if unita == "%" else valore

        if operazione == "inc":
            df.loc[maschera, parametro] = sottoinsieme - delta
            print(f"[TERAPIA] ↓ {valore}{unita} su '{parametro}' per pasto '{pasto}'")
        else:
            df.loc[maschera, parametro] = sottoinsieme + delta
            print(f"[TERAPIA] ↑ {valore}{unita} su '{parametro}' per pasto '{pasto}'")

        return df

    # Caso generico per altri parametri
    serie = df[parametro].astype(float)
    delta = (valore / 100.0) * serie if unita == "%" else valore

    if operazione == "inc":
        df[parametro] = serie - delta
        print(f"[TERAPIA] ↓ {valore}{unita} su '{parametro}'")
    else:
        df[parametro] = serie + delta
        print(f"[TERAPIA] ↑ {valore}{unita} su '{parametro}'")

    return df

def stampa_analisi(analysis, titolo):
    json_results = {
        "titolo": titolo,
        "mean_glucose": f"{analysis['median']['glucose']['variability']['mean_glucose']}",
        "std_deviation": f"{analysis['median']['glucose']['variability']['std_glucose']}",
        "tir": f"{analysis['median']['glucose']['time_in_ranges']['time_in_target']}",
        "time_in_hypoglycemia": f"{analysis['median']['glucose']['time_in_ranges']['time_in_hypoglycemia']}",
        "time_in_hyperglycemia": f"{analysis['median']['glucose']['time_in_ranges']['time_in_hyperglycemia']}"
    }
    return json_results

def formatta_analisi_testo(analisi):
    return (
        f"Terapia: {analisi['titolo']}\n"
        f"  - Glicemia media: {analisi['mean_glucose']}\n"
        f"  - Deviazione standard: {analisi['std_deviation']}\n"
        f"  - Tempo in range (TIR): {analisi['tir']}\n"
        f"  - Tempo in ipoglicemia: {analisi['time_in_hypoglycemia']}\n"
        f"  - Tempo in iperglicemia: {analisi['time_in_hyperglycemia']}"
    )



def formatta_data(data_str):
    from datetime import datetime
    # Converti la stringa in un oggetto datetime
    data = datetime.strptime(data_str, "%Y-%m-%d")
    # Dizionario dei nomi dei mesi in italiano
    mesi = [
        "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"
    ]
    # Costruisci la stringa "giorno mese"
    return f"{data.day} {mesi[data.month - 1]}"

