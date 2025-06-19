import os.path
from uuid import uuid4

import read_doc as rd
import index_manager as im
import s3_utils


def process_new_doc(original_name : str, file_content : bytes) -> dict:
    _, original_extension = os.path.splitext(original_name)
    extension_unique_file_s3 = f"{uuid4()}{original_extension}"
    file_path_s3 = s3_utils.s3_upload(file_content ,extension_unique_file_s3)


    extracted_text = rd.read_document(file_path_s3)
    if not extracted_text or extracted_text.startswith("Erro:"):
        raise ValueError(f"Cannot read doc data: {original_name}")

    processed_tokens = rd.pre_process_text_with_pos(extracted_text)
    key_words_tuple = rd.extract_key_word(processed_tokens, top_n=15)
    doc_entities = rd.extract_entities(extracted_text)

    actual_id = im.generate_doc_id()
    im.add_doc_into_idx(doc_id=actual_id,
                        path_saved_file=file_path_s3,
                        key_words_freq=key_words_tuple,
                        entities=doc_entities)
    json_key_words = [{"word": w, "frequency": f}for w, f in key_words_tuple]
    result_service = {
        "doc_id":actual_id,
        "original_file_name":original_name,
        "key_words": json_key_words,
        "detected_entitites": doc_entities
    }
    return result_service

def search_doc(query_str : str):
    results = im.search_idx(query_str)
    return results