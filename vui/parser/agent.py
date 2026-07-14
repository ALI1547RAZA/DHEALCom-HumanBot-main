import json
import re
import ollama


class Agent:
    """Generic agent that expects a JSON response from Ollama.

    Uses the Ollama client withnfigurable model.
    """

    def __init__(self, api_key, prompt=None, model=None):
        # Ollama client (api_key not needed for local Ollama)
        self.ollama_client = ollama.Client(
            host="http://172.16.16.206:11434"
        )
        # Default to a general-purpose model if none is provided
        self.model = model or "mistral"
        self.system_prompt = prompt or ""

    def extract_json(self, text):
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                print("Nessun oggetto JSON trovato nella risposta.")
                return None
            print(f"Extracted JSON string: {match.group()}")
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None

    def ask(self, user_text):
        """Call Ollama and return a parsed JSON object.

        The prompt is built as: system_prompt + user_text, and we expect the
        model to answer *only* with a JSON object, as described in prompt1.
        """
        try:
            full_prompt = f"{self.system_prompt}\n\nTesto:\n\"{user_text}\""
            response = self.ollama_client.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False,
            )
            result_text = response["response"]
            print(f"Raw response from agent: {result_text}")
            parsed = self.extract_json(result_text)
            if parsed is None:
                return {
                    "error": "Risposta non è un JSON valido",
                    "raw_response": result_text,
                }
            return parsed

        except Exception as e:
            return {"error": f"Errore durante la chiamata API: {e}"}


class MedicalAgent(Agent):
    """Agent specialized for medical explanations using Ollama.

    It returns plain TEXT (not JSON) that describes simulation results.
    """

    def __init__(self, api_key, prompt=None, model=None):
        super().__init__(api_key, prompt, model=model or "mistral")
        if not prompt:
            prompt = "Sei un medico che legge i risultati di una simulazione per il diabete di tipo 1.\n\nRiceverai uno o più oggetti JSON, ciascuno con i campi:\n- titolo\n- mean_glucose\n- std_deviation\n- tir\n- time_in_hypoglycemia\n- time_in_hyperglycemia\n\nISTRUZIONI:\n- NON scrivere commenti clinici, né frasi introduttive.\n- NON scrivere \"accettabile\", \"troppo alto\", \"suggerisce\", \"potrebbe\", ecc.\n- Usa SOLO il linguaggio oggettivo.\n- Se ricevi UN SOLO oggetto, scrivi:\n    \"La glicemia media è ... mg/dL. La deviazione standard è ... mg/dL. Il TIR è del ...%. Il tempo in ipoglicemia è ...%. Il tempo in iperglicemia è ...%.\"\n- Se ricevi DUE oggetti, scrivi SOLO i confronti di TUTTI i valori (glicemia media, deviazione standard, TIR, tempo in ipoglicemia, tempo in iperglicemia), mettendo in evidenza i valori numerici specifici. NON riportare prima l'analisi individuale di ogni simulazione.\n  Formato del confronto: \n  \"La glicemia media è 171.82 mg/dL con insulina basale aumentata di 10% contro 60.87 mg/dL con carboidrati aumentati di 200g a cena.\n  La deviazione standard è 35.51 mg/dL con insulina basale aumentata di 10% contro 128.37 mg/dL con carboidrati aumentati di 200g a cena.\n  Il TIR è del 62.12% con insulina basale aumentata di 10% contro 46.36% con carboidrati aumentati di 200g a cena.\n  Il tempo in ipoglicemia è 0.00% con insulina basale aumentata di 10% contro 43.79% con carboidrati aumentati di 200g a cena.\n  Il tempo in iperglicemia è 37.88% con insulina basale aumentata di 10% contro 9.85% con carboidrati aumentati di 200g a cena.\"\n\nNaturalizza il titolo secondo le seguenti regole:\n- _basal-inc-10% → insulina basale aumentata di 10%\n- _bolus-dec-2U → insulina prandiale ridotta di 2U\n- _cho-inc-200g-D → carboidrati aumentati di 200g a cena\n\nSigle pasti:\n- B = colazione\n- L = pranzo\n- D = cena\n- H = come trattamento dell'ipoglicemia\n- S = come spuntino\n\nRispondi solo in italiano."
        self.system_prompt = prompt
    def ask(self, simulation_objects):
        prompt = self._build_prompt(simulation_objects)

        try:
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            response = self.ollama_client.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False,
            )
            return response["response"].strip()
        except Exception as e:
            print(f"Errore MedicalAgent: {e}")
            return None
    def _build_prompt(self, objects):
        # Aggiunge i dati come JSON formattati
        return f"Ecco i dati delle simulazioni:\n{json.dumps(objects, indent=2)}"
