# Pythonの軽量イメージを使用します
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイルのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードとデータのコピー
COPY app/ ./app/
COPY data/ ./data/

# サーバー起動用ポートの公開
EXPOSE 8000

# サーバーの起動コマンド（セルフホスト用）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
