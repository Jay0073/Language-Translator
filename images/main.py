""" 
Group Project -- Team-8 -- Title-LANGUAGE TRANSLATOR
THE MAIN OBJECTIVES OF THIS PROJECT ARE:
To create a GUI based application
    1. that can RECOGNIZE SPEECH and convert it to text.
    2. that can translate the text from one language to another.
    3. that can SUMMARIZE the text given to it.

google can support 137 languages but 
this can support 107 global languages

"""


# these libraries for speech recognition, translation and GUI related things 
import speech_recognition as sr
from unidecode import unidecode
from googletrans import Translator, LANGUAGES
from tkinter import messagebox, ttk, filedialog
from customtkinter import *
from gtts import gTTS
from PIL import Image
import threading
import os
import time
import httpx


# these libraries for summarization
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.cluster.util import cosine_distance

import numpy as np
import networkx as nx


# global declarations
translator = Translator()

def ensure_nltk_resources():
    resources = {
        'tokenizers/punkt': 'punkt',
        'corpora/stopwords.zip': 'stopwords'
    }
    
    for resource_path, resource_name in resources.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(resource_name)


ensure_nltk_resources()

source_lang = 'en'
target_lang = 'en'

global print_in
print_in = True


# GUI GEOMETRY
set_appearance_mode('light')

def resour_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


root = CTk()
root.geometry("800x650")
root.iconbitmap(resour_path(r"images\\Translation-80_icon-icons.com_57255.ico"))
root.resizable(False, False)
root.title("Language Translator")

# ---------------------------------------------------------------------------------------------------------------
# THESE FUNCTION FOR PRINTING IN LABEL

def print_in_label():
        while print_in:
            progresslab1.configure(text="Recognizing.")
            time.sleep(1) 
            progresslab1.configure(text="Recognizing..")
            time.sleep(1)
            progresslab1.configure(text="Recognizing...")
            time.sleep(1)
            if print_in == False:
                break
            else:
                progresslab1.configure(text="Just a moment.")
                time.sleep(1)
                progresslab1.configure(text="Just a moment..")
                time.sleep(1)
                progresslab1.configure(text="Just a moment...")
                time.sleep(1)
            if print_in == False:
                break
            else:
                progresslab1.configure(text="Almost there.")
                time.sleep(1)
                progresslab1.configure(text="Almost there..")
                time.sleep(1)
                progresslab1.configure(text="Almost there...")
                time.sleep(1)

# --------------------------------------------------------------------------------
# THESE ARE SPEECH FUNCTIONS...

def speech():
    try:
        progresslab1.configure(text="Please wait...")
        rawtext = trans_text.get(0.0, 'end')
        text = rawtext.split('> ')
        lan = ''.join(key for key, value in LANGUAGES.items() if value ==  tar_box.get())
        tts = gTTS(text=text[1], lang=lan)
        tts.save("speech.mp3")
        progresslab1.configure(text="")
        os.system('start speech.mp3')
    except IndexError:
        progresslab1.configure(text="")
        messagebox.showerror(title="Language Translator", message="No Text to Speak!")
    except AssertionError:
        progresslab1.configure(text="")
        messagebox.showerror(title="Language Translator", message="No text to Speak!")
    except ValueError:
        messagebox.showerror(title="Language Translator", message=f"Sorry for inconvenience. This language is not supported : {tar_box.get()}")



def speech2():
    try:
        progresslab2.configure(text="Please wait...")
        rawtext = translated_text.get(0.0, 'end')
        text = rawtext.split('>  ')
        lan = ''.join(key for key, value in LANGUAGES.items() if value ==  targ_box.get())
        tts = gTTS(text=text[1], lang=lan)
        tts.save("speech.mp3")
        progresslab2.configure(text="")
        os.system('start speech.mp3')
    except IndexError:
        progresslab2.configure(text="")
        messagebox.showerror(title="Language Translator", message="No Text to Speak!")
    except AssertionError:
        progresslab2.configure(text="")
        messagebox.showerror(title="Language Translator", message="No text to Speak!")
    except ValueError:
        messagebox.showerror(title="Language Translator", message=f"Sorry for inconvenience. This language is not supported : {targ_box.get()}")


