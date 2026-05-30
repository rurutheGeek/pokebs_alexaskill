import logging
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from app.data_loader import load_pokemon_stats, get_pokemon_stats

logger = logging.getLogger("alexa_app")

# ポケモンデータの事前ロード
pokemon_data = load_pokemon_stats()

class LaunchRequestHandler(AbstractRequestHandler):
    """
    スキルが起動された時のハンドラーです。
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("LaunchRequestを受信しました。")
        speech_text = "ポケモンの種族値スキルへようこそ。ポケモンの名前を指定して種族値を尋ねてください。例えば、ピカチュウの種族値を教えて、と話しかけてください。"
        
        return (
            handler_input.response_builder
            .speak(speech_text)
            .ask(speech_text)
            .response
        )

class PokemonStatsIntentHandler(AbstractRequestHandler):
    """
    ポケモンの種族値を検索して応答するハンドラーです。
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("PokemonStatsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("PokemonStatsIntentを受信しました。")
        # slots が None の場合（スロット未定義インテント）に備えて空辞書にフォールバック
        slots = handler_input.request_envelope.request.intent.slots or {}

        # スロット「pokemon」から値を取得
        pokemon_slot = slots.get("pokemon")
        
        if pokemon_slot and pokemon_slot.value:
            pokemon_name = pokemon_slot.value
            logger.info(f"検索対象のポケモン名: {pokemon_name}")
            
            # データの検索
            stats = get_pokemon_stats(pokemon_name, pokemon_data)
            
            if stats:
                # ユーザーの要望形式: 「OOの種族値は60,60,60,60,60,60です のように」
                # 読み上げ時に聞き取りやすくするため、カンマで区切った数値を生成
                # Alexaはカンマ区切りの数字を適度に間を空けて読み上げます
                stats_str = f"{stats['hp']},{stats['attack']},{stats['defense']},{stats['sp_attack']},{stats['sp_defense']},{stats['speed']}"
                speech_text = f"{pokemon_name}の種族値は{stats_str}です。"
                logger.info(f"応答テキスト: {speech_text}")
            else:
                speech_text = f"{pokemon_name}の種族値は見つかりませんでした。別のポケモンを指定してください。"
                logger.warning(f"ポケモンが見つかりません: {pokemon_name}")
        else:
            speech_text = "ポケモンの名前が聞き取れませんでした。もう一度ポケモンの名前を教えてください。"
            logger.warning("ポケモンスロットが空です。")

        return (
            handler_input.response_builder
            .speak(speech_text)
            .ask("他のポケモンの種族値も調べますか？")
            .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """
    ヘルプインテントのハンドラーです。
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("HelpIntentを受信しました。")
        speech_text = "このスキルでは、ポケモンの名前を指定してその種族値を調べることができます。例えば、ピカチュウの種族値を教えて、と話しかけてください。"
        
        return (
            handler_input.response_builder
            .speak(speech_text)
            .ask(speech_text)
            .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """
    キャンセルおよびストップインテントのハンドラーです。
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("Cancel/StopIntentを受信しました。")
        speech_text = "わかりました。また種族値が知りたくなったら呼び出してください。バイバイ！"
        
        return (
            handler_input.response_builder
            .speak(speech_text)
            .set_should_end_session(True)
            .response
        )

class SessionEndedRequestHandler(AbstractRequestHandler):
    """
    セッション終了リクエストのハンドラーです。
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("SessionEndedRequestを受信しました。")
        # クリーンアップ処理などがあればここに記述します
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """
    例外が発生した際の共通例外ハンドラーです。
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(f"例外が発生しました: {str(exception)}", exc_info=True)
        speech_text = "申し訳ありません。処理中に問題が発生しました。もう一度試してください。"
        
        return (
            handler_input.response_builder
            .speak(speech_text)
            .ask(speech_text)
            .response
        )
