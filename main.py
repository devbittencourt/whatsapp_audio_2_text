import os
import speech_recognition as sr
from pydub import AudioSegment
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pyperclip
import time


AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"
inicio_tempo = time.time()

Tk().withdraw()
caminho_ogg = askopenfilename(title="Selecione um arquivo .ogg", filetypes=[("OGG files", "*.ogg")])
if not caminho_ogg:
    print("Nenhum arquivo selecionado.")
    exit()

r = sr.Recognizer()

transcricoes = []

for velocidade in [round(v, 2) for v in [0.885 + 0.015 * i for i in range(4)]]:

    audio_original = AudioSegment.from_file(caminho_ogg, format="ogg")
    audio = audio_original._spawn(audio_original.raw_data, overrides={
        "frame_rate": int(audio_original.frame_rate * velocidade)
    }).set_frame_rate(audio_original.frame_rate)

    duracao_ms = len(audio)
    segmento_ms = 30 * 1000
    texto_velocidade = []

    for i in range(0, duracao_ms, segmento_ms):
        segmento_audio = audio[i:i+segmento_ms]
        caminho_temp = f"temp_{velocidade}_{i}.wav"
        segmento_audio.export(caminho_temp, format="wav")

        with sr.AudioFile(caminho_temp) as source:
            audio_data = r.record(source)

        try:
            texto = r.recognize_google(audio_data, language="en-US")
            texto_velocidade.append(texto)
        except sr.UnknownValueError:
            texto_velocidade.append("[Inaudível]")
        except sr.RequestError as e:
            texto_velocidade.append("[Erro]")

        os.remove(caminho_temp)

    transcricao_geral = f"[Velocidade {velocidade}]\n" + "\n".join(texto_velocidade)
    transcricoes.append(transcricao_geral)

prompt = "Your prompt here"

resultado_final = prompt + "\n\n" + "\n\n".join(transcricoes)

print("Todas as transcrições:")
print(resultado_final)
pyperclip.copy(resultado_final)
fim_tempo = time.time()
duracao = fim_tempo - inicio_tempo
minutos = int(duracao // 60)
segundos = int(duracao % 60)
print(f"\nTempo total: {minutos} m {segundos} s")