def speech3():
    try:
        progresslab3.configure(text="Please wait...")
        text = summarized_text.get(1.3, 'end')
        detected_lang = translator.detect(text).lang
        lang = ''.join(value for key, value in LANGUAGES.items() if key == detected_lang)

        detect_lab2.configure(text=f"Detected Language : {lang}")
        tts = gTTS(text=text, lang=detected_lang)
        tts.save("speech.mp3")
        
        progresslab3.configure(text="")
        os.system('start speech.mp3')
    except IndexError:
        progresslab3.configure(text="")
        messagebox.showerror(title="Language Translator", message="No Text to Speak!")
    except AssertionError:
        progresslab3.configure(text="")
        messagebox.showerror(title="Language Translator", message="No text to Speak!")
    except ValueError:
        progresslab3.configure(text="")
        messagebox.showerror(title="Language Translator", message=f"Sorry for inconvenience. This language is not supported : {lang}")

# -----------------------------------------------------------------------------------------------------------------------
# SUMMARY FUNCTIONS

def preprocess_text(text):
    try:
        # Tokenization
        sentences = sent_tokenize(text)
        words = word_tokenize(text)

        # Remove punctuation and lowercase
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(text.lower())

        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word not in stop_words]

        # Stemming
        stemmer = PorterStemmer()
        words = [stemmer.stem(word) for word in words]

        return sentences, words
    except Exception as e:
        print("Error occurred during preprocessing:", e)
        messagebox.showerror(title="Language Translator", message=f"Error occured during preprocessing: {e}")
        return [], []

def sentence_similarity(sent1, sent2):
    all_words = list(set(sent1 + sent2))
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for w in sent1:
        vector1[all_words.index(w)] += 1

    for w in sent2:
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)

def build_similarity_matrix(sentences):
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                similarity_matrix[i][j] = sentence_similarity(sentences[i], sentences[j])
    return similarity_matrix

def generate_summary():
    prin = True
    num_sentences = int(slider.get())
    text = entered_text.get(0.0, 'end')

    detectedlang = translator.detect(text).lang
    x = ''.join(value for key, value in LANGUAGES.items() if key == detectedlang)
    detect_lab2.configure(text=f"Detected Language : {x}")
    # print(type(text))

    def print_inlab():
        while prin:
            progresslab3.configure(text="Summarizing.")
            time.sleep(1) 
            progresslab3.configure(text="Summarizing..")
            time.sleep(1)
            progresslab3.configure(text="Summarizing...")
            time.sleep(1)
            if prin == False:
                break
            else:
                progresslab3.configure(text="Just a moment.")
                time.sleep(1)
                progresslab3.configure(text="Just a moment..")
                time.sleep(1)
                progresslab3.configure(text="Just a moment...")
                time.sleep(1)
            if prin == False:
                break
            else:
                progresslab3.configure(text="Almost there.")
                time.sleep(1)
                progresslab3.configure(text="Almost there..")
                time.sleep(1)
                progresslab3.configure(text="Almost there...")
                time.sleep(1)


    
    try:
        print_inlabThr = threading.Thread(target=print_inlab)
        print_inlabThr.start()
        sentences, words = preprocess_text(text)
        if not sentences:
            return "Error: Text preprocessing failed."
        
        sentence_similarity_matrix = build_similarity_matrix(sentences)
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
        scores = nx.pagerank(sentence_similarity_graph)
        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        summary = ' '.join([sentence for _, sentence in ranked_sentences[:num_sentences]])
        
        prin = False
        print_inlabThr.join()
        progresslab3.configure(text="")


        his_summar_text.configure(state='normal')
        his_summar_text.insert(index='end', text=f"Summary Length: {num_sentences}\nSummarized Text: \n{summary}\n___________________________________________________________\n")
        his_summar_text.configure(state='disabled')

        summarized_text.configure(state='normal')
        summarized_text.delete(0.0, 'end')
        summarized_text.insert(index=0.0, text=f">  {summary}")
        summarized_text.configure(state='disabled')

    except Exception as e:
        messagebox.showerror(title="Language Translator", message=f"{e}")

    except httpx.HTTPCoreException as e:
        messagebox.showerror(title="Language Translator", message="An error occurred while making the HTTP request. Please try again")


    
