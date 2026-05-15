FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv sync --no-dev

COPY tifonator/ tifonator/

EXPOSE 7860

CMD ["uv", "run", "tifonator"]
