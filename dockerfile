# syntax=docker/dockerfile:1.4

# Stage 1: Install Python packages
FROM python:3.9.17-slim-bookworm@sha256:42a5da33675ec5a692e8cdbb09ffa4e39588c10dd9a96235e543c498484ee18e AS pythonpackages
COPY --link requirements.txt .

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:${PATH}"

RUN pip install --prefer-binary --extra-index-url https://www.piwheels.org/simple -r requirements.txt



from python:3.9.17-slim-bookworm as final
workdir /app
COPY --link --from=pythonpackages /app/venv ./venv
ENV PATH="/app/venv/bin:${PATH}"
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    libatlas3-base libgfortran5 \
    libopenblas-dev

#Set env
ENV PATH="/usr/lib/chromium/:${PATH}"
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Copy class files and main.py
COPY --link modules /app/modules
COPY --link auto.py .
COPY --link test.py .

ENTRYPOINT ["python3"]
CMD ["auto.py"] 