# -------------------------------------------------------------------------------
# TRANSLATING TEXT FUNCTION 

def translate():  
    printer = True
    def translating_lab_fun():
        while printer:
            progresslab2.configure(text="Translating.")
            time.sleep(1)
            progresslab2.configure(text="Translating..")
            time.sleep(1)
            progresslab2.configure(text="Translating...")
            time.sleep(1)

    translating_thread = threading.Thread(target=translating_lab_fun)

    try:
        
        text = entry_text.get(0.0, 'end')

        target_lang = ''.join(key for key, value in LANGUAGES.items() if value ==  targ_box.get())
        detectedlang = translator.detect(text).lang

        x = ''.join(value for key, value in LANGUAGES.items() if key == detectedlang)
        y = ''.join(value for key, value in LANGUAGES.items() if key == target_lang)

        detect_lab1.configure(text=f"Detected Language : {x}")

        if detectedlang == target_lang:
            translitted_text = unidecode(text)
            translated_text.configure(state='normal')
            translated_text.delete(0.0, 'end')
            translated_text.insert(index='end',text= f">  {text}\n\n\n>  {translitted_text}")
            translated_text.configure(state='disabled')

            his_text_text.configure(state='normal')
            his_text_text.insert(index='end', text=f"Given Text in {x}: \n>  {text}\nTranslated to {y}: \n>  {text}\nPronounciation: \n>  {translitted_text}\n___________________________________________________________\n")
            his_text_text.configure(state='disabled')
            
        else:
            translating_thread.start()

            tran_text = translator.translate(text, src=detectedlang, dest=target_lang).text
            translited_text = unidecode(tran_text)

            his_text_text.configure(state='normal')
            his_text_text.insert(index='end', text=f"Given Text in {x}: \n>  {text}Translated to {y}: \n>  {tran_text}\nPronounciation: \n>  {translited_text}\n___________________________________________________________\n")
            his_text_text.configure(state='disabled')

            printer = False
            translating_thread.join()
            progresslab2.configure(text="")

            translated_text.configure(state='normal')
            translated_text.delete(0.0, 'end')

            translated_text.insert(index='end',text= f"\n>  {tran_text}\n")
            translated_text.insert(index='end',text= f"\n>  {translited_text}\n")

            translated_text.configure(state='disabled')

    except IndexError:
        messagebox.showerror(title="Language Translator", message="Nothing to translate")
    except TypeError:
        messagebox.showerror(title="Language Translator", message="Entered text is invalid!")
    except httpx.HTTPCoreException as e:
        messagebox.showerror(title="Language Translator", message="An error occurred while making the HTTP request. Please try again")



# -------------------------------------------------------------------------------------------------------------------------
# SPEECH RECOGNITION AND TRANSLATING IT FUNCTION

