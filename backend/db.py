"""
PostgreSQL Centralized Database Manager with Failsafe Cache Fallback.
Provides unified database storage for predictions, analytics, optimization, and operational logs.
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("railway_db")

# PostgreSQL connection parameters with sensible defaults
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
PG_DB   = os.getenv("POSTGRES_DB", "railway_noc_db")

_pg_connection = None
_in_memory_cache = {
    "predictions": [],
    "optimizations": [],
    "logs": []
}

def get_db_connection():
    global _pg_connection
    try:
        import psycopg2
        if _pg_connection is None or _pg_connection.closed != 0:
            _pg_connection = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=PG_PASS,
                dbname=PG_DB,
                connect_timeout=3
            )
            _pg_connection.autocommit = True
        return _pg_connection
    except Exception as e:
        logger.warning(f"PostgreSQL unavailable ({e}). System operating in Failsafe Cache Mode.")
        return None

def init_db():
    conn = get_db_connection()
    if conn is None:
        logger.info("Using Failsafe In-Memory Cache for database layer.")
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id SERIAL PRIMARY KEY,
                    train_type VARCHAR(50),
                    current_station VARCHAR(50),
                    next_station VARCHAR(50),
                    speed INT,
                    current_delay INT,
                    weather VARCHAR(50),
                    predicted_delay FLOAT,
                    delay_status VARCHAR(50),
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS optimization_history (
                    id SERIAL PRIMARY KEY,
                    current_decision TEXT,
                    optimized_decision TEXT,
                    expected_time_saved_min INT,
                    expected_throughput_gain_pct FLOAT,
                    conflict_probability_pct FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        logger.info("PostgreSQL database schemas verified.")
        return True
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL tables: {e}")
        return False

def save_prediction(data: dict):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO prediction_history (
                        train_type, current_station, next_station, speed, current_delay,
                        weather, predicted_delay, delay_status, recommendations
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    data.get("train_type", ""),
                    data.get("current_station", ""),
                    data.get("next_station", ""),
                    data.get("speed", 0),
                    data.get("current_delay", 0),
                    data.get("weather", ""),
                    data.get("predicted_delay", 0.0),
                    data.get("delay_status", "ON TIME"),
                    json.dumps(data.get("recommendations", []))
                ))
            return True
        except Exception as e:
            logger.error(f"PostgreSQL insert failed: {e}")
            
    # Failsafe fallback cache
    _in_memory_cache["predictions"].append({
        **data,
        "timestamp": datetime.now().isoformat()
    })
    return True

def save_optimization(data: dict):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO optimization_history (
                        current_decision, optimized_decision, expected_time_saved_min,
                        expected_throughput_gain_pct, conflict_probability_pct
                    ) VALUES (%s, %s, %s, %s, %s);
                """, (
                    data.get("current_decision", ""),
                    data.get("optimized_decision", ""),
                    data.get("expected_time_saved_min", 0),
                    data.get("expected_throughput_gain_pct", 0.0),
                    data.get("conflict_probability_pct", 0.0)
                ))
            return True
        except Exception as e:
            logger.error(f"PostgreSQL insert optimization failed: {e}")
            
    _in_memory_cache["optimizations"].append({
        **data,
        "timestamp": datetime.now().isoformat()
    })
    return True

def get_prediction_logs(limit=50):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT train_type, current_station, next_station, speed, current_delay, weather, predicted_delay, delay_status, recommendations FROM prediction_history ORDER BY id DESC LIMIT %s;", (limit,))
                rows = cur.fetchall()
                return [{
                    "train_type": r[0], "current_station": r[1], "next_station": r[2],
                    "speed": r[3], "current_delay": r[4], "weather": r[5],
                    "predicted_delay": r[6], "delay_status": r[7],
                    "recommendations": json.loads(r[8]) if r[8] else []
                } for r in rows]
        except Exception as e:
            logger.error(f"Error reading prediction logs: {e}")

    return _in_memory_cache["predictions"][-limit:]
