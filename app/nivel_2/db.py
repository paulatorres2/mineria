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
    # ── Preprocess in pandas ──────────────────────────────────────────────────
    raw = df.copy()
    raw["fecha_hecho"] = pd.to_datetime(raw["fecha_hecho"], errors="coerce").dt.date
    raw["cantidad"] = pd.to_numeric(raw["cantidad"], errors="coerce").fillna(1).astype(int)
    if "spoa_caracterizacion" not in raw.columns:
        raw["spoa_caracterizacion"] = "SIN DATO"
    raw["spoa_caracterizacion"] = raw["spoa_caracterizacion"].fillna("SIN DATO")
    raw = raw.dropna(subset=["fecha_hecho"])

    # ── dim_tiempo ────────────────────────────────────────────────────────────
    dt = (
        raw[["fecha_hecho"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .assign(
            tiempo_id=lambda x: range(1, len(x) + 1),
            anio=lambda x: pd.to_datetime(x["fecha_hecho"]).dt.year,
            mes=lambda x: pd.to_datetime(x["fecha_hecho"]).dt.month,
            trimestre=lambda x: pd.to_datetime(x["fecha_hecho"]).dt.quarter,
            dia_semana=lambda x: pd.to_datetime(x["fecha_hecho"]).dt.dayofweek,
        )
    )
    conn.register("_dt", dt)
    conn.execute("CREATE OR REPLACE TABLE dim_tiempo AS SELECT * FROM _dt")
    conn.unregister("_dt")

    # ── dim_ubicacion ─────────────────────────────────────────────────────────
    du = (
        raw[["cod_depto", "departamento", "cod_muni", "municipio", "zona"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .assign(ubicacion_id=lambda x: range(1, len(x) + 1))
    )
    du = du[["ubicacion_id", "cod_depto", "departamento", "cod_muni", "municipio", "zona"]]
    conn.register("_du", du)
    conn.execute("CREATE OR REPLACE TABLE dim_ubicacion AS SELECT * FROM _du")
    conn.unregister("_du")

    # ── dim_arma ──────────────────────────────────────────────────────────────
    da = (
        raw[["arma_medio"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .assign(arma_id=lambda x: range(1, len(x) + 1))
    )
    da = da[["arma_id", "arma_medio"]]
    conn.register("_da", da)
    conn.execute("CREATE OR REPLACE TABLE dim_arma AS SELECT * FROM _da")
    conn.unregister("_da")

    # ── dim_modalidad ─────────────────────────────────────────────────────────
    dm = (
        raw[["_modalidad_presunta", "sexo", "spoa_caracterizacion"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .rename(columns={"_modalidad_presunta": "modalidad_presunta"})
        .assign(modalidad_id=lambda x: range(1, len(x) + 1))
    )
    dm = dm[["modalidad_id", "modalidad_presunta", "sexo", "spoa_caracterizacion"]]
    conn.register("_dm", dm)
    conn.execute("CREATE OR REPLACE TABLE dim_modalidad AS SELECT * FROM _dm")
    conn.unregister("_dm")

    # ── fact_homicidios (built via pandas merges, then loaded into DuckDB) ────
    fact = (
        raw
        .merge(dt[["tiempo_id", "fecha_hecho"]], on="fecha_hecho")
        .merge(du[["ubicacion_id", "cod_depto", "cod_muni", "zona"]],
               on=["cod_depto", "cod_muni", "zona"])
        .merge(da[["arma_id", "arma_medio"]], on="arma_medio")
        .merge(
            dm[["modalidad_id", "modalidad_presunta", "sexo", "spoa_caracterizacion"]].rename(
                columns={"modalidad_presunta": "_modalidad_presunta"}
            ),
            on=["_modalidad_presunta", "sexo", "spoa_caracterizacion"],
        )
    )[["tiempo_id", "ubicacion_id", "arma_id", "modalidad_id", "cantidad"]]

    conn.register("_fact", fact)
    conn.execute("CREATE OR REPLACE TABLE fact_homicidios AS SELECT * FROM _fact")
    conn.unregister("_fact")


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