def speak():
    global print_in, history_value_text
    lis = True
    to_print = threading.Thread(target=print_in_label)


    def to_listen_lab():
        while lis:
            progresslab1.configure(text="Listening.")
            time.sleep(0.5)
            progresslab1.configure(text="Listening..")
            time.sleep(0.5)
            progresslab1.configure(text="Listening...")
            time.sleep(0.5)
            progresslab1.configure(text="Listening....")
            time.sleep(0.5)


    to_listen = threading.Thread(target=to_listen_lab)


    source_lang = ''.join(key for key, value in LANGUAGES.items() if value == src_box.get())
    target_lang = ''.join(key for key, value in LANGUAGES.items() if value ==  tar_box.get())


    x = ''.join(value for key, value in LANGUAGES.items() if key == source_lang)
    y = ''.join(value for key, value in LANGUAGES.items() if key == target_lang)

    # Initialize the recognizer and translator
    recognizer = sr.Recognizer()
    translator = Translator()

    progresslab1.configure(text="Just a second")


    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)

        # Listening to the speech     
        try:

            to_listen.start()
            audio = recognizer.listen(source, timeout=5)
            lis = False
            to_listen.join()

            to_print.start()
            # Speech to text
            text = recognizer.recognize_google(audio, language=source_lang)
            translated_text = translator.translate(text, src=source_lang, dest=target_lang).text
            translit_text = unidecode(translated_text)

            his_speech_text.configure(state='normal')
            his_speech_text.insert(index='end', text=f"Recognized Speech in {x}: \n>  {text}\nTranslated text to {y}       : \n>  {translated_text}\nPronounciation  :\n>  {translit_text}\n___________________________________________________________\n")
            his_speech_text.configure(state='disabled')

            print_in = False
            to_print.join()
            progresslab1.configure(text="")
            
            org_text.configure(state='normal')
            trans_text.configure(state='normal')
            transliter_text.configure(state='normal')

            org_text.delete(0.0, 'end')
            trans_text.delete(0.0, 'end')
            transliter_text.delete(0.0, 'end')

            org_text.insert(index='end',text= f"\n>  {text}\n")
            trans_text.insert(index='end',text= f"\n>  {translated_text}\n")
            transliter_text.insert(index='end',text= f"\n>  {translit_text}\n")

            org_text.configure(state='disabled')
            trans_text.configure(state='disabled')
            transliter_text.configure(state='disabled')

        except sr.UnknownValueError:
            print_in = False
            to_print.join()
            progresslab1.configure(text="")
            messagebox.showinfo(title="Language Translator", message="Unable to understand. Please speak again")
    
        except sr.RequestError:
            print_in = False
            to_print.join()
            progresslab1.configure(text="")
            messagebox.showerror(title="Language Translator", message="Unable to fetch. Check your Internet connection..")

        except sr.WaitTimeoutError:
            progresslab1.configure(text="")
            messagebox.showerror(title="Language Translator",  message="Listening timed out. Please Speak Again.")

        # except Exception as e:
        #     print_in = False
        #     to_print.join()
        #     progresslab.configure(text="")
        #     print(f"An error occurred: {e}")

        except httpx.HTTPCoreException as e:
            messagebox.showerror(title="Language Translator", message="An error occurred while making the HTTP request. Please try again")



# ------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------
# history functions

def speech_his():
    tabs.set("History")
    his_tabs.set("Speech")

def text_his():
    tabs.set("History")
    his_tabs.set("Text")

def summar_his():
    tabs.set("History")
    his_tabs.set("Summarizer")



def clear_speech_text():
    his_speech_text.configure(state='normal')
    his_speech_text.delete(0.0, 'end')
    his_speech_text.configure(state='disabled')

def clear_text_text():
    his_text_text.configure(state='normal')
    his_text_text.delete(0.0, 'end')
    his_text_text.configure(state='disabled')

def clear_summar_text():
    his_summar_text.configure(state='normal')
    his_summar_text.delete(0.0, 'end')
    his_summar_text.configure(state='disabled')



def close_to_speech():
    tabs.set("Speech")

def close_to_text():
    tabs.set("Text")

def close_to_summar():
    tabs.set("Summarizer")


    
# -------------------------------------------------------------------------
# saving functions

def speech_save():
    data = his_speech_text.get(0.0, 'end')
    file = filedialog.asksaveasfilename(title="Save file as", 
                                        filetypes=[('Text file', '.txt')],
                                        defaultextension='.txt',
                                        initialdir=r"Project"
                                        )
    fileobj = open(file, 'w', encoding="utf-8")
    fileobj.write(data)
    fileobj.close()


def text_save():
    data = str(his_text_text.get(0.0, 'end'))
    file = filedialog.asksaveasfilename(title="Save file as", 
                                        filetypes=[('Text file', '.txt')],
                                        defaultextension='.txt',
                                        initialdir=r"Project"
                                        )
    fileobj = open(file, 'w', encoding="utf-8")
    fileobj.write(data)
    fileobj.close()

        
def summar_save():
    data = his_summar_text.get(0.0, 'end')
    file = filedialog.asksaveasfilename(title="Save file as", 
                                        filetypes=[('Text file', '.txt')],
                                        defaultextension='.txt',
                                        initialdir=r"Project"
                                        )
    fileobj = open(file, 'w', encoding="utf-8")
    fileobj.write(data)
    fileobj.close()

