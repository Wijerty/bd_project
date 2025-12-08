# Use the official PostgreSQL image
FROM postgres:15

# Set environment variables
ENV POSTGRES_DB=antifraud_p2p
ENV POSTGRES_USER=antifraud_user
ENV POSTGRES_PASSWORD=antifraud_pass

# Copy the enhanced schema file to the initialization directory
COPY enhanced_schema.sql /docker-entrypoint-initdb.d/

# Expose the PostgreSQL port
EXPOSE 5432

# Add a health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD pg_isready -U antifraud_user -d antifraud_p2p