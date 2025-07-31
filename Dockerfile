FROM --platform=linux/amd64 python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && pip install --no-cache-dir \
        PyMuPDF==1.23.8 nltk==3.8.1 scikit-learn==1.3.2 numpy==1.24.3 \
    && python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)" \
    && apt-get remove -y gcc g++ && apt-get autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip /tmp/* \
    && find /usr/local/lib/python3.9 -name "*.pyc" -delete
COPY main.py .
RUN mkdir -p /app/input /app/output
ENV PYTHONPATH=/app PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
CMD ["python", "main.py"]