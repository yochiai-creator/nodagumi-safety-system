
import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import urllib.parse
import requests

APP_TITLE = "野田組 安全教育管理システム V7"
PUBLIC_URL = "https://nodagumi-safety-system-sqr2d6pvnm3yc3q4kovivy.streamlit.app"
PASS_SCORE = 70

DEFAULT_DEPTS = ["容器請負", "アーム請負", "土木部", "警備", "派遣"]
DEFAULT_TYPES = [
    "フォークリフト安全講習",
    "ホイールローダー除雪作業",
    "除雪排雪ダンプ運転手",
    "警備員教育",
    "玉掛け安全教育",
    "クレーン安全教育",
    "KY活動",
    "新入社員安全教育",
    "安全大会",
    "その他",
]

def make_items(prefix, names, pt=1):
    return [(f"{prefix}：{name}", pt) for name in names]

FORKLIFT_SECTIONS = [
    ("① 始業前点検・車両外観", make_items("始業前点検", [
        "タイヤの損傷・摩耗を確認していない","タイヤ空気圧・異常変形を確認していない","ホイールナットの緩みを確認していない",
        "フォーク爪の摩耗・亀裂を確認していない","フォーク爪の曲がり・左右差を確認していない","バックレストの損傷を確認していない",
        "マストの変形・損傷を確認していない","リフトチェーンの張り・損傷を確認していない","油圧シリンダーの油漏れを確認していない",
        "油圧ホースの亀裂・漏れを確認していない","エンジンオイル量を確認していない","冷却水量を確認していない",
        "燃料またはバッテリー残量を確認していない","バッテリー端子・充電状態を確認していない","床面の油漏れ・液漏れ跡を確認していない",
        "消火器・安全備品の有無を確認していない","車体周辺の障害物を確認していない","点検結果を報告・記録していない",
        "異常時に使用停止判断をしていない","点検を形式的に済ませた",
    ])),
    ("② 運転席・操作装置確認", make_items("運転席確認", [
        "3点支持で乗車していない","シート位置を調整していない","シートベルトを着用していない","ミラーを調整していない",
        "ホーンの作動確認をしていない","前照灯・作業灯の確認をしていない","回転灯・警告灯の確認をしていない",
        "バックブザーの確認をしていない","ブレーキの効きを確認していない","駐車ブレーキの効きを確認していない",
        "ハンドル操作の異常を確認していない","リフト操作レバーの作動確認をしていない","チルト操作の作動確認をしていない",
        "計器類・警告灯を確認していない","周囲確認前にエンジン始動した",
    ])),
    ("③ 発進・基本走行", make_items("発進走行", [
        "発進前の前後左右確認が不足している","発進合図・声かけをしていない","急発進をした","構内制限速度を守っていない",
        "徐行場所で徐行していない","交差部で一時停止していない","出入口で左右確認をしていない","カーブで減速していない",
        "走行中に脇見をした","片手運転・不安定な姿勢で運転した","歩行者優先ができていない","他車両との車間距離が不足している",
        "死角に対する確認が不足している","濡れ床・段差で速度調整していない","周囲作業者への声かけが不足している",
    ])),
    ("④ 後進・狭所走行", make_items("後進狭所", [
        "後進前に後方目視確認をしていない","後進時にミラーだけに頼った","後進時の徐行が不足している","死角側の確認が不足している",
        "誘導者との合図確認が不足している","狭所で車体接触リスクを確認していない","旋回時の後部振り出し確認が不足している",
        "壁・柱・設備との間隔確認が不足している","人が近い状態で後進した","警告音・声かけが不足している",
    ])),
    ("⑤ 荷役・積付け", make_items("荷役", [
        "荷の重量を確認していない","許容荷重を確認していない","荷重中心を確認していない","パレット破損を確認していない",
        "荷崩れの危険を確認していない","フォーク幅を荷に合わせていない","フォークを十分に差し込んでいない","差し込み角度が不適切",
        "地切り確認をしていない","荷を高く上げたまま走行した","走行時のフォーク高さが不適切","マスト後傾が不足している",
        "急旋回で荷を不安定にした","荷役中の周囲確認が不足している","荷の陰の歩行者確認が不足している","段積み時の水平確認が不足している",
        "荷下ろし場所の安全確認が不足している","荷を乱暴に置いた","荷の押し込み・引きずりを行った","不安定な荷を単独判断で運搬した",
        "視界不良のまま前進走行した","長尺物の振れを確認していない","傾斜地で荷役リスクを確認していない","積付け後の荷姿確認が不足している",
        "作業完了後の周囲確認が不足している",
    ])),
    ("⑥ 駐車・終了措置", make_items("終了措置", [
        "所定場所に駐車していない","フォークを接地させていない","マストを安定位置に戻していない","駐車ブレーキをかけていない",
        "エンジン停止・電源OFFをしていない","キー管理が不適切","輪止め等の措置が不足している","作業後点検をしていない",
        "異常報告をしていない","作業場所の片付けが不足している",
    ])),
]

