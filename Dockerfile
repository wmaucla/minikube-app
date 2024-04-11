ARG PROJECT_NAME=minikube-k8s
ARG PY_ROOT_MODULE=pubg
ARG PY_VER_FULL=3.12.2
ARG PY_VER_MAJOR=3.12
ARG POETRY_VERSION=1.8.2

FROM python:3.12.2 as base
ARG PROJECT_NAME
ARG PY_VER_MAJOR
ARG POETRY_VERSION

ENV HOME=/opt/${PROJECT_NAME}
ENV VENV_BIN=${HOME}/.venv/bin
ENV PATH=${VENV_BIN}${PATH:+":$PATH"}

RUN mkdir --parents ${VENV_BIN} && pip install poetry==${POETRY_VERSION}
WORKDIR ${HOME}

# ===================
# Builder image
# ===================
FROM base as builder
ARG PY_ROOT_MODULE

COPY pyproject.toml poetry.lock ./

RUN poetry install --only=main --no-root

COPY ${PY_ROOT_MODULE} ${PY_ROOT_MODULE}/

# ===================
# Dev Image
# ===================
FROM builder as dev

ARG PY_ROOT_MODULE

RUN poetry install --no-root

COPY Makefile ./
COPY tests tests/

# ===================
# Prod Image
# ===================

FROM python:3.12.2-slim as prod
ARG PROJECT_NAME
ARG PY_ROOT_MODULE
ARG PY_VER_MAJOR

ENV HOME=/opt/${PROJECT_NAME}
ENV PROJ_PYTHONPATH=${HOME}/.venv/lib/python${PY_VER_MAJOR}/site-packages
ENV VENV_BIN=${HOME}/.venv/bin
ENV PATH=${VENV_BIN}${PATH:+":$PATH"}
RUN mkdir --parents ${VENV_BIN}

WORKDIR ${HOME}

# Pull dependencies cached from previous layer
COPY --from=builder ${PROJ_PYTHONPATH} ${PROJ_PYTHONPATH}
COPY --from=builder ${PROJECT_VENV_BIN} ${PROJECT_VENV_BIN}/
COPY --from=builder "${HOME}/${PY_ROOT_MODULE}" ${PY_ROOT_MODULE}/

ENV PYTHONPATH=${PROJ_PYTHONPATH}${PYTHONPATH:+":$PYTHONPATH"}
