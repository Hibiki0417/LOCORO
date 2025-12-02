FROM python:3.12-slim

#作業ディレクトリ
WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

#依存ファイルをコピー
COPY requirements.txt /app/

#依存インストール
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

#プロジェクトをコピー
COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

USER root