WHEEL_LOADER_SECTIONS = [
    ("① 始業前点検", make_items("始業前点検", [
        "タイヤ損傷・摩耗を確認していない","タイヤチェーン状態を確認していない","ホイールナット緩みを確認していない",
        "ブレーキ作動を確認していない","駐車ブレーキを確認していない","ハンドル操作を確認していない",
        "アクセル・ペダルの戻りを確認していない","ライト・作業灯を確認していない","回転灯を確認していない",
        "バックブザーを確認していない","ミラー・カメラを確認していない","バケット損傷を確認していない",
        "アーム・リンク部の異常を確認していない","油圧ホース漏れを確認していない","エンジンオイルを確認していない",
        "冷却水を確認していない","燃料を確認していない","ウォッシャー液を確認していない","車体下の漏れ跡を確認していない",
        "異常時に報告していない",
    ])),
    ("② 作業前KY・現場確認", make_items("作業前KY", [
        "除雪範囲を確認していない","作業順序を確認していない","歩行者動線を確認していない","一般車両動線を確認していない",
        "出入口・交差部を確認していない","側溝位置を確認していない","マンホール位置を確認していない","縁石・段差を確認していない",
        "埋設物・障害物を確認していない","雪置き場を確認していない","排雪場所を確認していない","誘導者の有無を確認していない",
        "合図方法を確認していない","作業中止基準を確認していない","視界不良時の対応を確認していない",
    ])),
    ("③ 除雪運転", make_items("除雪運転", [
        "作業速度が速すぎる","後進時の目視確認が不足している","死角確認が不足している","バケットを高く上げたまま走行した",
        "建物付近で徐行していない","車両付近で徐行していない","歩行者付近で一時停止していない","出入口で一時停止していない",
        "雪山で視界を遮った","雪を道路へ飛散させた","側溝へ脱輪するリスク確認が不足","マンホール衝突リスク確認が不足",
        "段差乗越え時の速度調整不足","旋回時の周囲確認不足","後部振り出し確認不足","作業員を死角に入れた",
        "無理な押し込み除雪をした","凍結路で急操作をした","傾斜地で安定確認不足","停止時の安全確保不足",
        "歩行者への声かけ不足","誘導者合図を確認していない","夜間照明不足を放置した","積雪で標識・障害物確認不足",
        "作業範囲外へ不用意に進入した","緊急停止判断が遅い","疲労・眠気の申告不足","無線連絡不足","現場変化への対応不足",
        "除雪後の通行安全確認不足",
    ])),
    ("④ 排雪ダンプ連携", make_items("排雪連携", [
        "ダンプ待機位置を確認していない","積込前に合図確認をしていない","ダンプ運転手位置確認不足","荷台中心への積込が不適切",
        "過積載につながる積込をした","偏荷重を確認していない","荷台周囲の人を確認していない","バケット接触リスク確認不足",
        "積込高さの確認不足","雪の飛散防止不足","連続作業時の安全間隔不足","バック連携の確認不足","合図者不在で無理に作業した",
        "ダンプ発進前確認不足","排雪ルートの共有不足",
    ])),
    ("⑤ 終業点検・報告", make_items("終業", [
        "作業後点検をしていない","バケットを接地していない","駐車ブレーキ不足","輪止め不足","キー管理不足",
        "燃料補給確認不足","損傷報告不足","ヒヤリハット共有不足","作業記録不足","翌日の危険箇所共有不足",
        "車両清掃不足","凍結防止措置不足","安全帯・備品片付け不足","除雪結果確認不足","責任者への報告不足",
        "現場写真記録不足","警告表示撤去確認不足","通行確保確認不足","異常放置","終業時の周囲確認不足",
    ])),
]

