# 转写
import torch
from faster_whisper import WhisperModel
import ffmpeg
import os
import pysubs2
from tqdm import tqdm
import time
from zhconv import convert
from pathlib import Path
import logging
from googletrans import Translator

# 设置日志级别为ERROR
logging.basicConfig(level=logging.ERROR)


class Transcriber:

    def __init__(self, model_size):
        torch.cuda.empty_cache()
        print('加载模型 Loading model...', model_size)
        if model_size == 'medium':
            self.model = WhisperModel("./model/faster-whisper-medium")
        elif model_size == 'large':
            self.model = WhisperModel("./model/faster-whisper-large-v2")
        else:
            self.model = WhisperModel(model_size)
        print('加载模型 完成')

    def transcribe(
        self,
        file_name,
        language='auto',
        word_timestamps=False,
        use_translator=False
    ):
        try:
            print('识别中 Transcribe in progress...')
            tic = time.time()
            segments, info = self.model.transcribe(audio=file_name,
                                                   beam_size=1,
                                                   best_of=1,
                                                   language=None if language == "auto" else language,
                                                   vad_filter='true',
                                                   word_timestamps=word_timestamps,
                                                   vad_parameters=dict(min_silence_duration_ms=1000))
            print('字幕生成中 ...')
            total_duration = round(info.duration, 2)
            results = []
            all_text = ''
            with tqdm(total=total_duration, unit=" seconds") as pbar:
                for s in segments:
                    text = convert(s.text, 'zh-cn')
                    if use_translator:
                        translator = Translator()
                        text = text+'\n'+translator.translate(
                            text, dest='zh-cn').text
                    segment_dict = {'start': s.start, 'end': s.end,
                                    'text': text}
                    results.append(segment_dict)
                    segment_duration = s.end - s.start
                    pbar.update(segment_duration)
                    all_text += (text + '\n')

            toc = time.time()

            print('识别完毕 Done')
            print(f'Time consumpution {toc-tic}s')
            return all_text, results
        except Exception:
            logging.exception("Failed")

    def transcribe_file(
        self,
        file_path,
        language='auto',
        word_timestamps=False,
        use_translator=False
    ):
        try:
            if not os.path.exists(file_path):
                raise ValueError(f"No {file_path} found in current path.")
            file_name = Path(file_path)
            all_text, results = self.transcribe(
                str(file_name), language, word_timestamps, use_translator)

            file_basename = file_name.parent / file_name.stem
            txt_path = str(file_basename)+'.txt'
            vtt_path = str(file_basename)+'.vtt'
            srt_path = str(file_basename)+'.srt'
            if os.path.exists(srt_path):
                os.remove(srt_path)
            if os.path.exists(vtt_path):
                os.remove(vtt_path)
            if os.path.exists(txt_path):
                os.remove(txt_path)
            subs = pysubs2.load_from_whisper(results)
            subs.save(vtt_path)
            subs.save(srt_path)
            subs.save(txt_path)
            torch.cuda.empty_cache()
        except Exception:
            logging.exception("Failed")

        return all_text
