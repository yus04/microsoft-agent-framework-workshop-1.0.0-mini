import asyncio
import datetime
import json
import logging
import re
import sys
import uuid
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("fastmcp").setLevel(logging.INFO)

# Windows では ProactorEventLoop + TCP切断の組み合わせで
# ConnectionResetError([WinError 10054]) が asyncio ロガーに出やすい（多くは無害）。
# ノートブック/エージェントがセッションを閉じるたびにノイズになるため、
# SelectorEventLoop を使い、asyncio ログも抑制します。
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# 非推奨警告を抑制（挙動には影響しないノイズ）
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="uvicorn")

mcp = FastMCP(
    name="Xbox Game Shop + CRM Social Mock API as Tools",
    instructions=(
        "This is a MOCK MCP server with embedded sample data, optimized for a Microsoft Xbox game shop scenario. "
        "It does NOT connect to any real database. "
        "All product, order, inventory, user, and CRM/social analytics data is accessible ONLY via the declared tools below. "
        "Return values are JSON strings."
    ),
)


def to_json(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except Exception as e:
        logger.exception("JSON変換エラー")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _parse_iso_date(date_str: str) -> datetime.date:
    return datetime.date.fromisoformat(date_str)


def _date_str(dt: datetime.datetime) -> str:
    return dt.date().isoformat()


_HASHTAG_REGEX = re.compile(r"#([0-9A-Za-z_ぁ-んァ-ン一-龠ー]+)")


@dataclass(frozen=True)
class Tweet:
    id: str
    created_at: datetime.datetime
    user_screen_name: str
    text: str
    lang: str
    product_name: Optional[str]
    favorite_count: int
    retweet_count: int
    reply_count: int
    quote_count: int


def _build_sample_data() -> Dict[str, Any]:
    """Microsoft Xboxゲームショップ + CRM(social分析)用途の“本物風”サンプルデータを埋め込みで生成。"""

    categories = [
        {"category_id": 1, "category_name": "Xbox 本体"},
        {"category_id": 2, "category_name": "Xbox ゲーム"},
        {"category_id": 3, "category_name": "アクセサリ"},
        {"category_id": 4, "category_name": "サブスクリプション/デジタルコード"},
        {"category_id": 5, "category_name": "公式グッズ"},
    ]

    products = [
        {
            "product_id": 1001,
            "category_id": 1,
            "product_name": "Xbox Series X (本体)",
            "brand": "Microsoft",
            "price": 49980,
            "currency": "JPY",
            "release_date": "2020-11-10",
            "rating": 4.6,
            "tags": ["xbox", "console"],
        },
        {
            "product_id": 1002,
            "category_id": 2,
            "product_name": "Rift Dungeon VII (Xbox Series X|S)",
            "brand": "Xbox Game Studios",
            "price": 7980,
            "currency": "JPY",
            "release_date": "2025-12-01",
            "rating": 4.4,
            "tags": ["xbox", "rpg"],
        },
        {
            "product_id": 1003,
            "category_id": 2,
            "product_name": "Skyline Kart Turbo (Xbox Series X|S)",
            "brand": "Xbox Game Studios",
            "price": 6980,
            "currency": "JPY",
            "release_date": "2024-10-10",
            "rating": 4.2,
            "tags": ["xbox", "racing", "family"],
        },
        {
            "product_id": 1004,
            "category_id": 3,
            "product_name": "Xbox ワイヤレス コントローラー",
            "brand": "Microsoft",
            "price": 8980,
            "currency": "JPY",
            "release_date": "2023-09-20",
            "rating": 4.1,
            "tags": ["xbox", "controller"],
        },
        {
            "product_id": 1005,
            "category_id": 3,
            "product_name": "Seagate ストレージ拡張カード 512GB (Xbox Series X|S)",
            "brand": "Seagate",
            "price": 15980,
            "currency": "JPY",
            "release_date": "2024-05-12",
            "rating": 4.0,
            "tags": ["xbox", "storage"],
        },
        {
            "product_id": 1006,
            "category_id": 4,
            "product_name": "Xbox Game Pass Ultimate 2か月 (デジタルコード)",
            "brand": "Microsoft",
            "price": 2980,
            "currency": "JPY",
            "release_date": "2019-06-11",
            "rating": 4.3,
            "tags": ["xbox", "gamepass", "digital"],
        },
        {
            "product_id": 1007,
            "category_id": 5,
            "product_name": "Xbox ロゴ Tシャツ (限定カラー)",
            "brand": "Microsoft",
            "price": 3980,
            "currency": "JPY",
            "release_date": "2025-12-20",
            "rating": 4.7,
            "tags": ["xbox", "limited", "merch"],
        },
        {
            "product_id": 1008,
            "category_id": 2,
            "product_name": "Coffee Quest: Tokyo (Xbox Series X|S)",
            "brand": "IndieBeans",
            "price": 2480,
            "currency": "JPY",
            "release_date": "2025-12-28",
            "rating": 4.0,
            "tags": ["xbox", "indie", "cozy"],
        },
        {
            "product_id": 1009,
            "category_id": 3,
            "product_name": "Xbox ワイヤレス ヘッドセット",
            "brand": "Microsoft",
            "price": 12980,
            "currency": "JPY",
            "release_date": "2024-07-07",
            "rating": 4.1,
            "tags": ["xbox", "audio"],
        },
        {
            "product_id": 1010,
            "category_id": 4,
            "product_name": "Xbox ギフトカード 5,000円 (デジタルコード)",
            "brand": "Microsoft",
            "price": 5000,
            "currency": "JPY",
            "release_date": "2020-01-01",
            "rating": 4.8,
            "tags": ["xbox", "gift", "digital"],
        },
    ]

    game_products = [
        {
            "product_id": 2001,
            "game_title": "Rift Dungeon VII",
            "platform": "Xbox Series X|S",
            "genre": "RPG",
            "age_rating": "CERO:C",
            "publisher": "Xbox Game Studios",
        },
        {
            "product_id": 2002,
            "game_title": "Skyline Kart Turbo",
            "platform": "Xbox Series X|S",
            "genre": "Racing",
            "age_rating": "CERO:A",
            "publisher": "Xbox Game Studios",
        },
        {
            "product_id": 2003,
            "game_title": "Coffee Quest: Tokyo",
            "platform": "Xbox Series X|S",
            "genre": "Adventure",
            "age_rating": "CERO:A",
            "publisher": "IndieBeans",
        },
    ]

    inventory = {
        "1001": {
            "product_id": "1001",
            "warehouse": "Kanto-1",
            "on_hand": 42,
            "reserved": 8,
            "available": 34,
            "reorder_point": 20,
            "lead_time_days": 7,
            "status": "healthy",
        },
        "1002": {
            "product_id": "1002",
            "warehouse": "Kansai-1",
            "on_hand": 120,
            "reserved": 15,
            "available": 105,
            "reorder_point": 40,
            "lead_time_days": 3,
            "status": "healthy",
        },
        "1004": {
            "product_id": "1004",
            "warehouse": "Kanto-1",
            "on_hand": 18,
            "reserved": 12,
            "available": 6,
            "reorder_point": 25,
            "lead_time_days": 5,
            "status": "low_stock",
        },
        "1007": {
            "product_id": "1007",
            "warehouse": "Kanto-2",
            "on_hand": 0,
            "reserved": 0,
            "available": 0,
            "reorder_point": 0,
            "lead_time_days": 0,
            "status": "sold_out",
        },
        "1008": {
            "product_id": "1008",
            "warehouse": "Kansai-1",
            "on_hand": 55,
            "reserved": 5,
            "available": 50,
            "reorder_point": 15,
            "lead_time_days": 2,
            "status": "healthy",
        },
        "1010": {
            "product_id": "1010",
            "warehouse": "digital",
            "on_hand": None,
            "reserved": None,
            "available": None,
            "reorder_point": None,
            "lead_time_days": 0,
            "status": "unlimited",
        },
    }

    users = [
        {
            "user_id": 101,
            "customer_id": "C-000101",
            "name": "佐藤 花",
            "email": "hana.sato@example.com",
            "segment": "VIP",
            "prefecture": "東京都",
            "created_at": "2023-06-12",
            "lifetime_value": 182400,
            "marketing_opt_in": True,
        },
        {
            "user_id": 102,
            "customer_id": "C-000102",
            "name": "田中 恒一",
            "email": "koichi.tanaka@example.com",
            "segment": "Standard",
            "prefecture": "大阪府",
            "created_at": "2024-02-03",
            "lifetime_value": 32480,
            "marketing_opt_in": False,
        },
        {
            "user_id": 103,
            "customer_id": "C-000103",
            "name": "鈴木 由美",
            "email": "yumi.suzuki@example.com",
            "segment": "ChurnRisk",
            "prefecture": "神奈川県",
            "created_at": "2024-08-19",
            "lifetime_value": 15460,
            "marketing_opt_in": True,
        },
        {
            "user_id": 104,
            "customer_id": "C-000104",
            "name": "Alex Chen",
            "email": "alex.chen@example.com",
            "segment": "Standard",
            "prefecture": "東京都",
            "created_at": "2025-01-10",
            "lifetime_value": 49800,
            "marketing_opt_in": True,
        },
        {
            "user_id": 105,
            "customer_id": "C-000105",
            "name": "高橋 美咲",
            "email": "misaki.takahashi@example.com",
            "segment": "New",
            "prefecture": "福岡県",
            "created_at": "2025-12-22",
            "lifetime_value": 12980,
            "marketing_opt_in": True,
        },
        {
            "user_id": 123,
            "customer_id": "C-000123",
            "name": "山本 恒一",
            "email": "koichi.yamamoto@example.com",
            "segment": "Standard",
            "prefecture": "愛知県",
            "created_at": "2024-07-15",
            "lifetime_value": 68420,
            "marketing_opt_in": True,
        },
    ]

    # Orders (EC業務の現実味: クーポン/送料/支払/キャンセル/返金などの状態を含める)
    orders = [
        # --- task: 2024/9/1-9/2 の売上集計に必要な注文 ---
        {
            "order_id": 840901,
            "customer_id": "C-000101",
            "user_id": 101,
            "order_date": datetime.date(2024, 9, 1),
            "status": "delivered",
            "payment_method": "credit_card",
            "shipping_fee": 550,
            "discount_amount": 0,
            "total_amount": 6980 + 550,
            "campaign": "AUTUMN_2024",
        },
        {
            "order_id": 840902,
            "customer_id": "C-000102",
            "user_id": 102,
            "order_date": datetime.date(2024, 9, 2),
            "status": "delivered",
            "payment_method": "konbini",
            "shipping_fee": 550,
            "discount_amount": 500,
            "total_amount": 7980 + 550 - 500,
            "campaign": "AUTUMN_2024",
        },
        {
            "order_id": 840903,
            "customer_id": "C-000123",
            "user_id": 123,
            "order_date": datetime.date(2024, 9, 2),
            "status": "cancelled",
            "payment_method": "credit_card",
            "shipping_fee": 550,
            "discount_amount": 0,
            "total_amount": 0,
            "campaign": "AUTUMN_2024",
            "cancel_reason": "payment_failed",
        },
        {
            "order_id": 900001,
            "customer_id": "C-000101",
            "user_id": 101,
            "order_date": datetime.date(2025, 12, 26),
            "status": "delivered",
            "payment_method": "credit_card",
            "shipping_fee": 0,
            "discount_amount": 1500,
            "total_amount": 49980 + 8980 - 1500,
            "campaign": "WINTER_SALE_2025",
        },
        {
            "order_id": 900002,
            "customer_id": "C-000102",
            "user_id": 102,
            "order_date": datetime.date(2025, 12, 30),
            "status": "shipped",
            "payment_method": "konbini",
            "shipping_fee": 550,
            "discount_amount": 0,
            "total_amount": 7980 + 550,
            "campaign": None,
        },
        {
            "order_id": 900003,
            "customer_id": "C-000103",
            "user_id": 103,
            "order_date": datetime.date(2026, 1, 2),
            "status": "cancelled",
            "payment_method": "credit_card",
            "shipping_fee": 550,
            "discount_amount": 500,
            "total_amount": 0,
            "campaign": "NEWYEAR_2026",
            "cancel_reason": "duplicate_order",
        },
        {
            "order_id": 900004,
            "customer_id": "C-000104",
            "user_id": 104,
            "order_date": datetime.date(2026, 1, 3),
            "status": "processing",
            "payment_method": "paypal",
            "shipping_fee": 550,
            "discount_amount": 0,
            "total_amount": 15980 + 550,
            "campaign": None,
        },
        {
            "order_id": 900005,
            "customer_id": "C-000105",
            "user_id": 105,
            "order_date": datetime.date(2026, 1, 4),
            "status": "delivered",
            "payment_method": "credit_card",
            "shipping_fee": 550,
            "discount_amount": 0,
            "total_amount": 12980 + 550,
            "campaign": "NEWYEAR_2026",
        },
        {
            "order_id": 900006,
            "customer_id": "C-000101",
            "user_id": 101,
            "order_date": datetime.date(2026, 1, 5),
            "status": "shipped",
            "payment_method": "credit_card",
            "shipping_fee": 0,
            "discount_amount": 0,
            "total_amount": 2980,
            "campaign": "DLC_DROP",
        },
    ]

    order_details = [
        {
            "order_id": 840901,
            "product_id": 1003,
            "product_name": "Skyline Kart Turbo (Xbox Series X|S)",
            "quantity": 1,
            "unit_price": 6980,
            "line_amount": 6980,
        },
        {
            "order_id": 840902,
            "product_id": 1002,
            "product_name": "Rift Dungeon VII (Xbox Series X|S)",
            "quantity": 1,
            "unit_price": 7980,
            "line_amount": 7980,
        },
        {
            "order_id": 840903,
            "product_id": 1004,
            "product_name": "Xbox ワイヤレス コントローラー",
            "quantity": 1,
            "unit_price": 8980,
            "line_amount": 8980,
        },
        {
            "order_id": 900001,
            "product_id": 1001,
            "product_name": "Xbox Series X (本体)",
            "quantity": 1,
            "unit_price": 49980,
            "line_amount": 49980,
        },
        {
            "order_id": 900001,
            "product_id": 1004,
            "product_name": "Xbox ワイヤレス コントローラー",
            "quantity": 1,
            "unit_price": 8980,
            "line_amount": 8980,
        },
        {
            "order_id": 900002,
            "product_id": 1002,
            "product_name": "Rift Dungeon VII (Xbox Series X|S)",
            "quantity": 1,
            "unit_price": 7980,
            "line_amount": 7980,
        },
        {
            "order_id": 900003,
            "product_id": 1003,
            "product_name": "Skyline Kart Turbo (Xbox Series X|S)",
            "quantity": 1,
            "unit_price": 6980,
            "line_amount": 6980,
        },
        {
            "order_id": 900004,
            "product_id": 1005,
            "product_name": "Seagate ストレージ拡張カード 512GB (Xbox Series X|S)",
            "quantity": 1,
            "unit_price": 15980,
            "line_amount": 15980,
        },
        {
            "order_id": 900005,
            "product_id": 1009,
            "product_name": "Xbox ワイヤレス ヘッドセット",
            "quantity": 1,
            "unit_price": 12980,
            "line_amount": 12980,
        },
        {
            "order_id": 900006,
            "product_id": 1006,
            "product_name": "Xbox Game Pass Ultimate 2か月 (デジタルコード)",
            "quantity": 1,
            "unit_price": 2980,
            "line_amount": 2980,
        },
    ]

    shipping_status = [
        # --- task: user_id=123 の配送状況 ---
        {
            "order_id": 840905,
            "user_id": 123,
            "product_id": 1004,
            "order_date": datetime.datetime(2026, 1, 4, 20, 15),
            "shipping_status": "in_transit",
            "shipping_date": datetime.datetime(2026, 1, 5, 9, 0),
            "delivery_date": None,
            "carrier": "Yamato",
            "tracking_number": "YT-20260105-0123",
        },
        {
            "order_id": 840904,
            "user_id": 123,
            "product_id": 1002,
            "order_date": datetime.datetime(2025, 12, 28, 14, 40),
            "shipping_status": "delivered",
            "shipping_date": datetime.datetime(2025, 12, 29, 18, 10),
            "delivery_date": datetime.datetime(2025, 12, 30, 12, 25),
            "carrier": "Sagawa",
            "tracking_number": "SG-20251229-0456",
        },
        {
            "order_id": 900002,
            "user_id": 102,
            "product_id": 1002,
            "order_date": datetime.datetime(2025, 12, 30, 10, 15),
            "shipping_status": "in_transit",
            "shipping_date": datetime.datetime(2025, 12, 31, 18, 30),
            "delivery_date": None,
            "carrier": "Yamato",
            "tracking_number": "YT-20251231-8123",
        },
        {
            "order_id": 900004,
            "user_id": 104,
            "product_id": 1005,
            "order_date": datetime.datetime(2026, 1, 3, 12, 10),
            "shipping_status": "label_created",
            "shipping_date": None,
            "delivery_date": None,
            "carrier": "Sagawa",
            "tracking_number": None,
        },
        {
            "order_id": 900006,
            "user_id": 101,
            "product_id": 1006,
            "order_date": datetime.datetime(2026, 1, 5, 9, 5),
            "shipping_status": "digital_delivery",
            "shipping_date": datetime.datetime(2026, 1, 5, 9, 6),
            "delivery_date": datetime.datetime(2026, 1, 5, 9, 6),
            "carrier": "digital",
            "tracking_number": None,
        },
    ]

    # CRM/social分析: “炎上未満の不満 + 改善要望 + 好意的レビュー + 多言語”を混ぜる
    base = datetime.datetime(2025, 12, 25, 8, 0)
    tweets: List[Tweet] = [
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=0, hours=1),
            user_screen_name="hana_sato",
            text="Xbox Series X届いた！起動早い #XboxStore #XboxSeriesX",
            lang="ja",
            product_name="Xbox Series X (本体)",
            favorite_count=32,
            retweet_count=4,
            reply_count=2,
            quote_count=1,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=1, hours=9),
            user_screen_name="koichi_t",
            text="Game Passのコードが見当たらない…商品ページ分かりづらい #UX #XboxStore",
            lang="ja",
            product_name="Xbox Game Pass Ultimate 2か月 (デジタルコード)",
            favorite_count=7,
            retweet_count=1,
            reply_count=3,
            quote_count=0,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=2, hours=20),
            user_screen_name="yumi_s",
            text="Xboxコントローラー在庫切れ早すぎ。再入荷通知ほしい #在庫 #XboxController",
            lang="ja",
            product_name="Xbox ワイヤレス コントローラー",
            favorite_count=11,
            retweet_count=2,
            reply_count=1,
            quote_count=0,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=3, hours=12),
            user_screen_name="alex_play",
            text="Shipping took longer than expected, but support was polite. #XboxStore #Delivery",
            lang="en",
            product_name=None,
            favorite_count=5,
            retweet_count=0,
            reply_count=1,
            quote_count=0,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=4, hours=10),
            user_screen_name="misaki_new",
            text="Xboxワイヤレスヘッドセット音質いい！通話もクリア #Xbox #レビュー",
            lang="ja",
            product_name="Xbox ワイヤレス ヘッドセット",
            favorite_count=21,
            retweet_count=3,
            reply_count=0,
            quote_count=0,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=5, hours=19),
            user_screen_name="deal_hunter",
            text="WINTER_SALE最高。ギフトカードも使えるの助かる #セール #XboxStore",
            lang="ja",
            product_name="Xbox ギフトカード 5,000円 (デジタルコード)",
            favorite_count=14,
            retweet_count=2,
            reply_count=1,
            quote_count=0,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=6, hours=8),
            user_screen_name="support_watch",
            text="配送状況ページ、追跡番号が空欄で不安… #配送遅延 #XboxStore",
            lang="ja",
            product_name=None,
            favorite_count=9,
            retweet_count=1,
            reply_count=2,
            quote_count=0,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=7, hours=15),
            user_screen_name="rpg_fan_jp",
            text="Rift Dungeon VII神ゲー。BGM最高 #RiftDungeonVII #RPG",
            lang="ja",
            product_name="Rift Dungeon VII (Xbox Series X|S)",
            favorite_count=48,
            retweet_count=8,
            reply_count=5,
            quote_count=2,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=8, hours=22),
            user_screen_name="parent_gamer",
            text="Skyline Kart Turboは家族で遊べる。難易度ちょうど良い #SkylineKart",
            lang="ja",
            product_name="Skyline Kart Turbo (Xbox Series X|S)",
            favorite_count=16,
            retweet_count=1,
            reply_count=0,
            quote_count=0,
        ),
        Tweet(
            id=str(uuid.uuid4()),
            created_at=base + datetime.timedelta(days=9, hours=11),
            user_screen_name="indie_beans",
            text="Coffee Quest: Tokyo ほっこり。短時間で遊べるのいい #indie #CoffeeQuest",
            lang="ja",
            product_name="Coffee Quest: Tokyo (Xbox Series X|S)",
            favorite_count=22,
            retweet_count=3,
            reply_count=1,
            quote_count=0,
        ),
    ]

    # --- task: #花咲さくら ハッシュタグ検索用の投稿（複数件） ---
    # 併せて「時間帯別ツイート」で優勢になる時間帯を作るため、同じhourに寄せる
    for i in range(6):
        tweets.append(
            Tweet(
                id=str(uuid.uuid4()),
                created_at=datetime.datetime(2026, 1, 2, 21, 5) + datetime.timedelta(minutes=i * 7),
                user_screen_name="roze_fan" if i < 4 else "hana_sato",
                text=(
                    "#花咲さくら の配信見ながらRift Dungeon VII周回！ #RiftDungeonVII #XboxStore"
                    if i % 2 == 0
                    else "今日も #花咲さくら 最高。Xbox Series Xで動作快適 #XboxSeriesX"
                ),
                lang="ja",
                product_name="Rift Dungeon VII (Xbox Series X|S)" if i % 2 == 0 else "Xbox Series X (本体)",
                favorite_count=40 + i * 3,
                retweet_count=6 + (i % 3),
                reply_count=2 + (i % 2),
                quote_count=1,
            )
        )

    # 上位ユーザーが同率にならないよう、roze_fan を1件だけ追加
    tweets.append(
        Tweet(
            id=str(uuid.uuid4()),
            created_at=datetime.datetime(2026, 1, 3, 21, 30),
            user_screen_name="roze_fan",
            text="#花咲さくら のおすすめでギフトカード買った。発行が早い #XboxStore",
            lang="ja",
            product_name="Xbox ギフトカード 5,000円 (デジタルコード)",
            favorite_count=24,
            retweet_count=2,
            reply_count=1,
            quote_count=0,
        )
    )

    # --- task: 「ユーザー別ツイート数上位」(上位3名が安定するよう補強) ---
    # roze_fan を最多、次に hana_sato、次に koichi_t になるように少数追加
    tweets.extend(
        [
            Tweet(
                id=str(uuid.uuid4()),
                created_at=datetime.datetime(2026, 1, 1, 21, 50),
                user_screen_name="roze_fan",
                text="在庫復活きた！Xboxコントローラー買えた #XboxController #XboxStore",
                lang="ja",
                product_name="Xbox ワイヤレス コントローラー",
                favorite_count=18,
                retweet_count=2,
                reply_count=1,
                quote_count=0,
            ),
            Tweet(
                id=str(uuid.uuid4()),
                created_at=datetime.datetime(2026, 1, 3, 21, 10),
                user_screen_name="hana_sato",
                text="配送ステータスが更新されて助かった #配送 #CS #XboxStore",
                lang="ja",
                product_name=None,
                favorite_count=12,
                retweet_count=1,
                reply_count=0,
                quote_count=0,
            ),
            Tweet(
                id=str(uuid.uuid4()),
                created_at=datetime.datetime(2026, 1, 4, 19, 40),
                user_screen_name="koichi_t",
                text="ハッシュタグ集計便利。#XboxStore の分析もっと見たい #analytics",
                lang="ja",
                product_name=None,
                favorite_count=6,
                retweet_count=0,
                reply_count=1,
                quote_count=0,
            ),
        ]
    )

    # 少し増やして“分析っぽさ”を出す（同じ期間・異なる時間帯）
    extra_texts = [
        ("ja", "在庫復活したら買う！ #在庫 #XboxSeriesX", "Xbox Series X (本体)"),
        ("ja", "コントローラーのスティック感度、設定で改善できた #XboxController #設定", "Xbox ワイヤレス コントローラー"),
        ("ja", "配送が1日遅れたけど連絡があって安心 #配送遅延 #CS", None),
        ("en", "Great discounts, checkout was smooth. #XboxStore #Sale", None),
        ("ja", "Game Pass購入完了、コード即時で助かる #デジタル #GamePass", "Xbox Game Pass Ultimate 2か月 (デジタルコード)"),
        ("ja", "限定Tシャツ再販してほしい… #限定 #グッズ", "Xbox ロゴ Tシャツ (限定カラー)"),
        ("ja", "拡張カード便利。容量増えると快適 #ストレージ #Xbox", "Seagate ストレージ拡張カード 512GB (Xbox Series X|S)"),
        ("en", "Controller stock is low everywhere :( #XboxController", "Xbox ワイヤレス コントローラー"),
    ]
    for i, (lang, text, product_name) in enumerate(extra_texts, start=1):
        tweets.append(
            Tweet(
                id=str(uuid.uuid4()),
                created_at=base + datetime.timedelta(days=(i % 10), hours=(i * 2) % 24, minutes=(i * 7) % 60),
                user_screen_name=["hana_sato", "koichi_t", "yumi_s", "alex_play", "misaki_new"][i % 5],
                text=text,
                lang=lang,
                product_name=product_name,
                favorite_count=3 + (i * 2) % 20,
                retweet_count=(i % 4),
                reply_count=(i % 3),
                quote_count=(i % 2),
            )
        )

    # ツイートの本文/商品名を Xbox ショップ向けに正規化（既存task: #花咲さくら、時間帯分布、上位ユーザー を維持）
    product_name_map = {
        "NebulaStation X": "Xbox Series X (本体)",
        "Dungeon Drift VII": "Rift Dungeon VII (Xbox Series X|S)",
        "Dungeon Drift VII Season Pass (Digital)": "Xbox Game Pass Ultimate 2か月 (デジタルコード)",
        "ProPad Wireless": "Xbox ワイヤレス コントローラー",
        "Skyline Kart Turbo": "Skyline Kart Turbo (Xbox Series X|S)",
        "Coffee Quest: Tokyo": "Coffee Quest: Tokyo (Xbox Series X|S)",
        "NoiseCancel Gaming Headset": "Xbox ワイヤレス ヘッドセット",
        "ギフトカード 5,000円": "Xbox ギフトカード 5,000円 (デジタルコード)",
        "NebulaStation X 限定スキンフィギュア": "Xbox ロゴ Tシャツ (限定カラー)",
        "HD Capture Mini": "Seagate ストレージ拡張カード 512GB (Xbox Series X|S)",
    }

    def _normalize_text(text: str) -> str:
        return (
            text.replace("#GameShop", "#XboxStore")
            .replace("#NebulaStationX", "#XboxSeriesX")
            .replace("#ProPad", "#XboxController")
            .replace("#DungeonDriftVII", "#RiftDungeonVII")
            .replace("NebulaStation X", "Xbox Series X")
        )

    normalized: List[Tweet] = []
    for tw in tweets:
        normalized.append(
            Tweet(
                id=tw.id,
                created_at=tw.created_at,
                user_screen_name=tw.user_screen_name,
                text=_normalize_text(tw.text),
                lang=tw.lang,
                product_name=product_name_map.get(tw.product_name, tw.product_name),
                favorite_count=tw.favorite_count,
                retweet_count=tw.retweet_count,
                reply_count=tw.reply_count,
                quote_count=tw.quote_count,
            )
        )
    tweets = normalized

    # CRM寄りの“ソーシャル分析”用: 擬似的なセンチメントを同梱
    def sentiment(text: str) -> str:
        negative_markers = ["遅延", "不安", "在庫切れ", "分かりづらい", "low", "everywhere"]
        positive_markers = ["最高", "助かる", "神", "いい", "smooth", "Great", "ほっこり"]
        t = text.lower()
        if any(m.lower() in t for m in negative_markers):
            return "negative"
        if any(m.lower() in t for m in positive_markers):
            return "positive"
        return "neutral"

    tweets_docs = []
    for tw in tweets:
        tweets_docs.append(
            {
                "_id": tw.id,
                "created_at": tw.created_at,
                "user": {"screen_name": tw.user_screen_name},
                "text": tw.text,
                "lang": tw.lang,
                "product_name": tw.product_name,
                "favorite_count": tw.favorite_count,
                "retweet_count": tw.retweet_count,
                "reply_count": tw.reply_count,
                "quote_count": tw.quote_count,
                "sentiment": sentiment(tw.text),
            }
        )

    return {
        "categories": categories,
        "products": products,
        "game_products": game_products,
        "inventory": inventory,
        "users": users,
        "orders": orders,
        "order_details": order_details,
        "shipping_status": shipping_status,
        "tweets": tweets_docs,
    }


