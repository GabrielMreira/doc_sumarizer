import os
import json

save_doc_path = "save_documents"
INVERTED_IDX_FILE = "indice_invertido.json"
DOC_METADATA_FILE = "documentos_metadados.json"

inverted_idx = {}
doc_metadata = {}
next_doc_id = 1

os.makedirs(save_doc_path, exist_ok=True)

def load_persisted_data():
    global inverted_idx, doc_metadata, next_doc_id
    try:
        if os.path.exists(INVERTED_IDX_FILE):
            with open(INVERTED_IDX_FILE, "r") as f:
                data_idx_json = json.load(f)
                inverted_idx = {term: set(doc_ids) for term, doc_ids in data_idx_json.items()}
                print("Inverted index loaded")
        else:
            print("Inverted index file not fount, initializing with empty index")

        if os.path.exists(DOC_METADATA_FILE):
            with open(DOC_METADATA_FILE, "r") as f:
                docs_metadata = json.load(f)
            print("Doc metadata loaded")

            if docs_metadata:
                numeric_ids = [int(doc_id.split('_')[1]) for doc_id in docs_metadata.keys() if doc_id.startswith("doc_")]
                if numeric_ids:
                    next_doc_id = max(numeric_ids) + 1
                else:
                    next_doc_id = 1
        else:
            print("Metadata file not fount, initializing with empty metadata")

    except Exception as e:
        print(f"Erro load persisted data: {str(e)}")
        inverted_idx = {}
        doc_metadata = {}
        next_doc_id = 1

def save_persisted_data():
    global inverted_idx, doc_metadata
    try:
        save_idx = {term: set(doc_ids) for term, doc_ids in inverted_idx.items()}
        with open(INVERTED_IDX_FILE, "w") as f:
            json.dump(save_idx, f, ident=2)

        with open(DOC_METADATA_FILE, "w") as f:
            json.dump(doc_metadata, f, ident=2)
    except Exception as e:
        print(f"Erro saving persisted data: {str(e)}")

def generate_doc_id():
    global next_doc_id
    generated_id = f"doc_{next_doc_id}"
    next_doc_id = next_doc_id + 1
    return generated_id

def add_doc_into_idx(doc_id, path_saved_file, key_words_freq, entities):
    global inverted_idx, doc_metadata
    list_key_words = [word for word, freq in key_words_freq]

    doc_metadata[doc_id] = {
        "server_path": path_saved_file,
        "key_words": list_key_words,
        "entidades": entities
    }

    for word, _ in key_words_freq:
        term = word.lower()
        if term not in inverted_idx:
            inverted_idx[term] = set()
        inverted_idx[term].add(doc_id)

    for entitie_type, list_entitie_text in entities.items():
        for entitie_text in list_entitie_text:
            term = entitie_text.lower()
            if term not in inverted_idx:
                inverted_idx[term] = set()
            inverted_idx[term].add(doc_id)

    save_persisted_data()

def search_idx(query_str):
    global inverted_idx, doc_metadata
    query_terms = [term.lower() for term in query_str.split() if term.strip]
    if not query_terms:
        return []

    docs_per_term = []
    for term in query_terms:
        if term in inverted_idx:
            docs_per_term.append(inverted_idx[term])

    if not docs_per_term:
        return []

    correspond_docs_id = docs_per_term[0]
    for i in range(1, len(docs_per_term)):
        correspond_docs_id = correspond_docs_id.intersection(docs_per_term[i])

    result = []
    for doc_id in correspond_docs_id:
        if doc_id in doc_metadata:
            meta = doc_metadata[doc_id].copy()
            meta['id'] = doc_id
            result.append(meta)

    return result
