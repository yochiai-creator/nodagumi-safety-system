
import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import urllib.parse

import gspread
from google.oauth2.service_account import Credentials

APP_TITLE = "野田組 安全教育管理システム"
PASS_SCORE = 70
SHEET_NAME = "安全教育履歴"

HEADERS = [
    "保存日時", "会社名", "教育種別", "実施日", "受講者名", "講師名",
    "点数", "減点合計", "判定", "減点項目", "一発失格", "指導メモ"
]

TRAINING_ITEMS = {
    "フォークリフト安全講習": {
        "sections": [
            ("始業前点検", [
                ("タイヤの空気圧・損傷の確認を怠った", 5),
                ("ブレーキ・ハンドルの効きを確認しなかった", 5),
                ("警報装置・前照灯・バックブザーを確認しなかった", 5),
                ("フォーク・チェーン・油圧の異常を見落とした", 5),
            ]),
            ("乗車・発進前", [
                ("シートベルトを着用しなかった", 10),
                ("乗車前後の周囲確認を怠った", 5),
                ("発進の合図をしなかった", 5),
                ("発進時の後方確認を怠った", 10),
            ]),
            ("走行操作", [
                ("制限速度を超過した", 10),
                ("交差点・出入口で徐行・一時停止しなかった", 10),
                ("後進時に目視で後方確認しなかった", 15),
                ("荷を高く上げたまま走行した", 10),
                ("カーブで減速しなかった", 5),
                ("歩行者を優先しなかった", 10),
            ]),
            ("荷役作業", [
                ("フォークを荷の下まで確実に差し込まなかった", 5),
                ("荷の安定・荷崩れの危険を確認しなかった", 5),
                ("マストを後傾させずに走行した", 5),
                ("制限荷重・能力を確認しなかった", 10),
                ("段積み・荷下ろしが不安定だった", 5),
            ]),
            ("駐車・終了措置", [
                ("フォークを接地させなかった", 5),
                ("パーキングブレーキをかけなかった", 5),
                ("エンジン停止・キーを抜かなかった", 5),
                ("輪止め等の措置をしなかった", 5),
            ]),
        ],
        "fails": [
            "人・物・設備に接触した",
            "フォークリフトを転倒させた",
            "荷を落下させた",
            "著しく危険な運転をした",
        ],
    },

    "玉掛け安全教育": {
        "sections": [
            ("作業前確認", [
                ("吊り荷の重量を確認しなかった", 10),
                ("使用するワイヤー・スリングの点検を怠った", 10),
                ("玉掛け用具の使用荷重を確認しなかった", 10),
                ("作業範囲内の立入禁止措置をしなかった", 10),
            ]),
            ("玉掛け方法", [
                ("吊り角度を確認しなかった", 10),
                ("片吊り・偏荷重の危険を確認しなかった", 10),
                ("フックの外れ止めを確認しなかった", 5),
                ("角当て等の保護措置をしなかった", 5),
            ]),
            ("合図・連携", [
                ("合図者を明確にしなかった", 10),
                ("合図が不明確だった", 5),
                ("吊り荷の下に入った、または入らせた", 15),
                ("周囲作業者への声かけが不足した", 5),
            ]),
            ("荷の移動・着地", [
                ("地切り確認をしなかった", 10),
                ("吊り荷の安定を確認せず移動した", 10),
                ("着地場所の安全確認を怠った", 5),
                ("玉掛け用具の取り外し時に荷の安定確認をしなかった", 5),
            ]),
        ],
        "fails": [
            "吊り荷を落下させた",
            "吊り荷の下に人が入った",
            "人・設備に接触した",
            "著しく危険な玉掛けを行った",
        ],
    },

    "クレーン安全教育": {
        "sections": [
            ("作業前点検", [
                ("クレーン本体・フック・ワイヤーの点検を怠った", 10),
                ("定格荷重を確認しなかった", 10),
                ("作業範囲・旋回範囲を確認しなかった", 10),
                ("警報装置・安全装置を確認しなかった", 5),
            ]),
            ("運転操作", [
                ("急操作・急停止を行った", 10),
                ("荷振れを抑えられなかった", 10),
                ("吊り荷を人の上に通した", 15),
                ("合図確認が不足した", 10),
            ]),
            ("荷の取扱い", [
                ("地切り確認をしなかった", 10),
                ("斜め吊りを行った", 15),
                ("荷の安定を確認せず移動した", 10),
                ("着地時の安全確認を怠った", 5),
            ]),
            ("終了措置", [
                ("フックを所定位置に戻さなかった", 5),
                ("電源・操作スイッチの停止確認を怠った", 5),
                ("作業後点検・異常報告を怠った", 5),
            ]),
        ],
        "fails": [
            "吊り荷を落下させた",
            "人・設備に接触した",
            "吊り荷の下を人が通過した",
            "著しく危険なクレーン操作を行った",
        ],
    },

    "KY活動": {
        "sections": [
            ("危険の洗い出し", [
                ("作業内容の確認が不十分だった", 10),
                ("危険ポイントの洗い出しが不足した", 10),
                ("過去災害・ヒヤリハットを反映しなかった", 5),
                ("作業場所の変化点を確認しなかった", 10),
            ]),
            ("対策の具体性", [
                ("対策が抽象的で実行しにくかった", 10),
                ("誰が何をするか明確でなかった", 10),
                ("保護具・工具・設備の確認が不足した", 5),
                ("第三者災害への対策が不足した", 10),
            ]),
            ("共有・実行", [
                ("作業員全員に周知できていなかった", 10),
                ("指差呼称・声かけが不足した", 5),
                ("作業中の見直しをしなかった", 5),
                ("不安全行動への注意が不足した", 10),
            ]),
        ],
        "fails": [
            "重大な危険を見落としたまま作業開始した",
            "立入禁止・墜落・重機接触などの重大対策が未実施だった",
            "虚偽または形式だけのKYを行った",
        ],
    },

    "新入社員安全教育": {
        "sections": [
            ("基本ルール", [
                ("会社の安全ルールを理解していない", 10),
                ("報連相の重要性を理解していない", 5),
                ("立入禁止区域を理解していない", 10),
                ("危険を感じた時の停止・確認ができていない", 10),
            ]),
            ("保護具・服装", [
                ("ヘルメット・安全靴等の着用が不適切", 10),
                ("服装・袖口・手袋等の巻き込まれ対策が不十分", 10),
                ("保護具の点検・交換基準を理解していない", 5),
            ]),
            ("現場行動", [
                ("重機・車両への接近ルールを理解していない", 10),
                ("歩行通路・安全通路を守れない", 10),
                ("勝手な判断で作業しようとした", 15),
                ("5S・整理整頓の重要性を理解していない", 5),
            ]),
            ("緊急時対応", [
                ("ケガ・事故発生時の報告先を理解していない", 10),
                ("火災・災害時の避難行動を理解していない", 5),
                ("体調不良時の申告ルールを理解していない", 5),
            ]),
        ],
        "fails": [
            "危険区域へ無断で立ち入った",
            "指示を無視して危険行動をした",
            "重大事故につながる行動をした",
        ],
    },

    "警備員教育": {
        "sections": [
            ("基本姿勢・服務", [
                ("制服・身だしなみが不適切だった", 5),
                ("挨拶・言葉遣いが不適切だった", 5),
                ("勤務場所・任務内容を理解していない", 10),
                ("守秘義務・個人情報の取扱い理解が不足した", 10),
            ]),
            ("巡回・監視", [
                ("巡回ルート・巡回時刻を理解していない", 10),
                ("異常確認時の報告が不十分だった", 10),
                ("施錠・火気・設備異常の確認が不足した", 10),
                ("記録記入が不正確だった", 5),
            ]),
            ("緊急時対応", [
                ("緊急連絡先を理解していない", 10),
                ("不審者対応の初動が不適切だった", 10),
                ("火災・設備異常時の対応を理解していない", 10),
                ("独断で危険対応をしようとした", 15),
            ]),
            ("引継ぎ", [
                ("申し送り事項が不十分だった", 5),
                ("勤務記録・報告書の記載が不足した", 5),
                ("次勤務者への異常共有が不足した", 10),
            ]),
        ],
        "fails": [
            "勤務場所を無断で離れた",
            "重大な異常を報告しなかった",
            "守秘義務に反する行為をした",
            "著しく不適切な警備対応をした",
        ],
    },

    "その他": {
        "sections": [
            ("理解度", [
                ("教育内容の理解が不足している", 10),
                ("作業手順の確認が不足している", 10),
                ("危険箇所の確認が不足している", 10),
            ]),
            ("安全行動", [
                ("保護具の着用・使用が不適切", 10),
                ("周囲確認が不足している", 10),
                ("声かけ・合図が不足している", 5),
                ("整理整頓が不足している", 5),
            ]),
            ("報告・記録", [
                ("異常時の報告方法を理解していない", 10),
                ("教育記録・確認事項が不十分", 5),
                ("改善指示への理解が不足している", 5),
            ]),
        ],
        "fails": [
            "重大事故につながる危険行動をした",
            "指示を無視した",
            "虚偽の報告をした",
        ],
    },
}


