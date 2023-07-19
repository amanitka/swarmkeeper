FROM python:alpine

RUN pip install --upgrade pip

RUN adduser  -D worker
USER worker
WORKDIR /home/worker

COPY --chown=worker:worker docker-entrypoint.sh docker-entrypoint.sh
COPY --chown=worker:worker ./*.py ./
COPY --chown=worker:worker requirements.txt requirements.txt

RUN pip install --user --no-cache-dir -r requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker . .

ENTRYPOINT ["sh", "docker-entrypoint.sh"]