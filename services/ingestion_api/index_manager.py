from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import insert as pg_insert, JSONB
import json
from database import Base, engine
from models import Document, InvertedIndexTerm

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
                                set_={'doc_id': InvertedIndexTerm.doc_id.op('||')(cast(json.dumps([doc_id]), JSONB))})

        await session.execute(stmt)


async def search_idx(session : AsyncSession,query_str: str):
    query_terms = [term.lower() for term in query_str.split() if term.strip]
    if not query_terms:
        return []

    prob_docs_ids = None

    for term in query_terms:
        result = await session.execute(select(InvertedIndexTerm.doc_id).where(InvertedIndexTerm.term==term))
        term_doc_ids = result.scalar_one_or_none()

        if term_doc_ids is None:
            return []

        term_ids_set = set(term_doc_ids)
        if prob_docs_ids is None:
            prob_docs_ids = term_ids_set
        else:
            prob_docs_ids.intersection_update(term_ids_set)

    if prob_docs_ids is None:
        return []

    stms_docs = select(Document).where(Document.id.in_(prob_docs_ids))
    result_docs = await session.execute(stms_docs)
    finded_docs = result_docs.scalars().all()

    return [{
        "id": doc.id,
        "original_name": doc.original_name,
        "storage_path": doc.storage_path,
        "key_words": doc.key_words,
        "entities": doc.doc_entities
    } for doc in finded_docs]