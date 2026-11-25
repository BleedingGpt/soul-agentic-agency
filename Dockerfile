FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY config.py llm.py tools.py memory.py agent.py app.py ./
COPY static ./static
COPY skills ./skills
# Secrets NEVER baked in: mount at runtime (-v ~/bourbon:/root/bourbon:ro --env-file .env)
# Brain: local Ollama via host, or cloud model via SOUL_MODEL + SOUL_OLLAMA_URL
EXPOSE 8000
CMD ["python3", "app.py"]
