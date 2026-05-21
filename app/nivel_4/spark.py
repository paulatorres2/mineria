import gc
import os
import sys
import time
from pathlib import Path

import pandas as pd

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

PARQUET_PATH = Path(__file__).parent / "homicidios.parquet"

COLUMN_MAP = {
    "FECHA HECHO": "fecha_hecho",
    "COD_DEPTO": "cod_depto",
    "DEPARTAMENTO": "departamento",
    "COD_MUNI": "cod_muni",
    "MUNICIPIO": "municipio",
    "ZONA": "zona",
    "SEXO": "sexo",
    "ARMA MEDIO": "arma_medio",
    " MODALIDAD PRESUNTA": "modalidad_presunta",
    "SPOA_CARACTERIZACION": "spoa_caracterizacion",
    "CANTIDAD": "cantidad",
}


def _load_spark_df(spark):
    path = "file:///" + str(PARQUET_PATH).replace("\\", "/")
    df = spark.read.parquet(path)
    for old, new in COLUMN_MAP.items():
        df = df.withColumnRenamed(old, new)
    return df


def _load_pandas_df() -> pd.DataFrame:
    import duckdb
    path = str(PARQUET_PATH).replace("\\", "/")
    df = duckdb.connect().execute(f"SELECT * FROM read_parquet('{path}')").df()
    return df.rename(columns=COLUMN_MAP)



# ── SSE streaming generators ─────────────────────────────────────────────────