SAMPLE = _build_sample_data()


##############################################################################
#                               TOOL ENDPOINTS                               #
##############################################################################


@mcp.tool(description="List all product categories")
async def get_all_categories() -> str:
    return to_json(SAMPLE["categories"][:10])


@mcp.tool(description="List all products (optionally filter by category)")
async def get_products(category_id: Optional[int] = None) -> str:
    products = SAMPLE["products"]
    if category_id is not None:
        products = [p for p in products if p.get("category_id") == category_id]
    return to_json(products[:10])


@mcp.tool(description="Get product detail by product_id")
async def get_product_detail(product_id: int) -> str:
    for p in SAMPLE["products"]:
        if int(p.get("product_id")) == int(product_id):
            return to_json(p)
    return json.dumps({"error": "Product not found"}, ensure_ascii=False)


@mcp.tool(description="List all game products")
async def get_game_products() -> str:
    return to_json(SAMPLE["game_products"][:10])


@mcp.tool(description="Get inventory status for a product")
async def get_inventory_status(product_id: str) -> str:
    inv = SAMPLE["inventory"].get(str(product_id))
    if not inv:
        return json.dumps({"error": "Inventory not found"}, ensure_ascii=False)
    return to_json(inv)


@mcp.tool(description="List all orders for a customer")
async def get_customer_orders(customer_id: str) -> str:
    customer_orders = [o for o in SAMPLE["orders"] if o.get("customer_id") == customer_id]
    customer_orders.sort(key=lambda x: x.get("order_date"), reverse=True)
    return to_json(customer_orders[:10])


