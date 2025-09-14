
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
# install streamlit
RUN pip install --no-cache-dir streamlit
EXPOSE 8501
CMD ["streamlit", "run", "app_streamlit.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