def _stream_spark(t0_total: float):
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import IntegerType, DoubleType
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import VectorAssembler
    from pyspark.ml.regression import GBTRegressor
    from pyspark.ml.evaluation import RegressionEvaluator

    # 1. Spark startup
    t0 = time.perf_counter()
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("homicidios_n4")
        .config("spark.driver.memory", "512m")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.execution.arrow.pyspark.enabled", "false")
        .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true")
        .config("spark.python.worker.faulthandler.enabled", "true")
        .getOrCreate()
    )
    t_startup = round(time.perf_counter() - t0, 3)
    yield {"phase": "startup", "t_startup": t_startup}

    try:
        # 2. Ingest & clean (lazy), then force cache fill
        df = _load_spark_df(spark)
        df = (
            df
            .withColumn("fecha_hecho", F.to_date("fecha_hecho"))
            .withColumn("cantidad", F.coalesce(F.col("cantidad").cast(IntegerType()), F.lit(1)))
            .filter(F.col("fecha_hecho").isNotNull())
            .withColumn("anio", F.year("fecha_hecho").cast(DoubleType()))
            .withColumn("mes", F.month("fecha_hecho").cast(DoubleType()))
        )
        df.cache()
        t0 = time.perf_counter()
        df.count()
        t_cache = round(time.perf_counter() - t0, 3)
        yield {"phase": "cache_fill", "t_cache": t_cache}

        # 3. GroupBy — Departamento / Año
        t0 = time.perf_counter()
        rows = (
            df.groupBy("departamento", "anio")
            .agg(F.sum("cantidad").alias("total"))
            .orderBy(F.desc("anio"), F.desc("total"))
            .collect()
        )
        t_depto = round(time.perf_counter() - t0, 3)
        yield {
            "phase": "por_departamento_anio",
            "rows": [{"departamento": r["departamento"], "anio": int(r["anio"]) if r["anio"] else None, "total": int(r["total"])} for r in rows],
            "tiempo": t_depto,
        }

        # 4. GroupBy — Arma / Zona top 10
        t0_spark = time.perf_counter()
        rows = (
            df.groupBy("arma_medio", "zona")
            .agg(F.sum("cantidad").alias("total"))
            .orderBy(F.desc("total"))
            .limit(10)
            .collect()
        )
        spark_seconds = round(time.perf_counter() - t0_spark, 3)
        yield {
            "phase": "arma_zona_top10",
            "rows": [{"arma_medio": r["arma_medio"], "zona": r["zona"], "total": int(r["total"])} for r in rows],
            "tiempo": spark_seconds,
        }

        # 5. GroupBy — Tendencia mensual
        t0 = time.perf_counter()
        rows = (
            df.groupBy("anio", "mes")
            .agg(F.sum("cantidad").alias("total"))
            .orderBy("anio", "mes")
            .collect()
        )
        t_tend = round(time.perf_counter() - t0, 3)
        yield {
            "phase": "tendencia_mensual",
            "rows": [{"anio": int(r["anio"]) if r["anio"] else None, "mes": int(r["mes"]) if r["mes"] else None, "total": int(r["total"])} for r in rows],
            "tiempo": t_tend,
        }

        # 6. GroupBy — Top municipios
        t0 = time.perf_counter()
        rows = (
            df.groupBy("municipio", "departamento")
            .agg(F.sum("cantidad").alias("total"))
            .orderBy(F.desc("total"))
            .limit(20)
            .collect()
        )
        t_muni = round(time.perf_counter() - t0, 3)
        yield {
            "phase": "top_municipios",
            "rows": [{"municipio": r["municipio"], "departamento": r["departamento"], "total": int(r["total"])} for r in rows],
            "tiempo": t_muni,
        }

        # 7. Benchmark Spark vs Pandas
        t0 = time.perf_counter()
        df_pandas = _load_pandas_df()
        t_pandas_load = round(time.perf_counter() - t0, 3)
        t0_pandas = time.perf_counter()
        _ = (
            df_pandas.assign(cantidad=pd.to_numeric(
                df_pandas["cantidad"], errors="coerce").fillna(1).astype(int))
            .groupby(["arma_medio", "zona"])["cantidad"].sum().nlargest(10)
        )
        pandas_seconds = round(time.perf_counter() - t0_pandas, 3)
        del df_pandas
        yield {"phase": "benchmark", "spark_seconds": spark_seconds, "pandas_seconds": pandas_seconds, "pandas_load": t_pandas_load}

        # 8. ML — Pronóstico mensual de homicidios (GBTRegressor MLlib)
        import math, shutil, tempfile
        import numpy as np

        t0 = time.perf_counter()

        # 8a. Agregar serie mensual con Spark (335k filas → ~280) y traer a Pandas
        monthly_spark = (
            df.groupBy("anio", "mes")
              .agg(F.sum("cantidad").alias("total"))
        )
        monthly_pdf = monthly_spark.toPandas()
        monthly_pdf["t_idx"] = (
            monthly_pdf["anio"].astype(int) * 100 + monthly_pdf["mes"].astype(int)
        )
        monthly_pdf = monthly_pdf.sort_values("t_idx").reset_index(drop=True)

        # 8b. Feature engineering en Pandas (~280 filas)
        feat_cols = ["lag_1", "lag_2", "lag_3", "lag_6", "lag_12", "mes_sin", "mes_cos", "t"]
        for lag in [1, 2, 3, 6, 12]:
            monthly_pdf[f"lag_{lag}"] = monthly_pdf["total"].shift(lag)
        t_min_val = int(monthly_pdf["t_idx"].min())
        monthly_pdf["mes_sin"] = np.sin(2 * math.pi * monthly_pdf["mes"].astype(float) / 12)
        monthly_pdf["mes_cos"] = np.cos(2 * math.pi * monthly_pdf["mes"].astype(float) / 12)
        monthly_pdf["t"]       = (monthly_pdf["t_idx"] - t_min_val).astype(float) / 100.0
        monthly_pdf["total"]   = monthly_pdf["total"].astype(float)
        monthly_pdf = monthly_pdf.dropna(subset=feat_cols).reset_index(drop=True)

        # Variables necesarias antes de liberar monthly_pdf
        historical   = [
            {"fecha": f"{int(r['anio'])}-{int(r['mes']):02d}", "total": int(r["total"])}
            for _, r in monthly_pdf.iterrows()
        ]
        split_t_idx = int(monthly_pdf["t_idx"].iloc[-24])
        lag_buffer  = monthly_pdf["total"].iloc[-12:].tolist()
        last_anio   = int(monthly_pdf["anio"].iloc[-1])
        last_mes    = int(monthly_pdf["mes"].iloc[-1])
        keep_cols   = feat_cols + ["total", "t_idx", "anio", "mes"]

        # 8c. Convertir a Spark via parquet temporal.
        #     spark.createDataFrame(pandas) serializa con Python workers → crash en Windows;
        #     spark.read.parquet() es JVM nativo → seguro.
        tmp_dir = tempfile.mkdtemp()
        try:
            tmp_monthly = os.path.join(tmp_dir, "monthly.parquet")
            monthly_pdf[keep_cols].to_parquet(tmp_monthly, index=False)
            del monthly_pdf
            monthly = spark.read.parquet("file:///" + tmp_monthly.replace("\\", "/"))
            monthly.cache()

            # 8d. Split temporal estricto — últimos 24 meses como test
            train_df = monthly.filter(F.col("t_idx") < split_t_idx)
            test_df  = monthly.filter(F.col("t_idx") >= split_t_idx)

            # 8e. Pipeline MLlib: VectorAssembler + GBTRegressor (JVM puro)
            assembler = VectorAssembler(
                inputCols=feat_cols, outputCol="features", handleInvalid="skip"
            )
            gbt = GBTRegressor(
                featuresCol="features", labelCol="total",
                maxIter=100, maxDepth=4, seed=42
            )
            pipeline = Pipeline(stages=[assembler, gbt])

            model       = pipeline.fit(train_df)
            predictions = model.transform(test_df)

            # 8f. Métricas con RegressionEvaluator
            rmse_eval = RegressionEvaluator(labelCol="total", predictionCol="prediction", metricName="rmse")
            mae_eval  = RegressionEvaluator(labelCol="total", predictionCol="prediction", metricName="mae")
            rmse = float(round(rmse_eval.evaluate(predictions), 1))
            mae  = float(round(mae_eval.evaluate(predictions), 1))

            pred_test_pdf = predictions.select("total", "prediction").toPandas()
            mape_arr = (
                (pred_test_pdf["total"] - pred_test_pdf["prediction"]).abs()
                / pred_test_pdf["total"].clip(lower=1)
            ) * 100
            mape = float(round(mape_arr.mean(), 2))
            del pred_test_pdf

            # 8g. Pronóstico recursivo a 3 meses.
            #     pd.DataFrame([row]).to_parquet + spark.read.parquet evita createDataFrame crash.
            forecast = []
            for step in range(1, 4):
                next_mes  = last_mes + step
                next_anio = last_anio
                while next_mes > 12:
                    next_mes  -= 12
                    next_anio += 1
                next_t_idx = next_anio * 100 + next_mes
                next_t     = float(next_t_idx - t_min_val) / 100.0
                row_data   = {
                    "lag_1":   lag_buffer[-1],
                    "lag_2":   lag_buffer[-2],
                    "lag_3":   lag_buffer[-3],
                    "lag_6":   lag_buffer[-6],
                    "lag_12":  lag_buffer[-12],
                    "mes_sin": float(np.sin(2 * math.pi * next_mes / 12)),
                    "mes_cos": float(np.cos(2 * math.pi * next_mes / 12)),
                    "t":       next_t,
                }
                tmp_fc = os.path.join(tmp_dir, f"fc_{step}.parquet")
                pd.DataFrame([row_data]).to_parquet(tmp_fc, index=False)
                fc_df    = spark.read.parquet("file:///" + tmp_fc.replace("\\", "/"))
                pred_val = max(0.0, float(model.transform(fc_df).collect()[0]["prediction"]))
                lag_buffer.append(pred_val)
                forecast.append({"fecha": f"{next_anio}-{next_mes:02d}", "total": round(pred_val)})

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        t_ml = round(time.perf_counter() - t0, 3)

        yield {
            "phase": "ml",
            "ml": {
                "available":    True,
                "rmse":         rmse,
                "mae":          mae,
                "mape":         mape,
                "n_estimators": 100,
                "features":     feat_cols,
                "historical":   historical,
                "forecast":     forecast,
            },
            "t_ml": t_ml,
        }

        gc.collect()
        yield {
            "phase": "done",
            "fases": {
                "spark_startup": t_startup, "cache_fill": t_cache,
                "groupby_depto": t_depto,  "groupby_arma": spark_seconds,
                "groupby_tend":  t_tend,   "groupby_muni": t_muni,
                "pandas_load":   t_pandas_load, "pandas_query": pandas_seconds,
                "ml_pipeline":   t_ml,
                "total":         round(time.perf_counter() - t0_total, 3),
            },
        }
    finally:
        spark.stop()


