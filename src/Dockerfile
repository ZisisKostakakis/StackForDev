FROM public.ecr.aws/lambda/python:3.11

RUN pip install poetry

COPY pyproject.toml ${LAMBDA_TASK_ROOT}
COPY poetry.lock ${LAMBDA_TASK_ROOT}
RUN poetry install

COPY generate_dockerfile.py ${LAMBDA_TASK_ROOT}

CMD [ "generate_dockerfile.handler" ]
