import re
import time
import hashlib
import threading
import requests
import feedparser
import yfinance as yf
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Veri Terminali Pro - Nihai Canli Veri Motoru")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BIST_SYMBOLS = [
    "A1CAP","ACSEL","ADEL","ADESE","ADGYO","AEFES","AFYON","AGESA","AGHOL","AGROT","AHGAZ","AKBNK","AKCNS","AKENR","AKFGY","AKFYE","AKGRT","AKMGY","AKSA","AKSEN",
    "AKSGY","AKSUE","ALARK","ALBRK","ALCAR","ALCTL","ALFAS","ALGYO","ALKA","ALKIM","ALMAD","ALTNY","ALVES","ANELE","ANGEN","ANHYT","ANSGR","ARASE","ARCLK","ARDYZ",
    "ARENA","ARSAN","ARTMS","ARZUM","ASELS","ASGYO","ASTOR","ASUZU","ATAGY","ATAKP","ATATP","ATEKS","ATLAS","ATSYH","AVGYO","AVHOL","AVOD","AVPGY","AVTUR","AYCES",
    "AYDEM","AYEN","AYES","AYGAZ","AZTEK","BAGFS","BAKAB","BALAT","BANVT","BARMA","BASCM","BASGZ","BAYRK","BEGYO","BERA","BEYAZ","BFREN","BIENY","BIGCH","BIMAS",
    "BINHO","BIOEN","BIZIM","BJKAS","BLCYT","BMSCH","BMSTL","BNTAS","BOBET","BORLS","BORSK","BOSSA","BRISA","BRKO","BRKSN","BRKVY","BRLSM","BRMEN","BRSAN","BRYAT",
    "BSOKE","BTCIM","BUCIM","BURCE","BURVA","BVSAN","BYDNR","CANTE","CASA","CATES","CCOLA","CELHA","CEMAS","CEMTS","CEOEM","CIMSA","CLEBI","CMBTN","CMENT","CONSE",
    "COSMO","CRDFA","CRFSA","CUSAN","CVKMD","CWENE","DAGHL","DAGI","DAPGM","DARDL","DENGE","DERHL","DERIM","DESA","DESPC","DEVA","DGATE","DGGYO","DGNMO","DIRIT",
    "DITAS","DMRGD","DMSAS","DNISI","DOAS","DOBUR","DOCO","DOFER","DOGUB","DOHOL","DOKTA","DURDO","DYOBY","DZGYO","ECILC","ECZYT","EDATA","EDIP","EGEEN","EGEPO",
    "EGGUB","EGPRO","EGSER","EKGYO","EKIZ","EKOS","EKSUN","ELITE","EMKEL","EMNIS","ENERY","ENJSA","ENKAI","ENSRI","EPLAS","ERBOS","ERCB","EREGL","ERSU","ESCAR",
    "ESCOM","ESEN","ETILR","ETYAT","EUHOL","EUKYO","EUPWR","EUREN","EUYO","EYGYO","FADE","FENER","FLAP","FMIZP","FONET","FORMT","FORTE","FRIGO","FROTO","FZLGY",
    "GARAN","GARFA","GEDIK","GEDZA","GENIL","GENTS","GEREL","GESAN","GIPTA","GLBMD","GLCVY","GLRYH","GLYHO","GMTAS","GOKNR","GOLTS","GOODY","GOZDE","GRNYO","GRSEL",
    "GRTRK","GSDDE","GSDHO","GSRAY","GUBRF","GWIND","GZNMI","HALKB","HATEK","HATSN","HDFGS","HEDEF","HEKTS","HKTM","HLGYO","HTTBT","HUBVC","HUNER","HURGZ","ICBCT",
    "ICUGS","IDGYO","IEYHO","IHAAS","IHEVA","IHGZT","IHLAS","IHLGM","IHYAY","IMASM","INDES","INFO","INGRM","INTEM","INVEO","INVES","IPEKE","ISATR","ISBIR","ISBTR",
    "ISCTR","ISDMR","ISFIN","ISGSY","ISGYO","ISKPL","ISKUR","ISMEN","ISSEN","ISYAT","IZENR","IZFAS","IZINV","IZMDC","JANTS","KAPLM","KAREL","KARSN","KARTN","KARYE",
    "KATMR","KAYSE","KBORU","KCAER","KCHOL","KENT","KERVN","KERVT","KFEIN","KGYO","KIMMR","KLGYO","KLKIM","KLMSN","KLNMA","KLRHO","KLSER","KLSYN","KMPUR","KNFRT",
    "KONKA","KONTR","KONYA","KOPOL","KORDS","KOZAA","KOZAL","KRDMA","KRDMB","KRDMD","KRGYO","KRONT","KRPLS","KRSTL","KRTEK","KRVGD","KSTUR","KTLEV","KTSKR","KUTPO",
    "KUVVA","KUYAS","KZBGY","KZGYO","LIDER","LIDFA","LINK","LKMNH","LMKDC","LOGO","LRSHO","LUKSK","MAALT","MACKO","MAGEN","MAKIM","MAKTK","MANAS","MARBL","MARKA",
    "MARTI","MAVI","MEDTR","MEGAP","MEGMT","MEKAG","MEPET","MERCN","MERIT","MERKO","METRO","METUR","MGROS","MHRGY","MIATK","MIPAZ","MMCAS","MNDRS","MNDTR","MOBTL",
    "MOGAN","MPARK","MRGYO","MRSHL","MSGYO","MTRKS","MTRYO","MZHLD","NATEN","NETAS","NIBAS","NTGAZ","NTHOL","NUGYO","NUHCM","OBAMS","OBASE","ODAS","ODINE","OFSYM",
    "ONCSM","ORCAY","ORGE","ORMA","OSMEN","OSTIM","OTKAR","OTTO","OYAKC","OYAYO","OYLUM","OYYAT","OZGYO","OZKGY","OZRDN","OZSUB","PAGYO","PAMEL","PAPIL","PARSN",
    "PASEU","PATEK","PCILT","PEGYO","PEKGY","PENGD","PENTA","PETKM","PETUN","PGSUS","PINSU","PKART","PKENT","PLTUR","PNLSN","PNSUT","POLHO","POLTK","PRDGS","PRKAB",
    "PRKME","PRZMA","PSDTC","PSGYO","QNBFB","QNBFL","QUAGR","RALYH","RAYSG","REEDR","RGYAS","RNPOL","RODRG","ROYAL","RTALB","RUBNS","RYGYO","RYSAS","SAFKR","SAHOL",
    "SAMAT","SANEL","SANFM","SANKO","SARKY","SASA","SAYAS","SDTTR","SEGYO","SEKFK","SEKUR","SELEC","SELGD","SELVA","SEYKM","SILVR","SISE","SKBNK","SKTAS","SKYLP",
    "SKYMD","SMART","SMRTG","SNGYO","SNICA","SNKRN","SNPAM","SODSN","SOKE","SOKM","SONME","SRVGY","SUMAS","SUNTK","SURGY","SUWEN","TABGD","TARKM","TATEN","TATGD",
    "TAVHL","TBORG","TCELL","TDGYO","TEKTU","TERA","TETMT","TEZOL","TGSAS","THYAO","TKFEN","TKNSA","TLMAN","TMPOL","TMSN","TNZTP","TOASO","TRCAS","TRGYO","TRILC",
    "TSGYO","TSKB","TSPOR","TTKOM","TTRAK","TUCLK","TUKAS","TUPRS","TUREX","TURGG","TURSG","UFUK","ULAS","ULKER","ULUFA","ULUSE","ULUUN","UMPAS","UNLU","USAK",
    "UZERB","VAKBN","VAKFN","VAKKO","VANGD","VBTYZ","VERTU","VERUS","VESBE","VESTL","VKFYO","VKGYO","VKING","VRGYO","YAPRK","YATAS","YAYLA","YBTAS","YEOTK","YESIL",
    "YGGYO","YGYO","YKBNK","YKSLN","YONGA","YUNSA","YYAPI","YYLGD","ZEDUR","ZOREN","ZRGYO"
]

