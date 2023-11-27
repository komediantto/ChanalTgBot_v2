FROM python:3.10-slim-bullseye as base-py-project

ENV WD=/bot

WORKDIR ${WD}

COPY ./req.txt ./

RUN pip install -r req.txt

ENV PYTHONPATH=${WD}:${PYTHONPATH}

COPY . ${WD}

CMD ["python", "main.py"]
