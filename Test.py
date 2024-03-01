import speech_recognition as sr  # Importing the SpeechRecognition library
import numpy as np  # Importing numpy for numerical operations
from RAG_Model import rag_response  # Importing a custom model for generating responses
import pyttsx3  # Importing the text-to-speech library

# Initializing the text-to-speech engine
speaker = pyttsx3.init()
speaker.setProperty("rate", 150)  # Setting the speech rate

# Setting the preferred voice for the text-to-speech engine
voices = speaker.getProperty('voices')     
speaker.setProperty('voice', voices[0].id)

# Function to run the assistant
def run_assistant():
    while True:
        recognizer = sr.Recognizer()  # Initializing the speech recognizer
        try:
            with sr.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic, duration=1)  # Adjusting for ambient noise
                print('listening')
                audio = recognizer.listen(mic)  # Listening to the microphone input
                text = recognizer.recognize_google(audio)  # Recognizing speech using Google Speech Recognition
                text = text.lower()  # Converting the recognized text to lowercase
                print(text)

                # Checking if the recognized text matches any of the predefined wake-up phrases
                if text in ['hi mishi', 'hi messi', 'hi missy', 'hey mishi', 'hey missy', 'hey nash', 'highness', 'mishi', 'messy', 'missy', 'nass', 'nas', 'play nash']:
                    print('How can I help you?')
                    speaker.say("How can I help you?")  # Speaking out a prompt
                    speaker.runAndWait()
                    audio = recognizer.listen(mic)  # Listening to the microphone input again
                    text = recognizer.recognize_google(audio)  # Recognizing speech using Google Speech Recognition
                    text = text.lower()  # Converting the recognized text to lowercase
                    print(text)

                    # Checking if the user wants to stop the assistant
                    if text == 'stop':
                        speaker.say("Bye")  # Speaking out a farewell message
                        speaker.runAndWait()
                        speaker.stop()
                        break
                    else:
                        if text is not None:
                            response, metaData, ref = rag_response(text)  # Generating a response using a custom model
                            speaker.say(response)  # Speaking out the response
                            speaker.runAndWait()

        except sr.UnknownValueError:
            pass  # Ignoring unrecognized speech
        except sr.RequestError:
            Er_response = "Sorry, something went wrong with the speech recognition service."
            speaker.say(Er_response)  # Speaking out an error message if the speech recognition service encounters an error

if __name__ == '__main__':
    run_assistant()  # Running the assistant function
