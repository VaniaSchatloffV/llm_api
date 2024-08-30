FROM python:3.9
WORKDIR /app
COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#COPY . .
EXPOSE 8007
#CMD ["python", "app.py"]
CMD ["tail", "-f", "/dev/null"]