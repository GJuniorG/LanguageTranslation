FROM python:3.7

WORKDIR /app

# install requirements first for caching
COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

CMD python app.py