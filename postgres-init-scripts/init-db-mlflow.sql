-- init-db-mlflow.sql
DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_database WHERE datname = 'mlflow_db'
    ) THEN
        CREATE DATABASE mlflow_db;
    END IF;
END
$$;