from typing import Optional
import os
import asyncpg
from dotenv import load_dotenv


DOTENV_PATH = '/root/.env'
load_dotenv(DOTENV_PATH)


async def find_data_in_db(input_phrase: str) -> Optional[list]:
    '''Функция осуществлять поиск фраз в базе данных и возвращает найденный результат'''
    connection = await asyncpg.connect(user=os.getenv("USER"), \
        password=os.getenv("PASSWORD"), database=os.getenv("DB_NAME"), host=os.getenv("HOST"))
    
    sql_query = '''SELECT sr.url, sr.result_header, sr.result_body
                   FROM search_results sr
                   JOIN phrases p ON sr.fk_phrase_id = p.phrase_id
                   WHERE p.phrase = $1;'''
    try:
        data = await connection.fetch(sql_query, input_phrase)
        return data if data else None

    except Exception as err:
        print("Произошла ошибка при поиске в базе данных: ", err)

    finally:
        await connection.close()


async def add_new_example(target_phrase: str, parsing_result: list[tuple[str, tuple]]) -> None:
    '''Функция добавляет результат поиска по фразе в базу данных в случае, если таковые в базе данных отсутсвуют'''
    connection = await asyncpg.connect(user=os.getenv("USER"), \
        password=os.getenv("PASSWORD"), database=os.getenv("DB_NAME"), host=os.getenv("HOST"))
    
    try:
        phrase_ref = await connection.fetchrow(
            "INSERT INTO phrases (phrase) VALUES ($1) RETURNING phrase_id", target_phrase
            )
        phrase_ref = phrase_ref["phrase_id"]
        
        sql_query_for_results = '''INSERT INTO search_results (fk_phrase_id, URL, result_header, result_body)
                                       VALUES ($1, $2, $3, $4);'''
        
        for URL, results in parsing_result:
            await connection.execute(sql_query_for_results, phrase_ref, URL, results[0], results[1])

    except Exception as err:
        print("Произошла ошибка при обновлении базы данных: ", err)

    finally:
        await connection.close()
