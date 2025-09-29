-- Create readonly_user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'readonly_user'
   ) THEN
      CREATE ROLE readonly_user LOGIN PASSWORD 'TS4!Tm5#=a8i';
   END IF;
END
$do$;

-- Ensure readonly_user can connect to the database
GRANT CONNECT ON DATABASE cohostrs TO readonly_user;

-- Ensure access to the public schema
GRANT USAGE ON SCHEMA public TO readonly_user;

-- Allow read-only access to existing tables and sequences
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO readonly_user;

-- Ensure new tables/sequences also get SELECT privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON SEQUENCES TO readonly_user;

-- Allow access to system metadata for schema and type inspection
GRANT USAGE ON SCHEMA information_schema TO readonly_user;
GRANT USAGE ON SCHEMA pg_catalog TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA information_schema TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO readonly_user;