DUMP_SECTIONS = [
    ("① 始業前点検", make_items("始業前点検", [
        "タイヤ損傷確認不足","空気圧確認不足","チェーン確認不足","ホイールナット確認不足","ブレーキ確認不足",
        "駐車ブレーキ確認不足","灯火類確認不足","回転灯確認不足","バックブザー確認不足","ミラー・カメラ確認不足",
        "荷台損傷確認不足","ダンプ装置確認不足","油圧漏れ確認不足","燃料確認不足","冷却水確認不足",
        "エンジンオイル確認不足","ウォッシャー液確認不足","車検・点検状態確認不足","車内備品確認不足","異常報告不足",
    ])),
    ("② 積込待機", make_items("積込待機", [
        "待機位置が不適切","重機作業範囲に進入した","誘導者合図確認不足","ホイールローダー死角確認不足","積込中に車両を動かした",
        "駐車ブレーキ不足","運転席離席時の安全措置不足","荷台周辺確認不足","他車との間隔不足","歩行者確認不足",
        "無線連絡不足","夜間視認性不足","待機中の脇見","積込順序の確認不足","現場ルール確認不足",
    ])),
    ("③ 積込確認", make_items("積込確認", [
        "過積載確認不足","偏荷重確認不足","荷台からの落雪確認不足","シート・飛散防止確認不足","荷姿確認不足",
        "積込後の周囲確認不足","発進合図不足","荷台接触確認不足","雪塊の落下リスク確認不足","積込完了確認不足",
        "荷台上の凍結塊確認不足","視界確保不足","最大積載量確認不足","車両安定確認不足","誘導者との最終確認不足",
    ])),
    ("④ 走行・運搬", make_items("走行運搬", [
        "速度超過","車間距離不足","凍結路で急操作","交差点徐行不足","一時停止不足","後進確認不足","歩行者確認不足",
        "一般車両への配慮不足","雪道での制動距離確認不足","カーブ減速不足","坂道でのギア選択不適切","視界不良時のライト不足",
        "落雪・飛散確認不足","ルート逸脱","無理な追越し","疲労運転","携帯操作","路肩寄りすぎ","側溝・段差確認不足",
        "誘導なしで危険箇所へ進入","バック時の合図不足","排雪場入口確認不足","歩道への雪落下確認不足","緊急時連絡不足",
        "天候変化への対応不足",
    ])),
    ("⑤ 排雪・荷下ろし", make_items("排雪", [
        "排雪場所の地盤確認不足","傾斜確認不足","上空障害物確認不足","周囲人員確認不足","荷台を上げたまま走行",
        "荷台上昇時の安定確認不足","横転リスク確認不足","雪詰まり対応不適切","荷台戻し確認不足","排雪後の後方確認不足",
        "誘導者合図確認不足","排雪場所からの退出確認不足","荷台ロック確認不足","地盤沈下リスク確認不足","無理な排雪動作",
    ])),
    ("⑥ 終業点検", make_items("終業", [
        "作業後点検不足","荷台戻し確認不足","ダンプ装置異常報告不足","駐車ブレーキ不足","輪止め不足",
        "車両清掃不足","燃料確認不足","日報記録不足","ヒヤリハット共有不足","翌日注意点共有不足",
    ])),
]

SECURITY_SECTIONS = [
    ("① 服務・基本姿勢", make_items("服務", [
        "制服・装備品が不適切","身だしなみ不良","挨拶・言葉遣い不適切","勤務場所の理解不足","任務内容の理解不足",
        "守秘義務理解不足","個人情報取扱い不適切","遅刻・早退","勤務中の私語過多","勤務中のスマホ私用",
        "立哨姿勢不良","来訪者対応不適切","苦情対応不適切","報連相不足","指示確認不足",
        "警備業務の範囲理解不足","危険時の単独判断","体調不良申告不足","装備点検不足","勤務前確認不足",
    ])),
    ("② 出入管理", make_items("出入管理", [
        "入館者確認不足","退館者確認不足","受付記録不備","身分確認不足","車両入退場確認不足",
        "搬入搬出確認不足","不審物確認不足","鍵管理不備","施錠確認不足","開錠手順不備",
        "許可証確認不足","立入禁止区域説明不足","来訪者誘導不足","無断入場見逃し","業者対応不備",
        "緊急車両対応不足","記録時刻不正確","入退場ルール説明不足","混雑時対応不足","異常時報告不足",
    ])),
    ("③ 巡回・監視", make_items("巡回", [
        "巡回ルート理解不足","巡回時刻不遵守","巡回記録不備","施錠確認不足","火気確認不足",
        "水漏れ確認不足","設備異常確認不足","照明異常確認不足","不審者確認不足","不審車両確認不足",
        "死角確認不足","外周確認不足","非常口確認不足","消火器確認不足","防犯カメラ確認不足",
        "警報盤確認不足","異臭・異音確認不足","巡回中の安全確認不足","階段・段差注意不足","報告遅れ",
    ])),
    ("④ 緊急対応", make_items("緊急対応", [
        "緊急連絡先理解不足","火災時初動不足","設備異常時対応不足","不審者対応不足","救急対応不足",
        "避難誘導理解不足","警察・消防連絡判断不足","責任者報告不足","単独で危険対応した","現場保存理解不足",
        "災害時の優先順位不明","停電時対応不足","警報発報時確認不足","夜間緊急時対応不足","クレーム時対応不足",
        "負傷者対応不足","防災設備理解不足","緊急放送理解不足","避難経路確認不足","記録作成不足",
    ])),
    ("⑤ 引継ぎ・記録", make_items("引継ぎ", [
        "申し送り不足","異常共有不足","勤務記録不足","時刻記録不正確","来訪者記録不足",
        "鍵引継ぎ不備","未処理事項共有不足","注意人物情報共有不足","設備異常共有不足","次勤務者確認不足",
        "報告書記入漏れ","口頭のみで記録なし","管理者報告不足","ヒヤリハット共有不足","改善事項未記入",
        "巡回結果未記入","写真記録不足","重要事項の優先度不明","退勤前確認不足","引継ぎ後の確認不足",
    ])),
]

