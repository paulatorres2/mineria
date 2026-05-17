import gc
import os

import duckdb
import pandas as pd
import requests

API_URL = "https://www.datos.gov.co/resource/m8fd-ahd9.json"

_conn: duckdb.DuckDBPyConnection | None = None


def _fetch_data() -> pd.DataFrame:
    resp = requests.get(API_URL, params={"$limit": "500000"}, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        raise ValueError(f"API returned unexpected format: {data}")
    return pd.DataFrame(data)


def _build_schema(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> None:
    # Register the raw DataFrame as a zero-copy view — no .copy() needed
    conn.register("_raw_df", df)

    # Materialise with type coercions; pandas ref released immediately after
    conn.execute("""
        CREATE OR REPLACE TABLE _raw AS
        SELECT
            TRY_CAST(fecha_hecho AS DATE)              AS fecha_hecho,
            COALESCE(TRY_CAST(cantidad AS INTEGER), 1) AS cantidad,
            cod_depto, departamento, cod_muni, municipio, zona,
            arma_medio,
            _modalidad_presunta,
            sexo,
            COALESCE(spoa_caracterizacion, 'SIN DATO') AS spoa_caracterizacion
        FROM _raw_df
        WHERE TRY_CAST(fecha_hecho AS DATE) IS NOT NULL
    """)
    conn.unregister("_raw_df")

    conn.execute("""
        CREATE OR REPLACE TABLE dim_tiempo AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY fecha_hecho) AS tiempo_id,
            fecha_hecho,
            YEAR(fecha_hecho)      AS anio,
            MONTH(fecha_hecho)     AS mes,
            QUARTER(fecha_hecho)   AS trimestre,
            DAYOFWEEK(fecha_hecho) AS dia_semana
        FROM (SELECT DISTINCT fecha_hecho FROM _raw)
    """)

    conn.execute("""
        CREATE OR REPLACE TABLE dim_ubicacion AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY cod_depto, cod_muni, zona) AS ubicacion_id,
            cod_depto, departamento, cod_muni, municipio, zona
        FROM (SELECT DISTINCT cod_depto, departamento, cod_muni, municipio, zona FROM _raw)
    """)

    conn.execute("""
        CREATE OR REPLACE TABLE dim_arma AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY arma_medio) AS arma_id,
            arma_medio
        FROM (SELECT DISTINCT arma_medio FROM _raw)
    """)

    conn.execute("""
        CREATE OR REPLACE TABLE dim_modalidad AS
        SELECT
            ROW_NUMBER() OVER (ORDER BY _modalidad_presunta, sexo, spoa_caracterizacion) AS modalidad_id,
            _modalidad_presunta AS modalidad_presunta,
            sexo,
            spoa_caracterizacion
        FROM (SELECT DISTINCT _modalidad_presunta, sexo, spoa_caracterizacion FROM _raw)
    """)

    # Fact table built entirely inside DuckDB — no pandas merges, no copies
    conn.execute("""
        CREATE OR REPLACE TABLE fact_homicidios AS
        SELECT
            dt.tiempo_id,
            du.ubicacion_id,
            da.arma_id,
            dm.modalidad_id,
            r.cantidad
        FROM _raw r
        JOIN dim_tiempo    dt ON r.fecha_hecho = dt.fecha_hecho
        JOIN dim_ubicacion du ON r.cod_depto   = du.cod_depto
                              AND r.cod_muni   = du.cod_muni
                              AND r.zona       = du.zona
        JOIN dim_arma      da ON r.arma_medio  = da.arma_medio
        JOIN dim_modalidad dm ON r._modalidad_presunta   = dm.modalidad_presunta
                              AND r.sexo                 = dm.sexo
                              AND r.spoa_caracterizacion = dm.spoa_caracterizacion
    """)

    conn.execute("DROP TABLE _raw")


def _md_conn() -> duckdb.DuckDBPyConnection:
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    if not token:
        raise RuntimeError(
            "MOTHERDUCK_TOKEN is not set.\n"
        )
    conn = duckdb.connect(f"md:?motherduck_token={token}")
    conn.execute("CREATE DATABASE IF NOT EXISTS homicidios")
    conn.execute("USE homicidios")
    return conn


def _tables_exist(conn: duckdb.DuckDBPyConnection) -> bool:
    names = {r[0] for r in conn.execute("SHOW TABLES").fetchall()}
    return "fact_homicidios" in names


def ensure_db() -> None:
    global _conn
    if _conn is not None:
        return
    if os.environ.get("MOTHERDUCK_TOKEN"):
        try:
            conn = _md_conn()
            if not _tables_exist(conn):
                df = _fetch_data()
                _build_schema(conn, df)
                del df
                gc.collect()
            _conn = conn
            return
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                "MotherDuck unavailable (%s) — falling back to in-memory DuckDB", exc
            )
    # Fallback: rebuild from API in-memory (slow first request, no persistence)
    df = _fetch_data()
    conn = duckdb.connect(":memory:")
    _build_schema(conn, df)
    del df
    gc.collect()
    _conn = conn


def _get_conn() -> duckdb.DuckDBPyConnection:
    assert _conn is not None, "Call ensure_db() before querying"
    return _conn


def query_por_departamento_anio() -> list[dict]:
    rows = _get_conn().execute("""
        SELECT u.departamento, t.anio, SUM(f.cantidad) AS total
        FROM fact_homicidios f
        JOIN dim_tiempo     t ON f.tiempo_id    = t.tiempo_id
        JOIN dim_ubicacion  u ON f.ubicacion_id = u.ubicacion_id
        GROUP BY u.departamento, t.anio
        ORDER BY t.anio DESC, total DESC
    """).fetchall()
    return [{"departamento": r[0], "anio": r[1], "total": r[2]} for r in rows]


def query_arma_zona_top10() -> list[dict]:
    rows = _get_conn().execute("""
        SELECT a.arma_medio, u.zona, SUM(f.cantidad) AS total
        FROM fact_homicidios f
        JOIN dim_arma       a ON f.arma_id      = a.arma_id
        JOIN dim_ubicacion  u ON f.ubicacion_id = u.ubicacion_id
        GROUP BY a.arma_medio, u.zona
        ORDER BY total DESC
        LIMIT 10
    """).fetchall()
    return [{"arma_medio": r[0], "zona": r[1], "total": r[2]} for r in rows]


def query_tendencia_mensual() -> list[dict]:
    rows = _get_conn().execute("""
        SELECT t.anio, t.mes, SUM(f.cantidad) AS total
        FROM fact_homicidios f
        JOIN dim_tiempo t ON f.tiempo_id = t.tiempo_id
        WHERE t.anio IS NOT NULL AND t.mes IS NOT NULL
        GROUP BY t.anio, t.mes
        ORDER BY t.anio ASC, t.mes ASC
    """).fetchall()
    return [{"anio": r[0], "mes": r[1], "total": r[2]} for r in rows]


def query_sexo_modalidad_top15() -> list[dict]:
    rows = _get_conn().execute("""
        SELECT m.sexo, m.modalidad_presunta, SUM(f.cantidad) AS total
        FROM fact_homicidios f
        JOIN dim_modalidad m ON f.modalidad_id = m.modalidad_id
        GROUP BY m.sexo, m.modalidad_presunta
        ORDER BY total DESC
        LIMIT 15
    """).fetchall()
    return [{"sexo": r[0], "modalidad_presunta": r[1], "total": r[2]} for r in rows]
