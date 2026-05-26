# ポケモン種族値Alexaスキル

## 概要
ポケモンの名前を指定して呼びかけると、そのポケモンの6つの種族値（HP、攻撃、防御、特攻、特防、素早さ）を順番に読み上げるAlexaカスタムスキルです。
本アプリケーションは FastAPI で構築されたWeb APIサーバーであり、AWS Lambdaなどのサーバーレス環境や、HTTPSエンドポイントとしてホストすることで動作します。

## ファイル構成
- app/main.py: FastAPIエンドポイントおよびログ設定の定義
- app/handlers.py: Alexaからのリクエストを処理する各種インテントハンドラー
- app/data_loader.py: ポケモンの種族値データをJSONから読み込み検索するユーティリティ
- data/pokemon_stats.json: データベースから抽出した1270件のポケモン種族値データ
- requirements.txt: 動作に必要なPythonパッケージのリスト

## ローカルでの実行方法
以下のコマンドでサーバーを起動できます。
```bash
uvicorn app.main:app --reload --port 8000
```
起動後、POSTメソッドでルートパス（/）にAlexaからのJSONリクエストを送信して動作を確認できます。

## デプロイおよびホスティング方法

本アプリケーションは標準的な FastAPI Web API アプリケーションであるため、Pythonが動作する任意の環境でセルフホストすることが可能です。また、各種クラウドプラットフォームやサーバーレス環境にも対応しています。

### 1. セルフホスト（Docker）
同封の Dockerfile を使用して、コンテナ環境での起動が可能です。

コンテナのビルド:
```bash
docker build -t pokemon-alexa-app -f output/Dockerfile .
```

コンテナの実行:
```bash
docker run -d -p 8000:8000 --name pokemon-alexa pokemon-alexa-app
```
これにより、ホストマシンのポート 8000 でHTTPSリバースプロキシ（Nginx、Cloudflare Tunnelなど）を介して公開準備が整います。

### 2. Cloudflare Workers (Python)
Cloudflare Workers の Python 環境を用いてホストする場合、Wrangler を使用してデプロイできます。

Wranglerの設定例 (wrangler.toml):
```toml
name = "pokemon-alexa-app"
main = "app/main.py"
compatibility_date = "2024-04-01"
compatibility_flags = ["python_workers"]
```
FastAPIアプリケーションオブジェクト（app）がエントリーポイントとして自動的にマッピングされます。詳細な仕様はCloudflare WorkersのPython開発ドキュメントを参照してください。

### 3. AWS Lambda
AWS Lambda で動かす場合は、以下の手順でZIPパッケージを作成します。

1. 以下のコマンドでパッケージ用のディレクトリを作成してライブラリをインストールします。
```bash
mkdir -p dist
pip install -r output/requirements.txt -t dist
```
2. 実装コードとデータを dist ディレクトリにコピーします。
```bash
cp app/*.py dist/
mkdir -p dist/data
cp data/pokemon_stats.json dist/data/
```
3. dist ディレクトリ配下のすべてのファイルをZIP圧縮してアップロードします。Lambdaのハンドラーには app.main.handler を指定します。


## Alexa開発者コンソールでの対話モデル設定
Alexa開発者コンソール（Alexa Developer Console）のビルドタブにて、以下の対話モデルJSON（Interaction Model JSON）を貼り付けてビルドしてください。

スキルの呼び出し名は「ポケモン種族値」に設定されています。

```json
{
  "interactionModel": {
    "languageModel": {
      "invocationName": "ポケモン種族値",
      "intents": [
        {
          "name": "AMAZON.CancelIntent",
          "samples": []
        },
        {
          "name": "AMAZON.HelpIntent",
          "samples": []
        },
        {
          "name": "AMAZON.StopIntent",
          "samples": []
        },
        {
          "name": "PokemonStatsIntent",
          "slots": [
            {
              "name": "pokemon",
              "type": "POKEMON_NAME"
            }
          ],
          "samples": [
            "{pokemon}の種族値を教えて",
            "{pokemon}の種族値は",
            "{pokemon}の種族値",
            "{pokemon}"
          ]
        }
      ],
      "types": [
        {
          "name": "POKEMON_NAME",
          "values": [
            {
              "name": {
                "value": "ピカチュウ"
              }
            },
            {
              "name": {
                "value": "リザードン"
              }
            },
            {
              "name": {
                "value": "ロトム"
              }
            },
            {
              "name": {
                "value": "ヒートロトム"
              }
            }
          ]
        }
      ]
    }
  }
}
```
読み上げ動作のテスト結果等については、experiments/data_generation_report.md に記述されています。