@mcp.tool(description="Get order details for an order")
async def get_order_details(order_id: int) -> str:
    rows = [d for d in SAMPLE["order_details"] if int(d.get("order_id")) == int(order_id)]
    return to_json(rows[:10])


@mcp.tool(description="Get shipping status for a user's order")
async def get_shipping_status(user_id: int) -> str:
    rows = [s for s in SAMPLE["shipping_status"] if int(s.get("user_id")) == int(user_id)]
    rows.sort(key=lambda x: x.get("order_date"), reverse=True)
    if not rows:
        return json.dumps({}, ensure_ascii=False)
    return to_json(rows[0])


@mcp.tool(description="Get shipping status for an order by order_id")
async def get_shipping_status_by_order_id(order_id: int) -> str:
    for row in SAMPLE["shipping_status"]:
        if int(row.get("order_id")) == int(order_id):
            return to_json(row)
    return json.dumps({}, ensure_ascii=False)


@mcp.tool(description="List all users")
async def get_all_users() -> str:
    return to_json(SAMPLE["users"][:10])


@mcp.tool(description="指定期間の売上合計を取得する")
async def get_total_sales(start_date: str, end_date: str) -> str:
    try:
        start = _parse_iso_date(start_date)
        end = _parse_iso_date(end_date)
    except ValueError as e:
        return json.dumps({"error": f"日付形式エラー: {e}"}, ensure_ascii=False)

    total = 0
    for o in SAMPLE["orders"]:
        od: datetime.date = o.get("order_date")
        if od and start <= od <= end:
            total += int(o.get("total_amount") or 0)
    return to_json([{"total_amount": total}])


