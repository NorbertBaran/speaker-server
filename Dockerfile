FROM python:3.10.12-alpine3.18
COPY ./ /speaker/
WORKDIR /speaker
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["uvicorn", "main:app"]