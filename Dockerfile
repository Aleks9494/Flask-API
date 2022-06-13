FROM python:3.10.3
COPY . /app
EXPOSE 5005
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "./run.py", "--host=0.0.0.0"]