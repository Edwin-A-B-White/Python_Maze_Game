FROM gitpod/workspace-python:latest

USER root
RUN apt-get update \
 && apt-get install -y xvfb \
 && rm -rf /var/lib/apt/lists/*

USER gitpod
