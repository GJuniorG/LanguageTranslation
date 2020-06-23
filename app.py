import codecs
import os
import atexit
import glob

from flask import Flask, request, jsonify, make_response
from translate import Translator
import DocReader

from config import *

UPLOAD_FOLDER_TRANSLATED = 'C:/Users/shipant/PycharmProjects/NLP_LanguageTranslation/FileStorage_Translated'
UPLOAD_FOLDER_INPUT = 'C:/Users/shipant/PycharmProjects/NLP_LanguageTranslation/FileStorage_Input'

ALLOWED_EXTENSIONS = {'docx'}

app = Flask(__name__)
translator = Translator(MODEL_PATH)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app.config["DEBUG"] = True  # turn off in prod
app.config['UPLOAD_FOLDER_INPUT'] = UPLOAD_FOLDER_INPUT
app.config['UPLOAD_FOLDER_TRANSLATED'] = UPLOAD_FOLDER_TRANSLATED


@app.route('/', methods=["GET"])
def health_check():
    """Confirms service is running"""
    return "Machine translation service is up and running."


@app.route('/lang_routes', methods=["GET"])
def get_lang_route():
    lang = request.args['lang']
    all_langs = translator.get_supported_langs()
    lang_routes = [l for l in all_langs if l[0] == lang]
    return jsonify({"output": lang_routes})


@app.route('/supported_languages', methods=["GET"])
def get_supported_languages():
    langs = translator.get_supported_langs()
    return jsonify({"output": langs})


@app.route('/texts/translate', methods=["POST"])
def get_prediction():
    source = request.json['source']
    target = request.json['target']
    text = request.json['text']
    print(text)
    translation = translator.translate(source, target, text)
    print(translation)
    return jsonify({"output": translation})


@app.route('/documents/translate', methods=["POST"])
def get_DocxTranslated():
    dict = request.form
    source = dict['source']
    target = dict['target']
    project_id = dict['project_id']

    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"status": "Failed: File not found"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"status": "Failed: File name empty"})

    if file and allowed_file(file.filename):
        filename = file.filename

        # Save the file in local storage
        filepath = os.path.join(app.config['UPLOAD_FOLDER_INPUT'], filename).replace("\\", "/")
        file.save(os.path.join(filepath))

        token = DocReader.translateDocx(source, target, file)

        file_data = codecs.open(os.path.join(UPLOAD_FOLDER_TRANSLATED, token + ".docx").replace("\\", "/"), 'rb').read()
        response = make_response()
        response.headers['my-custom-header'] = '200'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response.headers['Content-Disposition'] = 'attachment; filename = "Translation.docx"'
        response.data = file_data
        return response

    else:
        return jsonify({"status": "Failed"})


# defining function to run on shutdown
def close_running_threads():
    path = glob.glob(os.path.join(UPLOAD_FOLDER_INPUT, "*.docx"))
    for f in path:
        os.remove(f)
    print("Files cleared from input folder")

    files = glob.glob(os.path.join(UPLOAD_FOLDER_TRANSLATED, "*.docx"))
    for f in files:
        os.remove(f)
    print("Files cleared from translated folder")


# Register the function to be called on exit
atexit.register(close_running_threads)

app.run(host="0.0.0.0")
