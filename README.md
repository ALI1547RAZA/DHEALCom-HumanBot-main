# DHEALCom-HumanBot

Questo progetto è il completamento del progetto di DHEALCom-WebApp e serve per aggiungere le funzionalità di SpeechToText e TextToSpeech alla WebApp, sia relativamente alla aggiunta dei dati, sia alla cancellazione dei dati.

Requisito Phython `3.11`

---

## 🚀 Istruzioni per l’installazione

### Clonare la repository

```bash
git clone <link-della-repo>
cd <nome-cartella-repo>
```

---

### Creare l’ambiente Anaconda

Assicurati di avere **Anaconda** o **Miniconda** installato sul tuo sistema.  
Poi crea l’ambiente usando il file `requirements.yml`:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements_new.txt
```

---

### Creare un account su OpenRouter

1. Vai su 👉 [https://openrouter.ai](https://openrouter.ai)
2. Crea un account gratuito
3. Genera una **chiave API personale**

---

### Creare il file `.env`

Nella directory principale del progetto, crea un file chiamato `.env` e inserisci:

```sh
OPENAI_API_KEY="chiave_api_generata"
```

---

### Scegliere un modello gratuito su OpenRouter

- Vai su [https://openrouter.ai/models](https://openrouter.ai/models)
- Scrivi **"free"** nella barra di ricerca
- Copia il nome del modello gratuito
- Inseriscilo nel modulo di configurazione `parser/config.json`

---

### Avviare la webapp

```bash
python app.py
```

Il server partirà sulla porta specificata nel `config.json` (es. `http://localhost:8086`), e potrà essere interrogato dall'applicazione client DHEALCom-WebApp
