
FROM python:3.11-slim-bookworm AS compile-image
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt update && \
    apt install -y build-essential && \
    python -m venv --without-pip --system-site-packages /opt/wizaut && \
    mkdir -p /opt/wizaut/src/wizaut/ && \
    touch /opt/wizaut/src/wizaut/__init__.py && \
    rm -r /var/log/* /var/lib/apt/lists/* /var/cache/* /var/lib/dpkg/status*
WORKDIR /opt/wizaut
ENV PATH="/opt/wizaut/.venv/bin:$PATH"
ENV PATH="/root/.cargo/bin:$PATH"

COPY pyproject.toml requirements.txt README.md /opt/wizaut/
RUN /usr/local/bin/pip install --prefix /opt/wizaut --no-cache-dir --disable-pip-version-check --no-deps \
    -r /opt/wizaut/requirements.txt -e .

FROM python:3.11-slim-bookworm AS build-image
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN useradd -ms /bin/bash wizaut
USER wizaut
ENV PATH="/opt/wizaut/bin:$PATH"
ENV PYTHONPATH="/home/wizaut:/home/wizaut/src:/opt/wizaut/src:/opt/wizaut/lib/python3.11/site-packages:$PYTHONPATH"
WORKDIR /home/wizaut/
ENTRYPOINT ["python", "-m", "wizaut"]
EXPOSE 8000

COPY --chown=wizaut --from=compile-image /opt/wizaut /opt/wizaut
COPY --chown=wizaut . /opt/wizaut
