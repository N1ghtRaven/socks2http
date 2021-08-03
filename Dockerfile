FROM python:alpine3.12
MAINTAINER Nate River 'n1ra@red-eye.works'
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
EXPOSE 8080