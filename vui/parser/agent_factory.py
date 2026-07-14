import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
from dotenv import load_dotenv
from agent import Agent, MedicalAgent , TextTransformerAgent

def load_config():
    try:
        with open(os.path.join("vui", "parser", "config.json"), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        with open(os.path.join("parser", "config.json"), encoding="utf-8") as f:
            return json.load(f)

def get_api_key():
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")


def create_agent(agent_type="default"):
    config = load_config()
    api_key = ""  # No API key needed for Ollama
    # Prefer explicit "model" key, fall back to legacy "modello", then default in Agent classes
    model = config.get("model")
    if agent_type == "default":
        return Agent(api_key=api_key, prompt=config["prompt1"], model=model)
    elif agent_type == "medical":
        return MedicalAgent(api_key=api_key, prompt=config["prompt2"], model=model)
    elif agent_type == "text_transformer":
        return TextTransformerAgent(api_key=api_key, prompt=config.get("prompt3"), model=model)
    elif agent_type == "pod_manager":
        return TextTransformerAgent(api_key=api_key, prompt=config.get("prompt4"), model=model)
    else:
        raise ValueError(f"Tipo di agente non valido: {agent_type}")