# --------------------------------------------------------------------------
# tabs

tabs = CTkTabview(root)
tabs.pack()

tab1 = tabs.add("Speech")
tab2 = tabs.add("Text")
tab3 = tabs.add("Summarizer")
tab4 = tabs.add("History")

his_tabs = CTkTabview(tab4)
his_tabs.pack()

his_speech_tab = his_tabs.add("Speech")
his_text_tab = his_tabs.add("Text")
his_summar_tab = his_tabs.add("Summarizer")



# -----------------------------------------------------------------------------
# image opening

mic = Image.open(resour_path(r"images\\mic_microphone_record_voice_icon_124736.png"))

speaker = Image.open(resour_path(r"images\\Speaker_icon-icons.com_54138.png"))

his = Image.open(resour_path(r"images\\history-clock-button_icon-icons.com_72701.png"))

trans = Image.open(resour_path(r"images\\Google_Translate_23405.png"))

summar = Image.open(resour_path(r"images\\documentediting_editdocuments_text_documentedi_2820.png"))

arrowImg = CTkImage(light_image=Image.open(resour_path(r"images\\iconfinder-translate-4595786_122223.png")),
                     dark_image=Image.open(resour_path(r"images\\iconfinder-translate-4595786_122223.png")),
                     size=(80, 50))


# ---------------------------------------------------------------------------------
#                                      TAB 1 
# ------------------------------------------------------------------------------------------------------

# 1st frame
title_lab = CTkLabel(tab1, text="Speech to Text", font=('calibri', 40), bg_color='white')
title_lab.pack(pady=10)

frame1 = CTkFrame(tab1) #gray 14
frame1.pack(side='top', pady=(10, 0), padx=10)

org_text = CTkTextbox(frame1, font=(None, 19), width=550, height=100, state='disabled')
org_text.pack(padx=10)

trans_text = CTkTextbox(frame1, font=(None, 19), width=550, height=100, state='disabled')
trans_text.pack(padx=10, pady=10)

transliter_text = CTkTextbox(frame1, font=(None, 19), width=550, height=100, state='disabled')
transliter_text.pack(padx=10)

# 2nd frame
frame2 = CTkFrame(tab1)
frame2.pack(padx=10, pady=(10, 0))

fromlab = CTkLabel(frame2, text="From Language: ",  font=(None, 15))
fromlab.grid(row=0, column=0)

src_box = ttk.Combobox(fromlab, values=list(LANGUAGES.values()), height=25, width=20, font=(None, 13))
src_box.set("english")
src_box.bind("<<ComboboxSelected>>")
src_box.grid(pady=5)

arrowlab = CTkLabel(frame2, text="", image=arrowImg)
arrowlab.grid(row=0, column=1, padx=30)

tolab = CTkLabel(frame2, text="To Language: ", font=(None, 15))
tolab.grid(row=0, column=2)

tar_box = ttk.Combobox(tolab, values=list(LANGUAGES.values()), height=25, width=20, font=(None, 13))
tar_box.set("english")
tar_box.bind("<<ComboboxSelected>>")
tar_box.grid(pady=5)

progresslab1 = CTkLabel(frame2, text="", state="disabled", font=("",18))
progresslab1.grid(row=1, column=1)

# 3rd frame
frame3 = CTkFrame(tab1)
frame3.pack(side='bottom', padx=10)

spe_but = CTkButton(frame3, text="", command=lambda: threading.Thread(target=speak).start(),
                    image=CTkImage(dark_image=mic,light_image=mic, size=(50, 50)), 
                    corner_radius=30,
                    fg_color="transparent",
                    width=15,
                    height=30)
spe_but.grid(row=1, column=1, padx=30, pady=20)

speak_but = CTkButton(frame3, text="", command=lambda: threading.Thread(target=speech).start(),
                      image=CTkImage(dark_image=speaker,light_image=speaker, size=(30, 30)), 
                      corner_radius=30,
                      fg_color="transparent",
                      width=15,
                      height=30
                     )
