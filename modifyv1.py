import asyncio
import io
import re
import json
import html
import os
import httpx
import random
import string
import time
import unicodedata
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.request import HTTPXRequest

try:
    from telegram import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# ==================== EMOJI CONFIGURATION ENGINE ====================

EMOJI_ID_MAP = {
    "telegram": "5271801931814165886",
    "instagram": "5269682734820777950",
    "facebook": "5269427536453984598",
    "tiktok": "5271527792641595125",
    "x": "5269500885905468781",
    "whatsapp": "5271536803482981220",
    "discord": "5807892405306791778",
    "uber": "5298715455316303708",
    "up": "5244837092042750681",
    "down": "5246762912428603768",
    "add": "5397916757333654639",
    "setting": "5341715473882955310",
    "1st": "5440539497383087970",
    "2st": "5447203607294265305",
    "3rd": "5453902265922376865",
    "free": "5406756500108501710",
    "msg": "5253742260054409879",
    "link": "5271604874419647061",
    "status": "5231200819986047254",
    "home": "5416041192905265756",
    "gift_box": "5970074171449808121",
    "delete": "5422557736330106570",
    "refer_btn": "5420396762189831222",
    "get_number_btn": "5382357040008021292",
    "cross": "5420130255174145507",
    "stop": "5956074558044770726",
    "ban": "5420323339723881652",
    "done": "6298670698948724690",
    "nagad": "5352985330628730418",
    "bkash": "5348469219761626211",
    "rocket": "5346042941196507141",
    "binance": "5348212415077064131",
    "live": "5355102594886833928",
    "channel": "6215074610845585917",
    "admin": "5350396951407895212",
    "waiting": "6217721388736712699",
    "back": "5267490665117275176",
    "leader_board": "5280769763398671636",
    "money": "6233367447789899509",
    "change_number": "5402186569006210455"
}

PREMIUM_FLAGS = {
    "🇺🇸": "5913463998522592692",
    "🇺🇦": "5911406692007941050",
    "🇵🇱": "5913550391789752571",
    "🇰🇿": "5913724621433082323",
    "🇨🇳": "5913779335021466780",
    "🇦🇿": "5911197578640233518",
    "🇪🇺": "5911106310585193018",
    "🇦🇲": "5913272455866093666",
    "🇷🇺": "5913274246867456342",
    "🇺🇿": "5911051846104912282",
    "🇩🇪": "5911096835887337583",
    "🇯🇵": "5913293711659241040",
    "🇹🇷": "5910995113881901195",
    "🇧🇾": "5911011185649521599",
    "🇬🇧": "5913443365499703513",
    "🇮🇳": "5913754823643107921",
    "🇧🇷": "5911148568768418614",
    "🇿🇲": "5913564754160389778",
    "🇾🇪": "5913346492512341993",
    "🇻🇳": "5913428887164949581",
    "🇨🇲": "5911172109484167745",
    "🇨🇮": "5222233374948602940",
    "🇲🇬": "5913766918271012920",
    "🇷🇴": "5913460373570195273",
    "🇨🇫": "5913443245240619222",
    "🇹🇬": "5913423260757790970",
    "🇧🇯": "5913735869952430547",
    "🇸🇱": "5911210450657218661",
    "🇧🇩": "5911365056594973179",
    "🇰🇷": "5913371673905598425",
    "🇬🇶": "5911306279967529251",
    "🇬🇱": "5292014752283774878",
    "🇫🇴": "5296469342039327674",
    "🇧🇳": "5911336409163109113",
    "🇧🇬": "5294329219965272288",
    "🇧🇫": "5913407764515786948",
    "🇪🇷": "5433723401464198287",
    "🇲🇼": "5433968339154122439",
    "🇲🇷": "5433859405898594234",
    "🇳🇷": "5434131139889478358",
    "🇸🇦": "4985897134424328239",
    "🇹🇴": "5433640100573491806",
    "🇹🇻": "5433684690923961019",
    "🇹🇼": "5366187256937726720",
    "🇭🇰": "5292166459118606932",
    "🇲🇴": "6323557758096377611",
    "🇨🇺": "5431551436502611633",
    "🇰🇵": "5434142701941437163",
    "🇻🇪": "5434009132753499322",
    "🇸🇾": "5433910876786670092",
    "🇲🇲": "5433666360003540231",
    "🇳🇮": "5334807849418003620",
    "🇬🇳": "5913471858312744319",
    "🇰🇪": "5222279743415531561",
    "🏴󠁧󠁢󠁷󠁬󠁳󠁿": "5911297801702084799",
    "🇻🇦": "5911211932420938860",
    "🇻🇺": "5913511535220625585",
    "🇺🇾": "5913623088406204470",
    "🇦🇪": "5913726554168365343",
    "🇺🇬": "5913488939397681980",
    "🇹🇲": "5913315521503170180",
    "🇹🇳": "5911332947419468671",
    "🇹🇹": "5911228635548750294",
    "🇹🇭": "5913617968805187987",
    "🇹🇿": "5911418949844603556",
    "🇹🇯": "5911287639809463107",
    "🇨🇭": "5913271227505448072",
    "🇸🇪": "5911156510162949403",
    "🇸🇿": "5913374525763883286",
    "🇸🇷": "5913275539652611719",
    "🇸🇩": "5911387497799094470",
    "🇪🇸": "5911193287967904547",
    "🇱🇰": "5911293163137406640",
    "🇸🇸": "5911406262511211744",
    "🇿🇦": "5911203119148044594",
    "🇸🇴": "5911397852965244436",
    "🇸🇧": "5911482712929080608",
    "🇸🇮": "5913431983836368644",
    "🇸🇰": "5913751666842145020",
    "🇸🇬": "5911531460808051849",
    "🇸🇨": "5911185183364616913",
    "🇷🇸": "5913592598433369871",
    "🇸🇳": "5910995302860461643",
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿": "5911460091336331851",
    "🇸🇹": "5913574331937462345",
    "🇸🇲": "5913587968458625465",
    "🇼🇸": "5913325971158602854",
    "🇰🇳": "5913691898077253637",
    "🇻🇨": "5911318941531116255",
    "🇱🇨": "5911243659344351824",
    "🇵🇸": "5913684768431541668",
    "🇷🇼": "5911455229433352234",
    "🇶🇦": "5911260864983339619",
    "🇵🇷": "5911504350974317480",
    "🇵🇹": "5911023653939581472",
    "🇵🇭": "5911268638874145162",
    "🇵🇪": "5911207993935925780",
    "🇵🇾": "5911014265141072316",
    "🇵🇬": "5911107251183030903",
    "🇵🇦": "5913428968769327174",
    "🇵🇼": "5911283903187915549",
    "🇵🇰": "5913705895375672082",
    "🇴🇲": "5913570801474343473",
    "🇳🇴": "5913617397574537046",
    "🇳🇬": "5911143844304393105",
    "🇳🇪": "5911270086278124251",
    "🇳🇿": "5913640044937089340",
    "🇳🇱": "5913367645226275100",
    "🇳🇵": "5913496520014958723",
    "🇳🇦": "5911108535378252443",
    "🇲🇿": "5911333419865871464",
    "🇲🇦": "5911482111633658301",
    "🇲🇪": "5913239436157522151",
    "🇲🇳": "5911041383564580038",
    "🇲🇨": "5911245347266500057",
    "🇲🇩": "5913456847402045950",
    "🇲🇻": "5913501399097806832",
    "🇲🇱": "5911305266355245916",
    "🇲🇹": "5911023714069123567",
    "🇧🇲": "5913680005312811090",
    "🇲🇶": "5911378005921370347",
    "🇲🇭": "5913235935759175692",
    "🇲🇺": "5913291113204027321",
    "🇲🇽": "5913687302462246518",
    "🇫🇲": "5911271104185373336",
    "🇲🇾": "5913654360063087453",
    "🇲🇰": "5913394029210374721",
    "🇱🇺": "5913390842344640293",
    "🇱🇹": "5911172315642597775",
    "🇱🇮": "5911166650580734660",
    "🇱🇾": "5911236989260140996",
    "🇱🇷": "5913324167272337727",
    "🇰🇮": "5911294443037660118",
    "🇽🇰": "5911433681582429010",
    "🇰🇼": "5913290705182134003",
    "🇰🇬": "5911202161370337549",
    "🇱🇦": "5913718526874489279",
    "🇱🇻": "5913738489882480243",
    "🇱🇧": "5911504273664905447",
    "🇱🇸": "5911059881988723711",
    "🇮🇩": "5913479361620611038",
    "🇮🇷": "5911308891307643032",
    "🇮🇶": "5911382442622587735",
    "🇮🇪": "5913440715504881532",
    "🇮🇱": "5911471936856134692",
    "🇮🇹": "5913688444923547525",
    "🇯🇲": "5913232280742006526",
    "🇯🇴": "5913234136167878475",
    "🇮🇸": "5911047899029967246",
    "🇭🇺": "5913767635530551104",
    "🇭🇳": "5911406889576436289",
    "🇭🇹": "5913459789454643194",
    "🇬🇾": "5913579412883771480",
    "🇬🇼": "5911398694778836149",
    "🇬🇹": "5913324858762072330",
    "🇬🇩": "5913228063084121946",
    "🇬🇷": "5911210399117611448",
    "🇬🇭": "5913391155877252952",
    "🇬🇪": "5913434771270144023",
    "🇬🇲": "5913657267755945883",
    "🇬🇦": "5911037896051137264",
    "🇫🇷": "5913605586414473124",
    "🇫🇮": "5911041344909873378",
    "🇫🇯": "5911393832875856716",
    "🇪🇹": "5911078333168227043",
    "🇩🇴": "5911152099231536123",
    "🇩🇲": "5911377121158107430",
    "🇩🇯": "5911407709915190157",
    "🇩🇰": "5911206009661034712",
    "🇨🇾": "5911023550860366409",
    "🇭🇷🇨🇷": "5913692684056269311",
    "🇨🇷": "5911261745451635030",
    "🇨🇬": "5911338788574990168",
    "🇨🇩": "5913770362834783827",
    "🇰🇲": "5911338582416560604",
    "🇰🇭": "5913699998385573485",
    "🇨🇦": "5913623736946265914",
    "🇨🇻": "5913571501554012193",
    "🇹🇩": "5913299849167507310",
    "🇨🇿": "5911198691036764307",
    "🇨🇱": "5911470957603592832",
    "🇨🇴": "5913773060074246009",
    "🇧🇮": "5913766441529642752",
    "🇧🇼": "5911513782722499475",
    "🇧🇦": "5913700002680541032",
    "🇧🇴": "5913638795101606133",
    "🇧🇹": "5913236734623093021",
    "🇦🇷": "5913573356979884082",
    "🇦🇺": "5913632326880858455",
    "🇦🇹": "5911338831524664592",
    "🇧🇸": "5911451643135660214",
    "🇧🇭": "5913581663446634403",
    "🇧🇧": "5911016996740272263",
    "🇧🇪": "5913529642802745141",
    "🇧🇿": "5913355005137522807",
    "🇦🇬": "5913389025573475085",
    "🇦🇴": "5913753316109586411",
    "🇦🇩": "5911314702398396902",
    "🇩🇿": "5913782968563800236",
    "🇦🇱": "5911357458797826163",
    "🇦𝒇": "5913492040364068694",
    "🇿🇼": "5911092502265336396"
}

def p_em(key: str, fallback: str = "⭐") -> str:
    key_clean = str(key).strip().lower()
    if key_clean in EMOJI_ID_MAP:
        return f'<tg-emoji emoji-id="{EMOJI_ID_MAP[key_clean]}">{fallback}</tg-emoji>'
    if key in PREMIUM_FLAGS:
        return f'<tg-emoji emoji-id="{PREMIUM_FLAGS[key]}">{fallback}</tg-emoji>'
    return fallback

def strip_html_tags(text: str) -> str:
    return re.sub(r'<[^>]*>', '', str(text))

# ==================== CONFIG SECTION ====================

BOT_TOKEN = "8971890372:AAEGoTShXmgGo2MTE-AVvtyxXgj8S484hWM"
API_KEY = "mino_live_e73130c6a572f6057276f8b8743cd95b"  
BASE_URL = "https://mino-sms-panel.xyz"      

# --- SYSTEM IDS & ADMINS ---
ADMINS = [5587354616]
OTP_GROUP_ID = -5545576883

# --- SYSTEM LINKS & USERNAME SETTINGS ---
DEFAULT_WELCOME_MESSAGE = f"{p_em('live')} <b>MINO NUMBER BOT</b> {p_em('live')}\n━━━━━━━━━━━━━━━━━━━━━━━━\n{p_em('status')} <b>START INSTANT OTP RECEPTION NOW!</b> {p_em('status')}\n━━━━━━━━━━━━━━━━━━━━━━━━"
DEFAULT_OTP_GROUP_URL = "https://t.me/+zJLrtLvuuAAzMmY1"
DEFAULT_CHANNEL_URL = "https://t.me/rjonlinejobbd"
DEFAULT_SUPPORT_USERNAME = "@tanjimsaykot"
FORCE_JOIN_CHANNELS = ["https://t.me/rjonlinejobbd"]

# --- WITHDRAWAL & STATS LIMITS ---
DEFAULT_MIN_WITHDRAW = 0.5
DEFAULT_MAX_WITHDRAW = 100.0
DEFAULT_COOLDOWN_TIME = 1.0
DEFAULT_OTP_REWARD = 0.0020
DEFAULT_REFER_BONUS = 0.050
DEFAULT_NUMBERS_PER_REQUEST = 3
MAX_NUMBERS_PER_USER = 10000

# --- DATA FILES ---
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SETTINGS_FILE = "settings.json"
ACTIVE_NUMBERS_FILE = "active_numbers.json"
MANUAL_RANGES_FILE = "manual_ranges.json"

# ========================================================

