FROM python:3.12-slim

WORKDIR /app

# Only what the agent needs at runtime. No Jupyter, no notebook dependencies.
RUN pip install --no-cache-dir "openai>=1.60.0" "numpy>=1.26.0" "pydantic>=2.0.0"

COPY workshop_utils/ /app/workshop_utils/
COPY deploy/app/ /app/app/

# Run as a non-root user.
RUN useradd --create-home --uid 10001 agent && chown -R agent /app
USER agent

ENV PORT=8000
EXPOSE 8000

# The key is passed in at run time, never baked into the image.
CMD ["python", "-m", "app.main"]
