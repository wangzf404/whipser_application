import requests
import re
import json
import subprocess
import os
import logging
import pytube

# 设置日志级别为ERROR
logging.basicConfig(level=logging.ERROR)
UPLOAD_FOLDER = './download/blibli/'

def download_youtube_video(url):
    try:
        # 创建保存视频的文件夹
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        try:
            video_yt = pytube.YouTube(url)
        except Exception:
            raise(RuntimeError(f"{url} isn't recgnized."))
        try:
            video_yt.check_availability()
        except pytube.exceptions.VideoUnavailable:
            raise(RuntimeError(f"{url} isn't available."))

        video_streams = video_yt.streams.filter(
            type="video", mime_type="video/mp4", res="720p")
        video_streams.first().download(
            output_path=UPLOAD_FOLDER,
            filename=video_yt.video_id+".mp4"
        )
        return UPLOAD_FOLDER + video_yt.video_id+".mp4"
    except Exception:
        logging.exception("Failed")

def download_bilibili_video(url):
    try:
        # 创建保存视频的文件夹
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        session = requests.session()
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.37',
                "Referer": "https://www.bilibili.com",
                }
        resp = session.get(url, headers=headers)
        # print(resp.text)
        title = re.findall(
            r'<title data-vue-meta="true">(.*?)_哔哩哔哩_bilibili', resp.text)[0]
        play_info = re.findall(
            r'<script>window.__playinfo__=(.*?)</script>', resp.text)[0]

        '''print(title)
        print(play_info,type(play_info))  '''
        json_data = json.loads(play_info)
        # pprint.pprint(json_data)   #格式化输出，便于观看
        # print(type(json_data))
        # 音频地址  [0]清晰度最高
        audio_url = json_data['data']['dash']['audio'][0]['backupUrl'][0]
        video_url = json_data['data']['dash']['video'][0]['backupUrl'][0]  # 视频地址

        audio_content = session.get(audio_url, headers=headers).content  # 音频二进制内容
        video_content = session.get(video_url, headers=headers).content  # 视频二进制内容

        audio_path = UPLOAD_FOLDER+title+'.mp3'
        video_path = UPLOAD_FOLDER+title+'.mp4'
        video_temp_path = UPLOAD_FOLDER+'temp.mp4'

        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(video_temp_path):
            os.remove(video_temp_path)

        with open(audio_path, 'wb') as f:
            f.write(audio_content)
        with open(video_temp_path, 'wb') as f:
            f.write(video_content)
        print('-------合并视频-------')

        # 使用FFmpeg合并音频和视频
        command = f'ffmpeg -i {video_temp_path} -i {audio_path} -c:v copy -c:a copy {video_path}'
        subprocess.call(command, shell=True)
        return video_path
    except Exception:
        logging.exception("Failed")

download_bilibili_video(
    "https://www.bilibili.com/video/BV1Kz4y147gn/?spm_id_from=333.1007.tianma.3-3-7.click&vd_source=43a6ab1113d135fcf3da91ddb9d242d5")
