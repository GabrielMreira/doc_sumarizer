from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List, Any
import spacy
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import read_doc as rd
import services
import index_manager as im
from database import get_db

rd.nlp_pt = spacy.load('pt_core_news_sm')

@asynccontextmanager
async def lifespan_manager(app : FastAPI):
    await im.create_tables_db()
    yield

app = FastAPI(title="Document processing API",
              description="API for doc processing and extractition key words",
              version="0.1.0",
              lifespan=lifespan_manager)


@app.post("/process_doc/", response_model=Dict[str, Any])
async def process_doc_endpoint(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        file_content = await file.read()

        processed_result = await services.process_new_doc(session=db,
                                                          original_name=file.filename,
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
async def get_docs_endpoint(q: str, db: AsyncSession = Depends(get_db)):
    if not q:
        raise HTTPException(status_code=400, detail="Search param requested")

    try:
        results = await services.search_doc(db, q)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro searching: {str(e)}")
