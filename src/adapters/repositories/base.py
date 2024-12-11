from adapters.connector import get_connection
from typing import Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    def execute(self, role, query: str, params: Optional[Tuple[Any, ...]] = None) -> None:
        with get_connection(role) as conn:
            with conn.cursor() as cursor:
                logger.info(f"Executing query: {query} with params: {params}")
                cursor.execute(query, params)
                conn.commit()

    def executemany(self, role, query: str, params: List[Tuple[Any, ...]]) -> None:
        with get_connection(role) as conn:
            with conn.cursor() as cursor:
                logger.info(f"Executing batch query: {query} with params: {params}")
                cursor.executemany(query, params)
                conn.commit()

    def fetchall(
        self, role, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> List[Tuple[Any, ...]]:
        with get_connection(role) as conn:
            with conn.cursor() as cursor:
                logger.info(
                    f"Fetching all rows with query: {query} and params: {params}"
                )
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                try:
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                except:
                    logger.info(f"Nothing in return of fetchall")
                    return None
    def fetchone(
        self, role, query: str, params: Optional[Tuple[Any, ...]] = None
    ) -> Optional[Tuple[Any, ...]]:
        with get_connection(role) as conn:
            with conn.cursor() as cursor:
                logger.info(
                    f"Fetching one row with query: {query} and params: {params}"
                )
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                try:
                    result = dict(zip(columns, cursor.fetchone()))
                    conn.commit()
                    return result
                except:
                    logger.info(f"Nothing in return of fetchone")
                    return None
