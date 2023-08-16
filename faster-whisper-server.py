from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from transcribe import Transcriber
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