speak_but.grid(row=1, column=2, padx=30, pady=20)

history1_but = CTkButton(frame3, text="", command=speech_his,
                      image=CTkImage(dark_image=his, light_image=his, size=(30, 30)),
                      corner_radius=30,
                      fg_color="transparent",
                      width=15,
                      height=30)
history1_but.grid(row=1, column=0, padx=30, pady=20)


# ---------------------------------------------------------------------------------------------------------
#                                                   TAB 2
#--------------------------------------------------------------------------------------------

# 1st frame
title_lab2 = CTkLabel(tab2, text="Text to Speech", font=('calibri', 40), bg_color='white')
title_lab2.pack(pady=10)

frame4 = CTkFrame(tab2) #gray 14
frame4.pack(anchor='n', pady=(10, 0), padx=10)

entry_text = CTkTextbox(frame4, font=(None, 19), width=350, height=300)
entry_text.grid(row=0, column=0, padx=10, pady=10)

translated_text = CTkTextbox(frame4, font=(None, 19), width=350, height=300, state='disabled')
translated_text.grid(row=0, column=1, padx=10, pady=10)

detect_lab1 = CTkLabel(frame4, text="Detected Language : ", font=(None, 15))
detect_lab1.grid(row=1, column=0)

tolab2 = CTkLabel(frame4, text="Convert to: ", font=(None, 15))
tolab2.grid(row=1, column=1)

targ_box = ttk.Combobox(master=tolab2, values=list(LANGUAGES.values()), height=25, width=20, font=(None, 15))
targ_box.set("english")
targ_box.bind("<<ComboboxSelected>>")
targ_box.grid(pady=10)

# 2nd frame
frame5 = CTkFrame(tab2)
frame5.pack(anchor="center", padx=10)

progresslab2 = CTkLabel(frame5, text="", state="disabled", font=("",18))
progresslab2.grid()

# 3rd frame
frame6 = CTkFrame(tab2) #gray 14
frame6.pack(side='top', pady=(10, 0), padx=10)

translate_but = CTkButton(master=frame6, text="", command=lambda: threading.Thread(target=translate).start(),
                          image=CTkImage(dark_image=trans,light_image=trans, size=(50, 50)), 
                          corner_radius=30,
                          fg_color="transparent",
                          width=15,
                          height=30
                          )
translate_but.grid(row=0, column=1)

speak_but = CTkButton(frame6, text="", command=lambda: threading.Thread(target=speech2).start(),
                      image=CTkImage(dark_image=speaker,light_image=speaker, size=(30, 30)), 
                      corner_radius=30,
                      fg_color="transparent",
                      width=15,
                      height=30
                     )
speak_but.grid(row=0, column=2, padx=30, pady=20)

history2_but = CTkButton(frame6, text="", command=text_his,
                      image=CTkImage(dark_image=his, light_image=his, size=(30, 30)),
                      corner_radius=30,
                      fg_color="transparent",
                      width=15,
                      height=30)
history2_but.grid(row=0, column=0, padx=30, pady=20)


# ---------------------------------------------------------------------------------------------------
#                                          TAB 3
# -----------------------------------------------------------------------------------------------------

# 1st frame
title_lab3 = CTkLabel(tab3, text="Summarization", font=('calibri', 40), bg_color='white')
title_lab3.pack(pady=10)

frame7 = CTkFrame(tab3) #gray 14
frame7.pack(anchor='n', pady=(10, 0), padx=10)

entered_text = CTkTextbox(frame7, font=(None, 19), width=350, height=320)
entered_text.grid(row=0, column=0, padx=10, pady=10)

summarized_text = CTkTextbox(frame7, font=(None, 19), width=350, height=320, state='disabled')
summarized_text.grid(row=0, column=1, padx=10, pady=10)

detect_lab2 = CTkLabel(frame7, text="Detected Language : ", font=(None, 15))
detect_lab2.grid(row=1, column=0, padx=20, pady=5)

slider_lab = CTkLabel(frame7, text="Summary length: ", font=(None, 15))
slider_lab.grid(row=1, column=1, padx=20, pady=5)