# class MedicalAgent:
#     def __init__(self, api_key,prompt=None):
#         self.client = OpenAI(
#             base_url="https://openrouter.ai/api/v1",
#             api_key=api_key
#         )
#         self.model = "mistralai/mistral-7b-instruct:free"
#         if not prompt:
#             prompt = "Sei un medico che legge i risultati di una simulazione per il diabete di tipo 1.\n\nRiceverai uno o più oggetti JSON, ciascuno con i campi:\n- titolo\n- mean_glucose\n- std_deviation\n- tir\n- time_in_hypoglycemia\n- time_in_hyperglycemia\n\nISTRUZIONI:\n- NON scrivere commenti clinici, né frasi introduttive.\n- NON scrivere \"accettabile\", \"troppo alto\", \"suggerisce\", \"potrebbe\", ecc.\n- Usa SOLO il linguaggio oggettivo.\n- Se ricevi UN SOLO oggetto, scrivi:\n    \"La glicemia media è ... mg/dL. La deviazione standard è ... mg/dL. Il TIR è del ...%. Il tempo in ipoglicemia è ...%. Il tempo in iperglicemia è ...%.\"\n- Se ricevi DUE oggetti, scrivi SOLO i confronti di TUTTI i valori (glicemia media, deviazione standard, TIR, tempo in ipoglicemia, tempo in iperglicemia), mettendo in evidenza i valori numerici specifici. NON riportare prima l'analisi individuale di ogni simulazione.\n  Formato del confronto: \n  \"La glicemia media è 171.82 mg/dL con insulina basale aumentata di 10% contro 60.87 mg/dL con carboidrati aumentati di 200g a cena.\n  La deviazione standard è 35.51 mg/dL con insulina basale aumentata di 10% contro 128.37 mg/dL con carboidrati aumentati di 200g a cena.\n  Il TIR è del 62.12% con insulina basale aumentata di 10% contro 46.36% con carboidrati aumentati di 200g a cena.\n  Il tempo in ipoglicemia è 0.00% con insulina basale aumentata di 10% contro 43.79% con carboidrati aumentati di 200g a cena.\n  Il tempo in iperglicemia è 37.88% con insulina basale aumentata di 10% contro 9.85% con carboidrati aumentati di 200g a cena.\"\n\nNaturalizza il titolo secondo le seguenti regole:\n- _basal-inc-10% → insulina basale aumentata di 10%\n- _bolus-dec-2U → insulina prandiale ridotta di 2U\n- _cho-inc-200g-D → carboidrati aumentati di 200g a cena\n\nSigle pasti:\n- B = colazione\n- L = pranzo\n- D = cena\n- H = come trattamento dell'ipoglicemia\n- S = come spuntino\n\nRispondi solo in italiano."
#         self.system_prompt = prompt

#     def ask(self, simulation_objects):
#         prompt = self._build_prompt(simulation_objects)

#         try:
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": self.system_prompt},
#                     {"role": "user", "content": prompt},
#                 ],
#                 temperature=0.0,
#             )
#             return response.choices[0].message.content.strip()
#         except Exception as e:
#             return None

#     def _build_prompt(self, objects):
#         # Aggiunge i dati come JSON formattati
#         return f"Ecco i dati delle simulazioni:\n{json.dumps(objects, indent=2)}"

class TextTransformerAgent:
    """Agent that turns structured simulation data into patient‑friendly text.

    Uses Ollama to generate plain text (not JSON).
    """

    def __init__(self, api_key, prompt=None, model=None):
        self.ollama_client = ollama.Client(
            host="http://172.16.16.206:11434"
        )
        self.model = model or "mistral"
        self.system_prompt = prompt or ""

    def ask(self, simulation_objects):
        prompt = self._build_prompt(simulation_objects)

        try:
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            response = self.ollama_client.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False,
            )
            text = response["response"].strip()
            print("Risposta TextTransformerAgent:")
            print(text)
            return text
        except Exception as e:
            print("Errore TextTransformerAgent:", e)
            return None
    def _build_prompt(self, objects):
        # Aggiunge i dati come JSON formattati
        return f"Ecco i dati delle simulazioni:\n{json.dumps(objects, indent=2)}"