def _stream_pandas(t0_total: float):
    yield {"phase": "engine", "engine": "pandas-fallback"}

    t0 = time.perf_counter()
    df = _load_pandas_df()
    t_load = round(time.perf_counter() - t0, 3)
    yield {"phase": "parquet_load", "t_load": t_load}

    t0 = time.perf_counter()
    df["fecha_hecho"] = pd.to_datetime(
        df["fecha_hecho"], errors="coerce", utc=True)
    df = df[df["fecha_hecho"].notna()].copy()
    df["cantidad"] = pd.to_numeric(
        df["cantidad"], errors="coerce").fillna(1).astype(int)
    df["anio"] = df["fecha_hecho"].dt.year
    df["mes"] = df["fecha_hecho"].dt.month
    t_clean = round(time.perf_counter() - t0, 3)

    t0 = time.perf_counter()
    rows = (
        df.groupby(["departamento", "anio"])["cantidad"].sum()
        .reset_index().rename(columns={"cantidad": "total"})
        .sort_values(["anio", "total"], ascending=[False, False])
        .to_dict("records")
    )
    t_depto = round(time.perf_counter() - t0, 3)
    yield {"phase": "por_departamento_anio", "rows": [{"departamento": r["departamento"], "anio": int(r["anio"]), "total": int(r["total"])} for r in rows], "tiempo": t_depto}

    t0 = time.perf_counter()
    rows = (
        df.groupby(["arma_medio", "zona"])["cantidad"].sum()
        .reset_index().rename(columns={"cantidad": "total"})
        .nlargest(10, "total").to_dict("records")
    )
    pandas_seconds = round(time.perf_counter() - t0, 3)
    yield {"phase": "arma_zona_top10", "rows": [{"arma_medio": r["arma_medio"], "zona": r["zona"], "total": int(r["total"])} for r in rows], "tiempo": pandas_seconds}

    t0 = time.perf_counter()
    rows = (
        df.groupby(["anio", "mes"])["cantidad"].sum()
        .reset_index().rename(columns={"cantidad": "total"})
        .sort_values(["anio", "mes"]).to_dict("records")
    )
    t_tend = round(time.perf_counter() - t0, 3)
    yield {"phase": "tendencia_mensual", "rows": [{"anio": int(r["anio"]), "mes": int(r["mes"]), "total": int(r["total"])} for r in rows], "tiempo": t_tend}

    t0 = time.perf_counter()
    rows = (
        df.groupby(["municipio", "departamento"])["cantidad"].sum()
        .reset_index().rename(columns={"cantidad": "total"})
        .nlargest(20, "total").to_dict("records")
    )
    t_muni = round(time.perf_counter() - t0, 3)
    yield {"phase": "top_municipios", "rows": [{"municipio": r["municipio"], "departamento": r["departamento"], "total": int(r["total"])} for r in rows], "tiempo": t_muni}

    yield {"phase": "benchmark", "spark_seconds": None, "pandas_seconds": pandas_seconds}

    yield {"phase": "ml", "ml": {"available": False, "reason": "Java/PySpark no disponible en este entorno"}}

    t_total = round(time.perf_counter() - t0_total, 3)
    yield {
        "phase": "done",
        "fases": {
            "parquet_load":  t_load,   "limpieza":      t_clean,
            "groupby_depto": t_depto,  "groupby_arma":  pandas_seconds,
            "groupby_tend":  t_tend,   "groupby_muni":  t_muni,
            "total":         t_total,
        },
    }


def stream_pipeline():
    """Generator yielding phase dicts; the SSE route wraps each as a `data:` line."""
    t0_total = time.perf_counter()
    try:
        import pyspark  # noqa: F401
    except ImportError:
        yield from _stream_pandas(t0_total)
        return

    yield {"phase": "engine", "engine": "spark"}
    try:
        yield from _stream_spark(t0_total)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Spark failed, falling back to pandas: %s", exc)
        yield from _stream_pandas(t0_total)