def load_active_numbers():
    if not os.path.exists(ACTIVE_NUMBERS_FILE):
        return {}
    try:
        with open(ACTIVE_NUMBERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_active_numbers(data):
    try:
        with open(ACTIVE_NUMBERS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving active numbers: {e}")

# ==================== MANUAL RANGE STORAGE ====================

def load_manual_ranges():
    if not os.path.exists(MANUAL_RANGES_FILE):
        with open(MANUAL_RANGES_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(MANUAL_RANGES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_manual_ranges(data):
    try:
        with open(MANUAL_RANGES_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving manual ranges: {e}")

# ==================== BUTTON COLOR PATCH ENGINE ====================

def rbtn(text: str, style: str = None, callback_data: str = None, url: str = None, icon_custom_emoji_id: str = None):
    clean_text = strip_html_tags(text)
    kwargs = {"text": clean_text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    
    if style:
        kwargs["style"] = style
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
        
    try:
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("style", None)
        kwargs.pop("icon_custom_emoji_id", None)
        
        api_kwargs = {}
        if style:
            api_kwargs["style"] = style
        if icon_custom_emoji_id:
            api_kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
            
        if api_kwargs:
            kwargs["api_kwargs"] = api_kwargs
            
        return InlineKeyboardButton(**kwargs)


def rkbtn(text: str, icon_custom_emoji_id: str = None, style: str = None):
    kwargs = {"text": text}
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
    if style:
        kwargs["style"] = style
        
    try:
        return KeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("icon_custom_emoji_id", None)
        kwargs.pop("style", None)
        api_kwargs = {}
        if icon_custom_emoji_id:
            api_kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
        if style:
            api_kwargs["style"] = style
        if api_kwargs:
            kwargs["api_kwargs"] = api_kwargs
        return KeyboardButton(**kwargs)

# ==================== SYSTEM DYNAMIC SETTINGS ====================

def load_settings():
    default_settings = {
        "max_numbers_per_user": MAX_NUMBERS_PER_USER,
        "welcome_message": DEFAULT_WELCOME_MESSAGE,
        "otp_group_url": DEFAULT_OTP_GROUP_URL,
        "channel_url": DEFAULT_CHANNEL_URL,
        "support_username": DEFAULT_SUPPORT_USERNAME,
        "maintenance_mode": False,
        "min_withdraw": DEFAULT_MIN_WITHDRAW,
        "max_withdraw": DEFAULT_MAX_WITHDRAW,
        "api_key": API_KEY,
        "base_url": BASE_URL,
        "cooldown_time": DEFAULT_COOLDOWN_TIME,          
        "force_join_enabled": False,   
        "force_join_channels": FORCE_JOIN_CHANNELS, 
        "join_alert_enabled": True,     
        "otp_reward": DEFAULT_OTP_REWARD,          
        "refer_bonus": DEFAULT_REFER_BONUS,          
        "numbers_per_request": DEFAULT_NUMBERS_PER_REQUEST,
        "auto_range": True      
    }

    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default_settings, f, indent=1)
        return default_settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            
        updated = False
        
        for k, v in default_settings.items():
            if k not in data:
                data[k] = v
                updated = True
                
        if updated:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=1)
        return data
    except:
        return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=1)

def get_api_credentials():
    settings = load_settings()
    raw_key = settings.get("api_key", API_KEY)
    raw_url = settings.get("base_url", BASE_URL)
    raw_url = str(raw_url).strip().rstrip('/')
    return raw_key, raw_url

def get_withdraw_limits():
    settings = load_settings()
    return float(settings.get("min_withdraw", DEFAULT_MIN_WITHDRAW)), float(settings.get("max_withdraw", DEFAULT_MAX_WITHDRAW))

def is_under_maintenance(uid):
    settings = load_settings()
    return settings.get("maintenance_mode", False) and not is_admin(uid)

request_queue = asyncio.Queue() 
MAX_WORKERS = 50000 

client_async = httpx.AsyncClient(
    timeout=10.0,
    verify=False,
    limits=httpx.Limits(max_connections=1000, max_keepalive_connections=200)
)

active_numbers = load_active_numbers()
last_range = {}
last_request_time = {} 
CHECK_INTERVAL = 0.1

# ==================== GLOBAL RANGES CACHE ====================
_ranges_cache = {"data": None, "updated_at": 0.0, "fetching": False}

def get_platform_icon(platform_name: str) -> str:
    name_lower = platform_name.lower().strip()
    if name_lower in EMOJI_ID_MAP:
        return p_em(name_lower)
    return ""

def make_bold_text(text: str) -> str:
    out = []
    for char in str(text):
        o = ord(char)
        if 65 <= o <= 90: 
            out.append(chr(o - 65 + 0x1D5D4))
        elif 97 <= o <= 122: 
            out.append(chr(o - 97 + 0x1D5EE))
        elif 48 <= o <= 57: 
            out.append(chr(o - 48 + 0x1D7EC))
        else:
            out.append(char)
    return "".join(out)

def unstyle_text(text: str) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize('NFKC', str(text))
    return normalized

async def _bg_refresh_ranges():
    global _ranges_cache
    while True:
        try:
            settings = load_settings()
            if settings.get("auto_range", True) and not _ranges_cache["fetching"]:
                _ranges_cache["fetching"] = True
                try:
                    data, err = await fetch_top55_ranges_by_app()
                    if data:
                        import time as _time
                        _ranges_cache["data"] = data
                        _ranges_cache["updated_at"] = _time.monotonic()
                except Exception:
                    pass
                finally:
                    _ranges_cache["fetching"] = False
        except Exception:
            pass
        await asyncio.sleep(200)

# ==================== CHECK IF USER IS ADMIN ====================

def is_admin(user_id):
    return user_id in ADMINS

# ==================== WITHDRAW DATA FUNCTIONS ====================

def load_withdraw_requests():
    if not os.path.exists(WITHDRAW_DATA_FILE):
        with open(WITHDRAW_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(WITHDRAW_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_withdraw_requests(data):
    with open(WITHDRAW_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

# ==================== BANNED USERS FUNCTIONS ====================

def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_banned_users(banned_list):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(banned_list, f, indent=4)

def is_user_banned(uid):
    banned_list = load_banned_users()
    return str(uid) in banned_list

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

# ==================== DATA RANGE FILE ====================

def load_range_db():
    if not os.path.exists(DATA_RANGE_FILE):
        return {}
    try:
        with open(DATA_RANGE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_range_db(data):
    with open(DATA_RANGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_number_range_info(uid, number, range_text):
    db = load_range_db()
    flag_html, name = get_country_info(number)
    db[normalize_number(number)] = {
        "user_id": str(uid),
        "number": f"+{normalize_number(number)}",
        "range": range_text,
        "country": f"{flag_html} {name}"
    }
    save_range_db(db)

# ==================== COUNTRY MAPPING SECTION ====================

def get_country_info(number):
    number_str = str(number).strip()
    if '|' in number_str:
        number_str = number_str.split('|')[-1].strip()
        
    clean_num = re.sub(r'[^\w]', '', number_str).replace('_', '').replace(" ", "").strip()
    
    country_map = {
        "2376": ("🇨🇲", "Cameroon"),
        "2250": ("🇨🇮", "Ivory Coast"),
        "2613": ("🇲🇬", "Madagascar"),
        "4077": ("🇷🇴", "Romania"),
        "447": ("🇬🇧", "UK (Virtual)"),
        "1201": ("🇺🇸", "USA (Virtual)"),
        "1302": ("🇺🇸", "USA (Virtual)"),
        "1415": ("🇺🇸", "USA (Virtual)"),
        "1212": ("🇺🇸", "USA (Virtual)"),
        "1917": ("🇺🇸", "USA (Virtual)"),
        "1646": ("🇺🇸", "USA (Virtual)"),
        "1347": ("🇺🇸", "USA (Virtual)"),
        "237": ("🇨🇲", "Cameroon"),
        "225": ("🇨🇮", "Ivory Coast"),
        "261": ("🇲🇬", "Madagascar"),
        "20": ("🇪🇬", "Egypt"),
        "27": ("🇿🇦", "South Africa"),
        "234": ("🇳🇬", "Nigeria"),
        "254": ("🇰🇪", "Kenya"),
        "233": ("🇬🇭", "Ghana"),
        "212": ("🇲🇦", "Morocco"),
        "213": ("🇩🇿", "Algeria"),
        "216": ("🇹🇳", "Tunisia"),
        "218": ("🇱🇾", "Libya"),
        "249": ("🇸🇩", "Sudan"),
        "251": ("🇪🇹", "Ethiopia"),
        "252": ("🇸🇴", "Somalia"),
        "253": ("🇩🇿", "Djibouti"),
        "255": ("🇹🇿", "Tanzania"),
        "256": ("🇺🇬", "Uganda"),
        "257": ("🇧🇮", "Burundi"),
        "258": ("🇲🇿", "Mozambique"),
        "260": ("🇿🇲", "Zambia"),
        "263": ("🇿🇼", "Zimbabwe"),
        "264": ("🇳🇦", "Namibia"),
        "265": ("🇲🇼", "Malawi"),
        "266": ("🇱🇸", "Lesotho"),
        "267": ("🇧🇼", "Botswana"),
        "268": ("🇸🇿", "Eswatini"),
        "269": ("🇰🇲", "Comoros"),
        "220": ("🇬🇲", "Gambia"),
        "221": ("🇸🇳", "Senegal"),
        "222": ("🇲🇷", "Mauritania"),
        "223": ("🇲🇱", "Mali"),
        "224": ("🇬🇳", "Guinea"),
        "226": ("🇧🇫", "Burkina Faso"),
        "227": ("🇳🇪", "Niger"),
        "228": ("🇹🇬", "Togo"),
        "229": ("🇧🇯", "Benin"),
        "230": ("🇲🇺", "Mauritius"),
        "231": ("🇱🇷", "Liberia"),
        "232": ("🇸🇱", "Sierra Leone"),
        "235": ("🇹🇩", "Chad"),
        "236": ("🇨🇫", "Central African Republic"),
        "238": ("🇨🇻", "Cape Verde"),
        "239": ("🇸🇹", "Sao Tome and Principe"),
        "240": ("🇬🇶", "Equatorial Guinea"),
        "241": ("🇬🇦", "Gabon"),
        "242": ("🇨🇬", "Congo"),
        "243": ("🇨🇩", "DR Congo"),
        "244": ("🇦🇴", "Angola"),
        "245": ("🇬🇼", "Guinea-Bissau"),
        "247": ("🇸🇭", "Saint Helena"),
        "248": ("🇸🇨", "Seychelles"),
        "250": ("🇷🇼", "Rwanda"),
        "290": ("🇸🇭", "Saint Helena"),
        "291": ("🇪🇷", "Eritrea"),
        "40": ("🇷🇴", "Romania"),
        "44": ("🇬🇧", "United Kingdom"),
        "33": ("🇫🇷", "France"),
        "49": ("🇩🇪", "Germany"),
        "39": ("🇮🇹", "Italy"),
        "34": ("🇪🇸", "Spain"),
        "31": ("🇳🇱", "Netherlands"),
        "32": ("🇧🇪", "Belgium"),
        "41": ("🇨🇭", "Switzerland"),
        "43": ("🇦🇹", "Austria"),
        "46": ("🇸🇪", "Sweden"),
        "47": ("🇳🇴", "Norway"),
        "45": ("🇩🇰", "Denmark"),
        "358": ("🇫🇮", "Finland"),
        "351": ("🇵🇹", "Portugal"),
        "353": ("🇮🇪", "Ireland"),
        "36": ("🇭🇺", "Hungary"),
        "48": ("🇵🇱", "Poland"),
        "380": ("🇺🇦", "Ukraine"),
        "370": ("🇱🇹", "Lithuania"),
        "371": ("🇱🇻", "Latvia"),
        "372": ("🇪🇪", "Estonia"),
        "373": ("🇲🇩", "Moldova"),
        "374": ("🇦🇲", "Armenia"),
        "375": ("🇧🇾", "Belarus"),
        "376": ("🇦🇩", "Andorra"),
        "377": ("🇲🇨", "Monaco"),
        "378": ("🇸🇲", "San Marino"),
        "381": ("🇷🇸", "Serbia"),
        "382": ("🇲🇪", "Montenegro"),
        "383": ("🇽ковой", "Kosovo"),
        "385": ("🇭🇷", "Croatia"),
        "386": ("🇸🇮", "Slovenia"),
        "387": ("🇧🇦", "Bosnia and Herzegovina"),
        "389": ("🇲🇰", "North Macedonia"),
        "350": ("🇬🇮", "Gibraltar"),
        "352": ("🇱🇺", "Luxembourg"),
        "354": ("🇮🇸", "Iceland"),
        "355": ("🇦🇱", "Albania"),
        "356": ("🇲🇹", "Malta"),
        "357": ("🇨🇾", "Cyprus"),
        "359": ("🇧🇬", "Bulgaria"),
        "421": ("🇸🇰", "Slovakia"),
        "420": ("🇨🇿", "Czech Republic"),
        "298": ("🇫🇴", "Faroe Islands"),
        "299": ("🇬🇱", "Greenland"),
        "1": ("🇺🇸", "United States / Canada"),
        "7": ("🇷🇺", "Russia / Kazakhstan"),
        "880": ("🇧🇩", "Bangladesh"),
        "86": ("🇨🇳", "China"),
        "81": ("🇯🇵", "Japan"),
        "82": ("🇰🇷", "South Korea"),
        "84": ("🇻🇳", "Vietnam"),
        "66": ("🇹🇭", "Thailand"),
        "62": ("🇮🇩", "Indonesia"),
        "60": ("🇲🇾", "Malaysia"),
        "65": ("🇸🇬", "Singapore"),
        "63": ("🇵🇭", "Philippines"),
        "95": ("🇲🇲", "Myanmar"),
        "94": ("🇱🇰", "Sri Lanka"),
        "977": ("🇳🇵", "Nepal"),
        "93": ("🇦𝒇", "Afghanistan"),
        "98": ("🇮🇷", "Iran"),
        "90": ("🇹🇷", "Turkey"),
        "964": ("🇮🇶", "Iraq"),
        "963": ("🇸🇾", "Syria"),
        "961": ("🇱🇧", "Lebanon"),
        "962": ("🇯🇴", "Jordan"),
        "965": ("🇰🇼", "Kuwait"),
        "966": ("🇸🇦", "Saudi Arabia"),
        "967": ("🇾🇪", "Yemen"),
        "968": ("🇴🇲", "Oman"),
        "971": ("🇦🇪", "United Arab Emirates"),
        "972": ("🇮🇱", "Israel"),
        "973": ("🇧🇭", "Bahrain"),
        "974": ("🇶🇦", "Qatar"),
        "994": ("🇦🇿", "Azerbaijan"),
        "995": ("🇬🇪", "Georgia"),
        "996": ("🇰🇬", "Kyrgyzstan"),
        "992": ("🇹🇯", "Tajikistan"),
        "993": ("🇹🇲", "Turkmenistan"),
        "998": ("🇺🇿", "Uzbekistan"),
        "855": ("🇰🇭", "Cambodia"),
        "856": ("🇱🇦", "Laos"),
        "976": ("🇲🇳", "Mongolia"),
        "850": ("🇰🇵", "North Korea"),
        "55": ("🇧🇷", "Brazil"),
        "52": ("🇲🇽", "Mexico"),
        "54": ("🇦🇷", "Argentina"),
        "57": ("🇨🇴", "Colombia"),
        "51": ("🇵🇪", "Peru"),
        "58": ("🇻🇪", "Venezuela"),
        "56": ("🇨🇱", "Chile"),
        "593": ("🇪🇨", "Ecuador"),
        "591": ("🇧🇴", "Bolivia"),
        "595": ("🇵🇾", "Paraguay"),
        "598": ("🇺🇾", "Uruguay"),
        "502": ("🇬🇹", "Guatemala"),
        "503": ("🇸🇻", "El Salvador"),
        "504": ("🇭🇳", "Honduras"),
        "505": ("🇳🇮", "Nicaragua"),
        "506": ("🇨🇷", "Costa Rica"),
        "507": ("🇵🇦", "Panama"),
        "509": ("🇭🇹", "Haiti"),
        "501": ("🇧🇿", "Belize"),
        "61": ("🇦🇺", "Australia"),
        "64": ("🇳🇿", "New Zealand"),
        "675": ("🇵🇬", "Papua New Guinea"),
        "679": ("🇫🇯", "Fiji"),
        "685": ("🇼🇸", "Samoa"),
        "686": ("🇰🇮", "Kiribati"),
        "691": ("🇫🇲", "Micronesia"),
        "692": ("🇲🇭", "Marshall Islands"),
        "297": ("🇦🇼", "Aruba"),
        "1246": ("🇧🇧", "Barbados"),
        "1441": ("🇧🇲", "Bermuda"),
        "1345": ("🇰🇾", "Cayman Islands"),
        "53": ("🇨🇺", "Cuba"),
        "1473": ("🇬🇩", "Grenada"),
        "592": ("🇬🇾", "Guyana"),
        "1876": ("🇯🇲", "Jamaica"),
        "1758": ("🇱🇨", "Saint Lucia"),
        "1784": ("🇻🇨", "Saint Vincent"),
        "1868": ("🇹🇹", "Trinidad and Tobago"),
        "267": ("🇧🇼", "Botswana"),
        "387": ("🇧🇦", "Bosnia and Herzegovina"),
        "591": ("🇧🇴", "Bolivia"),
        "975": ("🇧🇹", "Bhutan"),
        "54": ("🇦🇷", "Argentina"),
        "61": ("🇦🇺", "Australia"),
        "43": ("🇦🇹", "Austria"),
        "1242": ("🇧🇸", "Bahamas"),
        "973": ("🇧🇭", "Bahrain"),
        "1246": ("🇧🇧", "Barbados"),
        "32": ("🇧🇪", "Belgium"),
        "501": ("🇧🇿", "Belize"),
        "1268": ("🇦🇬", "Antigua and Barbuda"),
        "244": ("🇦🇴", "Angola"),
        "376": ("🇦🇩", "Andorra"),
        "213": ("🇩🇿", "Algeria"),
        "355": ("🇦🇱", "Albania"),
        "93": ("🇦𝒇", "Afghanistan"),
        "263": ("🇿🇼", "Zimbabwe")
    }
    
    sorted_prefixes = sorted(country_map.keys(), key=len, reverse=True)
    for prefix in sorted_prefixes:
        if clean_num.startswith(prefix):
            raw_flag, c_name = country_map[prefix]
            return p_em(raw_flag, raw_flag), c_name
    
    return p_em("🇨🇮", "🇨🇮"), "IVORY COAST"

# ==================== SERVICE DETECTION & CLEANING ====================

def get_clean_app_name(app_name: str) -> str:
    name_lower = app_name.lower().strip()
    
    if "facebook" in name_lower or name_lower == "fb":
        return "Facebook"
    if "instagram" in name_lower or "instragram" in name_lower or name_lower == "insta":
        return "Instagram"
    if "whatsapp" in name_lower or "whats app" in name_lower:
        return "WhatsApp"
    if "tiktok" in name_lower:
        return "TikTok"
    if "telegram" in name_lower or name_lower == "tg":
        return "Telegram"
    if "uber" in name_lower or "ubar" in name_lower:
        return "Uber"
    if "daraz" in name_lower:
        return "Daraz"
    if "imo" in name_lower:
        return "Imo"
    if "discord" in name_lower:
        return "Discord"
    if "linkedin" in name_lower:
        return "Linkedin"
    if "bumble" in name_lower:
        return "Bumble"
        
    return app_name.strip().title()

def detect_service(full_sms):
    if not full_sms:
        return "SMS SERVICE"
    
    sms_lower = full_sms.lower()
    
    service_keywords = {
        "facebook": "FACEBOOK", "fb": "FACEBOOK", "instagram": "INSTAGRAM", "insta": "INSTAGRAM",
        "tiktok": "TIKTOK", "whatsapp": "WHATSAPP", "whats app": "WHATSAPP", "telegram": "TELEGRAM",
        "tg": "TELEGRAM", "discord": "DISCORD", "imo": "IMO", "uber": "UBER", "daraz": "DARAZ",
        "linkedin": "LINKEDIN", "bumble": "BUMBLE"
    }
    
    for keyword, service_name in sorted(service_keywords.items(), key=lambda x: len(x[0]), reverse=True):
        if keyword in sms_lower:
            return service_name
    
    return "SMS SERVICE"

# ==================== KEYBOARDS SECTION ====================

def main_keyboard(user_id):
    keyboard = [
        [rkbtn(make_bold_text("GET NUMBER"), icon_custom_emoji_id=EMOJI_ID_MAP.get("get_number_btn"), style="danger")],
        [
            rkbtn(make_bold_text("TRAFFIC"), icon_custom_emoji_id=EMOJI_ID_MAP.get("live"), style="primary"),
            rkbtn(make_bold_text("LEADERBOARD"), icon_custom_emoji_id=EMOJI_ID_MAP.get("leader_board"), style="primary")
        ],
        [
            rkbtn(make_bold_text("BALANCE"), icon_custom_emoji_id=EMOJI_ID_MAP.get("money"), style="success"), 
            rkbtn(make_bold_text("REFER & EARN"), icon_custom_emoji_id=EMOJI_ID_MAP.get("refer_btn"), style="success")
        ],
        [
            rkbtn(make_bold_text("SUPPORT"), icon_custom_emoji_id=EMOJI_ID_MAP.get("msg"), style="primary")
        ]
    ]
    if is_admin(user_id):
        keyboard.append([rkbtn(make_bold_text("ADMIN PANEL"), icon_custom_emoji_id=EMOJI_ID_MAP.get("admin"), style="primary")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    keyboard = [[rkbtn("CANCEL", icon_custom_emoji_id=EMOJI_ID_MAP.get("cross"), style="danger")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== ADMIN PANEL KEYBOARDS ====================

def admin_main_keyboard():
    keyboard = [
        [
            rkbtn("SYSTEM CONFIG", icon_custom_emoji_id=EMOJI_ID_MAP.get("setting"), style="primary"), 
            rkbtn("USER & BALANCE", icon_custom_emoji_id=EMOJI_ID_MAP.get("money"), style="success")
        ],
        [
            rkbtn("SECURITY & JOIN", icon_custom_emoji_id=EMOJI_ID_MAP.get("link"), style="primary"), 
            rkbtn("NOTICE & B-CAST", icon_custom_emoji_id=EMOJI_ID_MAP.get("live"), style="primary")
        ],
        [
            rkbtn("BACK TO MAIN", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"), style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_system_config_keyboard():
    keyboard = [
        [
            rkbtn("SET MAX NUMBERS LIMIT", icon_custom_emoji_id=EMOJI_ID_MAP.get("setting"), style="primary"), 
            rkbtn("SET WITHDRAW LIMITS", icon_custom_emoji_id=EMOJI_ID_MAP.get("money"), style="success")
        ],
        [
            rkbtn("SET OTP BONUS", icon_custom_emoji_id=EMOJI_ID_MAP.get("add"), style="success"), 
            rkbtn("SET REFER BONUS", icon_custom_emoji_id=EMOJI_ID_MAP.get("gift_box"), style="success")
        ],
        [
            rkbtn("SET NUMBERS PER REQUEST", icon_custom_emoji_id=EMOJI_ID_MAP.get("get_number_btn"), style="primary"), 
            rkbtn("SET COOLDOWN", icon_custom_emoji_id=EMOJI_ID_MAP.get("waiting"), style="primary")
        ],
        [
            rkbtn("TOGGLE AUTO RANGE", icon_custom_emoji_id=EMOJI_ID_MAP.get("status"), style="primary"),
            rkbtn("MANAGE MANUAL RANGES", icon_custom_emoji_id=EMOJI_ID_MAP.get("setting"), style="primary")
        ],
        [
            rkbtn("TOGGLE MAINTENANCE", icon_custom_emoji_id=EMOJI_ID_MAP.get("stop"), style="danger"), 
            rkbtn("BACK TO ADMIN", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"), style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_user_balance_keyboard():
    keyboard = [
        [
            rkbtn("ADD BALANCE", icon_custom_emoji_id=EMOJI_ID_MAP.get("add"), style="success"), 
            rkbtn("REMOVE BALANCE", icon_custom_emoji_id=EMOJI_ID_MAP.get("delete"), style="danger")
        ],
        [
            rkbtn("DIRECT MSG USER", icon_custom_emoji_id=EMOJI_ID_MAP.get("msg"), style="primary"), 
            rkbtn("SEARCH BY USERNAME", icon_custom_emoji_id=EMOJI_ID_MAP.get("status"), style="primary")
        ],
        [
            rkbtn("USER STATUS CHECK", icon_custom_emoji_id=EMOJI_ID_MAP.get("status"), style="primary"), 
            rkbtn("ALL USER ID", icon_custom_emoji_id=EMOJI_ID_MAP.get("link"), style="primary")
        ],
        [
            rkbtn("ALL USER BALANCE", icon_custom_emoji_id=EMOJI_ID_MAP.get("money"), style="success"), 
            rkbtn("BACK TO ADMIN", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"), style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_security_join_keyboard():
    keyboard = [
        [
            rkbtn("SET FORCE JOIN", icon_custom_emoji_id=EMOJI_ID_MAP.get("link"), style="primary"), 
            rkbtn("TOGGLE FORCE JOIN", icon_custom_emoji_id=EMOJI_ID_MAP.get("status"), style="primary")
        ],
        [
            rkbtn("BAN USER", icon_custom_emoji_id=EMOJI_ID_MAP.get("ban"), style="danger"), 
            rkbtn("UNBAN USER", icon_custom_emoji_id=EMOJI_ID_MAP.get("done"), style="success")
        ],
        [
            rkbtn("BAN USER LIST", icon_custom_emoji_id=EMOJI_ID_MAP.get("status"), style="primary"), 
            rkbtn("TOGGLE JOIN ALERT", icon_custom_emoji_id=EMOJI_ID_MAP.get("live"), style="primary")
        ],
        [
            rkbtn("BACK TO ADMIN", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"), style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_notice_bcast_keyboard():
    keyboard = [
        [
            rkbtn("BROADCAST NOTICE", icon_custom_emoji_id=EMOJI_ID_MAP.get("live"), style="primary"), 
            rkbtn("B-CAST WITH BUTTON", icon_custom_emoji_id=EMOJI_ID_MAP.get("link"), style="primary")
        ],
        [
            rkbtn("EDIT LINKS & TEXTS", icon_custom_emoji_id=EMOJI_ID_MAP.get("setting"), style="primary"), 
            rkbtn("BACK TO ADMIN", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"), style="danger")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

MENU_BUTTONS = {
    "GET NUMBER", "TRAFFIC", "LEADERBOARD", "SUPPORT", "ADMIN PANEL", "BALANCE", "REFER & EARN",
    "BACK TO MAIN", "BACK TO ADMIN", "CANCEL", "ADD BALANCE", "REMOVE BALANCE", 
    "SET MAX NUMBERS LIMIT", "EDIT LINKS & TEXTS", "BAN USER", "UNBAN USER",
    "BAN USER LIST", "SEND MESSAGE TO ALL USERS", "ALL USER ID", "ALL USER BALANCE",
    "SET WITHDRAW LIMITS", "TOGGLE MAINTENANCE", "RESET DAILY LIMITS",
    "DIRECT MSG USER", "SEARCH BY USERNAME", "SET FORCE JOIN", 
    "TOGGLE FORCE JOIN", "SET COOLDOWN", "BROADCAST NOTICE", "RESET LEADERBOARD",
    "SET OTP BONUS", "SET REFER BONUS", "SET NUMBERS PER REQUEST",
    "SYSTEM CONFIG", "USER & BALANCE", "SECURITY & JOIN", "NOTICE & B-CAST", "TOGGLE JOIN ALERT",
    "TOGGLE AUTO RANGE", "MANAGE MANUAL RANGES"
}

# ==================== HELPER FUNCTIONS SECTION ====================

def clean_range_id(range_str: str) -> str:
    if not range_str:
        return ""
    number_str = str(range_str).strip()
    if '|' in number_str:
        number_str = number_str.split('|')[-1].strip()
    return re.sub(r'[^\w]', '', number_str).replace('_', '').replace(" ", "").strip()

def format_balance(balance):
    return f"{balance:.4f}"

# ==================== OPTIMIZED OTP DETECTOR (FIXED N/A) ====================

def extract_otp(text):
    if not text or text == "No Content": 
        return "N/A"
    
    text_clean = str(text).strip()
    
    label_match = re.search(
        r'(?:code|otp|verify|verification|pin|gd|confirmation|kod|passcode|pass|identifier)[\s:-]+([a-zA-Z0-9]{3,10}(?:[\s-][a-zA-Z0-9]{3,10})?)\b', 
        text_clean, 
        re.IGNORECASE
    )
    if label_match:
        candidate = label_match.group(1).strip()
        if 3 <= len(candidate) <= 12 and not candidate.isalpha():
            return candidate
        elif candidate.isdigit():
            return candidate
            
    spaced_otp = re.search(r'\b(\d{3}[\s-]\d{3})\b', text_clean)
    if spaced_otp:
        return spaced_otp.group(1)
        
    digit_match = re.search(r'\b(\d{4,8})\b', text_clean)
    if digit_match:
        return digit_match.group(1)
        
    alphanum_match = re.search(r'\b([A-Z0-9]{4,8})\b', text_clean)
    if alphanum_match:
        return alphanum_match.group(1)
        
    url_match = re.search(r'https?://[^\s]+', text_clean)
    if url_match:
        url = url_match.group(0).strip()
        parsed_url = url.split('?')[0]  
        path_parts = [p for p in parsed_url.rstrip('/').split('/') if p]
        if len(path_parts) > 2:  
            last_part = path_parts[-1]
            if len(last_part) >= 4 and any(c.isalnum() for c in last_part):
                return last_part
        return url  
        
    numbers_only = re.sub(r'\D', '', text_clean)
    if 4 <= len(numbers_only) <= 8:
        return numbers_only
        
    return "N/A"

def normalize_number(num):
    return re.sub(r'\D', '', str(num))

def mask_number(num):
    num_str = str(num).replace('+', '').replace(' ', '').strip()
    if len(num_str) >= 8:
        return f"{num_str[:4]}✦✦✦{num_str[-4:]}"
    elif len(num_str) > 4:
        half = len(num_str) // 2
        return f"{num_str[:half]}✦✦✦{num_str[half:]}"
    return num_str

def format_otp_display(otp):
    otp = str(otp).strip()
    if otp.isdigit() and len(otp) == 6:
        return f"{otp[:3]}-{otp[3:]}"
    return otp

def get_date_reset_time():
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    return today_midnight

def is_valid_bangladesh_number(number):
    number = re.sub(r'\D', '', str(number))
    return len(number) == 11 and number.startswith('01')

def is_range_request(param):
    if not param:
        return False
    param_upper = str(param).upper().strip()
    
    if 'X' in param_upper:
        return True
        
    if param_upper.isdigit():
        if len(param_upper) <= 8:
            return True
            
    if any(char in param_upper for char in ['?', '*', '#', '-']):
        return True
        
    return False

def numbers_match(num1, num2):
    n1 = normalize_number(num1)
    n2 = normalize_number(num2)
    if not n1 or not n2:
        return False
    if n1 == n2:
        return True
    if len(n1) >= 7 and len(n2) >= 7:
        return n1.endswith(n2) or n2.endswith(n1)
    return False

# ==================== DATABASE FUNCTIONS SECTION ====================

def load_data(filename=USER_DATA_FILE):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data, filename=USER_DATA_FILE):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_user(uid, username=None, full_name=None):
    uid = str(uid)
    data = load_data()
    if uid not in data:
        data[uid] = {
            "user_id": uid, 
            "balance": 0.0, 
            "total_numbers": 0, 
            "username": username, 
            "full_name": full_name,
            "referrals": 0,
            "referral_earnings": 0.0,
            "referred_by": None,
            "withdrawal_method": None
        }
        save_data(data)
    else:
        updated = False
        if "referrals" not in data[uid]:
            data[uid]["referrals"] = 0
            updated = True
        if "referral_earnings" not in data[uid]:
            data[uid]["referral_earnings"] = 0.0
            updated = True
        if "referred_by" not in data[uid]:
            data[uid]["referred_by"] = None
            updated = True
        if "withdrawal_method" not in data[uid]:
            data[uid]["withdrawal_method"] = None
            updated = True
        if username: 
            data[uid]["username"] = username
            updated = True
        if full_name: 
            data[uid]["full_name"] = full_name
            updated = True
        if updated:
            save_data(data)
    return data[uid]

async def update_db_balance(uid, amount):
    uid = str(uid)
    data = load_data()
    if uid in data:
        data[uid]["balance"] = round(data[uid].get("balance", 0.0) + amount, 4)
        save_data(data)
        return data[uid]["balance"]
    return 0.0

def get_all_users():
    data = load_data(USER_DATA_FILE)
    return list(data.keys()) if data else []

def user_exists(uid):
    data = load_data(USER_DATA_FILE)
    return str(uid) in data

# ==================== STATS FUNCTIONS SECTION ====================

def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def add_number_taken(uid, count=1):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    for _ in range(count):
        stats[uid]["numbers_taken"].append(now)
    log_global_activity(uid, "NUMBER_TAKEN", {"count": count})
    save_stats(stats)

def add_otp_received(uid):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    stats[uid]["otps_received"].append(now)
    save_stats(stats)

def get_user_stats(uid):
    uid = str(uid)
    stats = load_stats()
    user_stats = stats.get(uid, {"numbers_taken": [], "otps_received": []})
    
    now = datetime.now()
    today_midnight = get_date_reset_time()
    
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    numbers_taken = user_stats.get("numbers_taken", [])
    otps_received = user_stats.get("otps_received", [])
    
    today_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) >= today_midnight)
    today_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) >= today_midnight)
    
    last24h_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_24h)
    last24h_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_24h)
    
    last7d_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_7d)
    last7d_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_7d)
    
    total_numbers = len(numbers_taken)
    total_otps = len(otps_received)
    
    return {
        "total_numbers": total_numbers,
        "total_otps": total_otps,
        "today_numbers": today_numbers,
        "today_otps": today_otps,
        "last24h_numbers": last24h_numbers,
        "last24h_otps": last24h_otps,
        "last7d_numbers": last7d_numbers,
        "last7d_otps": last7d_otps
    }

def log_global_activity(uid, action, details):
    if not os.path.exists(ACTIVITY_LOGS_FILE):
        with open(ACTIVITY_LOGS_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(ACTIVITY_LOGS_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    now = datetime.now()
    log_entry = {
        "uid": str(uid),
        "action": action,
        "details": details,
        "timestamp": now.isoformat(),
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M:%S")
    }
    logs.append(log_entry)
    with open(ACTIVITY_LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def get_global_system_stats():
    stats = load_stats()
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day)
    last_7d = now - timedelta(days=7)
    total_n, total_o = 0, 0
    today_n, today_o = 0, 0
    seven_n, seven_o = 0, 0
    for uid in stats:
        u_stats = stats[uid]
        n_list = u_stats.get("numbers_taken", [])
        o_list = u_stats.get("otps_received", [])
        total_n += len(n_list)
        total_o += len(o_list)
        for t in n_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_n += 1
            if dt >= last_7d: seven_n += 1
        for t in o_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_o += 1
            if dt >= last_7d: seven_o += 1
    return today_n, today_o, seven_n, seven_o, total_n, total_o

# ==================== MINO API - ACTIVE RANGES FLOW ====================

async def fetch_top55_ranges_by_app():
    settings = load_settings()
    auto_range_enabled = settings.get("auto_range", True)
    
    if not auto_range_enabled:
        manual_data = load_manual_ranges()
        top_ranges_by_app = {}
        for app_raw, rng_list in manual_data.items():
            primary_app = get_clean_app_name(app_raw)
            icon = get_platform_icon(primary_app)
            top_ranges_by_app[primary_app] = {
                "icon": icon,
                "ranges": list(rng_list),
                "total_otps": len(rng_list)
            }
        top_ranges_by_app = dict(
            sorted(top_ranges_by_app.items(),
                   key=lambda x: len(x[1]["ranges"]), reverse=True)
        )
        return top_ranges_by_app, None

    api_key, base_url = get_api_credentials()
    masked_key = f"{api_key[:6]}...{api_key[-6:]}" if len(api_key) > 12 else api_key
    print(f"[DEBUG] fetch_top55_ranges_by_app() | API Key: {masked_key} | Base URL: {base_url}")
    
    for attempt in range(2):
        try:
            url = f"{base_url}/liveaccess?api_key={api_key}"
            r = await client_async.get(
                url,
                timeout=httpx.Timeout(connect=4.0, read=10.0, write=4.0, pool=4.0)
            )
            print(f"[DEBUG] API Request to: {base_url}/liveaccess | Status: {r.status_code}")
            
            try:
                data = r.json()
            except Exception as json_err:
                print(f"[DEBUG] JSON Decode Error: {json_err}. Raw text: {r.text[:500]}")
                return None, f"JSONDecodeError: Expecting valid JSON, got HTML or bad response."

            top_ranges_by_app = {}
            
            ranges_dict = None
            if isinstance(data, dict):
                if "ranges" in data and isinstance(data["ranges"], dict):
                    ranges_dict = data["ranges"]
                elif "data" in data and isinstance(data["data"], dict) and "ranges" in data["data"] and isinstance(data["data"]["ranges"], dict):
                    ranges_dict = data["data"]["ranges"]
            
            if ranges_dict:
                for app_raw, rng_list in ranges_dict.items():
                    if not isinstance(rng_list, list):
                        continue
                    primary_app = get_clean_app_name(app_raw)
                    icon = get_platform_icon(primary_app)
                    if primary_app not in top_ranges_by_app:
                        top_ranges_by_app[primary_app] = {"icon": icon, "ranges": [], "total_otps": 0}
                    for rng in rng_list:
                        if rng and rng not in top_ranges_by_app[primary_app]["ranges"]:
                            top_ranges_by_app[primary_app]["ranges"].append(rng)
                    top_ranges_by_app[primary_app]["total_otps"] = len(top_ranges_by_app[primary_app]["ranges"])
            else:
                services_list = []
                if isinstance(data, dict):
                    inner = data.get("data")
                    if isinstance(inner, dict):
                        services_list = inner.get("services") or inner.get("ranges") or []
                    elif isinstance(inner, list):
                        services_list = inner
                    else:
                        services_list = data.get("services") or data.get("ranges") or []
                elif isinstance(data, list):
                    services_list = data
                
                if isinstance(services_list, list):
                    for rng_obj in services_list:
                        if not isinstance(rng_obj, dict):
                            continue
                        primary_raw = rng_obj.get("sid") or rng_obj.get("service") or rng_obj.get("app") or "Unknown"
                        rng_list = rng_obj.get("ranges", [])
                        primary_app = get_clean_app_name(primary_raw)
                        icon = get_platform_icon(primary_app)
                        if primary_app not in top_ranges_by_app:
                            top_ranges_by_app[primary_app] = {"icon": icon, "ranges": [], "total_otps": 0}
                        for rng in rng_list:
                            if rng and rng not in top_ranges_by_app[primary_app]["ranges"]:
                                top_ranges_by_app[primary_app]["ranges"].append(rng)
                        top_ranges_by_app[primary_app]["total_otps"] = len(top_ranges_by_app[primary_app]["ranges"])

            top_ranges_by_app = dict(
                sorted(top_ranges_by_app.items(),
                       key=lambda x: len(x[1]["ranges"]), reverse=True)
            )
            return top_ranges_by_app, None
            
        except Exception as e:
            print(f"[DEBUG] Connection Attempt {attempt+1} Error [{type(e).__name__}]: {e}")
            if attempt == 0:
                await asyncio.sleep(0.3)

    return None, "Server unreachable or invalid API key."

def build_app_buttons_from_cache(top_ranges_by_app):
    buttons = []
    for app_name, info in top_ranges_by_app.items():
        bold_name = make_bold_text(app_name)
        emoji_key = app_name.lower().strip()
        emoji_id = EMOJI_ID_MAP.get(emoji_key)
        buttons.append([rbtn(bold_name, "primary", callback_data=f"sel_app_{app_name}", icon_custom_emoji_id=emoji_id)])
    return buttons

async def show_app_selection(update, context):
    import time as _time
    uid = update.effective_user.id
    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
        await update.message.reply_text(
            f"{p_em('ban')} <b>YOU ARE BANNED</b> {p_em('ban')}\n\n"
            f"<blockquote>{p_em('msg')} Contact Support: {support}</blockquote>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return

    if is_under_maintenance(uid):
        await update.message.reply_text(f"{p_em('stop')} <b>SYSTEM UNDER MAINTENANCE</b> {p_em('stop')}\n\nSorry, the bot is currently undergoing maintenance. Please try again later.", parse_mode="HTML")
        return

    is_joined = await is_user_joined_force_channels(uid, context)
    if not is_joined:
        await update.message.reply_text(
            f"{p_em('channel')} <b>আপনাকে অবশ্যই আমাদের চ্যানেলে জয়েন করতে হবে!</b>\n\nনিচের বোতামগুলো ব্যবহার করে জয়েন করুন এবং চেক বোতামে ক্লিক করুন।",
            parse_mode="HTML",
            reply_markup=build_force_join_keyboard()
        )
        return

    context.user_data.pop("top_ranges_by_app", None)

    settings = load_settings()
    auto_range_enabled = settings.get("auto_range", True)

    cache_age = _time.monotonic() - _ranges_cache["updated_at"]
    if auto_range_enabled and _ranges_cache["data"] and cache_age < 300:
        top_ranges_by_app = _ranges_cache["data"]
        context.user_data["top_ranges_by_app"] = top_ranges_by_app
        buttons = build_app_buttons_from_cache(top_ranges_by_app)
        keyboard = InlineKeyboardMarkup(buttons)
        msg = f"{p_em('get_number_btn')} <b>SELECT APP TO GET</b>"
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return

    status = await update.message.reply_text(f"{p_em('waiting')} Loading ranges...")

    top_ranges_by_app, err = await fetch_top55_ranges_by_app()
    if err or not top_ranges_by_app:
        top_ranges_by_app, err = await fetch_top55_ranges_by_app()

    if err:
        await status.edit_text(
            f"{p_em('cross')} <b>Could not load ranges.</b>\n\n"
            f"<blockquote>{p_em('cross')} {err}</blockquote>",
            parse_mode="HTML"
        )
        return

    if not top_ranges_by_app:
        await status.edit_text(f"{p_em('cross')} No active ranges returned. Please ensure your configuration is correct.")
        return

    if auto_range_enabled:
        _ranges_cache["data"] = top_ranges_by_app
        _ranges_cache["updated_at"] = _time.monotonic()
        
    context.user_data["top_ranges_by_app"] = top_ranges_by_app

    buttons = build_app_buttons_from_cache(top_ranges_by_app)
    keyboard = InlineKeyboardMarkup(buttons)
    msg = f"{p_em('get_number_btn')} <b>SELECT APP TO GET</b>"
    await status.edit_text(msg, parse_mode="HTML", reply_markup=keyboard)

# ==================== TRAFFIC CONTROLLER ====================

async def show_traffic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
        await update.message.reply_text(
            f"{p_em('ban')} <b>YOU ARE BANNED</b> {p_em('ban')}\n\n"
            f"<blockquote>{p_em('msg')} Contact Support: {support}</blockquote>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return

    if is_under_maintenance(uid):
        await update.message.reply_text(f"{p_em('stop')} <b>SYSTEM UNDER MAINTENANCE</b> {p_em('stop')}", parse_mode="HTML")
        return

    is_joined = await is_user_joined_force_channels(uid, context)
    if not is_joined:
        await update.message.reply_text(
            f"{p_em('channel')} <b>আপনাকে অবশ্যই আমাদের চ্যানেলে জয়েন করতে হবে!</b>\n\nনিচের বোতামগুলো ব্যবহার করে জয়েন করুন এবং চেক বোতামে ক্লিক করুন।",
            parse_mode="HTML",
            reply_markup=build_force_join_keyboard()
        )
        return

    if not os.path.exists(ACTIVITY_LOGS_FILE):
        await update.message.reply_text(
            f"{p_em('live')} <b>Live Traffic (Last 1 Hours)</b>\n\n<i>No traffic logs recorded yet.</i>",
            parse_mode="HTML"
        )
        return

    try:
        with open(ACTIVITY_LOGS_FILE, "r") as f:
            logs = json.load(f)
    except Exception:
        logs = []

    one_hour_ago = datetime.now() - timedelta(hours=1)
    otp_logs = []
    
    for log in logs:
        if log.get("action") == "OTP_RECEIVED":
            ts_str = log.get("timestamp")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str)
                    if ts >= one_hour_ago:
                        otp_logs.append(log)
                except Exception:
                    pass

    if not otp_logs:
        await update.message.reply_text(
            f"{p_em('live')} <b>Live Traffic (Last 1 Hours)</b>\n\n<i>No OTP transactions in the last hour.</i>",
            parse_mode="HTML"
        )
        return

    counts = {}
    total_otps = 0
    for log in otp_logs:
        details = log.get("details", {})
        num = details.get("number")
        sms = details.get("sms")
        if num and sms:
            service = detect_service(sms).upper()
            flag_html, country_name = get_country_info(num)
            key = (service, flag_html, country_name)
            counts[key] = counts.get(key, 0) + 1
            total_otps += 1

    if total_otps == 0:
        await update.message.reply_text(
            f"{p_em('live')} <b>Live Traffic (Last 1 Hours)</b>\n\n<i>No OTP transactions in the last hour.</i>",
            parse_mode="HTML"
        )
        return

    sorted_traffic = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    lines = [
        f"{p_em('live')} <b>Live Traffic (Last 1 Hours)</b>\n"
    ]
    
    for (service, flag_html, country_name), count in sorted_traffic:
        percentage = (count / total_otps) * 100
        app_icon = get_platform_icon(service)
        if not app_icon:
            app_icon = p_em("status")
        lines.append(f"{app_icon} <b>{service}</b> | {flag_html} {country_name} | {percentage:.1f}%")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

# ==================== LEADERBOARD CONTROLLER ====================

async def show_leaderboard_command(update, context):
    stats = load_stats()
    sorted_users = []
    for u_id, u_stats in stats.items():
        otp_count = len(u_stats.get("otps_received", []))
        if otp_count > 0:
            sorted_users.append((u_id, otp_count))
    
    sorted_users = sorted(sorted_users, key=lambda x: x[1], reverse=True)[:10]
    
    lines = [
        f"{p_em('leader_board')} <b>OTP LEADERBOARD</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    ]
    if sorted_users:
        for idx, (user_id, count) in enumerate(sorted_users, 1):
            users_db = load_data(USER_DATA_FILE)
            u_info = users_db.get(str(user_id), {})
            name = u_info.get("full_name") or u_info.get("username") or f"User ({user_id[-4:]})"
            lines.append(f"<blockquote><b>#{idx}</b> {html.escape(name)} {p_em('status')} <code>{count} OTPs</code></blockquote>")
    else:
        lines.append("<i>No OTPs received yet. Take numbers and secure the chart!</i>")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")

# ==================== SUPPORT CONTROLLER ====================

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = load_settings()
    support_user = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
    support_text = (
        f"{p_em('msg')} <b>SUPPORT HELP CENTER</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{p_em('link')} <b>CLICK THE BUTTON BELOW TO CONTACT SUPPORT</b> {p_em('link')}"
    )
    keyboard = InlineKeyboardMarkup([
        [rbtn("SUPPORT TEAM", "success", url=f"https://t.me/{support_user.replace('@', '')}", icon_custom_emoji_id=EMOJI_ID_MAP.get("msg"))],
        [rbtn("DEVELOPER", "primary", url="t.me/tanjimsaykot", icon_custom_emoji_id=EMOJI_ID_MAP.get("link"))]
    ])
    await update.message.reply_text(support_text, reply_markup=keyboard, parse_mode="HTML")

# ==================== AUTO OTP MONITOR SECTION ====================

async def monitor_loop(app):
    while True:
        try:
            api_key, base_url = get_api_credentials()
            
            if not api_key:
                await asyncio.sleep(2.0)
                continue
                
            r = await client_async.get(f"{base_url}/success_otp?api_key={api_key}")
            
            try:
                res = r.json()
            except Exception:
                await asyncio.sleep(CHECK_INTERVAL)
                continue
            
            otps = []
            if isinstance(res, dict):
                if "data" in res and isinstance(res["data"], list):
                    otps = res["data"]
                elif "otps" in res and isinstance(res["otps"], list):
                    otps = res["otps"]
                elif "data" in res and isinstance(res["data"], dict) and "otps" in res["data"]:
                    otps = res["data"]["otps"]
                else:
                    otps = res.get("otps") or res.get("data") or []
            elif isinstance(res, list):
                otps = res

            if otps:
                paid_data = load_data(PAID_SMS_FILE)
                range_db = load_data(DATA_RANGE_FILE)
                paid_keys_set = set(paid_data.keys())
                processed_in_session = set()

                for otp in otps:
                    if not isinstance(otp, dict):
                        continue
                    
                    num = normalize_number(otp.get("number") or otp.get("phone") or otp.get("to") or "")
                    full_sms = (
                        otp.get('message') or 
                        otp.get('otp') or 
                        otp.get('sms') or 
                        otp.get('text') or 
                        otp.get('msg') or 
                        otp.get('content') or 
                        "No SMS Content"
                    )
                    
                    raw_otp_code = (
                        otp.get("otp_code") or 
                        otp.get("code") or 
                        otp.get("otp") or 
                        otp.get("otp_code_raw") or
                        otp.get("sms_code")
                    )
                    if raw_otp_code:
                        otp_code = str(raw_otp_code).strip()
                    else:
                        otp_code = extract_otp(full_sms)

                    otp_time = otp.get("created_at") or otp.get("timestamp") or ""
                    otp_id = str(otp.get("otp_id", ""))
                    
                    sms_key = otp_id if otp_id else f"{num}_{otp_code}_{otp_time}"

                    matched_key = None
                    for active_num in active_numbers.keys():
                        if numbers_match(num, active_num):
                            matched_key = active_num
                            break

                    if (matched_key is not None and
                            sms_key not in paid_keys_set and
                            sms_key not in processed_in_session):

                        details = active_numbers[matched_key]
                        paid_keys_set.add(sms_key)
                        processed_in_session.add(sms_key)
                        paid_data[sms_key] = {"uid": details["uid"], "otp": otp_code}

                        settings = load_settings()
                        otp_reward = settings.get("otp_reward", DEFAULT_OTP_REWARD)

                        await update_db_balance(details["uid"], otp_reward)
                        add_otp_received(details["uid"])
                        log_global_activity(details["uid"], "OTP_RECEIVED", {"number": matched_key, "otp": otp_code, "sms": full_sms})

                        num_range_info = range_db.get(matched_key, {}).get("range", "")
                        if not num_range_info:
                            num_range_info = active_numbers.get(matched_key, {}).get("range", "")
                        if not num_range_info and matched_key:
                            _d = re.sub(r'\D', '', str(matched_key))
                            num_range_info = (_d[:-3] + 'XXX') if len(_d) > 3 else (_d + 'XXX')

                        country_flag, country_name = get_country_info(matched_key)
                        service_name = detect_service(full_sms)
                        clean_num = matched_key.replace('+', '').strip()
                        full_number = f"+{clean_num}"
                        masked_number = f"+{mask_number(clean_num)}"

                        safe_full_sms = html.escape(str(full_sms))
                        safe_otp_code = html.escape(str(otp_code))
                        formatted_otp = format_otp_display(otp_code)

                        user_msg = (
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                            f" {p_em('done')} <b>OTP RECEIVED SUCCESSFULLY!</b> {p_em('done')}\n"
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                            f"<blockquote><b>{p_em('get_number_btn')} Number :</b> <code>{full_number}</code></blockquote>\n"
                            f"<blockquote><b>{p_em('waiting')} OTP    :</b> <code>{safe_otp_code}</code></blockquote>\n"
                            f"<blockquote><b>{p_em('money')} Bonus  :</b> <code>+{otp_reward:.4f}$ Credited</code></blockquote>\n"
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                            f" {p_em('msg')} <b>Full SMS:</b>\n"
                            f"<code>{safe_full_sms}</code>\n"
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>"
                        )

                        group_msg = (
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                            f" {p_em('live')} <b>MINO LIVE OTP RECEIVED</b> {p_em('live')}\n"
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                            f"<blockquote><b>{p_em('setting')} App Service :</b> <code>{service_name.upper()}</code></blockquote>\n"
                            f"<blockquote><b>{p_em('get_number_btn')} Mobile No :</b> <code>{masked_number}</code></blockquote>\n"
                            f"<blockquote><b>{p_em('status')} Country  :</b> {country_flag} {country_name}</blockquote>\n"
                            f"<blockquote><b>{p_em('waiting')} OTP Code :</b> <code>{safe_otp_code}</code></blockquote>\n"
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                            f" {p_em('msg')} <b>FULL SMS MESSAGE:</b>\n"
                            f"<code>{safe_full_sms}</code>\n"
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>"
                        )

                        btn_copy = rbtn(text=f"Copy OTP: {formatted_otp}", style="success", callback_data=f"copy_text_{otp_code.replace(' ', '')}")
                        
                        user_otp_keyboard = InlineKeyboardMarkup([
                            [btn_copy]
                        ])

                        group_buttons = InlineKeyboardMarkup([
                            [
                                rbtn("PANEL", "primary", url=settings.get("channel_url", DEFAULT_CHANNEL_URL), icon_custom_emoji_id="5350396951407895212"),
                                rbtn("DEVELOPER", "success", url="https://t.me/NETBOLDNETMAIR0", icon_custom_emoji_id="5271604874419647061")
                            ]
                        ])

                        try:
                            await app.bot.send_message(details["uid"], user_msg, parse_mode="HTML", reply_markup=user_otp_keyboard)
                        except Exception as e:
                            print(f"❌ User Message Send Fail: {e}")

                        try:
                            await app.bot.send_message(OTP_GROUP_ID, group_msg, parse_mode="HTML", reply_markup=group_buttons)
                        except Exception as e:
                            print(f"❌ Group Send Fail: {e}")

                        save_data(paid_data, PAID_SMS_FILE)

                current_time = datetime.now()
                active_numbers_changed = False
                for num_key in list(active_numbers.keys()):
                    entry = active_numbers[num_key]
                    if 'timestamp' not in entry:
                        entry['timestamp'] = current_time.isoformat()
                        active_numbers_changed = True
                    try:
                        ts = datetime.fromisoformat(entry['timestamp'])
                        if (current_time - ts).total_seconds() > 3600:
                            del active_numbers[num_key]
                            active_numbers_changed = True
                    except:
                        pass
                if active_numbers_changed:
                    save_active_numbers(active_numbers)

        except Exception as e:
            print(f"Monitor Error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== WORKER & API SECTION ====================

async def fetch_number_async(range_str):
    try:
        api_key, base_url = get_api_credentials()
        url = f"{base_url}/getnumber"
        
        clean_rid = clean_range_id(range_str)
        print(f"[DEBUG] fetch_number_async | Sending Clean rid: {clean_rid}")
        
        r = await client_async.post(
            url,
            json={"api_key": api_key, "rid": clean_rid, "national": 1, "remove_plus": 1}
        )
        print(f"[DEBUG] POST Request to: {url} | Status: {r.status_code}")
        print(f"[DEBUG] POST Response Body: {r.text}")
        
        try:
            data = r.json()
        except Exception:
            return None
            
        if data.get("status") == "success":
            return data.get("number")
    except Exception as e: 
        print(f"Fetch number error: {e}")
    return None

async def worker():
    while True:
        task = await request_queue.get()
        try:
            if task['type'] == 'process_numbers':
                await process_numbers(task['update'], task['context'], task['range_text'], task['count'], task.get('edit_message'))
            elif task['type'] == 'auto_number':
                await process_auto_number(task['update'], task['context'], task['range_text'])
        except Exception as e:
            print(f"Worker Error: {e}")
        finally:
            request_queue.task_done()

# ==================== AUTO NUMBER FROM LINK SECTION ====================

async def process_auto_number(update, context, range_text):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
        await context.bot.send_message(
            chat_id=chat_id, 
            text=(
                f"{p_em('ban')} <b>YOU ARE BANNED</b> {p_em('ban')}\n\n"
                f"<blockquote>{p_em('msg')} Support: {support}</blockquote>"
            ), 
            parse_mode="HTML", 
            reply_markup=main_keyboard(uid)
        )
        return

    if is_under_maintenance(uid):
        await context.bot.send_message(chat_id=chat_id, text=f"{p_em('stop')} <b>SYSTEM UNDER MAINTENANCE</b>", parse_mode="HTML")
        return

    is_joined = await is_user_joined_force_channels(uid, context)
    if not is_joined:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{p_em('channel')} <b>আপনাকে আমাদের চ্যানেলে জয়েন করতে হবে!</b>",
            parse_mode="HTML",
            reply_markup=build_force_join_keyboard()
        )
        return

    status_msg = await context.bot.send_message(chat_id=chat_id, text=f"{p_em('waiting')} SEARCHING...")

    try:
        result = await fetch_number_async(range_text)
        generated_num = normalize_number(result) if result else None
        
        if not generated_num:
            await status_msg.edit_text(f"{p_em('cross')} NO NUMBERS FOUND. TRY A VALID RANGE.")
            return
        
        add_number_taken(uid, 1)
        last_range[uid] = range_text
        active_numbers[generated_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now().isoformat()}
        save_active_numbers(active_numbers)
        save_number_range_info(uid, generated_num, range_text)
        
        country_flag, country_name = get_country_info(generated_num)
        
        final_text = (
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f" {p_em('get_number_btn')} <b>YOUR ACTIVE NUMBER DETAILS</b> {p_em('get_number_btn')}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<blockquote><b>{p_em('setting')} App     :</b> <code>{context.user_data.get('selected_app', 'Custom Range')}</code></blockquote>\n"
            f"<blockquote><b>{p_em('status')} Country :</b> {country_flag} <code>{country_name}</code></blockquote>\n"
            f"<blockquote><b>{p_em('get_number_btn')} Number  :</b> <code>+{generated_num}</code></blockquote>\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"{p_em('waiting')} <b>SMS STATUS:</b> Waiting for message... {p_em('waiting')}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>"
        )
        
        settings = load_settings()
        otp_group_url = settings.get("otp_group_url", DEFAULT_OTP_GROUP_URL)
        
        keyboard = [
            [rbtn("Change Number", "primary", callback_data="same_range", icon_custom_emoji_id=EMOJI_ID_MAP.get("change_number"))],
            [rbtn("Live OTP Group", "success", url=otp_group_url, icon_custom_emoji_id=EMOJI_ID_MAP.get("live"))]
        ]
        
        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
    except Exception as e:
        print(f"Auto Number Error: {e}")
        await status_msg.edit_text(f"{p_em('cross')} Error occurred: {str(e)}")

# ==================== USER PANEL SECTION ====================

async def process_numbers(update, context, range_text, count, edit_message=None):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
        await context.bot.send_message(
            chat_id=chat_id, 
            text=(
                f"{p_em('ban')} <b>YOU ARE BANNED</b> {p_em('ban')}\n\n"
                f"<blockquote>{p_em('msg')} Support: {support}</blockquote>"
            ), 
            parse_mode="HTML", 
            reply_markup=main_keyboard(uid)
        )
        return

    if is_under_maintenance(uid):
        await context.bot.send_message(chat_id=chat_id, text=f"{p_em('stop')} <b>SYSTEM UNDER MAINTENANCE</b>", parse_mode="HTML")
        return

    if is_joined := await is_user_joined_force_channels(uid, context):
        pass
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{p_em('channel')} <b>আপনাকে আমাদের চ্যানেলে জয়েন করতে হবে!</b>",
            parse_mode="HTML",
            reply_markup=build_force_join_keyboard()
        )
        return

    if not edit_message:
        status_msg = await context.bot.send_message(chat_id=chat_id, text=f"{p_em('waiting')} SEARCHING . . .")  
    else:
        status_msg = edit_message

    try:
        add_number_taken(uid, count)
        last_range[uid] = range_text   

        print(f"[DEBUG] process_numbers() using range: {range_text}")
        tasks = [fetch_number_async(range_text) for _ in range(count)]  
        results = await asyncio.gather(*tasks)  
        generated_nums = [normalize_number(n) for n in results if n]  

        if not generated_nums:  
            err_text = f"{p_em('cross')} NO NUMBERS FOUND. TRY A VALID RANGE."
            await status_msg.edit_text(err_text, parse_mode="HTML")
            return  

        for clean_num in generated_nums:  
            active_numbers[clean_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now().isoformat()}
            save_number_range_info(uid, clean_num, range_text)
        save_active_numbers(active_numbers)

        country_flag, country_name = get_country_info(generated_nums[0])
        
        num_lines = []
        for idx, g_num in enumerate(generated_nums, 1):
            num_lines.append(f"<blockquote>{p_em('get_number_btn')} <b>Number {idx}:</b> <code>+{g_num}</code></blockquote>")

        app_name = context.user_data.get('selected_app', 'Custom Range')
        
        final_text = (
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f" {p_em('get_number_btn')} <b>YOUR ACTIVE NUMBER DETAILS</b> {p_em('get_number_btn')}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<blockquote><b>{p_em('setting')} App     :</b> <code>{app_name}</code></blockquote>\n"
            f"<blockquote><b>{p_em('status')} Country :</b> {country_flag} <code>{country_name}</code></blockquote>\n"
            + "\n".join(num_lines) + "\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"{p_em('waiting')} <b>SMS STATUS:</b> Waiting for message... {p_em('waiting')}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>"
        )  

        settings = load_settings()
        otp_group_url = settings.get("otp_group_url", DEFAULT_OTP_GROUP_URL)

        keyboard = [
            [rbtn("SAME RANGE", "primary", callback_data="same_range", icon_custom_emoji_id=EMOJI_ID_MAP.get("change_number"))],
            [rbtn("OTP GROUP", "success", url=otp_group_url, icon_custom_emoji_id=EMOJI_ID_MAP.get("live"))]
        ]

        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        print(f"Process Number Error: {e}")
        await status_msg.edit_text(f"{p_em('cross')} System Error: {str(e)}", parse_mode="HTML")

# ==================== DYNAMIC FORCE JOIN INTERACTIVE SYSTEM ====================

async def p_em_or_emoji(flag, flag_fallback):
    return p_em(flag, flag_fallback)

async def is_user_joined_force_channels(user_id, context):
    settings = load_settings()
    if not settings.get("force_join_enabled", False):
        return True
    if user_id in ADMINS:
        return True
    channels = settings.get("force_join_channels", [])
    if not channels:
        return True
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True

def build_force_join_keyboard():
    settings = load_settings()
    channels = settings.get("force_join_channels", [])
    buttons = []
    for idx, ch in enumerate(channels, 1):
        clean_ch = ch.replace("@", "")
        buttons.append([rbtn(f"Join Channel {idx}", "primary", url=f"https://t.me/{clean_ch}")])
    buttons.append([rbtn("Check Joined", "success", callback_data="check_force_join")])
    return InlineKeyboardMarkup(buttons)

async def manage_force_join_menu(update_or_query, context, is_callback=False):
    settings = load_settings()
    channels = settings.get("force_join_channels", [])
    
    text = (
        f"{p_em('link')} <b>Force Join Channels Manager</b>\n\n"
        "এখানে আপনার সচল ফোর্স জয়েন চ্যানেলসমূহ রয়েছে। বট ব্যবহারের পূর্বে ইউজারদের অবশ্যই এখানে জয়েন করতে হবে।\n\n"
        "<b>সচল চ্যানেলসমূহ:</b>\n"
    )
    if channels:
        for idx, ch in enumerate(channels, 1):
            text += f"{idx}. <code>{ch}</code>\n"
    else:
        text += "<i>কোনো ফোর্স জয়েন চ্যানেল কনফিগার করা নেই।</i>\n"
        
    status = "Enabled" if settings.get("force_join_enabled", False) else "Disabled"
    text += f"\n<b>সিস্টেম স্ট্যাটাস:</b> {status}"
    
    buttons = []
    for ch in channels:
        buttons.append([rbtn(f"Delete {ch}", "danger", callback_data=f"del_fj_{ch}")])
        
    buttons.append([rbtn("Add Channel", "success", callback_data="add_fj_channel")])
    buttons.append([rbtn("Toggle FJ System", "primary", callback_data="toggle_fj_system")])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    if is_callback:
        await update_or_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update_or_query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

# ==================== ADMIN DYNAMIC MANUAL RANGE PANEL ====================

async def show_manual_ranges_menu(update_or_query, context, is_callback=False):
    settings = load_settings()
    auto_status = "ON" if settings.get("auto_range", True) else "OFF"
    manual_data = load_manual_ranges()
    
    text = (
        f"{p_em('setting')} <b>MANUAL RANGE MANAGER</b> {p_em('setting')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ <b>Auto Range System:</b> <code>{auto_status}</code>\n"
        f"💡 <i>(Auto Range OFF থাকলে বট আপনার অ্যাডমিন প্যানেলের সার্ভিসগুলো লোড করবে।)</i>\n\n"
        f"<b>কনফিগার করা সার্ভিসসমূহ:</b>\n"
    )
    
    if manual_data:
        for app, ranges in manual_data.items():
            icon = get_platform_icon(app) or "📱"
            text += f"<blockquote>{icon} <b>{app}:</b> {len(ranges)} ranges</blockquote>\n"
    else:
        text += "<i>কোনো ম্যানুয়াল সার্ভিস সেট করা নেই।</i>\n"
        
    buttons = [
        [
            rbtn("➕ Add Service", "success", callback_data="man_add_service"),
            rbtn("❌ Delete Service", "danger", callback_data="man_del_service_list")
        ],
        [
            rbtn("➕ Add Range", "primary", callback_data="man_add_range_list"),
            rbtn("❌ Delete Range", "danger", callback_data="man_del_range_select_service")
        ],
        [
            rbtn("🔄 Toggle Auto Range", "primary", callback_data="toggle_auto_range_callback")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    if is_callback:
        await update_or_query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update_or_query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

# ==================== WITHDRAW FUNCTIONS & SETTERS ====================

async def set_withdrawal_method_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
        await update.message.reply_text(
            f"{p_em('ban')} <b>YOU ARE BANNED</b> {p_em('ban')}\n\n"
            f"<blockquote>{p_em('msg')} Contact Support: {support}</blockquote>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return
        
    keyboard = InlineKeyboardMarkup([
        [
            rbtn("Bkash", "primary", callback_data="setmethod_Bkash", icon_custom_emoji_id=EMOJI_ID_MAP.get("bkash")),
            rbtn("Nagad", "primary", callback_data="setmethod_Nagad", icon_custom_emoji_id=EMOJI_ID_MAP.get("nagad"))
        ],
        [
            rbtn("Rocket", "primary", callback_data="setmethod_Rocket", icon_custom_emoji_id=EMOJI_ID_MAP.get("rocket")),
            rbtn("Binance", "primary", callback_data="setmethod_Binance", icon_custom_emoji_id=EMOJI_ID_MAP.get("binance"))
        ]
    ])
    await update.message.reply_text(
        f"{p_em('money')} <b>SELECT YOUR WITHDRAWAL METHOD</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Please select a withdrawal method from the options below. "
        "Once set, your withdrawal requests will automatically use this method.",
        parse_mode="HTML",
        reply_markup=keyboard
    )

async def withdraw_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = unstyle_text(update.message.text.strip())
    uid = update.effective_user.id
    
    if text == "CANCEL":
        context.user_data["withdraw_mode"] = None
        context.user_data["withdraw_method"] = None
        await update.message.reply_text(f"{p_em('cross')} WITHDRAW CANCELLED\n\n{p_em('home')} BACK TO MENU", reply_markup=main_keyboard(uid))
        return
    
    try:
        amount = float(text)
    except:
        await update.message.reply_text(f"{p_em('cross')} PLEASE SEND A VALID AMOUNT!", reply_markup=cancel_keyboard())
        return
    
    balance = get_user(uid)['balance']
    min_w, max_w = get_withdraw_limits()
    
    if amount < min_w or amount > max_w:
        await update.message.reply_text(f"{p_em('down')} MINIMUM WITHDRAW {min_w}$ \n\n{p_em('up')} MAX WITHDRAWAL {max_w}$", reply_markup=cancel_keyboard())
        return
    
    if amount > balance:
        await update.message.reply_text(f"{p_em('cross')} YOU DO NOT HAVE ENOUGH BALANCE !", reply_markup=cancel_keyboard())
        return
    
    context.user_data["withdraw_amount"] = amount
    context.user_data["withdraw_mode"] = "number"
    msg = (
        f"{p_em('get_number_btn')} PLEASE SEND YOUR ACCOUNT NUMBER !\n\n"
        f"<blockquote>💡 EXAMPLE: 17XXXXXXXX</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_keyboard())

async def withdraw_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = unstyle_text(update.message.text.strip())
    uid = update.effective_user.id
    
    if text == "CANCEL":
        context.user_data["withdraw_mode"] = None
        context.user_data["withdraw_method"] = None
        context.user_data["withdraw_amount"] = None
        await update.message.reply_text(f"{p_em('cross')} WITHDRAW CANCELLED\n\n{p_em('home')} BACK TO MENU", reply_markup=main_keyboard(uid))
        return
    
    method = context.user_data.get("withdraw_method")
    amount = context.user_data.get("withdraw_amount")
    payment_number = text
    payment_id = generate_payment_id()
    
    user_payment_msg = (
        f"{p_em('money')} <b>PAYMENT DETAILS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>{p_em('status')} METHOD: {method}</blockquote>\n"
        f"<blockquote>{p_em('get_number_btn')} YOUR NUMBER: {payment_number}</blockquote>\n\n"
        f"<blockquote>{p_em('status')} IF DETAILS ARE CORRECT, CONFIRM.</blockquote>"
    )
    
    confirm_keyboard = InlineKeyboardMarkup([
        [
            rbtn("CANCEL", "danger", callback_data="withdraw_cancel", icon_custom_emoji_id=EMOJI_ID_MAP.get("cross")),
            rbtn("CONFIRM", "success", callback_data="withdraw_confirm", icon_custom_emoji_id=EMOJI_ID_MAP.get("done"))
        ]
    ])
    
    context.user_data["temp_withdraw"] = {
        "method": method,
        "amount": amount,
        "number": payment_number,
        "payment_id": payment_id
    }
    
    await update.message.reply_text(
        user_payment_msg,
        parse_mode="HTML",
        reply_markup=confirm_keyboard
    )

async def process_withdraw_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    
    temp_data = context.user_data.get("temp_withdraw")
    if not temp_data:
        await query.message.reply_text(f"{p_em('cross')} SESSION EXPIRED. PLEASE TRY AGAIN.", reply_markup=main_keyboard(uid))
        return
    
    method = temp_data["method"]
    amount = temp_data["amount"]
    payment_number = temp_data["number"]
    payment_id = temp_data["payment_id"]
    
    new_balance = await update_db_balance(uid, -amount)
    
    withdraw_requests = load_withdraw_requests()
    withdraw_requests[str(payment_id)] = {
        "user_id": uid,
        "method": method,
        "amount": amount,
        "number": payment_number,
        "payment_id": payment_id,
        "status": "pending",
        "timestamp": datetime.now().isoformat()
    }
    save_withdraw_requests(withdraw_requests)
    
    user_confirm_msg = (
        f"{p_em('money')} <b>WITHDRAW REQUEST SENT</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>Withdraw request successfully submitted to admin. Please wait.</blockquote>\n\n"
        f"<blockquote>{p_em('status')} METHOD: <code>{method}</code>\n"
        f"{p_em('get_number_btn')} NUMBER: <code>{payment_number}</code>\n"
        f"{p_em('money')} AMOUNT: <code>{format_balance(amount)}$</code>\n"
        f"{p_em('link')} PAYMENT ID: <code>{payment_id}</code></blockquote>"
    )
    await query.message.edit_text(user_confirm_msg, parse_mode="HTML")

    success_back_msg = (
        f"{p_em('gift_box')} <b>WITHDRAW REQUEST SUBMIT SUCCESSFUL</b> {p_em('gift_box')}\n\n"
        f"{p_em('home')} <b>BACK TO MENU</b>"
    )
    await context.bot.send_message(
        chat_id=uid,
        text=success_back_msg,
        parse_mode="HTML",
        reply_markup=main_keyboard(uid)
    )

    admin_msg = (
        f"{p_em('money')} <b>NEW WITHDRAW REQUEST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<blockquote>{p_em('link')} USER ID : <code>{uid}</code>\n"
        f"{p_em('status')} METHOD: <code>{method}</code>\n"
        f"{p_em('get_number_btn')} NUMBER: <code>{payment_number}</code>\n"
        f"{p_em('link')} ID : <code>{payment_id}</code></blockquote>\n\n"
        f"<blockquote>{p_em('money')} AMOUNT: <code>{format_balance(amount)}$</code></blockquote>"
    )
    
    admin_decision_keyboard = InlineKeyboardMarkup([
        [
            rbtn("CANCEL", "danger", callback_data=f"admin_reject_{payment_id}", icon_custom_emoji_id=EMOJI_ID_MAP.get("cross")),
            rbtn("CONFIRM", "success", callback_data=f"admin_approve_{payment_id}", icon_custom_emoji_id=EMOJI_ID_MAP.get("done"))
        ]
    ])
    
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(
                admin_id, 
                admin_msg, 
                parse_mode="HTML", 
                reply_markup=admin_decision_keyboard
            )
        except Exception as e:
            print(f"Failed to send to admin {admin_id}: {e}")
    
    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None
    context.user_data["withdraw_method"] = None
    context.user_data["withdraw_amount"] = None

async def process_withdraw_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    
    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None
    context.user_data["withdraw_method"] = None
    context.user_data["withdraw_amount"] = None
    
    await query.message.edit_text(f"{p_em('cross')} WITHDRAW CANCELLED\n\n{p_em('home')} BACK TO MENU")
    await context.bot.send_message(uid, "PLEASE USE THE BUTTONS BELOW :", reply_markup=main_keyboard(uid))

# ==================== ADMIN PANEL - WITHDRAW APPROVAL ====================

async def admin_approve_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str):
    query = update.callback_query
    await query.answer()
    
    withdraw_requests = load_withdraw_requests()
    if payment_id not in withdraw_requests:
        await query.message.reply_text(f"{p_em('cross')} WITHDRAW REQUEST NOT FOUND!")
        return
    
    request_data = withdraw_requests[payment_id]
    uid = request_data["user_id"]
    method = request_data["method"]
    amount = request_data["amount"]
    payment_number = request_data["number"]
    
    withdraw_requests[payment_id]["status"] = "approved"
    save_withdraw_requests(withdraw_requests)
    
    user_final_msg = (
        f"{p_em('done')} <b>WITHDRAWAL SUCCESS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<blockquote>আপনার উইথড্র রিকোয়েস্টটি সফলভাবে অ্যাপ্রুভ করা হয়েছে!</blockquote>\n\n"
        f"<blockquote>{p_em('status')} METHOD: <code>{method}</code>\n"
        f"{p_em('get_number_btn')} NUMBER: <code>{payment_number}</code>\n"
        f"{p_em('money')} AMOUNT: <code>{format_balance(amount)}$</code>\n"
        f"{p_em('link')} ID: <code>{payment_id}</code></blockquote>"
    )
    
    try:
        await context.bot.send_message(uid, user_final_msg, parse_mode="HTML")
    except:
        pass
    
    await query.message.edit_text(
        f"WITHDRAW REQUEST CONFIRMED SUCCESSFULLY\n\n"
        f"Payment ID: {payment_id}\n"
        f"User ID: {uid}\n"
        f"Amount: {format_balance(amount)}$\n\n"
        f"Payment has been approved!",
        parse_mode="Markdown"
    )

async def admin_reject_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str):
    query = update.callback_query
    await query.answer()
    
    withdraw_requests = load_withdraw_requests()
    if payment_id not in withdraw_requests:
        await query.message.reply_text(f"{p_em('cross')} WITHDRAW REQUEST NOT FOUND!")
        return
    
    request_data = withdraw_requests[payment_id]
    uid = request_data["user_id"]
    method = request_data["method"]
    amount = request_data["amount"]
    payment_number = request_data["number"]
    
    withdraw_requests[payment_id]["status"] = "rejected"
    save_withdraw_requests(withdraw_requests)
    
    await update_db_balance(uid, amount)
    
    user_reject_msg = (
        f"{p_em('cross')} WITHDRAWAL REQUEST REJECTED\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ Sorry, the admin has rejected your withdrawal request. Funds are refunded to your balance.\n\n"
        f"💵 METHOD: {method}\n"
        f"📞 NUMBER: {payment_number}\n"
        f"💵 AMOUNT: {format_balance(amount)}$"
    )
    
    try:
        await context.bot.send_message(uid, user_reject_msg, parse_mode="Markdown")
    except:
        pass
    
    await query.message.edit_text(
        f"WITHDRAW REQUEST CANCELLED & REFUNDED\n\n"
        f"Payment ID: {payment_id}\n"
        f"User ID: {uid}\n"
        f"Amount: {format_balance(amount)}$"
    )

# ==================== ADMIN PANEL - BALANCE MANAGEMENT ====================

async def admin_add_balance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_balance_mode"] = True
    context.user_data["remove_balance_mode"] = False
    await update.message.reply_text(f"{p_em('money')} **SEND USER ID TO ADD BALANCE FOR USER!** {p_em('money')}\n\n📝 PLEASE SEND THE TELEGRAM USER ID:", parse_mode="Markdown")

async def admin_remove_balance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["remove_balance_mode"] = True
    context.user_data["add_balance_mode"] = False
    await update.message.reply_text(f"{p_em('money')} **SEND USER ID TO REMOVE BALANCE FROM USER!** {p_em('money')}\n\n📝 PLEASE SEND THE TELEGRAM USER ID:", parse_mode="Markdown")

async def process_add_balance_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid_to_add = unstyle_text(update.message.text.strip())
    
    if not uid_to_add.isdigit():
        await update.message.reply_text(f"{p_em('cross')} INVALID USER ID! PLEASE SEND A VALID NUMERIC TELEGRAM ID.")
        return
    
    uid_to_add_int = int(uid_to_add)
    
    if not user_exists(uid_to_add_int):
        await update.message.reply_text(f"{p_em('cross')} USER NOT FOUND! THIS USER HAS NEVER STARTED THE BOT.")
        context.user_data["add_balance_mode"] = False
        return
    
    context.user_data["pending_add_user"] = uid_to_add_int
    await update.message.reply_text(f"{p_em('money')} **SEND AMOUNT TO ADD BALANCE:**\n\n💵 ENTER AMOUNT IN $:", parse_mode="Markdown")

async def process_remove_balance_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid_to_remove = unstyle_text(update.message.text.strip())
    
    if not uid_to_remove.isdigit():
        await update.message.reply_text(f"{p_em('cross')} INVALID USER ID! PLEASE SEND A VALID NUMERIC TELEGRAM ID.")
        return
    
    uid_to_remove_int = int(uid_to_remove)
    
    if not user_exists(uid_to_remove_int):
        await update.message.reply_text(f"{p_em('cross')} USER NOT FOUND! THIS USER HAS NEVER STARTED THE BOT.")
        context.user_data["remove_balance_mode"] = False
        return
    
    context.user_data["pending_remove_user"] = uid_to_remove_int
    await update.message.reply_text(f"{p_em('money')} **SEND AMOUNT TO REMOVE BALANCE:**\n\n💵 ENTER AMOUNT IN $:", parse_mode="Markdown")

async def process_add_balance_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount_text = unstyle_text(update.message.text.strip())
    
    try:
        amount = float(amount_text)
        if amount <= 0:
            await update.message.reply_text(f"{p_em('cross')} INVALID AMOUNT! PLEASE SEND A POSITIVE NUMBER.")
            return
    except:
        await update.message.reply_text(f"{p_em('cross')} INVALID AMOUNT! PLEASE SEND A VALID NUMBER.")
        return
    
    uid = context.user_data.get("pending_add_user")
    if not uid:
        context.user_data["add_balance_mode"] = False
        await update.message.reply_text(f"{p_em('cross')} SESSION EXPIRED. PLEASE TRY AGAIN.")
        return
    
    user_data = get_user(uid)
    old_balance = user_data.get("balance", 0)
    new_balance = await update_db_balance(uid, amount)
    
    admin_msg = (
        f"{p_em('done')} **ADD BALANCE SUCCESSFUL** {p_em('done')}\n\n"
        f"🆔 USER ID : `{uid}`\n"
        f"💵 ADD BALANCE AMOUNT : `{format_balance(amount)}$`\n"
        f"📊 PREVIOUS BALANCE : `{format_balance(old_balance)}$`\n"
        f"📈 NEW BALANCE : `{format_balance(new_balance)}$`"
    )
    
    admin_keyboard = InlineKeyboardMarkup([
        [rbtn("COPY USER ID", "primary", callback_data=f"copy_id_{uid}")]
    ])
    
    await update.message.reply_text(admin_msg, parse_mode="Markdown", reply_markup=admin_keyboard)
    
    user_msg = (
        f"{p_em('gift_box')} **THE ADMIN HAS ADDED MONEY TO YOUR ACCOUNT** {p_em('gift_box')}\n\n"
        f"💵 **AMOUNT OF MONEY :** `{format_balance(amount)}$`\n"
        f"📊 **YOUR NEW BALANCE :** `{format_balance(new_balance)}$`"
    )
    
    try:
        await context.bot.send_message(uid, user_msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"{p_em('cross')} COULD NOT NOTIFY USER. BUT BALANCE ADDED SUCCESSFULLY.")
    
    context.user_data["add_balance_mode"] = False
    context.user_data["pending_add_user"] = None

async def process_remove_balance_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount_text = unstyle_text(update.message.text.strip())
    
    try:
        amount = float(amount_text)
        if amount <= 0:
            await update.message.reply_text(f"{p_em('cross')} INVALID AMOUNT! PLEASE SEND A POSITIVE NUMBER.")
            return
    except:
        await update.message.reply_text(f"{p_em('cross')} INVALID AMOUNT! PLEASE SEND A VALID NUMBER.")
        return
    
    uid = context.user_data.get("pending_remove_user")
    if not uid:
        context.user_data["remove_balance_mode"] = False
        await update.message.reply_text(f"{p_em('cross')} SESSION EXPIRED. PLEASE TRY AGAIN.")
        return
    
    user_data = get_user(uid)
    old_balance = user_data.get("balance", 0)
    
    if amount > old_balance:
        error_msg = (
            f"{p_em('cross')} **INSUFFICIENT BALANCE!** {p_em('cross')}\n\n"
            f"🆔 USER ID : `{uid}`\n"
            f"💵 CURRENT BALANCE : `{format_balance(old_balance)}$`\n"
            f"💵 REQUESTED REMOVE : `{format_balance(amount)}$`"
        )
        await update.message.reply_text(error_msg, parse_mode="Markdown")
        context.user_data["remove_balance_mode"] = False
        context.user_data["pending_remove_user"] = None
        return
    
    new_balance = await update_db_balance(uid, -amount)
    
    admin_msg = (
        f"{p_em('done')} **REMOVE BALANCE SUCCESSFUL** {p_em('done')}\n\n"
        f"🆔 USER ID : `{uid}`\n"
        f"💵 REMOVE BALANCE AMOUNT : `{format_balance(amount)}$`\n"
        f"📊 PREVIOUS BALANCE : `{format_balance(old_balance)}$`\n"
        f"📈 NEW BALANCE : `{format_balance(new_balance)}$`"
    )
    
    admin_keyboard = InlineKeyboardMarkup([
        [rbtn("COPY USER ID", "primary", callback_data=f"copy_id_{uid}")]
    ])
    
    await update.message.reply_text(admin_msg, parse_mode="Markdown", reply_markup=admin_keyboard)
    
    user_msg = (
        f"{p_em('stop')} **ADMIN HAS REMOVED MONEY FROM YOUR ACCOUNT** {p_em('stop')}\n\n"
        f"💵 **AMOUNT REMOVED :** `{format_balance(amount)}$`\n"
        f"📊 **YOUR NEW BALANCE :** `{format_balance(new_balance)}$`"
    )
    
    try:
        await context.bot.send_message(uid, user_msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"{p_em('cross')} COULD NOT NOTIFY USER. BUT BALANCE REMOVED SUCCESSFULLY.")
    
    context.user_data["remove_balance_mode"] = False
    context.user_data["pending_remove_user"] = None

# ==================== ADMIN PANEL - BAN/UNBAN ====================

async def admin_ban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["admin_ban_mode"] = True
    context.user_data["admin_unban_mode"] = False
    await update.message.reply_text(f"{p_em('ban')} SENT TELEGRAM ID TO BAN USER {p_em('ban')}\n\n📝 Please send the Telegram User ID you want to ban:")

async def admin_unban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["admin_unban_mode"] = True
    context.user_data["admin_ban_mode"] = False
    await update.message.reply_text(f"{p_em('done')} SENT UNBAN USER ID {p_em('done')}\n\n📝 Please send the Telegram User ID you want to unban:")

async def process_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid_to_ban = unstyle_text(update.message.text.strip())
    
    if not uid_to_ban.isdigit():
        await update.message.reply_text(f"{p_em('cross')} INVALID USER ID! Please send a valid numeric Telegram ID.")
        return
    
    uid_to_ban_int = int(uid_to_ban)
    
    if not user_exists(uid_to_ban_int):
        await update.message.reply_text(f"{p_em('cross')} USER NOT FOUND IN DATABASE.")
        context.user_data["admin_ban_mode"] = False
        return
    
    if is_user_banned(uid_to_ban_int):
        await update.message.reply_text(f"{p_em('cross')} USER IS ALREADY BANNED.")
        context.user_data["admin_ban_mode"] = False
        return
    
    ban_user(uid_to_ban_int)
    
    try:
        await context.bot.send_message(
            uid_to_ban_int,
            f"{p_em('ban')} **YOU HAVE BEEN BANNED** {p_em('ban')}\n\n"
            "❌ YOU HAVE BEEN BANNED FROM USING THIS BOT.",
            parse_mode="Markdown"
        )
    except:
        pass
    
    await update.message.reply_text(
        f"{p_em('done')} USER BAN SUCCESSFUL {p_em('done')}\n\n"
        f"Banned User ID: {uid_to_ban}",
        parse_mode="Markdown",
        reply_markup=admin_security_join_keyboard()
    )
    context.user_data["admin_ban_mode"] = False

async def process_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid_to_unban = unstyle_text(update.message.text.strip())
    
    if not uid_to_unban.isdigit():
        await update.message.reply_text(f"{p_em('cross')} INVALID USER ID! Please send a valid numeric Telegram ID.")
        return
    
    uid_to_unban_int = int(uid_to_unban)
    
    if not is_user_banned(uid_to_unban_int):
        await update.message.reply_text(f"{p_em('cross')} THIS USER IS NOT BANNED.")
        context.user_data["admin_unban_mode"] = False
        return
    
    unban_user(uid_to_unban_int)
    
    try:
        await context.bot.send_message(
            uid_to_unban_int,
            f"{p_em('done')} **YOU HAVE BEEN UNBANNED** {p_em('done')}\n\n"
            "🎁 CONGRATULATIONS! YOU HAVE BEEN UNBANNED.",
            parse_mode="Markdown"
        )
    except:
        pass
    
    await update.message.reply_text(
        f"{p_em('done')} USER UNBAN SUCCESSFUL {p_em('done')}\n\n"
        f"Unbanned User ID: {uid_to_unban}",
        parse_mode="Markdown",
        reply_markup=admin_security_join_keyboard()
    )
    context.user_data["admin_unban_mode"] = False

async def show_banned_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banned_list = load_banned_users()
    
    if not banned_list:
        await update.message.reply_text(f"{p_em('status')} **BANNED USER LIST** {p_em('status')}\n\n✅ No users are currently banned.", parse_mode="Markdown", reply_markup=admin_security_join_keyboard())
        return
    
    banned_text = f"{p_em('status')} **BANNED USER LIST** {p_em('status')}\n\n"
    for i, uid in enumerate(banned_list, 1):
        banned_text += f"{i}. User ID: {uid}\n"
    
    banned_text += f"\n📊 Total Banned Users: {len(banned_list)}"
    
    await update.message.reply_text(banned_text, parse_mode="Markdown", reply_markup=admin_security_join_keyboard())

# ==================== ADMIN DYNAMIC SETTERS ====================

async def admin_set_max_numbers_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid): return
    context.user_data["admin_edit_mode"] = "max_limit"
    await update.message.reply_text(
        f"{p_em('setting')} <b>SET MAX NUMBERS LIMIT (BATCH BATCH)</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<blockquote>প্রিতিটি ইউজার একসাথে সর্বোচ্চ কতটি নাম্বার তুলতে পারবেন তা টাইপ করে পাঠান:</blockquote>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_set_cooldown_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid): return
    context.user_data["admin_edit_mode"] = "cooldown"
    await update.message.reply_text(
        f"{p_em('waiting')} <b>SET COOLDOWN TIME</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<blockquote>নাম্বার রিকোয়েস্ট এর কুলডাউন সেকেন্ড সংখ্যায় পাঠান (যেমন: 4.0):</blockquote>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_edit_links_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid): return
    
    keyboard = InlineKeyboardMarkup([
        [rbtn("Edit Welcome Msg", "primary", callback_data="edit_txt_welcome", icon_custom_emoji_id=EMOJI_ID_MAP.get("setting"))],
        [rbtn("Edit OTP Group Link", "primary", callback_data="edit_txt_otpgroup", icon_custom_emoji_id=EMOJI_ID_MAP.get("link"))],
        [rbtn("Edit Channel Link", "primary", callback_data="edit_txt_channel", icon_custom_emoji_id=EMOJI_ID_MAP.get("channel"))],
        [rbtn("Edit Support Username", "primary", callback_data="edit_txt_support", icon_custom_emoji_id=EMOJI_ID_MAP.get("msg"))],
        [
            rbtn("Edit API Key", "primary", callback_data="edit_api_key", icon_custom_emoji_id=EMOJI_ID_MAP.get("setting")),
            rbtn("Edit API Base URL", "primary", callback_data="edit_api_url", icon_custom_emoji_id=EMOJI_ID_MAP.get("link"))
        ],
        [rbtn("Back", "danger", callback_data="admin_back_to_config", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"))]
    ])
    
    await update.message.reply_text(
        f"{p_em('setting')} <b>EDIT LINKS & TEXTS SYSTEM</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "নিচের বোতামগুলো থেকে সিলেক্ট করুন আপনি কোন লেখা বা লিংক পরিবর্তন করতে চান:",
        parse_mode="HTML",
        reply_markup=keyboard
    )

# ==================== MESSAGE HANDLER SECTION ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.effective_user.id
    raw_text = update.message.text.strip()
    
    text = unstyle_text(raw_text)

    if text in MENU_BUTTONS or text == "CANCEL":
        context.user_data.pop("withdraw_mode", None)
        context.user_data.pop("withdraw_method", None)
        context.user_data.pop("withdraw_amount", None)
        context.user_data.pop("admin_edit_mode", None)
        context.user_data.pop("add_balance_mode", None)
        context.user_data.pop("pending_add_user", None)
        context.user_data.pop("remove_balance_mode", None)
        context.user_data.pop("pending_remove_user", None)
        context.user_data.pop("admin_ban_mode", None)
        context.user_data.pop("admin_unban_mode", None)
        context.user_data.pop("mode", None)
        context.user_data.pop("broadcast_mode", None)

    if context.user_data.get("withdraw_mode") == "amount":
        await withdraw_amount_received(update, context)
        return
    
    if context.user_data.get("withdraw_mode") == "number":
        await withdraw_number_received(update, context)
        return

    edit_mode = context.user_data.get("admin_edit_mode")
    if edit_mode and is_admin(uid):
        context.user_data["admin_edit_mode"] = None
        settings = load_settings()
        
        if edit_mode == "welcome":
            settings["welcome_message"] = raw_text
            await update.message.reply_text("✅ Welcome Message সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
            save_settings(settings)
        elif edit_mode == "otpgroup":
            if text.startswith("http"):
                settings["otp_group_url"] = text
                await update.message.reply_text("✅ OTP Group লিংক সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text("❌ ভুল লিংক ফরম্যাট! অবশ্যই https:// থাকতে হবে।", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "channel":
            if text.startswith("http"):
                settings["channel_url"] = text
                await update.message.reply_text("✅ Channel লিংক সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text("❌ ভুল লিংক ফরম্যাট!", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "support":
            if text.startswith("@") or text.startswith("http"):
                settings["support_username"] = text
                await update.message.reply_text("✅ Support Username সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text("❌ ভুল ইউজারনেম ফরম্যাট!", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "max_limit":
            if text.isdigit():
                settings["max_numbers_per_user"] = int(text)
                await update.message.reply_text(f"✅ ইউজার একসাথে সর্বোচ্চ {text} টি নাম্বার তুলতে পারবেন!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text("❌ ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "cooldown":
            try:
                settings["cooldown_time"] = float(text)
                await update.message.reply_text(f"✅ Cooldown লিমিট সফলভাবে {text} সেকেন্ড সেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            except:
                await update.message.reply_text("❌ ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "add_force_join":
            channel_username = text.strip()
            if not channel_username.startswith("@"):
                channel_username = "@" + channel_username
            channels = settings.get("force_join_channels", [])
            if channel_username not in channels:
                channels.append(channel_username)
                settings["force_join_channels"] = channels
                save_settings(settings)
                await update.message.reply_text(f"✅ Successfully added {channel_username}!", reply_markup=admin_security_join_keyboard())
            else:
                await update.message.reply_text(f"⚠️ {channel_username} is already in the list!", reply_markup=admin_security_join_keyboard())
        elif edit_mode == "otp_bonus":
            try:
                val = float(text)
                settings["otp_reward"] = val
                await update.message.reply_text(f"✅ OTP Reward সফলভাবে {val}$ সেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            except:
                await update.message.reply_text("❌ ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "refer_bonus":
            try:
                val = float(text)
                settings["refer_bonus"] = val
                await update.message.reply_text(f"✅ Referral Bonus সফলভাবে {val}$ সেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            except:
                await update.message.reply_text("❌ ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "numbers_per_request":
            try:
                val = int(text)
                if val < 1: raise ValueError
                settings["numbers_per_request"] = val
                await update.message.reply_text(f"✅ Numbers Per Request সফলভাবে {val} টি সেট করা হয়েছে!", reply_markup=admin_system_config_keyboard())
                save_settings(settings)
            except:
                await update.message.reply_text("❌ ভুল ইনপুট!", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "withdraw_limits":
            parts = text.split()
            if len(parts) == 2:
                try:
                    settings["min_withdraw"] = float(parts[0])
                    settings["max_withdraw"] = float(parts[1])
                    await update.message.reply_text(f"✅ Withdraw Limits সফলভাবে আপডেট করা হয়েছে: Minimum {parts[0]}$ , Maximum {parts[1]}$", reply_markup=admin_system_config_keyboard())
                    save_settings(settings)
                except:
                    await update.message.reply_text("❌ ভুল ফরম্যাট!", reply_markup=admin_system_config_keyboard())
            else:
                await update.message.reply_text("❌ ভুল ফরম্যাট! উদাহরণ: `0.5 100`", parse_mode="Markdown", reply_markup=admin_system_config_keyboard())
        elif edit_mode == "direct_msg_uid":
            if text.isdigit():
                context.user_data["admin_direct_uid"] = text
                context.user_data["admin_edit_mode"] = "direct_msg_text"
                await update.message.reply_text("💬 **Now enter the message content to send:**", parse_mode="Markdown", reply_markup=cancel_keyboard())
            else:
                await update.message.reply_text("❌ Invalid User ID!", reply_markup=admin_user_balance_keyboard())
        elif edit_mode == "direct_msg_text":
            target_uid = context.user_data.get("admin_direct_uid")
            try:
                await context.bot.send_message(chat_id=int(target_uid), text=f"💬 **MESSAGE FROM ADMIN:**\n\n{raw_text}", parse_mode="Markdown")
                await update.message.reply_text("✅ Message sent successfully!", reply_markup=admin_user_balance_keyboard())
            except Exception as e:
                await update.message.reply_text(f"❌ Failed to send message: {e}", reply_markup=admin_user_balance_keyboard())
        elif edit_mode == "search_username":
            uname = text.replace("@", "").strip().lower()
            users = load_data(USER_DATA_FILE)
            found = False
            for u_id, details in users.items():
                if str(details.get("username", "")).lower() == uname:
                    found = True
                    stats = get_user_stats(u_id)
                    status_msg = (
                        f"👤 **USER FOUND CHECK** 📊\n\n"
                        f"🆔 **User ID:** `{u_id}`\n"
                        f"🏷️ **Username:** @{details.get('username')}\n"
                        f"💵 **Balance:** `{details.get('balance', 0.0)}$`\n\n"
                        f"⚡ **TODAY STATUS**\n"
                        f"📱 NUMBERS TAKEN : {stats['today_numbers']}\n"
                        f"🔑 OTPS RECEIVED : {stats['today_otps']}"
                    )
                    kb = InlineKeyboardMarkup([[rbtn("CHECK ALL DATA", "success", callback_data=f"full_logs_{u_id}")]])
                    await update.message.reply_text(status_msg, parse_mode="Markdown", reply_markup=kb)
                    break
            if not found:
                await update.message.reply_text("❌ No user found with that username.", reply_markup=admin_user_balance_keyboard())
        elif edit_mode == "broadcast_btn_msg":
            context.user_data["admin_broadcast_msg"] = raw_text
            context.user_data["admin_edit_mode"] = "broadcast_btn_text"
            await update.message.reply_text("💬 **Enter the Button Text:**", parse_mode="Markdown", reply_markup=cancel_keyboard())
        elif edit_mode == "broadcast_btn_text":
            context.user_data["admin_broadcast_btn_text"] = raw_text
            context.user_data["admin_edit_mode"] = "broadcast_btn_url"
            await update.message.reply_text("💬 **Enter the Button URL (https://...):**", parse_mode="Markdown", reply_markup=cancel_keyboard())
        elif edit_mode == "broadcast_btn_url":
            if text.startswith("http"):
                msg_content = context.user_data.get("admin_broadcast_msg")
                btn_txt = context.user_data.get("admin_broadcast_btn_text")
                btn_url = text
                
                users = load_data(USER_DATA_FILE)
                success, fail = 0, 0
                kb = InlineKeyboardMarkup([[rbtn(btn_txt, "primary", url=btn_url)]])
                
                status_msg = await update.message.reply_text("🚀 Broadcasting started...")
                for target_uid in users.keys():
                    try:
                        await context.bot.send_message(chat_id=int(target_uid), text=f"<blockquote>{p_em('live')} <b>ADMIN NOTICE :</b></blockquote>\n\n{msg_content}", parse_mode="HTML", reply_markup=kb)
                        success += 1
                    except:
                        fail += 1
                    await asyncio.sleep(0.05)
                
                await status_msg.delete()
                await update.message.reply_text(f"✅ Broadcast with button completed!\n\nSuccess: `{success}`\nFailed: `{fail}`", parse_mode="Markdown", reply_markup=admin_notice_bcast_keyboard())
            else:
                await update.message.reply_text("❌ Invalid URL! Must start with https://.", reply_markup=admin_notice_bcast_keyboard())
        elif edit_mode == "api_key":
            settings["api_key"] = text
            await update.message.reply_text("✅ API Key সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
            save_settings(settings)
        elif edit_mode == "api_url":
            if text.startswith("http"):
                settings["base_url"] = text
                await update.message.reply_text("✅ API Base URL সফলভাবে আপডেট করা হয়েছে!", reply_markup=admin_notice_bcast_keyboard())
                save_settings(settings)
            else:
                await update.message.reply_text("❌ ভুল লিংক ফরম্যাট! অবশ্যই https:// থাকতে হবে।", reply_markup=admin_notice_bcast_keyboard())
        
        elif edit_mode == "add_manual_service":
            service_name = raw_text.strip().title()
            manual_data = load_manual_ranges()
            if service_name not in manual_data:
                manual_data[service_name] = []
                save_manual_ranges(manual_data)
                await update.message.reply_text(f"✅ Service <b>{service_name}</b> successfully added!", parse_mode="HTML")
            else:
                await update.message.reply_text(f"⚠️ Service <b>{service_name}</b> already exists!", parse_mode="HTML")
            await show_manual_ranges_menu(update, context, is_callback=False)
        elif edit_mode == "add_manual_range_input":
            range_input = raw_text.strip()
            service_name = context.user_data.get("selected_manual_service")
            if service_name:
                manual_data = load_manual_ranges()
                if service_name in manual_data:
                    if range_input not in manual_data[service_name]:
                        manual_data[service_name].append(range_input)
                        save_manual_ranges(manual_data)
                        await update.message.reply_text(f"✅ Added range <code>{range_input}</code> to <b>{service_name}</b>!", parse_mode="HTML")
                    else:
                        await update.message.reply_text(f"⚠️ This range already exists for <b>{service_name}</b>!", parse_mode="HTML")
                else:
                    await update.message.reply_text("❌ Service not found!")
            context.user_data.pop("selected_manual_service", None)
            await show_manual_ranges_menu(update, context, is_callback=False)
        return

    if context.user_data.get("add_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_add_user"):
            await process_add_balance_amount(update, context)
        else:
            await process_add_balance_user(update, context)
        return
    
    if context.user_data.get("remove_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_remove_user"):
            await process_remove_balance_amount(update, context)
        else:
            await process_remove_balance_user(update, context)
        return

    if context.user_data.get("admin_ban_mode") and is_admin(uid):
        await process_ban_user(update, context)
        return
    
    if context.user_data.get("admin_unban_mode") and is_admin(uid):
        await process_unban_user(update, context)
        return

    if not is_admin(uid) and is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
        await update.message.reply_text(
            f"{p_em('ban')} <b>YOU ARE BANNED</b> {p_em('ban')}\n\n"
            f"<blockquote>{p_em('msg')} Contact Support: {support}</blockquote>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return

    if is_under_maintenance(uid):
        await update.message.reply_text(f"{p_em('stop')} <b>SYSTEM UNDER MAINTENANCE</b>", parse_mode="Markdown")
        return

    if text == "CANCEL":
        context.user_data.clear()
        await update.message.reply_text(f"{p_em('cross')} CANCELLED", reply_markup=main_keyboard(uid))
        return

    if text == "BALANCE":
        user_data = get_user(uid)
        balance = user_data.get("balance", 0.0)
        active_method = user_data.get("withdrawal_method", "Not Set")
        min_w, max_w = get_withdraw_limits()
        
        balance_msg = (
            f"{p_em('money')} <b>BALANCE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>{p_em('money')} Current balance: {balance:.4f}$</blockquote>\n"
            f"<blockquote>{p_em('down')} Minimum withdraw: {min_w}$</blockquote>\n"
            f"<blockquote>{p_em('status')} Set Method: {active_method}</blockquote>\n\n"
            f"ℹ️ <i>To set or change your withdrawal method, please use:</i> /setwithdrawalmethod"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                rbtn("WITHDRAW", "success", callback_data="initiate_withdraw", icon_custom_emoji_id=EMOJI_ID_MAP.get("money"))
            ],
            [
                rbtn("Back to Menu", "danger", callback_data="back_to_menu_inline", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"))
            ]
        ])
        await update.message.reply_text(balance_msg, parse_mode="HTML", reply_markup=keyboard)
        return

    if text == "REFER & EARN":
        user_data = get_user(uid)
        settings = load_settings()
        refer_bonus = settings.get("refer_bonus", DEFAULT_REFER_BONUS)
        
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        ref_link = f"https://t.me/{bot_username}?start={uid}"
        
        referrals = user_data.get("referrals", 0)
        referral_earnings = user_data.get("referral_earnings", 0.0)
        balance = user_data.get("balance", 0.0)
        
        refer_msg = (
            f"{p_em('refer_btn')} <b>REFER & EARN</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>{p_em('link')} <b>Your referral link:</b>\n"
            f"<code>{ref_link}</code></blockquote>\n\n"
            f"<blockquote>{p_em('status')} Total referrals: {referrals}</blockquote>\n"
            f"<blockquote>{p_em('money')} Referral earnings: {referral_earnings:.4f}$</blockquote>\n"
            f"<blockquote>{p_em('gift_box')} Per referral: {refer_bonus:.4f}$</blockquote>\n\n"
            f"<blockquote>{p_em('money')} Your current balance: {balance:.4f}$</blockquote>"
        )
        await update.message.reply_text(refer_msg, parse_mode="HTML")
        return

    if text == "SYSTEM CONFIG" and is_admin(uid):
        await update.message.reply_text("System Configuration Category:", parse_mode="Markdown", reply_markup=admin_system_config_keyboard())
        return

    if text == "USER & BALANCE" and is_admin(uid):
        await update.message.reply_text("User & Balance Category:", parse_mode="Markdown", reply_markup=admin_user_balance_keyboard())
        return

    if text == "SECURITY & JOIN" and is_admin(uid):
        await update.message.reply_text("Security & Force Join Category:", parse_mode="Markdown", reply_markup=admin_security_join_keyboard())
        return

    if text == "NOTICE & B-CAST" and is_admin(uid):
        await update.message.reply_text("Notices & Broadcasting Category:", parse_mode="Markdown", reply_markup=admin_notice_bcast_keyboard())
        return

    if text == "ADD BALANCE" and is_admin(uid):
        await admin_add_balance_start(update, context)
        return

    if text == "REMOVE BALANCE" and is_admin(uid):
        await admin_remove_balance_start(update, context)
        return

    if text == "SET MAX NUMBERS LIMIT" and is_admin(uid):
        await admin_set_max_numbers_start(update, context)
        return

    if text == "SET WITHDRAW LIMITS" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "withdraw_limits"
        await update.message.reply_text(
            f"{p_em('money')} <b>SET WITHDRAW LIMITS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<blockquote>উইথড্রর সর্বনিম্ন এবং সর্বোচ্চ সীমা স্পেস দিয়ে টাইপ করে পাঠান (যেমন: 0.5 100.0):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "TOGGLE AUTO RANGE" and is_admin(uid):
        settings = load_settings()
        settings["auto_range"] = not settings.get("auto_range", True)
        save_settings(settings)
        _ranges_cache["data"] = None
        _ranges_cache["updated_at"] = 0.0
        status = "ENABLED (API AUTO ON)" if settings["auto_range"] else "DISABLED (CUSTOM RANGES ACTIVE)"
        await update.message.reply_text(f"🔄 Auto Range System has been set to: <b>{status}</b>", parse_mode="HTML", reply_markup=admin_system_config_keyboard())
        return

    if text == "MANAGE MANUAL RANGES" and is_admin(uid):
        await show_manual_ranges_menu(update, context, is_callback=False)
        return

    if text == "TOGGLE MAINTENANCE" and is_admin(uid):
        settings = load_settings()
        settings["maintenance_mode"] = not settings.get("maintenance_mode", False)
        save_settings(settings)
        status = "ENABLED" if settings["maintenance_mode"] else "DISABLED"
        await update.message.reply_text(f"{p_em('stop')} Maintenance Mode has been {status}!", reply_markup=admin_system_config_keyboard())
        return

    if text == "RESET DAILY LIMITS" and is_admin(uid):
        stats = load_stats()
        for u_id in stats:
            stats[u_id]["numbers_taken"] = []
            stats[u_id]["otps_received"] = []
        save_stats(stats)
        await update.message.reply_text(f"{p_em('done')} All user daily stats and limits have been reset successfully!", reply_markup=admin_system_config_keyboard())
        return

    if text == "DIRECT MSG USER" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "direct_msg_uid"
        await update.message.reply_text(
            f"{p_em('msg')} <b>DIRECT MESSAGE TO USER</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<blockquote>মেসেজ সার্চ করার জন্য ইউজারের Telegram ID টাইপ করে পাঠান:</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "SEARCH BY USERNAME" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "search_username"
        await update.message.reply_text(
            f"{p_em('status')} <b>SEARCH USER BY USERNAME</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<blockquote>ইউজারের ইউজারনেম টাইপ করে পাঠান:</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "EDIT LINKS & TEXTS" and is_admin(uid):
        await admin_edit_links_start(update, context)
        return

    if text == "SET FORCE JOIN" and is_admin(uid):
        await manage_force_join_menu(update, context, is_callback=False)
        return

    if text == "TOGGLE FORCE JOIN" and is_admin(uid):
        settings = load_settings()
        settings["force_join_enabled"] = not settings.get("force_join_enabled", False)
        save_settings(settings)
        status = "ENABLED" if settings["force_join_enabled"] else "DISABLED"
        await update.message.reply_text(f"{p_em('link')} Force Join System has been {status}!", reply_markup=admin_security_join_keyboard())
        return

    if text == "TOGGLE JOIN ALERT" and is_admin(uid):
        settings = load_settings()
        settings["join_alert_enabled"] = not settings.get("join_alert_enabled", True)
        save_settings(settings)
        status = "ENABLED" if settings["join_alert_enabled"] else "DISABLED"
        await update.message.reply_text(f"{p_em('live')} New User Join Notification is now {status}!", reply_markup=admin_security_join_keyboard())
        return

    if text == "SET COOLDOWN" and is_admin(uid):
        await admin_set_cooldown_start(update, context)
        return

    if text == "SET OTP BONUS" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "otp_bonus"
        await update.message.reply_text(
            f"{p_em('money')} **SET OTP REWARD BONUS**\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<blockquote>প্রতিটি ওটিপি সফল আসার পর ইউজার কত ডলার বোনাস পাবে তা টাইপ করে পাঠান (যেমন: 0.0020):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "SET REFER BONUS" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "refer_bonus"
        await update.message.reply_text(
            f"{p_em('gift_box')} **SET REFERRAL BONUS**\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<blockquote>প্রতিটি সফল রেফারেলের জন্য বোনাস অ্যামাউন্ট টাইপ করে পাঠান (যেমন: 0.050):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "SET NUMBERS PER REQUEST" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "numbers_per_request"
        await update.message.reply_text(
            f"{p_em('get_number_btn')} **SET NUMBERS PER REQUEST (BATCH SIZE)**\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<blockquote>ইউজার যখন একটি কান্ট্রি সিলেক্ট করবে, তখন তাকে একসাথে কয়টি নাম্বার দেওয়া হবে তা পাঠান (যেমন: 1 বা 3):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return

    if text == "BROADCAST NOTICE" and is_admin(uid):
        context.user_data["broadcast_mode"] = True
        await update.message.reply_text("Send the notice message content to broadcast to all users:", reply_markup=cancel_keyboard())
        return

    if text == "B-CAST WITH BUTTON" and is_admin(uid):
        context.user_data["admin_edit_mode"] = "broadcast_btn_msg"
        await update.message.reply_text("Enter the Broadcast Message content:", parse_mode="Markdown", reply_markup=cancel_keyboard())
        return

    if text == "TRAFFIC":
        await show_traffic(update, context)
        return

    if text == "LEADERBOARD":
        await show_leaderboard_command(update, context)
        return

    if text == "SUPPORT":
        await support_command(update, context)
        return

    if text == "GET NUMBER":
        await show_app_selection(update, context)
        return

    if context.user_data.get("mode") in ["range_1"]:
        if "X" in text.upper() or text.isdigit():
            count = 1
            context.user_data["mode"] = None
            await request_queue.put({'type': 'process_numbers', 'update': update, 'context': context, 'range_text': raw_text, 'count': count})
        return

    if text == "ADMIN PANEL" and is_admin(uid):
        context.user_data["admin_mode"] = "main"
        admin_welcome = f"{p_em('setting')} <b>WELCOME ADMIN PANEL</b> {p_em('setting')}"
        await update.message.reply_text(admin_welcome, reply_markup=admin_main_keyboard(), parse_mode="HTML")
        return

    if text == "BACK TO MAIN" and context.user_data.get("admin_mode"):
        context.user_data.clear()
        await update.message.reply_text("Back to main menu.", reply_markup=main_keyboard(uid))
        return

    if text == "BACK TO ADMIN":
        context.user_data.clear()
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text("Back to admin panel.", reply_markup=admin_main_keyboard())
        return
    
    if text == "USER STATUS CHECK" and is_admin(uid):
        context.user_data["mode"] = "input_user_id"
        msg = (
            f"<blockquote>{p_em('status')} <b>ENTER TELEGRAM ID</b> {p_em('status')}</blockquote>\n\n"
            "<blockquote>মেসেজ সার্চ করার জন্য ইউজারের টেলিগ্রাম আইডি টাইপ করুন:</blockquote>"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("mode") == "input_user_id" and is_admin(uid):
        target_uid = text.strip()
        if not target_uid.isdigit():
            await update.message.reply_text(f"{p_em('cross')} INVALID ID! PLEASE SEND A NUMERIC TELEGRAM ID.")
            return
        
        context.user_data["mode"] = None
        stats = get_user_stats(target_uid)
        
        status_msg = (
            f"{p_em('status')} <b>USER STATUS CHECK</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱ <b>TODAY ({datetime.now().strftime('%d/%m/%Y')})</b>\n"
            f"📱 NUMBERS TAKEN : {stats['today_numbers']}\n"
            f"🔑 OTPS RECEIVED : {stats['today_otps']} ⏱\n\n"
            f"🔥 <b>LAST 7 DAYS</b>\n"
            f"📱 NUMBERS TAKEN : {stats['last7d_numbers']}\n"
            f"🔑 OTPS RECEIVED : {stats['last7d_otps']} 🚀\n\n"
            f"🌐 <b>ALL TIME RECORD</b>\n"
            f"📱 TOTAL NUMBERS : {stats['total_numbers']}\n"
            f"🔑 TOTAL OTPS : {stats['total_otps']} 🏆\n"
        )
        
        keyboard = InlineKeyboardMarkup([
            [rbtn("CHECK ALL DATA", "success", callback_data=f"full_logs_{target_uid}")]
        ])
        
        await update.message.reply_text(status_msg, parse_mode="HTML", reply_markup=keyboard)
        return

    if text == "ALL USER ID" and is_admin(uid):
        users = get_all_users()
        if users:
            total_users = len(users)
            file_lines = []
            for i, user_id in enumerate(users, 1):
                file_lines.append(f"{i}. {user_id}")
            
            file_content = "\n".join(file_lines)
            file = io.BytesIO(file_content.encode("utf-8"))
            file.name = f"ALL_USERS_{total_users}.txt"
            
            caption = f"{p_em('status')} **ALL USER LIST** {p_em('status')}\n\n🎁 Total Users: {total_users}"
            await update.message.reply_document(
                document=file,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=admin_user_balance_keyboard()
            )
        else:
            await update.message.reply_text("No users found.", reply_markup=admin_user_balance_keyboard())
        return

    if text == "ALL USER BALANCE" and is_admin(uid):
        user_db = load_data(USER_DATA_FILE)
        if user_db:
            total_users = len(user_db)
            total_system_balance = 0.0
            balance_lines = []
            
            for i, (user_id, info) in enumerate(user_db.items(), 1):
                u_bal = info.get("balance", 0.0)
                total_system_balance += u_bal
                balance_lines.append(f"{i}. ID: {user_id} | Balance: {u_bal:.4f}$")
            
            file_content = "ALL USER BALANCE REPORT\n\n"
            file_content += f"Total Users: {total_users}\n"
            file_content += f"Total System Balance: {total_system_balance:.4f}$\n\n"
            file_content += "\n".join(balance_lines)
            
            file_io = io.BytesIO(file_content.encode("utf-8"))
            file_io.name = f"{total_system_balance:.4f}usd.txt"
            
            report_msg = (
                f"{p_em('money')} <b>ALL USER BALANCE REPORT</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<blockquote>Total Users: {total_users}</blockquote>\n"
                f"<blockquote>Total System Balance: {total_system_balance:.4f}$ </blockquote>"
            )
            
            await update.message.reply_document(
                document=file_io,
                caption=report_msg,
                parse_mode="HTML",
                reply_markup=admin_user_balance_keyboard()
            )
        else:
            await update.message.reply_text("No user data found.")
        return

    if text == "BAN USER LIST" and is_admin(uid):
        await show_banned_users_list(update, context)
        return

    if text == "BAN USER" and is_admin(uid):
        await admin_ban_user_start(update, context)
        return

    if text == "UNBAN USER" and is_admin(uid):
        await admin_unban_user_start(update, context)
        return

    if text == "SEND MESSAGE TO ALL USERS" and is_admin(uid):
        context.user_data["broadcast_mode"] = True
        await update.message.reply_text(
            f"{p_em('live')} <b>ADMIN BROADCAST SYSTEM</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💬 আপনি এখন যা পাঠাবেন তা সব ইউজারের কাছে ব্রডকাস্ট মেসেজ হিসেবে চলে যাবে।", 
            parse_mode="HTML", 
            reply_markup=cancel_keyboard()
        )
        return

    if context.user_data.get("broadcast_mode") and is_admin(uid):
        context.user_data["broadcast_mode"] = False
        
        user_db = load_data(USER_DATA_FILE)
        all_uids = list(user_db.keys())
        
        if not all_uids:
            await update.message.reply_text("❌ ব্রডকাস্টের জন্য কোনো ইউজার পাওয়া যায়নি!")
            return

        success_ids, fail_ids = [], []
        status_msg = await update.message.reply_text(f"{p_em('live')} <b>ব্রডকাস্ট শুরু হয়েছে...</b>\n{p_em('status')} টার্গেট: {len(all_uids)} জন ইউজার।", parse_mode="HTML")

        def format_broadcast_msg(text_content):
            if not text_content: return f"<blockquote>{p_em('live')} <b>ADMIN NOTICE :</b></blockquote>"
            formatted = re.sub(r'(\d{3,}[xX]{3,})', r'<code>\1</code>', str(text_content))
            return f"<blockquote>{p_em('live')} <b>ADMIN NOTICE :</b></blockquote>\n\n{formatted}"

        for user_id_str in all_uids:
            try:
                target_id = int(user_id_str)
                
                if update.message.text:
                    await context.bot.send_message(chat_id=target_id, text=format_broadcast_msg(update.message.text), parse_mode="HTML")
                else:
                    new_caption = format_broadcast_msg(update.message.caption) if update.message.caption else f"<blockquote>{p_em('live')} <b>ADMIN NOTICE :</b></blockquote>"
                    await context.bot.copy_message(
                        chat_id=target_id,
                        from_chat_id=update.message.chat_id,
                        message_id=update.message.message_id,
                        caption=new_caption,
                        parse_mode="HTML"
                    )
                
                success_ids.append(user_id_str)
            except:
                fail_ids.append(user_id_str)
            
            await asyncio.sleep(0.05)

        report_text = (
            f"{p_em('done')} <b>ADMIN NOTICE COMPLETE !</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 <b>BROADCAST REPORT:</b>\n\n"
            f"<blockquote>Successfully Sent: {len(success_ids)} Users !</blockquote>\n"
            f"<blockquote>Failed to Send: {len(fail_ids)} Users !</blockquote>"
        )
        
        await status_msg.delete()
        await context.bot.send_message(chat_id=uid, text=report_text, parse_mode="HTML", reply_markup=main_keyboard(uid))

        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if success_ids:
            s_file = io.BytesIO(("\n".join(success_ids)).encode()); s_file.name = f"SUCCESS_{random_suffix}.txt"
            await context.bot.send_document(chat_id=uid, document=s_file, caption="✅ Success User List")
        if fail_ids:
            f_file = io.BytesIO(("\n".join(fail_ids)).encode()); f_file.name = f"FAILED_{random_suffix}.txt"
            await context.bot.send_document(chat_id=uid, document=f_file, caption="❌ Failed User List")
        
        return

    else:
        await update.message.reply_text("PLEASE USE THE BUTTONS BELOW :", reply_markup=main_keyboard(uid))

# ==================== COMMAND HANDLERS SECTION ====================

async def get1number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
        await update.message.reply_text(
            f"{p_em('ban')} <b>YOU ARE BANNED</b> {p_em('ban')}\n\n"
            f"<blockquote>{p_em('msg')} Contact Support: {support}</blockquote>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return
    await show_app_selection(update, context)

# ==================== START & CALLBACK SECTION ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uid_str = str(uid)
    username = update.effective_user.username
    full_name = update.effective_user.full_name
    
    existing_data = load_data(USER_DATA_FILE)
    is_new_user = uid_str not in existing_data
    
    get_user(uid, username, full_name)
    
    if is_new_user:
        settings = load_settings()
        if settings.get("join_alert_enabled", True):
            alert_msg = (
                f"{p_em('live')} <b>NEW USER JOINED!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
                f"🏷️ <b>Name:</b> {html.escape(full_name or 'N/A')}\n"
                f"👤 <b>Username:</b> @{username if username else 'N/A'}"
            )
            for admin_id in ADMINS:
                try:
                    await context.bot.send_message(chat_id=admin_id, text=alert_msg, parse_mode="HTML")
                except:
                    pass
    
    args = context.args
    if args:
        param = unstyle_text(args[0])
        
        if is_range_request(param):
            range_text = param
            await request_queue.put({
                'type': 'auto_number', 
                'update': update, 
                'context': context, 
                'range_text': range_text
            })
            return
        
        elif param.isdigit() and is_new_user:
            referrer_id = str(param)
            if referrer_id != uid_str and referrer_id in existing_data:
                user_data = get_user(uid)
                user_data["referred_by"] = referrer_id
                existing_data[uid_str] = user_data
                save_data(existing_data, USER_DATA_FILE)
                
                settings = load_settings()
                refer_bonus = settings.get("refer_bonus", DEFAULT_REFER_BONUS)
                
                referrer_data = existing_data[referrer_id]
                referrer_data["balance"] = round(referrer_data.get("balance", 0.0) + refer_bonus, 4)
                referrer_data["referrals"] = referrer_data.get("referrals", 0) + 1
                referrer_data["referral_earnings"] = round(referrer_data.get("referral_earnings", 0.0) + refer_bonus, 4)
                
                existing_data[referrer_id] = referrer_data
                save_data(existing_data, USER_DATA_FILE)
                
                try:
                    ref_fullname = full_name or "N/A"
                    ref_uname = username if username else "N/A"
                    await context.bot.send_message(
                        chat_id=int(referrer_id),
                        text=(
                            f"{p_em('gift_box')} <b>New Referral Successful!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"👤 User: {html.escape(ref_fullname)} (@{ref_uname})\n"
                            f"💵 Bonus Credited: <code>+{refer_bonus}$</code>"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Failed to notify referrer: {e}")
    
    context.user_data.clear()
    
    settings = load_settings()
    start_msg = settings.get("welcome_message", DEFAULT_WELCOME_MESSAGE)
    
    try:
        bot_info = await context.bot.get_me()
        bot_name = bot_info.first_name
        start_msg = start_msg.replace("MINO NUMBER BOT", bot_name).replace("Fresh Otp Master bot", bot_name)
    except Exception:
        pass
    
    await update.message.reply_text(start_msg, parse_mode="HTML")
    await update.message.reply_text("PLEASE USE THE BUTTONS BELOW :", reply_markup=main_keyboard(uid))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    await query.answer()
    
    if not is_admin(uid) and is_user_banned(uid):
        settings = load_settings()
        support = settings.get("support_username", DEFAULT_SUPPORT_USERNAME)
        await query.edit_message_text(
            f"{p_em('ban')} <b>YOU ARE BANNED</b> {p_em('ban')}\n\n"
            f"<blockquote>{p_em('msg')} Contact Support: {support}</blockquote>",
            parse_mode="HTML"
        )
        return
    
    if is_under_maintenance(uid):
        await query.message.reply_text(f"{p_em('stop')} **SYSTEM UNDER MAINTENANCE**", parse_mode="Markdown")
        return

    if data == "toggle_fj_system":
        settings = load_settings()
        settings["force_join_enabled"] = not settings.get("force_join_enabled", False)
        save_settings(settings)
        await manage_force_join_menu(query, context, is_callback=True)
        return
        
    if data == "add_fj_channel":
        context.user_data["admin_edit_mode"] = "add_force_join"
        await context.bot.send_message(
            chat_id=uid,
            text="➕ <b>Enter the channel username to add (e.g. @MyChannel):</b>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return
        
    if data.startswith("del_fj_"):
        channel_to_del = data.replace("del_fj_", "")
        settings = load_settings()
        channels = settings.get("force_join_channels", [])
        if channel_to_del in channels:
            channels.remove(channel_to_del)
            settings["force_join_channels"] = channels
            save_settings(settings)
            await query.answer(f"✅ Deleted {channel_to_del}", show_alert=True)
        await manage_force_join_menu(query, context, is_callback=True)
        return

    if data == "check_force_join":
        is_joined = await is_user_joined_force_channels(uid, context)
        if is_joined:
            await query.message.delete()
            settings = load_settings()
            start_msg = settings.get("welcome_message", DEFAULT_WELCOME_MESSAGE)
            await context.bot.send_message(chat_id=uid, text=start_msg, parse_mode="HTML")
            await context.bot.send_message(chat_id=uid, text="PLEASE USE THE BUTTONS BELOW :", reply_markup=main_keyboard(uid))
        else:
            await query.answer("❌ আপনি can't access! আপনি এখনো সব চ্যানেলে জয়েন করেননি!", show_alert=True)
        return

    if data.startswith("setmethod_"):
        method_name = data.split("_")[1]
        uid_str = str(uid)
        user_db = load_data(USER_DATA_FILE)
        if uid_str in user_db:
            user_db[uid_str]["withdrawal_method"] = method_name
            save_data(user_db, USER_DATA_FILE)
            await query.edit_message_text(
                f"{p_em('done')} <b>WITHDRAWAL METHOD SET SUCCESSFULLY!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<blockquote>Your withdrawal method is now set to: <b>{method_name}</b></blockquote>\n"
                f"You can now use the Balance menu to request withdrawals.",
                parse_mode="HTML"
            )
        else:
            await query.answer("❌ Error: User not found.", show_alert=True)
        return

    if data == "initiate_withdraw":
        user_data = get_user(uid)
        balance = user_data.get("balance", 0.0)
        method_name = user_data.get("withdrawal_method")
        min_w, max_w = get_withdraw_limits()
        
        if not method_name:
            await query.answer("❌ Please set your withdrawal method first using /setwithdrawalmethod !", show_alert=True)
            return
            
        if balance < min_w:
            await query.answer(f"❌ Insufficient balance! Minimum withdrawal is {min_w}$.", show_alert=True)
            return
            
        context.user_data["withdraw_method"] = method_name
        context.user_data["withdraw_mode"] = "amount"
        
        await query.message.reply_text(
            f"{p_em('money')} **Withdrawal Method: {method_name}**\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💵 Total Balance: `{balance:.4f}$`\n"
            f"📉 Minimum Withdraw: `{min_w}$`\n\n"
            f"Please enter the amount to withdraw (in $):",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard()
        )
        return

    if data == "back_to_menu_inline":
        await query.message.delete()
        await context.bot.send_message(
            chat_id=uid,
            text=f"{p_em('home')} Returning to Main Menu.",
            reply_markup=main_keyboard(uid)
        )
        return

    if data == "withdraw_confirm":
        await process_withdraw_confirm(update, context)
        return
    
    if data == "withdraw_cancel":
        await process_withdraw_cancel(update, context)
        return
    
    if data.startswith("pre_approve_"):
        pid = data.replace("pre_approve_", "")
        keyboard = InlineKeyboardMarkup([
            [
                rbtn("NO, BACK", "danger", callback_data=f"back_admin_{pid}", icon_custom_emoji_id=EMOJI_ID_MAP.get("back")),
                rbtn("YES, CONFIRM", "success", callback_data=f"admin_approve_{pid}", icon_custom_emoji_id=EMOJI_ID_MAP.get("done"))
            ]
        ])
        await query.edit_message_text(f"{p_em('status')} **Are you sure you want to CONFIRM this payment?**", reply_markup=keyboard, parse_mode="Markdown")
        return

    if data.startswith("pre_reject_"):
        pid = data.replace("pre_reject_", "")
        keyboard = InlineKeyboardMarkup([
            [
                rbtn("NO, BACK", "danger", callback_data=f"back_admin_{pid}", icon_custom_emoji_id=EMOJI_ID_MAP.get("back")),
                rbtn("YES, REJECT", "success", callback_data=f"admin_reject_{pid}", icon_custom_emoji_id=EMOJI_ID_MAP.get("cross"))
            ]
        ])
        await query.edit_message_text(f"{p_em('status')} **Are you sure you want to REJECT this payment?**", reply_markup=keyboard, parse_mode="Markdown")
        return

    if data.startswith("back_admin_"):
        pid = data.replace("back_admin_", "")
        keyboard = InlineKeyboardMarkup([
            [
                rbtn("CANCEL", "danger", callback_data=f"pre_reject_{pid}", icon_custom_emoji_id=EMOJI_ID_MAP.get("cross")),
                rbtn("CONFIRM", "success", callback_data=f"pre_approve_{pid}", icon_custom_emoji_id=EMOJI_ID_MAP.get("done"))
            ]
        ])
        await query.edit_message_text(f"{p_em('stop')} **Action Cancelled. Decision again:**", reply_markup=keyboard, parse_mode="Markdown")
        return

    if data.startswith("admin_approve_"):
        payment_id = data.replace("admin_approve_", "")
        await admin_approve_withdraw(update, context, payment_id)
        return
    
    if data.startswith("admin_reject_"):
        payment_id = data.replace("admin_reject_", "")
        await admin_reject_withdraw(update, context, payment_id)
        return

    if data == "admin_back_to_config":
        context.user_data.clear()
        context.user_data["admin_mode"] = "main"
        await query.message.reply_text("Back to admin panel.", reply_markup=admin_main_keyboard())
        return

    if data == "same_range":
        settings = load_settings()
        cooldown = settings.get("cooldown_time", DEFAULT_COOLDOWN_TIME)
        current_time = time.time()
        time_passed = current_time - last_request_time.get(uid, 0.0)
        
        if time_passed < cooldown:
            wait_time = round(cooldown - time_passed, 1)
            await query.answer(f"⏱ Please wait {wait_time}s before changing number.", show_alert=True)
            return

        last_request_time[uid] = current_time
        r_text = last_range.get(uid)
        if r_text:
            await query.answer("🔄 Changing number...")
            await request_queue.put({
                'type': 'process_numbers', 
                'update': update, 
                'context': context, 
                'range_text': r_text, 
                'count': settings.get("numbers_per_request", DEFAULT_NUMBERS_PER_REQUEST),
                'edit_message': query.message
            })

    elif data == "back_to_apps":
        import time as _time
        settings = load_settings()
        auto_range_enabled = settings.get("auto_range", True)
        
        cache_age = _time.monotonic() - _ranges_cache["updated_at"]
        if auto_range_enabled and _ranges_cache["data"] and cache_age < 300:
            top_ranges_by_app = _ranges_cache["data"]
        else:
            top_ranges_by_app, err = await fetch_top55_ranges_by_app()
            if err or not top_ranges_by_app:
                top_ranges_by_app, err = await fetch_top55_ranges_by_app()
            if top_ranges_by_app:
                if auto_range_enabled:
                    _ranges_cache["data"] = top_ranges_by_app
                    _ranges_cache["updated_at"] = _time.monotonic()
            else:
                await query.edit_message_text(
                    f"{p_em('cross')} <b>Could not load ranges.</b>\n\n"
                    "<blockquote>Please try again in a moment.</blockquote>",
                    parse_mode="HTML"
                )
                return
        context.user_data["top_ranges_by_app"] = top_ranges_by_app
        buttons = build_app_buttons_from_cache(top_ranges_by_app)
        keyboard = InlineKeyboardMarkup(buttons)
        msg = f"{p_em('get_number_btn')} <b>SELECT APP TO GET</b>"
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return

    elif data.startswith("sel_app_"):
        app_name = data[len("sel_app_"):]
        cached = context.user_data.get("top_ranges_by_app", {})
        if app_name in cached:
            info = cached[app_name]
            ranges = info["ranges"]
        else:
            try:
                fresh_data, fetch_err = await fetch_top55_ranges_by_app()
                if fresh_data and app_name in fresh_data:
                    info  = fresh_data[app_name]
                    ranges = info["ranges"]
                    context.user_data["top_ranges_by_app"] = fresh_data
                    
                    settings = load_settings()
                    if settings.get("auto_range", True):
                        import time as _time2
                        _ranges_cache["data"]       = fresh_data
                        _ranges_cache["updated_at"] = _time2.monotonic()
                else:
                    ranges = []
            except Exception as e:
                await query.edit_message_text(f"❌ Failed to load ranges: {e}")
                return
        if not ranges:
            await query.edit_message_text(f"📱 {app_name} ➜ No active ranges found.", parse_mode="HTML")
            return

        country_buttons_map = {}
        for rng in ranges:
            flag, name = get_country_info(rng)
            country_key = f"{flag} {name}"
            if country_key not in country_buttons_map:
                country_buttons_map[country_key] = []
            country_buttons_map[country_key].append(rng)

        buttons = []
        row = []
        if "country_ranges" not in context.user_data:
            context.user_data["country_ranges"] = {}

        for country_label, rng_list in country_buttons_map.items():
            idx = len(context.user_data["country_ranges"]) + 1
            idx_str = str(idx)
            context.user_data["country_ranges"][idx_str] = {
                "app": app_name,
                "label": country_label,
                "ranges": rng_list
            }
            
            flag_emoji = ""
            match = re.search(r'([\U0001F1E6-\U0001F1FF]{2})', country_label)
            flag_emoji_id = None
            if match:
                flag_emoji = match.group(1)
                flag_emoji_id = PREMIUM_FLAGS.get(flag_emoji)
            
            if flag_emoji_id:
                clean_label = country_label.replace(flag_emoji, "").strip()
                row.append(rbtn(clean_label, "primary", callback_data=f"sel_cty_{idx_str}", icon_custom_emoji_id=flag_emoji_id))
            else:
                row.append(rbtn(country_label, "primary", callback_data=f"sel_cty_{idx_str}"))
            
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        
        buttons.append([rbtn("Back", "danger", callback_data="back_to_apps", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"))])
        keyboard = InlineKeyboardMarkup(buttons)
        context.user_data["selected_app"] = app_name
        msg = f"{p_em('status')} <b>Select Country for {app_name}:</b>"
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return

    elif data.startswith("sel_cty_"):
        settings = load_settings()
        cooldown = settings.get("cooldown_time", DEFAULT_COOLDOWN_TIME)
        current_time = time.time()
        time_passed = current_time - last_request_time.get(uid, 0.0)
        
        if time_passed < cooldown:
            wait_time = round(cooldown - time_passed, 1)
            await query.answer(f"⏱ Please wait {wait_time}s before requesting a new number.", show_alert=True)
            return

        idx_str = data[len("sel_cty_"):]
        cty_info = context.user_data.get("country_ranges", {}).get(idx_str)
        if not cty_info:
            await query.edit_message_text(f"{p_em('cross')} Session expired. Please try getting number again.", parse_mode="HTML")
            return
        
        app_name = cty_info["app"]
        country_label = cty_info["label"]
        country_ranges = cty_info["ranges"]

        available_ranges = country_ranges[:45]
        selected_range = random.choice(available_ranges)

        clean_rid = clean_range_id(selected_range)

        count = settings.get("numbers_per_request", DEFAULT_NUMBERS_PER_REQUEST)
        api_key, base_url = get_api_credentials()
        tasks = []
        for _ in range(count):
            tasks.append(client_async.post(
                f"{base_url}/getnumber",
                json={"api_key": api_key, "rid": clean_rid, "national": 1, "remove_plus": 1}
            ))
            
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        generated_nums = []
        for r in responses:
            if isinstance(r, Exception):
                print(f"[DEBUG] Batch fetch exception: {r}")
                continue
            try:
                print(f"[DEBUG] Batch response Status: {r.status_code}")
                numdata = r.json()
                if isinstance(numdata, dict):
                    if numdata.get("status") == "success":
                        full_number = numdata.get("number")
                        if full_number:
                            generated_nums.append(normalize_number(full_number))
            except Exception as e:
                print(f"[DEBUG] Batch response parse error: {e}")
                continue

        if not generated_nums:
            kb = InlineKeyboardMarkup([[rbtn("Back", "danger", callback_data=f"sel_app_{app_name}", icon_custom_emoji_id=EMOJI_ID_MAP.get("back"))]])
            await query.edit_message_text(f"{p_em('cross')} FAILED ➜ No valid numbers could be fetched.", reply_markup=kb, parse_mode="HTML")
            return

        for g_num in generated_nums:
            active_numbers[g_num] = {"uid": uid, "range": selected_range, "timestamp": datetime.now().isoformat()}
            save_number_range_info(uid, g_num, selected_range)
        save_active_numbers(active_numbers)
        
        last_range[uid] = selected_range
        last_request_time[uid] = current_time
        add_number_taken(uid, len(generated_nums))
        
        country_flag, country_name_local = get_country_info(generated_nums[0])
        
        num_lines = []
        for idx, g_num in enumerate(generated_nums, 1):
            num_lines.append(f"<blockquote>{p_em('get_number_btn')} <b>Number {idx}:</b> <code>+{g_num}</code></blockquote>")
        
        txt = (
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f" {p_em('get_number_btn')} <b>YOUR ACTIVE NUMBER DETAILS</b> {p_em('get_number_btn')}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"<blockquote><b>{p_em('setting')} App     :</b> <code>{app_name}</code></blockquote>\n"
            f"<blockquote><b>{p_em('status')} Country :</b> {country_flag} <code>{country_name_local}</code></blockquote>\n"
            + "\n".join(num_lines) + "\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
            f"{p_em('waiting')} <b>SMS STATUS:</b> Waiting for message... {p_em('waiting')}\n"
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>"
        )
        
        settings = load_settings()
        otp_group_url = settings.get("otp_group_url", DEFAULT_OTP_GROUP_URL)
        
        kb2 = InlineKeyboardMarkup([
            [rbtn("Change Number", "primary", callback_data="same_range", icon_custom_emoji_id=EMOJI_ID_MAP.get("change_number"))],
            [rbtn("Live OTP Group", "success", url=otp_group_url, icon_custom_emoji_id=EMOJI_ID_MAP.get("live"))]
        ])
        
        await query.edit_message_text(txt, parse_mode="HTML", reply_markup=kb2)
        return

    elif data == "edit_txt_welcome":
        context.user_data["admin_edit_mode"] = "welcome"
        await context.bot.send_message(uid, f"{p_em('msg')} <b>নতুন Welcome Message টাইপ করে পাঠান:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_txt_otpgroup":
        context.user_data["admin_edit_mode"] = "otpgroup"
        await context.bot.send_message(uid, f"{p_em('link')} <b>নতুন OTP Group লিংক পাঠান (https:// সহ):</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_txt_channel":
        context.user_data["admin_edit_mode"] = "channel"
        await context.bot.send_message(uid, f"{p_em('channel')} <b>নতুন Channel লিংক পাঠান (https:// সহ):</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_txt_support":
        context.user_data["admin_edit_mode"] = "support"
        await context.bot.send_message(uid, f"{p_em('msg')} <b>নতুন Support Username পাঠান (@ সহ):</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_api_key":
        context.user_data["admin_edit_mode"] = "api_key"
        await context.bot.send_message(uid, f"{p_em('setting')} <b>নতুন API Key টাইপ করে পাঠান:</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    elif data == "edit_api_url":
        context.user_data["admin_edit_mode"] = "api_url"
        await context.bot.send_message(uid, f"{p_em('link')} <b>নতুন API Base URL পাঠান (https:// সহ):</b>", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    elif data == "man_range_menu":
        await show_manual_ranges_menu(query, context, is_callback=True)
        return
    elif data == "toggle_auto_range_callback":
        settings = load_settings()
        settings["auto_range"] = not settings.get("auto_range", True)
        save_settings(settings)
        _ranges_cache["data"] = None
        _ranges_cache["updated_at"] = 0.0
        await show_manual_ranges_menu(query, context, is_callback=True)
        return
    elif data == "man_add_service":
        context.user_data["admin_edit_mode"] = "add_manual_service"
        await context.bot.send_message(
            chat_id=uid,
            text="✍️ <b>Enter the name of the new manual service (e.g., Telegram, IMO):</b>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return
    elif data == "man_del_service_list":
        manual_data = load_manual_ranges()
        if not manual_data:
            await query.answer("No manual services available to delete!", show_alert=True)
            return
        buttons = []
        for app in manual_data.keys():
            buttons.append([rbtn(f"Delete {app}", "danger", callback_data=f"man_delsrv_{app}")])
        buttons.append([rbtn("🔙 Back", "primary", callback_data="man_range_menu")])
        await query.message.edit_text("❌ <b>Select a service to delete completely:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        return
    elif data.startswith("man_delsrv_"):
        app_to_del = data.replace("man_delsrv_", "")
        manual_data = load_manual_ranges()
        if app_to_del in manual_data:
            del manual_data[app_to_del]
            save_manual_ranges(manual_data)
            await query.answer(f"✅ Deleted service: {app_to_del}", show_alert=True)
        await show_manual_ranges_menu(query, context, is_callback=True)
        return
    elif data == "man_add_range_list":
        manual_data = load_manual_ranges()
        if not manual_data:
            await query.answer("Please add a service first before inserting ranges!", show_alert=True)
            return
        buttons = []
        for app in manual_data.keys():
            buttons.append([rbtn(f"Add Range to {app}", "primary", callback_data=f"man_addrng_{app}")])
        buttons.append([rbtn("🔙 Back", "primary", callback_data="man_range_menu")])
        await query.message.edit_text("➕ <b>Select a service to add range:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        return
    elif data.startswith("man_addrng_"):
        app_selected = data.replace("man_addrng_", "")
        context.user_data["admin_edit_mode"] = "add_manual_range_input"
        context.user_data["selected_manual_service"] = app_selected
        await context.bot.send_message(
            chat_id=uid,
            text=f"✍️ <b>Enter the range you want to add to {app_selected} (e.g. +23769... or +22501...):</b>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return
    elif data == "man_del_range_select_service":
        manual_data = load_manual_ranges()
        if not manual_data:
            await query.answer("No services or ranges configured!", show_alert=True)
            return
        buttons = []
        for app in manual_data.keys():
            buttons.append([rbtn(f"Ranges of {app}", "primary", callback_data=f"man_delrnglist_{app}")])
        buttons.append([rbtn("🔙 Back", "primary", callback_data="man_range_menu")])
        await query.message.edit_text("❌ <b>Select a service to view and delete its ranges:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        return
    elif data.startswith("man_delrnglist_"):
        app_selected = data.replace("man_delrnglist_", "")
        manual_data = load_manual_ranges()
        ranges = manual_data.get(app_selected, [])
        if not ranges:
            await query.answer("This service has no ranges to delete!", show_alert=True)
            return
        buttons = []
        for idx, rng in enumerate(ranges):
            buttons.append([rbtn(f"Delete {rng}", "danger", callback_data=f"man_delrngitem_{app_selected}_{idx}")])
        buttons.append([rbtn("🔙 Back", "primary", callback_data="man_range_menu")])
        await query.message.edit_text(f"❌ <b>Select a range of {app_selected} to delete:</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        return
    elif data.startswith("man_delrngitem_"):
        parts = data.replace("man_delrngitem_", "").split("_")
        if len(parts) >= 2:
            app_name = "_".join(parts[:-1])
            idx = int(parts[-1])
            manual_data = load_manual_ranges()
            if app_name in manual_data and idx < len(manual_data[app_name]):
                removed_rng = manual_data[app_name].pop(idx)
                save_manual_ranges(manual_data)
                await query.answer(f"✅ Deleted range: {removed_rng}", show_alert=True)
        await show_manual_ranges_menu(query, context, is_callback=True)
        return

    elif data.startswith("copy_name_"):
        name_to_copy = data.replace("copy_name_", "")
        await query.answer(f"✅ Copied: {name_to_copy}", show_alert=True)
    
    elif data.startswith("copy_id_"):
        id_to_copy = data.replace("copy_id_", "")
        await query.answer(f"✅ Copied ID: {id_to_copy}", show_alert=True)
    
    elif data.startswith("copy_text_"):
        text_to_copy = data.replace("copy_text_", "")
        await query.answer(f"✅ Copied: {text_to_copy}", show_alert=True)

    elif data.startswith("full_logs_"):
        target_uid = data.replace("full_logs_", "")
        stats = get_user_stats(target_uid)
        
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        user_data_db = load_data(USER_DATA_FILE)
        user_info = user_data_db.get(str(target_uid), {})
        
        user_otps = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "OTP_RECEIVED"]
        
        content = f"{p_em('status')} USER FULL DATA REPORT {p_em('status')}\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        content += f"🆔 USER TELEGRAM ID : {target_uid}\n"
        content += f"🏷️ USER NAME : {str(user_info.get('full_name', 'N/A')).upper()}\n"
        content += f"👤 TELEGRAM USERNAME : @{str(user_info.get('username', 'NO_USERNAME')).upper()}\n"
        content += f"💵 CURRENT BALANCE : {user_info.get('balance', 0.0)}$\n\n"
        content += f"📊 SYSTEM STATUS SUMMARY:\n"
        content += f"⏱ TODAY NUMBERS TAKEN : {stats['today_numbers']}\n"
        content += f"⏱ TODAY OTPS RECEIVED : {stats['today_otps']}\n"
        content += f"🚀 LAST 7 DAYS NUMBERS : {stats['last7d_numbers']}\n"
        content += f"🚀 LAST 7 DAYS OTPS : {stats['last7d_otps']}\n"
        content += f"🏆 LIFETIME NUMBERS : {stats['total_numbers']}\n"
        content += f"🏆 LIFETIME OTPS : {stats['total_otps']}\n\n"
        content += f"📜 DETAILED OTP LOGS:\n\n"
        
        if not user_otps:
            content += "❌ NO OTP DATA FOUND FOR THIS USER.\n"
        else:
            for i, log in enumerate(user_otps, 1):
                try:
                    dt_obj = datetime.fromisoformat(log['timestamp'])
                    formatted_time = dt_obj.strftime("%I:%M:%S %p")
                    date_str = dt_obj.strftime("%d/%m/%Y")
                    details = log.get('details', {})
                    content += f"{i}. DATE: {date_str} | TIME: {formatted_time}\n"
                    content += f"   📱 NUMBER: {details.get('number', 'N/A')}\n"
                    content += f"   🔑 OTP: {details.get('otp', 'N/A')}\n"
                    content += f"   💬 SMS: {details.get('sms', 'N/A')}\n"
                    content += f"   -----------------------------------\n"
                except: continue

        content += f"\n\n🚀 GENERATED BY MINO OTP BOT"
        
        file = io.BytesIO(content.encode("utf-8"))
        file.name = f"USER_{target_uid}_FULL_DATA.txt"
        
        await context.bot.send_document(
            chat_id=uid,
            document=file,
            caption=f"{p_em('done')} <b>ALL DATA FOR USER:</b> <code>{target_uid}</code>",
            parse_mode="HTML"
        )

# ==================== ACTIVE DATABASE OPTIMIZER ====================

async def optimize_database_system(chat_id):
    data = load_data()
    active_numbers.clear()
    save_active_numbers(active_numbers)
    
    users = data.setdefault("users", [])
    balances = data.setdefault("balances", {})
    for uid in list(balances.keys()):
        if uid not in users:
            del balances[uid]
    
    save_data(data)

# ==================== MAIN & POST INIT SECTION ====================

async def post_init(application): 
    for _ in range(20):
        asyncio.create_task(worker())
    asyncio.create_task(monitor_loop(application))
    asyncio.create_task(_bg_refresh_ranges())

def main():
    request_config = HTTPXRequest(connect_timeout=20.0, read_timeout=20.0)
    
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request_config)
        .concurrent_updates(True)
        .post_init(post_init)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get1number", get1number_command))
    app.add_handler(CommandHandler("setwithdwalmethod", set_withdrawal_method_command))
    app.add_handler(CommandHandler("setwithdrawalmethod", set_withdrawal_method_command))
    
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 BOT RUNNING...")  
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

# নতুন কোডটি এখানে দিন
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
