from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
import json

from watchfiles import awatch

from .database import Base, engine
from .models import Document, InvertedIndexTerm

async def create_tables_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_doc_into_idx(session: AsyncSession, doc_id : str, original_file_name : str, storage_path: str, key_words_freq: list, entities : dict):
    key_word_list = [{"word": w, "frequence": f} for w, f in key_words_freq]

    new_doc = Document(id=doc_id,
                       original_name=original_file_name,
                       storage_path= storage_path,
                       doc_entities= entities,
                       key_words= key_word_list)

    session.add(new_doc)

    update_terms = set(p for p, _ in key_words_freq)
    for list_entities_text in entities.values():
        for text_entitie in list_entities_text:
            update_terms.add(text_entitie.lower())

    for term in update_terms:
        stmt = pg_insert(InvertedIndexTerm).values(
            term=term,
            doc_id=[doc_id]
        ).on_conflict_do_update(index_elements=['term'],
                                set_={'doc_id': InvertedIndexTerm.doc_id.op('||')(json.dumps([doc_id]))})

        await session.execute(stmt)


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
