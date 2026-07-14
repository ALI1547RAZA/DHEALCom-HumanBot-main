from speaker import Speaker
def main():
    testi = {
        "testo1": "Ciao, come stai?",
        # "testo2": "Oggi è una bella giornata.",
        # "testo3": "Questo è un test di sintesi vocale.",
        # "testo4": "Spero che funzioni correttamente.",
        # "testo5": "La sintesi vocale è molto utile.",
        # "testo6": "Posso parlare"
    }
    speaker = Speaker()
    for titolo, testo in testi.items():
        print(f"Titolo: {titolo}, Testo: {testo}")
        speaker.speak(testo, titolo, save=True)
if __name__ == "__main__":
    main()
