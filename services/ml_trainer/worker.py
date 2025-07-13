import asyncio
import os
import spacy
from sqlalchemy.future import select
from sqlalchemy import delete
from sklearn.feature_extraction.text import TfidfVectorizer

from database import AsyncSessionLocal, engine, Base
from models import Document, TfidScore
import read_doc as rd

rd.SPACY_MODEL_PT = spacy.load('pt_core_news_sm')

TRAIN_INTERVAL = int(os.getenv("TRAINING_INTERVAL", 3600))

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def calc_save_tfid():
    processed_docs = []
    docs_id = []

    async with AsyncSessionLocal() as session:
        stmt = select(Document.id, Document.storage_path)
        result = await session.execute(stmt)
        db_docs = result.all()

        if not db_docs:
            return

        for doc_id, storage_path in db_docs:
            text = rd.read_document(storage_path)
            if text and not text.startswith("Erro:"):
                tokens = rd.pre_process_text_with_pos(text)
                processed_docs.append(" ".join(tokens))
                docs_id.append(doc_id)

        if not processed_docs:
            return

        vectorizer = TfidfVectorizer(max_features=1000)
        tfid_matrix = vectorizer.fit_transform(processed_docs)
        feature_names = vectorizer.get_feature_names_out()

        await session.execute(delete(TfidScore))

        for doc_index, doc_id in enumerate(docs_id):
            for term_idx, score in zip(tfid_matrix[doc_index].indices, tfid_matrix[doc_index].data):
                if score > 0:
                    term = feature_names[term_idx]
                    new_score = TfidScore(doc_id=doc_id, term=term, score=float(score))
                    session.add(new_score)

        await session.commit()

async def main():
    await create_tables()

    while True:
        try:
            await calc_save_tfid()
        except Exception as e:
            print(f"Error processing doc: {str(e)}")

        await asyncio.sleep(TRAIN_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())