@mcp.tool(description="指定期間の日別受注数を取得する")
async def get_daily_order_counts(start_date: str, end_date: str) -> str:
    try:
        start = _parse_iso_date(start_date)
        end = _parse_iso_date(end_date)
    except ValueError as e:
        return json.dumps({"error": f"日付形式エラー: {e}"}, ensure_ascii=False)

    counts: Dict[str, int] = defaultdict(int)
    for o in SAMPLE["orders"]:
        od: datetime.date = o.get("order_date")
        if not od or not (start <= od <= end):
            continue
        counts[od.isoformat()] += 1

    result = [
        {"order_date": day, "order_count": counts[day]}
        for day in sorted(counts.keys())
    ]
    return to_json(result)


@mcp.tool(description="日別のツイート数を取得する")
async def get_daily_tweet_counts() -> str:
    counts: Dict[str, int] = defaultdict(int)
    for doc in SAMPLE["tweets"]:
        created_at: datetime.datetime = doc.get("created_at")
        if not created_at:
            continue
        counts[_date_str(created_at)] += 1

    results = [{"date": day, "count": counts[day]} for day in sorted(counts.keys())]
    return to_json(results)


@mcp.tool(description="ユーザー別のツイート数上位を取得する")
async def get_top_users_by_tweet_count(limit: int = 10) -> str:
    c = Counter()
    for doc in SAMPLE["tweets"]:
        user = (doc.get("user") or {}).get("screen_name")
        if user:
            c[user] += 1
    results = [{"user": u, "tweet_count": n} for u, n in c.most_common(limit)]
    return to_json(results)