GENERIC_SECTIONS = [
    ("① 理解度", make_items("理解度", [f"教育内容の理解不足 {i}" for i in range(1, 26)])),
    ("② 安全行動", make_items("安全行動", [f"安全行動の確認不足 {i}" for i in range(1, 26)])),
    ("③ 報告記録", make_items("報告記録", [f"報告・記録の不足 {i}" for i in range(1, 26)])),
    ("④ 改善姿勢", make_items("改善姿勢", [f"改善意識の不足 {i}" for i in range(1, 26)])),
]

TRAINING_ITEMS = {
    "フォークリフト安全講習": {
        "sections": FORKLIFT_SECTIONS,
        "fails": ["人・設備・車両に接触した","フォークリフトを転倒させた","荷を落下させた","シートベルト未着用で運転した","著しく危険な運転をした"],
    },
    "ホイールローダー除雪作業": {
        "sections": WHEEL_LOADER_SECTIONS,
        "fails": ["人・車両・建物・設備に接触した","作業員を死角に入れたまま作業した","車両を横転・転落させた","著しく危険な除雪作業をした"],
    },
    "除雪排雪ダンプ運転手": {
        "sections": DUMP_SECTIONS,
        "fails": ["人・車両・設備に接触した","荷台を上げたまま走行した","車両を転倒・転落させた","過積載または著しい偏荷重で走行した"],
    },
    "警備員教育": {
        "sections": SECURITY_SECTIONS,
        "fails": ["勤務場所を無断で離れた","重大な異常を報告しなかった","守秘義務に反する行為をした","著しく不適切な警備対応をした"],
    },
    "玉掛け安全教育": {"sections": GENERIC_SECTIONS, "fails": ["吊り荷落下","吊り荷下立入","人・設備接触","著しい危険行為"]},
    "クレーン安全教育": {"sections": GENERIC_SECTIONS, "fails": ["吊り荷落下","人・設備接触","斜め吊り重大危険","著しい危険操作"]},
    "KY活動": {"sections": GENERIC_SECTIONS, "fails": ["重大危険の見落とし","重大対策未実施","虚偽または形式だけのKY"]},
    "新入社員安全教育": {"sections": GENERIC_SECTIONS, "fails": ["危険区域への無断立入","指示無視","重大事故につながる行動"]},
    "安全大会": {"sections": GENERIC_SECTIONS, "fails": ["著しく不適切な受講態度","安全指示無視"]},
    "その他": {"sections": GENERIC_SECTIONS, "fails": ["重大事故につながる危険行動","指示無視","虚偽報告"]},
}

def get_script_url():
    url = st.secrets.get("GAS_WEBAPP_URL", "")
    if not url:
        st.error("Streamlit Secrets に GAS_WEBAPP_URL が設定されていません。")
        st.stop()
    return url

def gas_get(action):
    r = requests.get(get_script_url(), params={"action": action}, timeout=25)
    r.raise_for_status()
    return r.json()

def gas_post(payload):
    r = requests.post(get_script_url(), json=payload, timeout=35)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60)
def load_master_data():
    data = gas_get("master")
    emp_df = pd.DataFrame(data.get("employees", []))
    dept_df = pd.DataFrame(data.get("departments", []))
    type_df = pd.DataFrame(data.get("training_types", []))
    return emp_df, dept_df, type_df

def load_sheet_df(action):
    data = gas_get(action)
    return pd.DataFrame(data if isinstance(data, list) else data.get("rows", []))