@st.cache_resource(show_spinner=False)
def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(st.secrets["spreadsheet_id"])

    try:
        ws = spreadsheet.worksheet(SHEET_NAME)
    except Exception:
        ws = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=len(HEADERS))
        ws.append_row(HEADERS)

    values = ws.get_all_values()
    if not values:
        ws.append_row(HEADERS)
    elif values[0] != HEADERS:
        ws.insert_row(HEADERS, 1)

    return ws


def load_history():
    ws = get_sheet()
    records = ws.get_all_records()
    return pd.DataFrame(records, columns=HEADERS)


def save_record(record):
    ws = get_sheet()
    ws.append_row([record.get(h, "") for h in HEADERS], value_input_option="USER_ENTERED")


def make_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="安全教育履歴")
        ws = writer.book["安全教育履歴"]
        for col, width in {
            "A": 20, "B": 18, "C": 22, "D": 12, "E": 18, "F": 18,
            "G": 8, "H": 10, "I": 18, "J": 70, "K": 50, "L": 60
        }.items():
            ws.column_dimensions[col].width = width
    return output.getvalue()


def print_html(record):
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>安全教育採点表</title>
<style>
body {{ font-family: sans-serif; padding: 24px; line-height: 1.6; }}
h1 {{ border-bottom: 3px solid #333; padding-bottom: 8px; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
td, th {{ border: 1px solid #333; padding: 8px; vertical-align: top; }}
.result {{ font-size: 28px; font-weight: bold; }}
@media print {{ button {{ display:none; }} }}
</style>
</head>
<body>
<button onclick="window.print()">印刷 / PDF保存</button>
<h1>安全教育 採点表</h1>
<table>
<tr><th>会社名</th><td>{record["会社名"]}</td><th>教育種別</th><td>{record["教育種別"]}</td></tr>
<tr><th>実施日</th><td>{record["実施日"]}</td><th>受講者名</th><td>{record["受講者名"]}</td></tr>
<tr><th>講師名</th><td>{record["講師名"]}</td><th>保存日時</th><td>{record["保存日時"]}</td></tr>
</table>
<p class="result">点数：{record["点数"]} / 100点　判定：{record["判定"]}</p>
<table>
<tr><th>減点合計</th><td>-{record["減点合計"]}点</td></tr>
<tr><th>減点項目</th><td>{record["減点項目"] or "なし"}</td></tr>
<tr><th>一発失格</th><td>{record["一発失格"] or "なし"}</td></tr>
<tr><th>指導メモ</th><td>{record["指導メモ"] or ""}</td></tr>
</table>
</body>
</html>"""


st.set_page_config(page_title=APP_TITLE, page_icon="🦺", layout="wide")

st.markdown("""
<style>
.main .block-container { padding-top: 1rem; max-width: 1100px; }
.big-score { font-size: 3.2rem; font-weight: 900; line-height: 1; }
.pass { color: #16a34a; }
.fail { color: #dc2626; }
</style>
""", unsafe_allow_html=True)

st.title("🦺 野田組 安全教育管理システム")
st.caption("教育種別ごとに採点項目が自動切替・Googleスプレッドシート自動保存")

tab_score, tab_history, tab_qr, tab_check = st.tabs(["📝 採点", "📊 履歴", "📱 QR共有", "⚙️ 接続確認"])

with tab_score:
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("会社名", value="有限会社野田組")
        training_type = st.selectbox("教育種別", list(TRAINING_ITEMS.keys()))
        trainee = st.text_input("受講者名")
    with col2:
        training_date = st.date_input("実施日", value=date.today())
        instructor = st.text_input("講師名")
        memo = st.text_area("指導メモ・改善指示", height=100)

    current = TRAINING_ITEMS[training_type]
    sections = current["sections"]
    fails = current["fails"]

    st.info(f"現在の採点項目：{training_type}")

    st.divider()
    st.subheader("減点項目")
    checked_items = []
    deduction = 0

    for s_i, (section, items) in enumerate(sections):
        with st.expander(section, expanded=True):
            for i_i, (text, pt) in enumerate(items):
                key = f"{training_type}_item_{s_i}_{i_i}"
                if st.checkbox(f"−{pt}点　{text}", key=key):
                    checked_items.append(f"−{pt}点 {text}")
                    deduction += pt

    st.subheader("一発失格・検定中止")
    fail_items = []
    for i, text in enumerate(fails):
        key = f"{training_type}_fail_{i}"
        if st.checkbox(text, key=key):
            fail_items.append(text)

    failed = bool(fail_items)
    score = 0 if failed else max(0, 100 - deduction)
    result = "不合格・検定中止" if failed else ("合格" if score >= PASS_SCORE else "不合格")

    st.divider()
    cls = "pass" if result == "合格" else "fail"
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.markdown(f'<div class="big-score {cls}">{score}</div><div>/ 100点</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f"### {result}")
        st.write(f"減点合計：-{deduction}点")
    with c3:
        st.write("**減点内容**")
        st.write(" / ".join(checked_items) if checked_items else "なし")
        if fail_items:
            st.error("一発失格：" + " / ".join(fail_items))

    record = {
        "保存日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "会社名": company,
        "教育種別": training_type,
        "実施日": str(training_date),
        "受講者名": trainee,
        "講師名": instructor,
        "点数": score,
        "減点合計": deduction,
        "判定": result,
        "減点項目": " / ".join(checked_items),
        "一発失格": " / ".join(fail_items),
        "指導メモ": memo,
    }

    b1, b2 = st.columns(2)
    with b1:
        if st.button("💾 Googleスプレッドシートに保存", type="primary", use_container_width=True):
            if not trainee:
                st.error("受講者名を入力してください。")
            else:
                try:
                    save_record(record)
                    st.success("保存しました。")
                except Exception as e:
                    st.error(f"保存できません：{e}")
    with b2:
        st.download_button(
            "🖨️ 印刷用HTMLを保存",
            data=print_html(record).encode("utf-8"),
            file_name=f"安全教育採点表_{trainee or '未入力'}_{training_date}.html",
            mime="text/html",
            use_container_width=True,
        )

with tab_history:
    st.subheader("安全教育履歴")
    try:
        df = load_history()
        if df.empty:
            st.info("履歴がありません。")
        else:
            colh1, colh2, colh3 = st.columns(3)
            with colh1:
                name_filter = st.text_input("受講者名で検索")
            with colh2:
                result_filter = st.selectbox("判定", ["すべて", "合格", "不合格", "不合格・検定中止"])
            with colh3:
                type_filter = st.selectbox("教育種別", ["すべて"] + list(TRAINING_ITEMS.keys()))

            view = df.copy()
            if name_filter:
                view = view[view["受講者名"].fillna("").astype(str).str.contains(name_filter, case=False, na=False)]
            if result_filter != "すべて":
                view = view[view["判定"] == result_filter]
            if type_filter != "すべて":
                view = view[view["教育種別"] == type_filter]

            st.dataframe(view, use_container_width=True, height=420)
            st.download_button(
                "📥 Excelダウンロード",
                data=make_excel_bytes(view),
                file_name="安全教育履歴.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"履歴を読み込めません：{e}")

with tab_qr:
    st.subheader("QR共有")
    public_url = st.text_input("公開URLを貼り付け", placeholder="https://xxxxx.streamlit.app")
    if public_url:
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?" + urllib.parse.urlencode({"size": "240x240", "data": public_url})
        st.image(qr_url, caption="配布用QRコード", width=240)

with tab_check:
    st.subheader("Googleスプレッドシート接続確認")
    try:
        ws = get_sheet()
        st.success("接続OK")
        st.write(f"接続先シート：{SHEET_NAME}")
    except Exception as e:
        st.error("接続NG")
        st.code(str(e))
