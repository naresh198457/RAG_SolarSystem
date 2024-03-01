import speech_recognition as sr
import numpy as np
from RAG_Model import rag_response
import pyttsx3

speaker = pyttsx3.init()
speaker.setProperty("rate",150)
                
voices = speaker.getProperty('voices')     
speaker.setProperty('voice', voices[0].id) 


def run_assistant():
    while True:
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic, duration=1)
                print('listening')
                audio=recognizer.listen(mic)
                #text=recognizer.recognize_google(audio,language = 'en-IN', show_all = True)
                text=recognizer.recognize_google(audio)
                #text=text['alternative'][0]['transcript'].lower()
                text=text.lower()
                print(text)
                # ['hi nash', 'hi naash', 'hi nice','hey nice', 'hey naas','hey nash', 'highness','nash','nice','naash','nass','nas', 'play nash']
                if text in ['hi mishi', 'hi messi', 'hi missy','hey mishi', 'hey missy','hey nash', 'highness','mishi','messy','missy','nass','nas', 'play nash']:
                    print('How can i help you')
                    speaker.say("How can i help you")
                    speaker.runAndWait()
                    audio=recognizer.listen(mic)
                    text=recognizer.recognize_google(audio)
                    text=text.lower()
                    print(text)

                    if text=='stop':
                        speaker.say("Bye")
                        speaker.runAndWait()
                        speaker.stop()
                        break
                    else:
                        if text is not None:
                            response, metaData,ref=rag_response(text)
                            print(response)
                            print(ref)
                            speaker.say(response)
                            speaker.runAndWait()
        except sr.UnknownValueError:
            pass  # Ignore unrecognized speech
        except sr.RequestError:
            Er_response = "Sorry, something went wrong with the speech recognition service."
            speaker.say(Er_response)

if __name__=='__main__':
    run_assistant()