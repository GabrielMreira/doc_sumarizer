import tempfile
import PyPDF2
import docx
import os
from collections import Counter
import re
import s3_utils

nlp_pt = {}

def extract_entities(text):
    print("Extracting named entities")
    doc = nlp_pt(text)
    entities = {}

    for ent in doc.ents:
        type = ent.label_
        entity_text = ent.text.strip()

        if type not in entities:
            entities[type] = []

        if entity_text.lower() not in [e.lower() for e in entities[type]]:
            entities[type].append(entity_text)

    return entities

def extract_key_word(tokens, top_n=10):
    if not tokens:
        return []

    print(f"Extractiong the {top_n} key words most frequently")
    frequence = Counter(tokens)

    key_words = frequence.most_common(top_n)
    return key_words

def pre_process_text_with_pos(text, allowed_classes = ['NOUN', 'PROPN', 'ADJ']):
    print(f"Initializing pre process")

    clean_text = re.sub(r'\s+', ' ', text).strip()

    doc = nlp_pt(clean_text)
    clean_tokens = []
    for token in doc:
        if ((not token.is_stop) and (not token.is_punct)
                and token.is_alpha and token.pos_ in allowed_classes):
            clean_tokens.append(token.lemma_.lower())

    print(f"Pre processing finished")
    return clean_tokens

def read_document(file_path : str):
    if file_path.startswith("s3://"):
        buckec_name, key = file_path.replace("s3://", "").split("/", 1)
        _,original_extension = os.path.splitext(file_path)

        with tempfile.NamedTemporaryFile(suffix=original_extension) as tmp_file:
            s3_utils.read_from_s3(origin_file_name=key, temporary_file_path=tmp_file.name)
            return _read_document_local(tmp_file.name)
    else:
        _read_document_local(file_path)


def _read_document_local(file_path):
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension == ".pdf":
        print(f"Detecting pdf file")
        return read_pdf(file_path)
    elif extension == ".docx":
        print(f"Detecting docx file")
        return read_docx(file_path)
    else:
        print(f"File format not supported")
        return None

def read_pdf(file_path):
    complete_text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            pages = len(reader.pages)
            print(f"Reading {pages} pages from pdf file")

            for i in range (pages):
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    complete_text += page_text + "\n"
        return complete_text.strip()
    except FileNotFoundError:
        return f"File not found in path {file_path}"
    except Exception as e:
        return f"Error reading the file {file_path}: {e}"


def read_docx(file_path):
    complete_text = ""
    try:
        document = docx.Document(file_path)
        print(f"Reading paragraphs from docx file")

        for paragraph in document.paragraphs:
            complete_text += paragraph.text
        return complete_text.strip()
    except FileNotFoundError:
        return f"File not found in path {file_path}"
    except Exception as e:
        return f"Error reading the file {file_path}: {e}"