COMPANY_NAME_TO_SYMBOL = {
    "TÜRK HAVA YOLLARI": "THYAO", "THY": "THYAO", "ASELSAN": "ASELS", "EREĞLİ": "EREGL", "ERDEMİR": "EREGL",
    "KOÇ HOLDİNG": "KCHOL", "SABANCI": "SAHOL", "GARANTİ": "GARAN", "AKBANK": "AKBNK", "İŞ BANKASI": "ISCTR",
    "YAPI KREDİ": "YKBNK", "TÜPRAŞ": "TUPRS", "FORD OTOSAN": "FROTO", "TOFAŞ": "TOASO", "ŞİŞECAM": "SISE",
    "BİM": "BIMAS", "MİGROS": "MGROS", "TURKCELL": "TCELL", "TÜRK TELEKOM": "TTKOM", "PEGASUS": "PGSUS",
    "ASTOR": "ASTOR", "KONTR": "KONTR", "KONTROLMATİK": "KONTR", "SASA": "SASA", "HEKTAŞ": "HEKTS",
    "ODİNE": "ODINE", "ENKA": "ENKAI", "KARDEMİR": "KRDMD", "PETKİM": "PETKM", "ARÇELİK": "ARCLK",
    "VESTEL": "VESTL", "EMLAK KONUT": "EKGYO", "GÜBRE FABRİKALARI": "GUBRF", "TAV": "TAVHL", "KOZA": "KOZAL"
}

INDICES_AND_FX = [
    {"symbol": "XU100", "yf": "XU100.IS", "name": "BIST 100 Endeksi", "market": "BIST", "sector": "ENDEKS"},
    {"symbol": "XU030", "yf": "XU030.IS", "name": "BIST 30 Endeksi", "market": "BIST", "sector": "ENDEKS"},
    {"symbol": "ALTIN", "yf": "GC=F", "name": "Ons Altın (COMEX USD)", "market": "COMMODITY", "sector": "DEĞERLİ MADEN"},
    {"symbol": "GUMUS", "yf": "SI=F", "name": "Ons Gümüş (COMEX USD)", "market": "COMMODITY", "sector": "DEĞERLİ MADEN"},
    {"symbol": "BRENT", "yf": "BZ=F", "name": "Brent Ham Petrol (USD)", "market": "COMMODITY", "sector": "ENERJİ"},
    {"symbol": "DOGALGAZ", "yf": "NG=F", "name": "Doğalgaz (NYMEX USD)", "market": "COMMODITY", "sector": "ENERJİ"},
    {"symbol": "USD/TRY", "yf": "TRY=X", "name": "ABD Doları / Türk Lirası", "market": "FOREX", "sector": "DÖVİZ"},
    {"symbol": "EUR/TRY", "yf": "EURTRY=X", "name": "Euro / Türk Lirası", "market": "FOREX", "sector": "DÖVİZ"},
]

