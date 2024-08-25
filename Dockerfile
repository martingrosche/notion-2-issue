FROM python:3.10

COPY requirements.txt /requirements.txt
COPY script.py /script.py
COPY utils/ /utils/

RUN pip install -r /requirements.txt

CMD ["python", "/script.py"]
