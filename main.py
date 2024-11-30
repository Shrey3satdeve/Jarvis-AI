import speech_recognition as sr
import os
import webbrowser
import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
import pyttsx3  # For text-to-speech on Windows
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Initialize Hugging Face model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")

chatStr = ""

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# Spotify API Credentials
SPOTIPY_CLIENT_ID = 'your_spotify_client_id'  
SPOTIPY_CLIENT_SECRET = 'your_spotify_client_secret'  
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope="user-library-read user-read-playback-state user-modify-playback-state"))


def say(text):
    """Function to speak the text."""
    engine.say(text)
    engine.runAndWait()


def listen():
    """Function to listen for voice input and return text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except sr.WaitTimeoutError:
            print("No command heard. Waiting for wake word.")
            return None
        except Exception as e:
            print("Error:", e)
            return None


def play_spotify_song(song_name):
    """Function to search and play a song on Spotify."""
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        sp.start_playback(uris=[track_uri])
        say(f"Now playing {track['name']} by {track['artists'][0]['name']}")
    else:
        say("Sorry, I couldn't find the song on Spotify.")


def chat_hf(query):
    """Chat function using Hugging Face GPT-2."""
    global chatStr
    print(chatStr)
    chatStr += f"User: {query}\nJarvis: "
    
    # Encode the input and generate response
    inputs = tokenizer.encode(chatStr, return_tensors="pt")
    outputs = model.generate(inputs, max_new_tokens=50, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True).split("Jarvis:")[-1].strip()
    say(reply)
    chatStr += f"{reply}\n"
    return reply


def main():
    """Main function to run Jarvis."""
    print("Welcome to Jarvis A.I")
    say("Jarvis A.I is now active! Say 'Hey Jarvis' to start.")
    
    while True:
        wake_word = listen()  
        if wake_word and "hey jarvis" in wake_word.lower():
            say("I'm listening. What can I do for you?")
            command = listen()  
            
            if command:
                # Handle commands
                sites = [["youtube", "https://www.youtube.com"], 
                         ["wikipedia", "https://www.wikipedia.com"], 
                         ["google", "https://www.google.com"],
                         ["spotify", "https://www.spotify.com"],
                         ["bhopal","https://vtop.vitbhopal.ac.in/vtop"]]

                
                # Open websites
                for site in sites:
                    if f"open {site[0]}" in command.lower():
                        say(f"Opening {site[0]}...")
                        webbrowser.open(site[1])

                # Open music on Spotify
                if "play" in command.lower() and "song" in command.lower():
                    song_name = command.lower().replace("play", "").replace("song", "").strip()
                    play_spotify_song(song_name)

                # Announce the time
                elif "the time" in command.lower():
                    hour = datetime.datetime.now().strftime("%H")
                    minute = datetime.datetime.now().strftime("%M")
                    say(f"The time is {hour} hours and {minute} minutes.")

                # Quit command
                elif "quit" in command.lower() or "exit" in command.lower():
                    say("Goodbye!")
                    exit()

                # Reset chat history
                elif "reset chat" in command.lower():
                    global chatStr
                    chatStr = ""
                    say("Chat history reset.")

                # Default: Chat with GPT-2
                else:
                    print("Chatting...")
                    chat_hf(command)
            else:
                say("I didn't hear a command. Please say 'Hey Jarvis' again when you're ready.")

if __name__ == '__main__':
    main()