GLOBAL_LEADERS = [
    {"symbol": "NVDA", "yf": "NVDA", "name": "NVIDIA Corporation (NASDAQ)", "market": "GLOBAL", "sector": "YARI İLETKEN"},
    {"symbol": "AAPL", "yf": "AAPL", "name": "Apple Inc. (NASDAQ)", "market": "GLOBAL", "sector": "TEKNOLOJİ"},
    {"symbol": "MSFT", "yf": "MSFT", "name": "Microsoft Corp. (NASDAQ)", "market": "GLOBAL", "sector": "YAZILIM"},
    {"symbol": "TSLA", "yf": "TSLA", "name": "Tesla Inc. (NASDAQ)", "market": "GLOBAL", "sector": "OTOMOTİV"},
    {"symbol": "META", "yf": "META", "name": "Meta Platforms (NASDAQ)", "market": "GLOBAL", "sector": "TEKNOLOJİ"},
]

MARKET_CACHE = {}
META_ENRICHED_AT = {}
CACHE_LOCK = threading.Lock()
DATA_LOCK = threading.Lock()


def _cache_key(symbol: str, market: str = "") -> str:
    s = symbol.upper().strip()
    m = (market or "").upper().strip()
    return f"{m}:{s}" if m else s


def set_market_item(key: str, value: dict):
    sym = value.get("symbol", key).upper().strip()
    mkt = value.get("market", "").upper().strip()
    ck = _cache_key(sym, mkt)
    with CACHE_LOCK:
        MARKET_CACHE[ck] = value
        # Geriye dönük doğrudan sembol aramaları için de sakla (aynı sembolde çakışma olursa öncelik koru)
        if sym not in MARKET_CACHE or MARKET_CACHE[sym].get("market") == mkt:
            MARKET_CACHE[sym] = value


def get_market_snapshot() -> list:
    with CACHE_LOCK:
        seen_keys = set()
        out = []
        for k, v in MARKET_CACHE.items():
            if ":" in k:
                out.append(v)
                seen_keys.add(k)
        for k, v in MARKET_CACHE.items():
            if ":" not in k:
                ck = _cache_key(v.get("symbol", k), v.get("market", ""))
                if ck not in seen_keys:
                    out.append(v)
        return out


def get_market_item(key: str, market: str = ""):
    s = key.upper().strip()
    with CACHE_LOCK:
        if market:
            item = MARKET_CACHE.get(_cache_key(s, market))
            if item:
                return item
        if s in MARKET_CACHE:
            return MARKET_CACHE[s]
        for mkt in ("BIST", "GLOBAL", "COMMODITY", "FOREX", "CRYPTO"):
            item = MARKET_CACHE.get(_cache_key(s, mkt))
            if item:
                return item
        return None


NEWS_CACHE = []
SPK_KAP_CACHE = []
BALANCE_CACHE = {}
ARTICLE_CACHE = {}


def sync_all_crypto_coingecko():
    while True:
        try:
            now_str = time.strftime("%H:%M:%S")
            for page in range(1, 3):
                url = "https://api.coingecko.com/api/v3/coins/markets"
                params = {
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 125,
                    "page": page,
                    "sparkline": "false"
                }
                resp = requests.get(url, params=params, timeout=12)
                if resp.status_code == 200:
                    for c in resp.json():
                        sym = c["symbol"].upper()
                        price = float(c.get("current_price") or 0)
                        chg = float(c.get("price_change_percentage_24h") or 0)
                        high = float(c.get("high_24h") or price)
                        low = float(c.get("low_24h") or price)
                        vol = float(c.get("total_volume") or 0)
                        decimals = 6 if price < 0.01 else (4 if price < 2 else 2)
                        set_market_item(_cache_key(sym, "CRYPTO"), {
                            "symbol": sym,
                            "yf": f"{sym}-USD",
                            "name": f"{c['name']} (USD)",
                            "market": "CRYPTO",
                            "sector": "KRİPTO",
                            "price": round(price, decimals),
                            "prevPrice": round(price, decimals),
                            "changePct": round(chg, 2),
                            "high": round(high, decimals),
                            "low": round(low, decimals),
                            "volume": int(vol),
                            "updatedAt": now_str
                        })
                time.sleep(1.5)
        except Exception:
            pass
        time.sleep(30)


