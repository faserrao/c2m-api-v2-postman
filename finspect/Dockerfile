FROM python:3.9-slim

# Install libmagic
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml setup.py README.md LICENSE ./
COPY finspect/ ./finspect/

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 finspect && \
    chown -R finspect:finspect /app

USER finspect

# Set entrypoint
ENTRYPOINT ["finspect"]
CMD ["--help"]