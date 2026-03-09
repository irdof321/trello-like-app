FROM python:3.12-slim

WORKDIR /app


# Create non-root user
RUN addgroup --system --gid 1001 django
RUN adduser --system --uid 1001 django

COPY --chown=django:django  requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=django:django  . .

EXPOSE 8000

USER django

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]