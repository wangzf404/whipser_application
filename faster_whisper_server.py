from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from transcribe import Transcriber
from online_download import download_bilibili_video,download_youtube_video
from openai_api import summarize_text
import os
import logging

app = Flask(__name__)

# 设置日志级别为DEBUG或更高级别，可以根据需要调整
app.logger.setLevel(logging.DEBUG)

# 创建一个日志处理程序，输出到控制台
console_handler = logging.StreamHandler()
app.logger.addHandler(console_handler)

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
# 上传文件的保存路径
UPLOAD_FOLDER = './download'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/online_download")
def online_video_file():
    video_path = None
    online_url = request.args.get('online_url')
    if "bilibili.com" in online_url:
        video_path = download_bilibili_video(online_url)
    elif "youtube.com" in online_url:
        video_path = download_youtube_video(online_url)
    else:
        raise ValueError(f"视频格式错误.") 
    response = {
        'video_path': video_path,
    }
    return jsonify(response), 200


@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.error(error)
    response = {
        'error': 'An internal error occurred.'
    }
    return jsonify(response), 500


@app.route('/upload_file', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        return jsonify({'file_path': filename,
                        'code': 200})


@app.route("/video")
def video_file():
    file_path = request.args.get('file_path')
    return send_file(file_path, mimetype='video/mp4')


@app.route("/summary", methods=['POST'])
def summary():
    data = request.json
    txt_content = data.get('txt_content').replace(r'<br/>', ' ')
    max_tokens = data.get('max_tokens')
    if(txt_content == ""):
        return ""
    return summarize_text(txt_content, max_tokens)


@app.route("/sub")
def sub_file():
    vtt_content = ""
    try:
        sub_path = request.args.get('sub_path')
        with open(sub_path, 'r', encoding='utf-8') as file:
            vtt_content = file.read()
    except Exception as e:
        print("Error:", str(e))

    return vtt_content


@app.route('/transcription', methods=['POST'])
def transcription():
    try:
        data = request.json

        file_path = data.get('filePath')
        model = data.get('model')
        source_language = data.get('language')
        use_translator = data.get('translator')
        transcriber = Transcriber(model)

        txt_content = transcriber.transcribe_file(
            file_path, source_language, False, use_translator)
        response = {
            'file_path': file_path,
            'txt_content': txt_content
        }
        return jsonify(response), 200
    except Exception as e:
        logging.exception("Failed")
        return jsonify({'error': str(e)}), 500


app.run()
