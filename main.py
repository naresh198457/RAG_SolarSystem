# Importing necessary modules and libraries
from flask import Flask, render_template, url_for, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import speech_recognition as sr
from RAG_Model import rag_response 
import pyttsx3  

# Setting up the text-to-speech engine ---------------------------------------
# Initialize the text-to-speech engine
speaker = pyttsx3.init()
# Set the speech rate
speaker.setProperty("rate",150)

# Get available voices and set the preferred voice
voices = speaker.getProperty('voices')     
speaker.setProperty('voice', voices[0].id) 

# Function to convert text to speech
def text_to_speech(text):
    engine = pyttsx3.init()  # Initialize the text-to-speech engine
    engine.setProperty('rate', 160)  # Set the speech rate
    engine.setProperty('volume', 1.0)  # Set the volume level
    engine.say(text)  # Convert text to speech
    engine.runAndWait()
# ---------------------------------------------------------------------------

# Flask forms for different pages -------------------------------------------
# Form for the speech input page
class TestForm(FlaskForm):
    submit = SubmitField('Speak')

# Form for displaying questions and answers
class displayForm(FlaskForm):
    Question = StringField('Question', render_kw={'readonly': True})
    Answer = StringField('Answer', render_kw={'readonly': True})

# Form for displaying error messages
class ErrordisplayForm(FlaskForm):
    Error_message = StringField('Error Message', render_kw={'readonly': True})
# ---------------------------------------------------------------------------

# Creating Flask application instance ---------------------------------------
app = Flask(__name__)  # Flask app initialization
app.config['SECRET_KEY'] = 'any secret string'  # Secret key for form security
# ---------------------------------------------------------------------------

# Home page route and view ---------------------------------------------------
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')  # Render the home page template
# ---------------------------------------------------------------------------

# Page for interaction with the bot -----------------------------------------
@app.route('/Nash', methods=['POST', 'GET'])
def Nash():  
    # Global variables initialization
    global Error_message
    global Question
    global Answer
    global nash
    form = TestForm()  # Initialize form instance
    Question = ''
    Answer = ''
    nash = ''

    if form.validate_on_submit():
        while True:
            recognizer = sr.Recognizer()  # Initialize speech recognizer
            try:
                with sr.Microphone() as mic:
                    recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                    print('listening')
                    nash = 'listening'
                    audio = recognizer.listen(mic)  # Listen for speech input
                    text = recognizer.recognize_google(audio)  # Convert speech to text
                    text = text.lower()  # Convert text to lowercase
                    print(text)
                    
                    # Check for specific wake-up phrases
                    if text in ['hi mishi', 'hi messi', 'hi missy', 'hey mishi', 'hey missy', 'hey nash', 'highness', 'mishi', 'messy', 'missy', 'nass', 'nas', 'play nash']:
                        nash = 'How can I help you?'
                        print('How can I help you?')
                        speaker.say("How can I help you?")
                        speaker.runAndWait()
                        print('working')
                        audio = recognizer.listen(mic)  # Listen for further input
                        print('it is recording')
                        text = recognizer.recognize_google(audio)  # Convert speech to text
                        text = text.lower()  # Convert text to lowercase
                        print(text)
                        Question = ''
                        Answer = ''

                        # Check for stop command
                        if text == 'stop':
                            speaker.say("Bye")
                            speaker.runAndWait()
                            speaker.stop()
                            break
                        else:
                            if text is not None:
                                Question = text
                                response, metaData, ref = rag_response(text)  # Generate response using custom model
                                Answer = response
                                print(response)
                                speaker.say(response)
                                speaker.runAndWait()
                    
            except sr.UnknownValueError:
                Error_message = 'Speech Recognition could not understand audio'
                return redirect(url_for('errordisplay'))  # Redirect to error display page
            
            except sr.RequestError as e:
                Error_message = f'Could not request results from Google Speech Recognition service: {e}'
                return redirect(url_for('errordisplay'))  # Redirect to error display page

    return render_template('Nash.html', form=form, Question=Question, Answer=Answer, nash=nash)  # Render the contact page template
# ---------------------------------------------------------------------------

# Route for displaying questions and answers --------------------------------
@app.route('/display', methods=['POST', 'GET'])
def display():
    return render_template('display.html')  # Render the display page template
# ---------------------------------------------------------------------------

# Route for displaying error messages --------------------------------------
@app.route('/errordisplay', methods=['POST', 'GET'])
def errordisplay():
    ErrorMeg = Error_message
    return render_template('Error_display.html', ErrorMeg=ErrorMeg)  # Render the error display page template
# ---------------------------------------------------------------------------

# Running the Flask application ---------------------------------------------
if __name__ == '__main__': 
    app.run(debug=True, port=5000)  # Run the Flask application in debug mode on port 5000