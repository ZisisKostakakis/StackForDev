FROM public.ecr.aws/lambda/python:3.11

RUN pip install poetry

COPY pyproject.toml ${LAMBDA_TASK_ROOT}
COPY poetry.lock ${LAMBDA_TASK_ROOT}
COPY src/ ${LAMBDA_TASK_ROOT}/src/

RUN poetry config virtualenvs.create false \
    && poetry install --with lambda --no-interaction --no-ansi --no-root

CMD [ "src.generate_dockerfile.lambda_handler" ]