def make_excel_bytes(df, sheet_name="出力"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return output.getvalue()

def get_rank(score, failed):
    if failed:
        return "D"
    if score >= 95:
        return "S"
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    return "D"

def needs_retraining(score, failed):
    return "必要" if failed or score < PASS_SCORE else "不要"

def risk_analysis(checked_items, fail_items):
    text = " ".join(checked_items + fail_items)
    risks = []
    if any(k in text for k in ["後進", "死角", "歩行者", "接触", "周囲", "車両"]):
        risks.append("接触災害リスク高")
    if any(k in text for k in ["転倒", "横転", "傾斜", "凍結", "速度", "急"]):
        risks.append("転倒・スリップリスク高")
    if any(k in text for k in ["荷", "吊り", "過積載", "偏荷重", "荷台"]):
        risks.append("荷役・荷崩れリスク高")
    if any(k in text for k in ["報告", "記録", "引継ぎ", "連絡"]):
        risks.append("報連相・記録不備リスク")
    return " / ".join(risks) if risks else "重大リスクは限定的"

def ai_evaluation(training_type, score, rank, checked_items, fail_items):
    focus_map = {
        "フォークリフト安全講習": "後進時の目視確認、歩行者優先、荷の高さ、停止確認",
        "ホイールローダー除雪作業": "死角確認、後進時確認、ダンプとの合図、雪山・障害物確認",
        "除雪排雪ダンプ運転手": "積込待機位置、過積載防止、荷台上昇時確認、凍結路面での速度管理",
        "警備員教育": "巡回確認、異常時報告、緊急連絡、引継ぎ記録",
    }
    focus = focus_map.get(training_type, "基本動作、安全確認、報告記録")
    if fail_items:
        summary = f"総合評価：{rank}ランク。検定中止に該当する重大な危険行動が確認されました。"
        guidance = "一発失格項目について原因を確認し、同種作業前に必ず再教育と再評価を実施してください。"
    elif score >= 95:
        summary = f"総合評価：{rank}ランク。安全意識・基本動作ともに非常に良好です。"
        guidance = "現状の安全行動を継続し、他の作業員の模範となる行動を継続してください。"
    elif score >= 85:
        summary = f"総合評価：{rank}ランク。基本的な安全行動は良好ですが、一部に改善余地があります。"
        guidance = "減点項目について口頭指導を行い、次回作業時に改善状況を確認してください。"
    elif score >= 70:
        summary = f"総合評価：{rank}ランク。合格基準には達していますが、確認不足が見られます。"
        guidance = "作業前確認、周囲確認、合図確認を重点的に指導してください。"
    else:
        summary = f"総合評価：{rank}ランク。安全意識・確認動作に改善が必要です。"
        guidance = "必ず再教育を実施し、基本ルール・作業手順・危険予知を再確認してください。"
    if checked_items:
        weak_points = "、".join([x.replace("−", "-") for x in checked_items[:8]])
        guidance += f" 特に「{weak_points}」を重点的に改善してください。"
    return summary, guidance, focus

def print_html(record):
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>安全教育記録票</title>
<style>
body {{ font-family: sans-serif; padding: 24px; line-height: 1.6; }}
h1 {{ border-bottom: 3px solid #333; padding-bottom: 8px; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
td, th {{ border: 1px solid #333; padding: 8px; vertical-align: top; }}
.result {{ font-size: 28px; font-weight: bold; }}
.sign {{ height: 70px; }}
@media print {{ button {{ display:none; }} }}
</style></head><body>
<button onclick="window.print()">印刷 / PDF保存</button>
<h1>野田組 安全教育記録票</h1>
<table>
<tr><th>社員ID</th><td>{record["社員ID"]}</td><th>氏名</th><td>{record["氏名"]}</td></tr>
<tr><th>部署</th><td>{record["部署"]}</td><th>教育種別</th><td>{record["教育種別"]}</td></tr>
<tr><th>実施日</th><td>{record["実施日"]}</td><th>講師名</th><td>{record["講師名"]}</td></tr>
</table>
<p class="result">点数：{record["点数"]} / 100点　判定：{record["判定"]}　ランク：{record["ランク"]}</p>
<table>
<tr><th>再教育要否</th><td>{record["再教育要否"]}</td></tr>
<tr><th>AI総評</th><td>{record["AI総評"]}</td></tr>
<tr><th>改善指導</th><td>{record["改善指導"]}</td></tr>
<tr><th>リスク分析</th><td>{record["リスク分析"]}</td></tr>
<tr><th>重点確認事項</th><td>{record["重点確認事項"]}</td></tr>
<tr><th>減点項目</th><td>{record["減点項目"] or "なし"}</td></tr>
<tr><th>一発失格</th><td>{record["一発失格"] or "なし"}</td></tr>
<tr><th>指導メモ</th><td>{record["指導メモ"] or ""}</td></tr>
<tr><th>写真</th><td>{record["写真有無"]}：{record["写真ファイル名"]}</td></tr>
</table>
<table>
<tr><th>受講者署名</th><td class="sign">{record["受講者署名"]}</td></tr>
<tr><th>講師署名</th><td class="sign">{record["講師署名"]}</td></tr>
</table>
</body></html>"""

st.set_page_config(page_title=APP_TITLE, page_icon="🦺", layout="wide")
st.markdown("""
<style>
.main .block-container { padding-top: 1rem; max-width: 1180px; }
.big-score { font-size: 3.2rem; font-weight: 900; line-height: 1; }
.pass { color: #16a34a; }
.fail { color: #dc2626; }
</style>
""", unsafe_allow_html=True)

st.title("🦺 野田組 安全教育管理システム V7")
st.caption("Apps Script連携版：Google Cloud / JSONキー不要")

tabs = st.tabs(["🏠 ダッシュボード","📝 採点","📊 履歴","👥 社員マスター","📅 年間教育台帳","⚠️ 再教育対象","📝 ヒヤリハット","📱 QR共有","⚙️ 接続確認"])
tab_dash, tab_score, tab_history, tab_emp, tab_annual, tab_retrain, tab_hiyari, tab_qr, tab_check = tabs

with tab_dash:
    st.subheader("ダッシュボード")
    try:
        emp_df, dept_df, type_df = load_master_data()
        hist_df = load_sheet_df("history")
        retrain_df = load_sheet_df("retrain")
        active_emp = emp_df[emp_df.get("在籍", "").astype(str).isin(["在籍", "TRUE", "True", "true", "1"])] if not emp_df.empty and "在籍" in emp_df.columns else emp_df
        this_month = datetime.now().strftime("%Y-%m")
        month_hist = hist_df[hist_df.get("実施日", "").astype(str).str.startswith(this_month)] if not hist_df.empty and "実施日" in hist_df.columns else hist_df
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("在籍社員数", len(active_emp))
        c2.metric("今月教育件数", len(month_hist))
        c3.metric("再教育対象", len(retrain_df))
        avg_score = round(pd.to_numeric(hist_df.get("点数", pd.Series(dtype=float)), errors="coerce").mean(), 1) if not hist_df.empty else 0
        c4.metric("平均点", avg_score if pd.notna(avg_score) else 0)
        if not hist_df.empty:
            if "部署" in hist_df.columns and "点数" in hist_df.columns:
                chart = hist_df.copy()
                chart["点数"] = pd.to_numeric(chart["点数"], errors="coerce")
                st.write("部署別平均点")
                st.bar_chart(chart.groupby("部署")["点数"].mean())
            st.write("最新履歴")
            st.dataframe(hist_df.tail(20), use_container_width=True)
        else:
            st.info("まだ教育履歴がありません。")
    except Exception as e:
        st.error(f"読み込みエラー：{e}")

with tab_score:
    try:
        emp_df, dept_df, type_df = load_master_data()
    except Exception as e:
        st.error(f"マスター読み込みエラー：{e}")
        st.stop()
    active_emp = emp_df[emp_df.get("在籍", "").astype(str).isin(["在籍", "TRUE", "True", "true", "1"])] if not emp_df.empty and "在籍" in emp_df.columns else emp_df

    col1, col2 = st.columns(2)
    with col1:
        dept_options = ["すべて"] + sorted(active_emp["部署"].dropna().astype(str).unique().tolist()) if not active_emp.empty and "部署" in active_emp.columns else ["すべて"] + DEFAULT_DEPTS
        dept_filter = st.selectbox("部署", dept_options)
        emp_view = active_emp if dept_filter == "すべて" or active_emp.empty else active_emp[active_emp["部署"].astype(str) == dept_filter]
        names = emp_view["氏名"].dropna().astype(str).tolist() if not emp_view.empty and "氏名" in emp_view.columns else []
        trainee_name = st.selectbox("受講者", names if names else ["社員マスターに登録してください"])
        selected = emp_view[emp_view["氏名"].astype(str) == trainee_name].head(1) if not emp_view.empty and "氏名" in emp_view.columns else pd.DataFrame()
        emp_id = str(selected["社員ID"].iloc[0]) if not selected.empty and "社員ID" in selected.columns else ""
        dept = str(selected["部署"].iloc[0]) if not selected.empty and "部署" in selected.columns else dept_filter
        st.text_input("社員ID", value=emp_id, disabled=True)
        st.text_input("部署表示", value=dept, disabled=True)
    with col2:
        training_types = type_df["教育種別"].dropna().astype(str).tolist() if not type_df.empty and "教育種別" in type_df.columns else DEFAULT_TYPES
        training_type = st.selectbox("教育種別", training_types)
        training_date = st.date_input("実施日", value=date.today())
        instructor = st.text_input("講師名")
        memo = st.text_area("指導メモ・改善指示", height=90)

    training_key = training_type if training_type in TRAINING_ITEMS else "その他"
    current = TRAINING_ITEMS[training_key]
    checked_items = []
    deduction = 0

    st.info(f"現在の採点項目：{training_type}（安全優先・100項目級）")
    st.subheader("減点項目")
    for s_i, (section, items) in enumerate(current["sections"]):
        with st.expander(f"{section}（{len(items)}項目）", expanded=False):
            for i_i, (text, pt) in enumerate(items):
                if st.checkbox(f"−{pt}点　{text}", key=f"{training_type}_{s_i}_{i_i}"):
                    checked_items.append(f"−{pt}点 {text}")
                    deduction += pt

    st.subheader("一発失格・検定中止")
    fail_items = []
    for i, text in enumerate(current["fails"]):
        if st.checkbox(text, key=f"{training_type}_fail_{i}"):
            fail_items.append(text)

    failed = bool(fail_items)
    score = 0 if failed else max(0, 100 - deduction)
    result = "不合格・検定中止" if failed else ("合格" if score >= PASS_SCORE else "不合格")
    rank = get_rank(score, failed)
    retraining = needs_retraining(score, failed)
    ai_summary, ai_guidance, ai_focus = ai_evaluation(training_key, score, rank, checked_items, fail_items)
    risk = risk_analysis(checked_items, fail_items)

    st.divider()
    cls = "pass" if result == "合格" else "fail"
    c1,c2,c3 = st.columns([1,1,2])
    with c1:
        st.markdown(f'<div class="big-score {cls}">{score}</div><div>/ 100点</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f"### {result}")
        st.write(f"ランク：{rank}")
        st.write(f"再教育：{retraining}")
    with c3:
        st.write("**AI総評・リスク分析**")
        st.info(ai_summary)
        st.warning(ai_guidance)
        st.error(risk if "高" in risk else risk)

    st.subheader("写真添付・電子サイン")
    photo = st.file_uploader("教育実施写真・現場写真（任意）", type=["jpg","jpeg","png"])
    sc1, sc2 = st.columns(2)
    with sc1:
        trainee_sign = st.text_input("受講者署名（氏名入力で代用）", value=trainee_name if "登録してください" not in trainee_name else "")
    with sc2:
        instructor_sign = st.text_input("講師署名（氏名入力で代用）", value=instructor)

    record = {
        "保存日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "社員ID": emp_id, "氏名": trainee_name, "部署": dept, "教育種別": training_type,
        "実施日": str(training_date), "講師名": instructor, "点数": score, "減点合計": deduction,
        "判定": result, "ランク": rank, "再教育要否": retraining,
        "AI総評": ai_summary, "改善指導": ai_guidance, "重点確認事項": ai_focus, "リスク分析": risk,
        "減点項目": " / ".join(checked_items), "一発失格": " / ".join(fail_items), "指導メモ": memo,
        "写真ファイル名": photo.name if photo else "", "写真有無": "あり" if photo else "なし",
        "受講者署名": trainee_sign, "講師署名": instructor_sign,
    }

    b1,b2 = st.columns(2)
    with b1:
        if st.button("💾 保存", type="primary", use_container_width=True):
            if not emp_id or "登録してください" in trainee_name:
                st.error("社員を選択してください。")
            else:
                try:
                    res = gas_post({"action": "save_training", "record": record})
                    if res.get("ok"):
                        st.cache_data.clear()
                        st.success("保存しました。教育履歴・年間台帳を更新しました。")
                    else:
                        st.error(f"保存失敗：{res.get('error')}")
                except Exception as e:
                    st.error(f"保存エラー：{e}")
    with b2:
        st.download_button("🖨️ 教育記録票HTML/PDF用", print_html(record).encode("utf-8"),
                           f"安全教育記録票_{trainee_name}_{training_date}.html", "text/html", use_container_width=True)

with tab_history:
    st.subheader("教育履歴")
    try:
        df = load_sheet_df("history")
        if df.empty:
            st.info("履歴がありません。")
        else:
            st.dataframe(df, use_container_width=True, height=420)
            st.download_button("Excelダウンロード", make_excel_bytes(df, "教育履歴"), "教育履歴.xlsx", use_container_width=True)
    except Exception as e:
        st.error(f"読み込みエラー：{e}")

with tab_emp:
    st.subheader("社員マスター")
    try:
        emp_df, dept_df, type_df = load_master_data()
        dept_options = dept_df["部署"].dropna().astype(str).tolist() if not dept_df.empty and "部署" in dept_df.columns else DEFAULT_DEPTS
        with st.expander("社員を追加", expanded=False):
            c1,c2,c3,c4,c5 = st.columns(5)
            new_id = c1.text_input("社員ID")
            new_name = c2.text_input("氏名")
            new_dept = c3.selectbox("部署", dept_options)
            new_qual = c4.text_input("資格")
            new_status = c5.selectbox("在籍", ["在籍","退職"])
            if st.button("社員追加", type="primary"):
                if not new_id or not new_name:
                    st.error("社員IDと氏名を入力してください。")
                else:
                    res = gas_post({"action":"add_employee","record":{"社員ID":new_id,"氏名":new_name,"部署":new_dept,"資格":new_qual,"在籍":new_status}})
                    if res.get("ok"):
                        st.cache_data.clear()
                        st.success("社員を追加しました。")
                    else:
                        st.error(res.get("error"))
        st.dataframe(emp_df, use_container_width=True)
        st.caption("削除・一括編集はGoogleスプレッドシートの社員マスターで直接行う運用が安全です。")
    except Exception as e:
        st.error(f"読み込みエラー：{e}")

with tab_annual:
    st.subheader("年間教育台帳")
    try:
        df = load_sheet_df("annual")
        if df.empty:
            st.info("年間教育台帳がありません。")
        else:
            st.dataframe(df, use_container_width=True, height=440)
            st.download_button("年間教育台帳Excel", make_excel_bytes(df, "年間教育台帳"), "年間教育台帳.xlsx", use_container_width=True)
    except Exception as e:
        st.error(f"読み込みエラー：{e}")

with tab_retrain:
    st.subheader("再教育対象者")
    try:
        df = load_sheet_df("retrain")
        if df.empty:
            st.info("再教育対象者はありません。")
        else:
            st.dataframe(df, use_container_width=True, height=440)
            st.download_button("再教育対象者Excel", make_excel_bytes(df, "再教育対象者"), "再教育対象者.xlsx", use_container_width=True)
    except Exception as e:
        st.error(f"読み込みエラー：{e}")

with tab_hiyari:
    st.subheader("ヒヤリハット")
    try:
        emp_df, dept_df, type_df = load_master_data()
        dept_options = dept_df["部署"].dropna().astype(str).tolist() if not dept_df.empty and "部署" in dept_df.columns else DEFAULT_DEPTS
        names = emp_df["氏名"].dropna().astype(str).tolist() if not emp_df.empty and "氏名" in emp_df.columns else []
        with st.form("hiyari_form"):
            c1,c2,c3 = st.columns(3)
            h_date = c1.date_input("発生日", value=date.today())
            h_dept = c2.selectbox("部署", dept_options)
            h_name = c3.selectbox("氏名", names if names else ["未登録"])
            category = st.selectbox("分類", ["重機接触","転倒","墜落","挟まれ","飛来落下","交通","火災","その他"])
            content = st.text_area("内容")
            cause = st.text_area("原因")
            measure = st.text_area("対策")
            level = st.selectbox("重要度", ["低","中","高","重大"])
            submitted = st.form_submit_button("ヒヤリハット登録")
            if submitted:
                res = gas_post({"action":"save_hiyari","record":{
                    "登録日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "発生日": str(h_date), "部署": h_dept, "氏名": h_name, "分類": category,
                    "内容": content, "原因": cause, "対策": measure, "重要度": level
                }})
                if res.get("ok"):
                    st.success("登録しました。")
                else:
                    st.error(res.get("error"))
        df = load_sheet_df("hiyari")
        if not df.empty:
            st.dataframe(df, use_container_width=True, height=300)
    except Exception as e:
        st.error(f"読み込みエラー：{e}")

with tab_qr:
    st.subheader("QR共有")
    st.write("このURLをWABや社内掲示で共有してください。URLは固定表示なので毎回消えません。")
    st.code(PUBLIC_URL)
    qr_url = "https://api.qrserver.com/v1/create-qr-code/?" + urllib.parse.urlencode({"size":"280x280","data":PUBLIC_URL})
    st.image(qr_url, caption="野田組 安全教育管理システム QRコード", width=280)
    st.download_button("URLテキストを保存", PUBLIC_URL.encode("utf-8"), "nodagumi_safety_url.txt", "text/plain", use_container_width=True)

with tab_check:
    st.subheader("接続確認")
    st.write("Apps Script Web App URL")
    st.code(st.secrets.get("GAS_WEBAPP_URL", "未設定"))
    if st.button("接続テスト"):
        try:
            data = gas_get("ping")
            if data.get("ok"):
                st.success("接続OK")
            else:
                st.error(data)
        except Exception as e:
            st.error(f"接続エラー：{e}")
