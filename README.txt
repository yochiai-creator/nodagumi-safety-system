Nodagumi Safety Google Sheets Custom Version

教育種別ごとに減点項目が切り替わる版です。

ローカル起動:
python -m pip install -r requirements.txt
python -m streamlit run app.py

本格運用:
Googleスプレッドシート連携してStreamlit Cloudで公開します。


追加更新:
- 除雪ホイールローダーを追加
- 除雪ダンプを追加
- 各100項目版
- QR共有タブを固定URL表示に修正


修正版内容:
- QR共有タブの PUBLIC_URL 未定義エラーを修正
- QR共有URLを固定表示
- Streamlit Secrets の PUBLIC_APP_URL でQR共有URLを上書き可能
- 除雪ホイールローダー100項目を1点/2点/3点/5点の重み付き減点に修正
- 除雪ダンプ100項目を1点/2点/3点/5点の重み付き減点に修正

Streamlit SecretsでURLを上書きする場合:
PUBLIC_APP_URL = "https://nodagumi-safety-v7.streamlit.app"
