# Multi-platform Docker testing image for LUCA: Genesis to Cosmos (scorputer/3DGame)
FROM python:3.11-slim

LABEL maintainer="scorputer"
LABEL description="LUCA 3D Evolution Engine & Cross-Platform WebGL Server (Windows/Android/iOS/Linux)"

WORKDIR /app

# Copy source code, unit tests, and WebGL client
COPY src/ ./src/
COPY tests/ ./tests/
COPY web_client/ ./web_client/
COPY server.py ./server.py
COPY README.md ./README.md

# Run full regression suite during image build to guarantee auditable quality
RUN python3 -m unittest discover -s tests -p "test_*.py" -v

EXPOSE 8080

# Launch the cross-platform HTTP/WebSocket co-evolution server
CMD ["python3", "server.py", "--port", "8080"]
