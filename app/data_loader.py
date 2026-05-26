import json
import logging
import os

# ログの設定。親ロガー等で設定されている前提だが、個別でも初期化可能にする
logger = logging.getLogger("alexa_app")

def load_pokemon_stats(file_path="data/pokemon_stats.json"):
    """
    ポケモンの種族値データをJSONファイルから読み込みます。
    """
    if not os.path.exists(file_path):
        logger.error(f"データファイルが見つかりません: {file_path}")
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"種族値データをロードしました。件数: {len(data)}")
            return data
    except Exception as e:
        logger.error(f"データのロード中にエラーが発生しました: {str(e)}")
        return {}

def get_pokemon_stats(pokemon_name, data):
    """
    指定されたポケモン名に一致する種族値データを取得します。
    部分一致やひらがな・カタカナの正規化なども検討可能ですが、
    基本は完全一致で検索します。
    """
    if not pokemon_name:
        return None
    
    # 検索キーのトリムと正規化
    name_key = pokemon_name.strip()
    
    # 完全一致で検索
    if name_key in data:
        return data[name_key]
        
    # ひらがなをカタカナに変換して再検索する簡易正規化
    # アレクサからの音声認識でひらがなで届く可能性があるため
    normalized_key = "".join([chr(ord(c) + 96) if 12353 <= ord(c) <= 12435 else c for c in name_key])
    if normalized_key in data:
        return data[normalized_key]
        
    logger.warning(f"ポケモンが見つかりませんでした: {pokemon_name} (正規化キー: {normalized_key})")
    return None
