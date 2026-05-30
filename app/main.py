import json
import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_model import RequestEnvelope

from app.handlers import (
    LaunchRequestHandler,
    PokemonStatsIntentHandler,
    HelpIntentHandler,
    CancelOrStopIntentHandler,
    SessionEndedRequestHandler,
    CatchAllExceptionHandler
)

# ログファイルを出力する設定
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("alexa_app")
logger.info("アプリケーションを起動します。")

# Alexaスキルのビルドとハンドラーの登録
sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PokemonStatsIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
skill = sb.create()

# AWS Lambda用ハンドラーのエントリーポイント
handler = sb.lambda_handler()

serializer = DefaultSerializer()

# FastAPIアプリケーションの初期化
app = FastAPI(title="ポケモン種族値Alexaスキル")

@app.post("/")
async def alexa_endpoint(request: Request):
    """
    Alexaからのリクエストを受け取るメインのエンドポイントです。
    """
    try:
        # リクエストのバイト列を取得し、エンコーディングに応じてデコードする。
        # Alexaシミュレーター(ja-JP)はShift-JIS(cp932)でリクエストを送る場合がある。
        body = await request.body()
        try:
            body_str = body.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8デコード失敗。cp932(Shift-JIS)でリトライします。")
            body_str = body.decode("cp932")
        payload = json.loads(body_str)
        logger.info(f"受信したリクエスト: {json.dumps(payload, ensure_ascii=False)}")
        
        # リクエストエンベロープにデシリアライズ
        request_envelope = serializer.deserialize(json.dumps(payload), RequestEnvelope)
        
        # スキルの処理を実行
        response_envelope = skill.invoke(request_envelope, None)
        
        # レスポンスをJSONにシリアライズ
        response_payload = serializer.serialize(response_envelope)
        logger.info(f"送信するレスポンス: {json.dumps(response_payload, ensure_ascii=False)}")
        
        return JSONResponse(content=response_payload)
        
    except Exception as e:
        logger.error(f"エンドポイントでエラーが発生しました: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "内部サーバーエラーが発生しました。"}
        )

@app.get("/health")
async def health_check():
    """
    サーバーの稼働状態を確認するヘルスチェックエンドポイントです。
    """
    logger.info("ヘルスチェックが呼び出されました。")
    return {"status": "healthy"}
