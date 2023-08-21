FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN apt-get update \
    && pip3 install --upgrade setuptools \
    && pip3 install -r requirements.txt
RUN chmod 755 .
COPY . .
CMD ["python", "__main__.py"]