slider = CTkSlider(slider_lab, from_=3, to=7, number_of_steps=6)
slider.grid(pady=5)

# 2nd frame
frame8 = CTkFrame(tab3)
frame8.pack(anchor="center", padx=10)

progresslab3 = CTkLabel(frame8, text="", font=("",18))
progresslab3.pack()

# 3rd frame
frame9 = CTkFrame(tab3) #gray 14
frame9.pack(side='top', pady=(0, 10), padx=10)

summarize_but = CTkButton(master=frame9, text="", command=lambda: threading.Thread(target=generate_summary).start(),
                          image=CTkImage(dark_image=summar,light_image=summar, size=(40, 40)), 
                          corner_radius=90,
                          fg_color="transparent",
                          width=15,
                          height=30
                          )
summarize_but.grid(row=0, column=1)

speak1_but = CTkButton(frame9, text="", command=lambda: threading.Thread(target=speech3).start(),
                      image=CTkImage(dark_image=speaker,light_image=speaker, size=(30, 30)), 
                      corner_radius=90,
                      fg_color="transparent",
                      width=15,
                      height=30
                     )
speak1_but.grid(row=0, column=2, padx=30, pady=20)

history3_but = CTkButton(frame9, text="", command=summar_his,
                      image=CTkImage(dark_image=his, light_image=his, size=(30, 30)),
                      corner_radius=90,
                      fg_color="transparent",
                      width=15,
                      height=30)
history3_but.grid(row=0, column=0, padx=30, pady=20)


# -------------------------------------------------------------------------------------------------------
#                                     HISTORY TABS
# ----------------------------------------------------------------------------------------------------

# ---------------1st tab
CTkLabel(his_speech_tab, text="Speech History", font=('calibri', 30), bg_color='white').pack(pady=(10,0))

his_speech_text = CTkTextbox(his_speech_tab, font=(None, 14), width=500, height=400, state='disabled')
his_speech_text.pack(padx=10, pady=10)

clear_but_speech_tab = CTkButton(his_speech_tab, text="Clear", command=clear_speech_text)
clear_but_speech_tab.pack(side="left", pady=(5, 10))

save_but_speech_tab = CTkButton(his_speech_tab, text="Save", command=speech_save)
save_but_speech_tab.pack(side="left", pady=(5, 10), padx=50)

close_but_speech_tab = CTkButton(his_speech_tab, text="Close", command=close_to_speech)
close_but_speech_tab.pack(side="right", pady=(5, 10))


# ----------- 2nd lab
CTkLabel(his_text_tab, text="Text History", font=('calibri', 30), bg_color='white').pack(pady=(10,0))

his_text_text = CTkTextbox(his_text_tab, font=(None, 14), width=500, height=400, state='disabled')
his_text_text.pack(padx=10, pady=10)

clear_but_text_tab = CTkButton(his_text_tab, text="Clear", command=clear_text_text)
clear_but_text_tab.pack(side="left", pady=(5, 10))

save_but_text_tab = CTkButton(his_text_tab, text="Save", command=text_save)
save_but_text_tab.pack(side="left", pady=(5, 10), padx=50)

close_but_text_tab = CTkButton(his_text_tab, text="Close", command=close_to_text)
close_but_text_tab.pack(side="right", pady=(5, 10))

# ----------- 3rd lab
CTkLabel(his_summar_tab, text="Summarization History", font=('calibri', 30), bg_color='white').pack(pady=(10,0))

his_summar_text = CTkTextbox(his_summar_tab, font=(None, 14), width=500, height=400, state='disabled')
his_summar_text.pack(padx=10, pady=10)

clear_but_summar_tab = CTkButton(his_summar_tab, text="Clear", command=clear_summar_text)
clear_but_summar_tab.pack(side="left", pady=(5, 10))

save_but_summar_tab = CTkButton(his_summar_tab, text="Save", command=summar_save)
save_but_summar_tab.pack(side="left", pady=(5, 10), padx=50)

close_but_summar_tab = CTkButton(his_summar_tab, text="Close", command=close_to_summar)
close_but_summar_tab.pack(side="right", pady=(5, 10))



root.mainloop()