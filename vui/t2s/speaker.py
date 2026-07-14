import pyttsx3
class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
    def speak(self, text, title=None, save=None):
        if save:
            title = f'{title}.wav' or 'output.wav'
            self.engine.save_to_file(text, title)
        self.engine.say(text)
        self.engine.runAndWait()
