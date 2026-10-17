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

# root 以外（uid 10001）で動かす。ログ（/app/logs）は配信先のディレクトリを重ねるので、
# 配信先でもこの uid に書き込みを許す
RUN useradd --system --uid 10001 --no-create-home app && mkdir -p /app/logs && chown app /app/logs
USER 10001

# サーバー起動用ポートの公開
EXPOSE 8000

# サーバーの起動コマンド（セルフホスト用）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