def _maybe_enrich_metadata(item: dict, ticker_obj):
    sym = item["symbol"]
    if item.get("market") != "BIST" or item.get("sector") == "ENDEKS":
        return item["name"], item["sector"]
    now = time.time()
    last_enr = META_ENRICHED_AT.get(sym, 0)
    existing = get_market_item(sym, item.get("market", "")) or item
    cur_name = existing.get("name", item["name"])
    cur_sector = existing.get("sector", item["sector"])

    if (now - last_enr) < 3600 and "(Borsa İstanbul)" not in cur_name and cur_sector != "BIST":
        return cur_name, cur_sector

    META_ENRICHED_AT[sym] = now
    try:
        info = ticker_obj.info or {}
        long_name = info.get("longName") or info.get("shortName")
        sec = info.get("sector")
        new_name = f"{long_name} ({sym})" if long_name else cur_name
        new_sector = sec if sec else cur_sector
        return new_name, new_sector
    except Exception:
        return cur_name, cur_sector


def _extract_quote_from_ticker(item, ticker_obj, now_str):
    price = 0.0
    prev = 0.0
    high = 0.0
    low = 0.0
    vol = 0
    try:
        info = ticker_obj.fast_info
        price = float(info.last_price or 0)
        prev = float(info.previous_close or price)
        high = float(info.day_high or price)
        low = float(info.day_low or price)
        vol = int(getattr(info, "last_volume", 0) or 0)
    except Exception:
        pass

    if not price or price <= 0:
        hist = ticker_obj.history(period="5d")
        if hist is not None and not hist.empty:
            price = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
            high = float(hist["High"].iloc[-1])
            low = float(hist["Low"].iloc[-1])
            vol = int(hist["Volume"].iloc[-1] or 0)

    if price and price > 0:
        chg = ((price - prev) / prev * 100) if prev else 0.0
        decimals = 4 if price < 2 else 2
        enriched_name, enriched_sector = _maybe_enrich_metadata(item, ticker_obj)
        set_market_item(_cache_key(item["symbol"], item["market"]), {
            **item,
            "name": enriched_name,
            "sector": enriched_sector,
            "price": round(price, decimals),
            "prevPrice": round(prev, decimals),
            "changePct": round(chg, 2),
            "high": round(high or price, decimals),
            "low": round(low or price, decimals),
            "volume": vol,
            "updatedAt": now_str
        })


def sync_bist_and_global():
    for item in INDICES_AND_FX + GLOBAL_LEADERS:
        if get_market_item(item["symbol"], item["market"]) is None:
            set_market_item(_cache_key(item["symbol"], item["market"]), {
                **item, "price": 0.0, "prevPrice": 0.0, "changePct": 0.0,
                "high": 0.0, "low": 0.0, "volume": 0, "updatedAt": "Bekliyor"
            })

    for s in BIST_SYMBOLS:
        if get_market_item(s, "BIST") is None:
            set_market_item(_cache_key(s, "BIST"), {
                "symbol": s, "yf": f"{s}.IS", "name": f"{s} (Borsa İstanbul)",
                "market": "BIST", "sector": "BIST", "price": 0.0, "prevPrice": 0.0,
                "changePct": 0.0, "high": 0.0, "low": 0.0, "volume": 0, "updatedAt": "Bekliyor"
            })

    all_yf_items = (
        INDICES_AND_FX
        + [{"symbol": s, "yf": f"{s}.IS", "name": f"{s} (Borsa İstanbul)", "market": "BIST", "sector": "BIST"} for s in BIST_SYMBOLS]
        + GLOBAL_LEADERS
    )

    chunk_size = 75
    while True:
        for i in range(0, len(all_yf_items), chunk_size):
            chunk = all_yf_items[i:i + chunk_size]
            try:
                yf_str = " ".join([x["yf"] for x in chunk])
                tickers = yf.Tickers(yf_str)
                now_str = time.strftime("%H:%M:%S")
                for item in chunk:
                    try:
                        _extract_quote_from_ticker(item, tickers.tickers[item["yf"]], now_str)
                    except Exception:
                        pass
            except Exception:
                pass
            time.sleep(0.6)
        time.sleep(4)


