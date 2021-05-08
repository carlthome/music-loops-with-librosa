FROM python:3.9-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
  libsndfile1=1.0.28-6 \
  ffmpeg=7:4.1.6-1~deb10u1

RUN pip install \
  streamlit==0.81.1 \
  librosa==0.8.0 \
  audioread==2.1.9 \
  soundfile==0.10.3.post1 \
  matplotlib==3.4.1

FROM base AS develop

RUN apt-get update && apt-get install -y --no-install-recommends \
  git=1:2.20.1-2+deb10u3

RUN pip install \
  pytest==6.2.4 \
  pytest-cov==2.11.1 \
  mypy==0.812 \
  black==21.5b0 \
  isort==5.8.0 \
  pyflakes==2.3.1 \
  ipython==7.23.1

COPY --from=docker:20.10.6 /usr/local/bin/docker /usr/local/bin
COPY --from=gcr.io/google.com/cloudsdktool/cloud-sdk:339.0.0-alpine /google-cloud-sdk /google-cloud-sdk
ENV PATH "/google-cloud-sdk/bin:$PATH"
RUN docker --version
RUN gcloud --version
RUN gcloud components install -q cloud-build-local kubectl minikube

ARG user=developer
RUN \
  groupadd docker; \
  useradd -m ${user} -G docker -s /bin/bash
USER ${user}
WORKDIR /home/${user}

FROM develop AS test

COPY . .
RUN \
  echo "\n\033[1mChecking type hints with mypy...\033[00m" ;\
  mypy **/*.py ;\
  echo "\n\033[1mChecking formatting with black...\033[00m" ;\
  black --check . ;\
  echo "\n\033[1mChecking import order with isort...\033[00m" ;\
  isort . --check --diff ;\
  echo "\n\033[1mChecking unused symbols with pyflakes...\033[00m" ;\
  pyflakes ;\
  echo "\n\033[1mChecking unit tests with pytest...\033[00m" ;\
  pytest -rN -qq --tb=line --cov=. ;

FROM base AS serve

RUN useradd -m www

COPY assets .
COPY src .
COPY README.md .

ENV PORT=8080
ENV STREAMLIT_SERVER_PORT=${PORT}

ENTRYPOINT ["streamlit", "run", "app.py"]