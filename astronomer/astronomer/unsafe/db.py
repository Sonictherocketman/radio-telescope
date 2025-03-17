import sqlite3

from . import settings


CREATE_TASK_TABLE_SCRIPT = """
    CREATE TABLE IF NOT EXISTS "task" (
        id VARCHAR(12) DEFAULT NULL,
        start_at TIMESTAMP DEFAULT NULL,
        end_at TIMESTAMP DEFAULT NULL,
        frequency NUMERIC DEFAULT NULL,
        sample_rate NUMERIC DEFAULT NULL,
        sample_size NUMERIC DEFAULT NULL,
        ppm NUMERIC DEFAULT NULL,
        gain NUMERIC DEFAULT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
"""
CREATE_TELESCOPE_TABLE_SCRIPT = """
    CREATE TABLE IF NOT EXISTS "telescope" (
        id INTEGER DEFAULT NULL,
        name VARCHAR(256) DEFAULT NULL,
        latitude NUMERIC DEFAULT NULL,
        longitude NUMERIC DEFAULT NULL,
        elevation NUMERIC DEFAULT NULL
    );
"""

# Found via: https://kerkour.com/sqlite-for-servers
SETUP_DATABASE_SCRIPT = """
    PRAGMA journal_mode = WAL;
    PRAGMA busy_timeout = 5000;
    PRAGMA synchronous = NORMAL;
    PRAGMA cache_size = 1000000000;
    PRAGMA foreign_keys = true;
    PRAGMA temp_store = memory;
"""


SETUP_SCRIPTS = (
    SETUP_DATABASE_SCRIPT,
    CREATE_TASK_TABLE_SCRIPT,
    CREATE_TELESCOPE_TABLE_SCRIPT,
)


def setup_and_connect():
    connection = sqlite3.connect(settings.DATABASE_LOCATION)
    connection.row_factory = sqlite3.Row
    with connection as cursor:
        for script in SETUP_SCRIPTS:
            cursor.executescript(script)
    return connection


def truncate_tables(cursor):
    cursor.executescript("""
        BEGIN;
        DELETE FROM task;
        DELETE FROM telescope;
        END;
    """)


def insert_telescope(telescope, cursor):
    cursor.execute("""
        INSERT INTO telescope (
            id,
            name,
            latitude,
            longitude,
            elevation
        ) VALUES(
            ?,
            ?,
            ?,
            ?,
            ?
        )
    """, (
        telescope['id'],
        telescope['name'],
        telescope['latitude'],
        telescope['longitude'],
        telescope['elevation'],
    ))


def list_active_tasks(cursor, now):
    return cursor.execute("""
        SELECT * FROM task
        WHERE
            ? >= start_at
            AND ? <= end_at
        ;
    """, (now.isoformat(), now.isoformat()))


def insert_task(task, cursor):
    return cursor.execute("""
        INSERT INTO task (
            id,
            start_at,
            end_at,
            frequency,
            sample_rate,
            sample_size,
            ppm,
            gain
        ) VALUES(
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
    """, (
        task['id'],
        task['start_at'],
        task['end_at'],
        task['frequency'],
        task['sample_rate'],
        task['sample_size'],
        task['ppm'],
        task['gain'],
    ))


def update_task(task, cursor):
    return cursor.execute("""
        UPDATE task
        SET start_at = ?,
            end_at = ?,
            frequency = ?,
            sample_rate = ?,
            sample_size = ?,
            ppm = ?,
            gain = ?
        WHERE id = ?
    """, (
        task['start_at'],
        task['end_at'],
        task['frequency'],
        task['sample_rate'],
        task['sample_size'],
        task['ppm'],
        task['gain'],
        task['id'],
    ))


def delete_task(task, cursor):
    return cursor.execute("""
        DELETE task WHERE id = ?
    """, (
        task['id'],
    ))