@app.get("/api/search")
def search_global_assets(q: str = Query("")):
    query = q.strip().upper()
    snapshot = get_market_snapshot()
    if not query:
        return snapshot[:80]
    local_matches = [v for v in snapshot if query in v["symbol"].upper() or query in v["name"].upper()]
    if len(query) >= 2:
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            resp = requests.get(url, params={"q": query, "quotesCount": 12, "newsCount": 0}, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
            if resp.status_code == 200:
                for qt in resp.json().get("quotes", []):
                    yf_sym = qt.get("symbol", "")
                    if not yf_sym:
                        continue
                    exch = qt.get("exchDisp", qt.get("exchange", "GLOBAL"))
                    long_name = qt.get("longname") or qt.get("shortname") or yf_sym
                    clean_sym = yf_sym.replace(".IS", "") if yf_sym.endswith(".IS") else yf_sym
                    mkt = "BIST" if yf_sym.endswith(".IS") else "GLOBAL"
                    existing = get_market_item(clean_sym, mkt)
                    if existing is None:
                        existing = {
                            "symbol": clean_sym, "yf": yf_sym, "name": f"{long_name} ({exch})",
                            "market": mkt, "sector": exch, "price": 0.0, "prevPrice": 0.0,
                            "changePct": 0.0, "high": 0.0, "low": 0.0, "volume": 0, "updatedAt": "Tıkla"
                        }
                        set_market_item(_cache_key(clean_sym, mkt), existing)
                    if not any(x["symbol"] == clean_sym and x["market"] == mkt for x in local_matches):
                        local_matches.append(existing)
        except Exception:
            pass
    return local_matches[:50]


@app.get("/api/quote/{symbol}")
def fetch_single_live_quote(symbol: str):
    sym = symbol.upper().strip()
    item = get_market_item(sym)
    yf_code = item["yf"] if item else (f"{sym}.IS" if sym in BIST_SYMBOLS else sym)
    try:
        t = yf.Ticker(yf_code)
        p = float(t.fast_info.last_price)
        prev = float(t.fast_info.previous_close or p)
        chg = round(((p - prev) / prev * 100), 2) if prev else 0.0
        decimals = 6 if p < 0.01 else (4 if p < 2 else 2)
        mkt = item["market"] if item else ("BIST" if yf_code.endswith(".IS") else "GLOBAL")
        updated = {
            "symbol": sym, "yf": yf_code,
            "name": (item["name"] if item else (t.info or {}).get("longName", sym)),
            "market": mkt,
            "sector": (item["sector"] if item else (t.info or {}).get("sector", "PİYASA")),
            "price": round(p, decimals), "prevPrice": round(prev, decimals), "changePct": chg,
            "high": round(float(t.fast_info.day_high or p), decimals),
            "low": round(float(t.fast_info.day_low or p), decimals),
            "volume": int(getattr(t.fast_info, "last_volume", 0) or 0),
            "updatedAt": time.strftime("%H:%M:%S")
        }
        set_market_item(_cache_key(sym, mkt), updated)
        return updated
    except Exception:
        return item or {"symbol": sym, "price": 0, "changePct": 0}


@app.get("/api/markets")
def get_markets():
    return get_market_snapshot()


@app.get("/api/movers")
def get_bist_movers(limit: int = Query(60)):
    snapshot = get_market_snapshot()
    bist_active = [
        m for m in snapshot
        if m.get("market") == "BIST" and m.get("sector") != "ENDEKS" and isinstance(m.get("price"), (int, float)) and m["price"] > 0
    ]
    sorted_desc = sorted(bist_active, key=lambda x: x.get("changePct", 0), reverse=True)
    sorted_asc = sorted(bist_active, key=lambda x: x.get("changePct", 0))
    cap = len(bist_active) if limit <= 0 else limit
    return {
        "gainers": sorted_desc[:cap],
        "losers": sorted_asc[:cap],
        "totalActive": len(bist_active),
        "updatedAt": time.strftime("%H:%M:%S")
    }


@app.get("/api/akd-takas/{symbol}")
def get_akd_and_takas(symbol: str):
    sym = symbol.upper().strip()
    item = get_market_item(sym, "BIST") or get_market_item(sym) or {"price": 100.0, "changePct": 0.0, "volume": 1500000, "high": 102.0, "low": 98.0, "name": sym}
    price = float(item.get("price") or 100.0)
    chg = float(item.get("changePct") or 0.0)
    vol = int(item.get("volume") or 1250000)
    high = float(item.get("high") or price * 1.02)
    low = float(item.get("low") or price * 0.98)

    pos_ratio = ((price - low) / (high - low)) if high > low else 0.5
    pos_ratio = max(0.15, min(0.88, pos_ratio))
    net_flow_pct = round((pos_ratio - 0.5) * 100 + (chg * 2.2), 1)
    net_flow_pct = max(-68.0, min(68.0, net_flow_pct))

    seed = int(hashlib.md5(f"{sym}-{time.strftime('%Y%m%d')}".encode()).hexdigest()[:8], 16)
    brokers = [
        "BofA Securities", "İş Yatırım", "Yapı Kredi Yatırım", "Garanti BBVA", "QNB Finansinvest",
        "Ak Yatırım", "Deniz Yatırım", "Osmanlı Yatırım", "Tacirler Yatırım", "Ziraat Yatırım",
        "Vakıf Yatırım", "Halk Yatırım", "TEB Yatırım", "Gedik Yatırım", "İnfo Yatırım",
        "Ünlü Menkul", "HSBC Yatırım", "PhillipCapital", "A1 Capital", "Meksa Yatırım"
    ]
    custodians = [
        "CitiBank Yabancı", "Deutsche Bank Yabancı", "İş Yatırım Saklama", "Garanti BBVA Saklama",
        "Yapı Kredi Saklama", "Ak Yatırım Saklama", "Emeklilik Fonları", "Yatırım Fonları"
    ]

    buyers = []
    sellers = []
    base_lot = max(50000, int(vol * 0.16))
    for i in range(10):
        b_name = brokers[(seed + i) % len(brokers)]
        s_name = brokers[(seed + i + 10) % len(brokers)]
        factor = max(0.15, 1.35 - i * 0.12)
        b_lot = int(base_lot * factor * (1.15 if chg >= 0 else 0.85))
        s_lot = int(base_lot * factor * (0.85 if chg >= 0 else 1.15))
        buyers.append({
            "rank": i + 1, "broker": b_name, "netLot": b_lot,
            "netTl": round(b_lot * price, 0),
            "avgCost": round(price * (0.991 + i * 0.0012), 2),
            "sharePct": round(max(1.8, 22.5 - i * 2.1), 1)
        })
        sellers.append({
            "rank": i + 1, "broker": s_name, "netLot": -s_lot,
            "netTl": round(-s_lot * price, 0),
            "avgCost": round(price * (1.008 - i * 0.0012), 2),
            "sharePct": round(max(1.8, 21.8 - i * 2.0), 1)
        })

    takas_list = []
    rem = 100.0
    for i in range(7):
        pct = round(min(rem, max(2.1, (24.5 - i * 2.9) + ((seed >> i) % 3))), 2)
        rem = round(rem - pct, 2)
        wk_diff = round((((seed >> (i + 2)) % 15) - 6) * 0.16 + (chg * 0.04), 2)
        mo_diff = round(wk_diff * 2.4, 2)
        takas_list.append({
            "institution": custodians[i], "sharePct": pct,
            "weeklyChangePct": wk_diff, "monthlyChangePct": mo_diff
        })
    takas_list.append({
        "institution": "Diğer Kurumlar", "sharePct": max(0.0, round(rem, 2)),
        "weeklyChangePct": round(-sum(x["weeklyChangePct"] for x in takas_list), 2),
        "monthlyChangePct": round(-sum(x["monthlyChangePct"] for x in takas_list), 2)
    })

    return {
        "symbol": sym,
        "name": item.get("name", sym),
        "price": price,
        "changePct": chg,
        "totalVolume": vol,
        "totalTurnoverTl": round(vol * price, 0),
        "netMoneyFlowPct": net_flow_pct,
        "top5BuyerShare": round(sum(x["sharePct"] for x in buyers[:5]), 1),
        "top5SellerShare": round(sum(x["sharePct"] for x in sellers[:5]), 1),
        "buyers": buyers,
        "sellers": sellers,
        "takas": takas_list,
        "isModelEstimate": True,
        "updatedAt": time.strftime("%H:%M:%S")
    }


def _normalize_yf_interval_period(interval: str, period: str):
    valid_intervals = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"}
    iv = interval if interval in valid_intervals else "1d"
    pr = "max" if period in ["all", "MAX", "max"] else period
    if iv in {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"} and pr in {"1y", "2y", "5y", "10y", "max"}:
        pr = "60d"
    return iv, pr


@app.get("/api/history/{symbol}")
def get_history(symbol: str, interval: str = "1d", period: str = "max"):
    sym = symbol.upper().strip()
    item = get_market_item(sym)
    yf_code = item["yf"] if item else (f"{sym}.IS" if sym in BIST_SYMBOLS else sym)
    safe_interval, safe_period = _normalize_yf_interval_period(interval, period)
    try:
        df = yf.Ticker(yf_code).history(period=safe_period, interval=safe_interval)
        if df is None or df.empty:
            df = yf.Ticker(yf_code).history(period="max", interval="1d")
        candles = []
        for idx, row in df.iterrows():
            if row["Close"] != row["Close"] or row["Open"] != row["Open"]:
                continue
            ts = int(idx.timestamp()) if safe_interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"] else idx.strftime("%Y-%m-%d")
            candles.append({
                "time": ts,
                "open": round(float(row["Open"]), 6),
                "high": round(float(row["High"]), 6),
                "low": round(float(row["Low"]), 6),
                "close": round(float(row["Close"]), 6),
                "volume": int(row["Volume"] or 0)
            })
        return candles
    except Exception:
        return []


def format_num(val):
    if val is None or val != val:
        return "A/D"
    num = float(val)
    sign = "-" if num < 0 else ""
    num = abs(num)
    if num >= 1e12:
        return f"{sign}{num/1e12:.2f} Trilyon"
    if num >= 1e9:
        return f"{sign}{num/1e9:.2f} Milyar"
    if num >= 1e6:
        return f"{sign}{num/1e6:.2f} Milyon"
    return f"{sign}{num:,.0f}"


@app.get("/api/balance/{symbol}")
def get_balance(symbol: str):
    sym = symbol.upper().strip()
    with DATA_LOCK:
        cached = BALANCE_CACHE.get(sym)
        if cached and (time.time() - cached["ts"] < 600):
            return cached["data"]

    item = get_market_item(sym)
    yf_code = item["yf"] if item else (f"{sym}.IS" if sym in BIST_SYMBOLS else sym)
    name = item["name"] if item else sym
    sector = item["sector"] if item else "PİYASA"

    try:
        t = yf.Ticker(yf_code)
        info = t.info or {}
        fin = t.quarterly_financials
        bs = t.quarterly_balance_sheet
        cf = t.quarterly_cashflow

        def get_row(df, keys):
            if df is None or df.empty:
                return "A/D"
            col = df.columns[0]
            for k in keys:
                if k in df.index:
                    return format_num(df.loc[k, col])
            return "A/D"

        period = str(fin.columns[0])[:10] if (fin is not None and not fin.empty) else "Son Dönem"
        prev_period = str(fin.columns[1])[:10] if (fin is not None and len(fin.columns) > 1) else "Önceki Dönem"

        result = {
            "symbol": sym, "name": info.get("longName", name), "sector": info.get("sector", sector),
            "period": period, "prevPeriod": prev_period,
            "revenue": get_row(fin, ["Total Revenue", "Operating Revenue"]),
            "grossProfit": get_row(fin, ["Gross Profit"]),
            "ebitda": get_row(fin, ["EBITDA", "Normalized EBITDA", "Operating Income"]),
            "netProfit": get_row(fin, ["Net Income", "Net Income Common Stockholders"]),
            "prevNetProfit": format_num(fin.loc["Net Income", fin.columns[1]]) if (fin is not None and len(fin.columns) > 1 and "Net Income" in fin.index) else "A/D",
            "totalAssets": get_row(bs, ["Total Assets"]),
            "currentAssets": get_row(bs, ["Current Assets"]),
            "totalDebt": get_row(bs, ["Total Debt", "Total Liabilities Net Minority Interest"]),
            "cashEquiv": get_row(bs, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]),
            "totalEquity": get_row(bs, ["Stockholders Equity", "Total Equity Gross Minority Interest"]),
            "freeCashflow": get_row(cf, ["Free Cash Flow", "Operating Cash Flow"]),
            "marketCap": format_num(info.get("marketCap")) if info.get("marketCap") else "A/D",
            "pe": round(float(info["trailingPE"]), 2) if info.get("trailingPE") else "A/D",
            "pb": round(float(info["priceToBook"]), 2) if info.get("priceToBook") else "A/D",
            "roe": f"%{round(float(info['returnOnEquity']) * 100, 1)}" if info.get("returnOnEquity") else "A/D",
            "profitMargin": f"%{round(float(info['profitMargins']) * 100, 1)}" if info.get("profitMargins") else "A/D"
        }
        with DATA_LOCK:
            BALANCE_CACHE[sym] = {"ts": time.time(), "data": result}
        return result
    except Exception:
        return {
            "symbol": sym, "name": name, "sector": sector, "period": "Güncel", "prevPeriod": "-",
            "revenue": "A/D", "grossProfit": "A/D", "ebitda": "A/D", "netProfit": "A/D", "prevNetProfit": "A/D",
            "totalAssets": "A/D", "currentAssets": "A/D", "totalDebt": "A/D", "cashEquiv": "A/D",
            "totalEquity": "A/D", "freeCashflow": "A/D", "marketCap": "A/D",
            "pe": "A/D", "pb": "A/D", "roe": "A/D", "profitMargin": "A/D"
        }


def detect_symbol_and_category(text: str, is_kap: bool = False):
    up = text.upper()
    words = re.findall(r"\b[A-Z0-9]{4,6}\b", up)
    for w in words:
        if w in BIST_SYMBOLS:
            return w, "BIST"

    for cname, sym in COMPANY_NAME_TO_SYMBOL.items():
        if cname in up:
            return sym, "BIST"

    crypto_map = {"BITCOIN": "BTC", "BTC": "BTC", "ETHEREUM": "ETH", "ETH": "ETH", "SOLANA": "SOL", "RIPPLE": "XRP", "KRİPTO": "BTC"}
    for k, sym in crypto_map.items():
        if k in up:
            return sym, "CRYPTO"

    comm_map = {"ALTIN": "ALTIN", "ONS": "ALTIN", "GÜMÜŞ": "GUMUS", "PETROL": "BRENT", "BRENT": "BRENT", "DOĞALGAZ": "DOGALGAZ", "DOLAR": "USD/TRY", "EURO": "EUR/TRY"}
    for k, sym in comm_map.items():
        if k in up:
            return sym, "COMMODITY"

    global_map = {"NVIDIA": "NVDA", "APPLE": "AAPL", "TESLA": "TSLA", "MICROSOFT": "MSFT", "NASDAQ": "NVDA", "FED": "NVDA"}
    for k, sym in global_map.items():
        if k in up:
            return sym, "GLOBAL"

    if is_kap or "SPK" in up or "SERMAYE PİYASASI" in up:
        return "SPK / BIST", "BIST"
    if any(k in up for k in ["BORSA", "BIST", "ENDEKS", "HİSSE", "HALKA ARZ"]):
        return "XU100", "BIST"
    return "MAKRO", "MAKRO"


def clean_html_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    txt = re.sub(r"<script[^>]*>.*?</script>", " ", raw_html, flags=re.S | re.I)
    txt = re.sub(r"<style[^>]*>.*?</style>", " ", txt, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = txt.replace("&nbsp;", " ").replace("&quot;", '"').replace("&amp;", "&").replace("&#39;", "'")
    return re.sub(r"\s+", " ", txt).strip()


def fetch_rss_with_headers(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return feedparser.parse(resp.content)


def update_live_news_and_spk():
    global NEWS_CACHE, SPK_KAP_CACHE
    rss_sources = [
        ("BLOOMBERG HT", "https://www.bloomberght.com/rss"),
        ("CNBC-E FİNANS", "https://www.cnbce.com/rss"),
        ("GOOGLE FİNANS TR", "https://news.google.com/rss/search?q=borsa+istanbul+OR+kripto+OR+alt%C4%B1n+when:1d&hl=tr&gl=TR&ceid=TR:tr"),
        ("GLOBAL PİYASALAR", "https://news.google.com/rss/search?q=nasdaq+OR+fed+OR+nvidia+hisse+when:1d&hl=tr&gl=TR&ceid=TR:tr")
    ]
    spk_sources = [
        ("KAP BİLDİRİMİ", "https://news.google.com/rss/search?q=site:kap.org.tr+OR+%22KAP%22+hisse+bedelsiz+OR+ihale+OR+bilanco+when:3d&hl=tr&gl=TR&ceid=TR:tr"),
        ("SPK BÜLTEN & TEDBİR", "https://news.google.com/rss/search?q=%22SPK%22+b%C3%BClteni+OR+tedbir+OR+halka+arz+when:3d&hl=tr&gl=TR&ceid=TR:tr")
    ]
    while True:
        news_items = []
        seen_titles = set()
        for source_name, url in rss_sources:
            try:
                feed = fetch_rss_with_headers(url)
                for idx, entry in enumerate(feed.entries[:12]):
                    title = entry.get("title", "").strip()
                    if not title or title in seen_titles:
                        continue
                    seen_titles.add(title)
                    raw_sum = entry.get("summary", entry.get("description", ""))
                    if entry.get("content"):
                        raw_sum = entry["content"][0].get("value", raw_sum)
                    full_summary = clean_html_text(raw_sum) or title
                    sym, cat = detect_symbol_and_category(f"{title} {full_summary}", is_kap=False)
                    pub_time = entry.get("published", "")
                    time_label = pub_time[17:22] if len(pub_time) >= 22 else time.strftime("%H:%M")
                    news_items.append({
                        "id": f"NEWS-{hashlib.md5(title.encode()).hexdigest()[:10]}",
                        "source": source_name,
                        "symbol": sym,
                        "category": cat,
                        "headline": title,
                        "summary": full_summary[:240],
                        "fullSummary": full_summary,
                        "link": entry.get("link", "#"),
                        "time": time_label
                    })
            except Exception:
                pass
        if news_items:
            with DATA_LOCK:
                NEWS_CACHE = news_items[:40]

        spk_items = []
        seen_kap = set()
        for source_name, url in spk_sources:
            try:
                feed = fetch_rss_with_headers(url)
                for idx, entry in enumerate(feed.entries[:15]):
                    title = entry.get("title", "").strip()
                    if not title or title in seen_kap:
                        continue
                    seen_kap.add(title)
                    raw_sum = entry.get("summary", entry.get("description", ""))
                    if entry.get("content"):
                        raw_sum = entry["content"][0].get("value", raw_sum)
                    full_summary = clean_html_text(raw_sum) or title
                    sym, _ = detect_symbol_and_category(f"{title} {full_summary}", is_kap=True)
                    spk_items.append({
                        "id": f"KAP-{hashlib.md5(title.encode()).hexdigest()[:10]}",
                        "source": source_name,
                        "code": f"KAP-{984100 + idx}",
                        "symbol": sym,
                        "headline": title,
                        "summary": full_summary[:240],
                        "fullSummary": full_summary,
                        "link": entry.get("link", "#"),
                        "time": time.strftime("%H:%M")
                    })
            except Exception:
                pass
        if spk_items:
            with DATA_LOCK:
                SPK_KAP_CACHE = spk_items[:30]
        time.sleep(45)


@app.get("/api/article")
def get_full_article(url: str = Query("")):
    if not url or url == "#":
        return {"paragraphs": []}
    with DATA_LOCK:
        cached = ARTICLE_CACHE.get(url)
        if cached and (time.time() - cached["ts"] < 1800):
            return {"paragraphs": cached["paragraphs"]}
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"
        }
        resp = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        html = resp.text
        html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
        html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
        raw_ps = re.findall(r"<p[^>]*>(.*?)</p>", html, flags=re.S | re.I)
        paragraphs = []
        seen = set()
        for p in raw_ps:
            clean_p = clean_html_text(p)
            if len(clean_p) >= 45 and clean_p not in seen:
                if any(skip in clean_p.lower() for skip in ["çerez", "cookie", "gizlilik politikası", "abone ol", "tüm hakları saklıdır"]):
                    continue
                seen.add(clean_p)
                paragraphs.append(clean_p)
            if len(paragraphs) >= 14:
                break
        with DATA_LOCK:
            ARTICLE_CACHE[url] = {"ts": time.time(), "paragraphs": paragraphs}
        return {"paragraphs": paragraphs}
    except Exception:
        return {"paragraphs": []}


@app.get("/api/news")
def get_news():
    with DATA_LOCK:
        return list(NEWS_CACHE)


@app.get("/api/spk-kap")
def get_spk_kap():
    with DATA_LOCK:
        return list(SPK_KAP_CACHE)


if __name__ == "__main__":
    threading.Thread(target=sync_all_crypto_coingecko, daemon=True).start()
    threading.Thread(target=sync_bist_and_global, daemon=True).start()
    threading.Thread(target=update_live_news_and_spk, daemon=True).start()
    print("Veri Terminali Pro Sunucusu Baslatildi -> http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)