import os
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List, Any
import spacy
import read_doc as rd
import services
import index_manager as im

rd.nlp_pt = spacy.load('pt_core_news_sm')

@asynccontextmanager
async def lifespan_manager(app : FastAPI):
    im.load_persisted_data()
    yield

app = FastAPI(title="Document processing API",
              description="API for doc processing and extractition key words",
              version="0.1.0",
              lifespan=lifespan_manager)


@app.post("/process_doc/", response_model=Dict[str, Any])
async def process_doc_endpoint(file: UploadFile = File(...)):
    try:
        file_content = await file.read()

        processed_result = services.process_new_doc(original_name=file.filename,
                                                  file_content=file_content)
        return processed_result
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        if file:
            await file.close()

@app.get("/buscar/", response_model=List[Dict[str, Any]])
async def get_docs_endpoint(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Search param requested")

    try:
        results = services.search_doc(q)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro searching: {str(e)}")