@mcp.tool(description="ハッシュタグの出現頻度上位を取得する")
async def get_top_hashtags(limit: int = 10) -> str:
    c = Counter()
    for doc in SAMPLE["tweets"]:
        text = doc.get("text") or ""
        for m in _HASHTAG_REGEX.finditer(text):
            c[f"#{m.group(1)}"] += 1
    results = [{"hashtag": tag, "count": n} for tag, n in c.most_common(limit)]
    return to_json(results)


@mcp.tool(description="言語ごとのツイート数を集計する")
async def get_language_distribution() -> str:
    c = Counter()
    total = 0
    for doc in SAMPLE["tweets"]:
        lang = doc.get("lang")
        if not lang:
            continue
        c[lang] += 1
        total += 1

    results = []
    for lang, count in c.most_common():
        results.append({"lang": lang, "count": count, "ratio": round(count / total, 4) if total else 0})
    return to_json(results)


@mcp.tool(description="時間帯別のツイート数を取得する")
async def get_hourly_tweet_distribution() -> str:
    c = Counter()
    for doc in SAMPLE["tweets"]:
        created_at: datetime.datetime = doc.get("created_at")
        if created_at is None:
            continue
        c[int(created_at.hour)] += 1

    results = [{"hour": h, "count": c[h]} for h in range(24) if c[h] > 0]
    return to_json(results)


