import os.path
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
import read_doc as rd
import index_manager as im
import s3_utils


async def process_new_doc(session: AsyncSession, original_name : str, file_content : bytes) -> dict:
    _, original_extension = os.path.splitext(original_name)
    extension_unique_file_s3 = f"{uuid4()}{original_extension}"
    file_path_s3 = s3_utils.s3_upload(file_content, extension_unique_file_s3)


    extracted_text = rd.read_document(file_path_s3)
    if not extracted_text or extracted_text.startswith("Erro:"):
        raise ValueError(f"Cannot read doc data: {original_name}")

    processed_tokens = rd.pre_process_text_with_pos(extracted_text)
    key_words_tuple = rd.extract_key_word(processed_tokens, top_n=15)
    doc_entities = rd.extract_entities(extracted_text)

    actual_id = f"doc_{uuid4()}"
    await im.add_doc_into_idx(session=session,
                              doc_id=actual_id,
                              original_file_name=original_name,
                              storage_path=file_path_s3,
                              key_words_freq=key_words_tuple,
                              entities=doc_entities)

    await session.commit()
    return {"doc_id": actual_id, "status": "processed"}

async def search_doc(session: AsyncSession,query_str : str):
    results = await im.search_idx(session, query_str)
    return results