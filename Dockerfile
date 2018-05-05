ARG PYTHON3_VERSION

FROM python:${PYTHON3_VERSION}

WORKDIR /opt/lz

COPY lz/ lz/
COPY tests/ tests/
COPY README.md .
COPY setup.py .
COPY setup.cfg .

RUN python3 -m pip install -e .