@mcp.tool(description="日別の平均いいね・リプライ・リツイート数を取得する")
async def get_daily_average_engagement() -> str:
    buckets: Dict[str, Dict[str, Any]] = {}

    def _ensure(day: str) -> Dict[str, Any]:
        if day not in buckets:
            buckets[day] = {
                "sum_favorite": 0,
                "sum_reply": 0,
                "sum_retweet": 0,
                "sum_quote": 0,
                "count": 0,
            }
        return buckets[day]

    for doc in SAMPLE["tweets"]:
        created_at: datetime.datetime = doc.get("created_at")
        if not created_at:
            continue
        day = _date_str(created_at)
        b = _ensure(day)
        b["sum_favorite"] += int(doc.get("favorite_count") or 0)
        b["sum_reply"] += int(doc.get("reply_count") or 0)
        b["sum_retweet"] += int(doc.get("retweet_count") or 0)
        b["sum_quote"] += int(doc.get("quote_count") or 0)
        b["count"] += 1

    results = []
    for day in sorted(buckets.keys()):
        b = buckets[day]
        n = max(int(b["count"]), 1)
        results.append(
            {
                "date": day,
                "avg_favorite": round(b["sum_favorite"] / n, 2),
                "avg_reply": round(b["sum_reply"] / n, 2),
                "avg_retweet": round(b["sum_retweet"] / n, 2),
                "avg_quote": round(b["sum_quote"] / n, 2),
            }
        )

    return to_json(results)


