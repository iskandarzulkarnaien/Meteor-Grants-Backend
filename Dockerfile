FROM python:3.10

WORKDIR /run

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENTRYPOINT [ "python" ]
CMD ["python", "run.py"]