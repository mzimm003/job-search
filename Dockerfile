FROM python:3.13
ARG testing=1
ARG documentation=1
ARG browser=1

RUN useradd -m -u 1000 user
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    mesa-utils \
    xauth \
    x11-utils \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ENV DISPLAY=host.docker.internal:0.0
ENV LIBGL_ALWAYS_INDIRECT=1

RUN pip install -U pip setuptools poetry
COPY pyproject.toml .
RUN poetry config virtualenvs.create false && \
poetry install --no-root --no-interaction --no-ansi \
$( if [ "$testing" = "1" ]; then echo "-E testing"; fi) \
$( if [ "$documentation" = "1" ]; then echo "-E documentation"; fi) \
$( if [ "$browser" = "1" ]; then echo "-E browser"; fi)

USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /home/user