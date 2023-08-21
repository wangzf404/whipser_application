import asyncio
import websockets
from transcribe import Transcriber
import logging
import io
import soundfile as sf
import tempfile
import os
from pydub import AudioSegment
import whisper
import speech_recognition as sr
from queue import Queue

# 设置日志级别为ERROR
logging.basicConfig(level=logging.ERROR)

transcriber = Transcriber('medium')

UPLOAD_FOLDER = './download/mic/'
recorder = sr.Recognizer()
last_sample = bytes()
data_queue = Queue()
recorder.dynamic_energy_threshold = False

async def receive_audio(websocket, path):
    counter = 1
    audio_buffer = b''
    
    while True:
        try:
            # 接收语音数据
            audio_data = await websocket.recv()
            
            # 将语音数据添加到缓冲区
            audio_buffer += audio_data
            print('接收到音频数据'+len(audio_buffer))
            # 每 30 秒存储为一个文件
            if len(audio_buffer) >= 3 * 1000000:  # 假设每秒的语音数据大小为 1000000 字节
                file_name = f"{UPLOAD_FOLDER}temp{counter}.wav"
                with open(file_name, "wb") as f:
                    f.write(audio_buffer)
                print(f"Saved {file_name}")
                counter += 1
                audio_buffer = b''
            
        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed by client")
            break

if __name__ == '__main__':
    start_server = websockets.serve(receive_audio, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    print("WebSocket server is listening on ws://localhost:8765")
    asyncio.get_event_loop().run_forever()
