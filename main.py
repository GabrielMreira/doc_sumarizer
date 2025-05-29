import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List, Any
import spacy

import read_doc as rd

rd.nlp_pt = spacy.load('pt_core_news_sm')

app = FastAPI(title="Document processing API",
              description="API for doc processing and extractition key words",
              version="0.1.0")

@app.post("/process_doc/", response_model=Dict[str, Any])
async def process_doc_endpoint(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

            text_extrated = rd.read_document(temp_file_path)

            if not text_extrated or text_extrated.startswith("Erro:"):
                raise HTTPException(status_code=400, detail=f"Error processing the file {text_extrated}")

            processed_tokens = rd.pre_process_text_with_pos(text_extrated)
            tuple_key_words = rd.extract_key_word(processed_tokens, 10)
            key_words = [{"word": w, "frequence": f} for w, f in tuple_key_words]
            extracted_entities = rd.extract_entities(text_extrated)

            result = {"file_name": file.filename,
                      "content_type": file.content_type,
                      "principal_key_words": key_words,
                      "detected_entities": extracted_entities}
            return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")