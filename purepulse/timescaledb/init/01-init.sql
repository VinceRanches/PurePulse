SELECT 'CREATE DATABASE purepulse OWNER purepulse'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'purepulse')\gexec

\c purepulse
CREATE EXTENSION IF NOT EXISTS timescaledb;