@mcp.tool(description="product_name 別のツイート数を集計する")
async def get_product_mentions_count() -> str:
    c = Counter()
    for doc in SAMPLE["tweets"]:
        pn = doc.get("product_name")
        if pn:
            c[pn] += 1
    results = [{"product_name": pn, "count": n} for pn, n in c.most_common()]
    return to_json(results)


@mcp.tool(description="特定のハッシュタグを含むツイートを検索する")
async def search_tweets_by_hashtag(hashtag: str, limit: int = 100) -> str:
    tag = hashtag.lstrip("#")
    pattern = re.compile(rf"#({re.escape(tag)})\b", re.IGNORECASE)

    matched = []
    for doc in SAMPLE["tweets"]:
        text = doc.get("text") or ""
        if pattern.search(text):
            matched.append(doc)

    matched.sort(key=lambda d: d.get("created_at"), reverse=True)
    matched = matched[: int(limit)]

    results = []
    for doc in matched:
        results.append(
            {
                "id": str(doc.get("_id")),
                "created_at": doc.get("created_at"),
                "user": (doc.get("user") or {}).get("screen_name"),
                "text": doc.get("text"),
                "favorite_count": doc.get("favorite_count", 0),
                "retweet_count": doc.get("retweet_count", 0),
                "reply_count": doc.get("reply_count", 0),
                "quote_count": doc.get("quote_count", 0),
            }
        )

    return to_json(results)


##############################################################################
#                                RUN SERVER                                  #
##############################################################################


def main() -> None:
    logger.info("Starting MOCK Game Shop + CRM Social MCP Server...")
    try:
        mcp.run(
            transport="streamable-http",
            host="127.0.0.1",
            port=8000,
        )
    except KeyboardInterrupt:
        logger.info("Shutting down server (KeyboardInterrupt)")
    except asyncio.CancelledError:
        logger.info("Shutting down server (CancelledError)")
    except Exception:
        logger.exception("Error running server")
        raise


if __name__ == "__main__":
    main()
