import os
import re
import uuid
import time

from transformers import MarianMTModel, MarianTokenizer
from docx import Document

UPLOAD_FOLDER_TRANSLATED = 'FileStorage_Translated'


def translat(src_text):
    print("\t " + "INPUT ::: " + str(src_text))
    time1 = time.time()
    translated = model.generate(**tokenizer.prepare_translation_batch(src_text))
    tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    print("\t " + "OUTPUT ::: " + str(tgt_text))
    time2 = time.time()
    duration = (time2 - time1) * 1000.0
    return tgt_text, duration


def translateDocx(source, target, file):
    start_time = time.time()
    global model_name
    global tokenizer
    global model
    print("Initiating translation....")
    # if source == 'en' and target == 'de':
    #     model_name = 'Helsinki-NLP/opus-mt-en-de'
    # if source == 'de' and target == 'en':
    #     model_name = 'Helsinki-NLP/opus-mt-de-en'
    model_name = 'Helsinki-NLP/opus-mt-' + source + '-' + target

    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    doc = Document(file)
    for p in doc.paragraphs:
        inline = p.runs
        for i in range(len(inline)):
            text = inline[i].text
            textsL = [text]
            textsL = filter(lambda x: not re.match(r'^\s*$', x), textsL)
            for text_value in textsL:
                textElem = [text_value]
                translationList, duration = translat(textElem)
                for translatedE in translationList:
                    text = text.replace(text_value, translatedE)
                    inline[i].text = text

    end_time = time.time()
    duration = (start_time - end_time) * 1000.0
    print("Translation finished.....")
    print('Total translate took {:.3f} ms'.format(duration))
    token = str(uuid.uuid4())
    doc.save(os.path.join(UPLOAD_FOLDER_TRANSLATED, token + ".docx"))

    return token
