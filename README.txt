野田組 安全教育管理システム V7 Apps Script版

重要:
Google Cloud、サービスアカウント、JSONキーは不要です。

入っているもの:
- app.py
- code.gs
- requirements.txt
- README.txt

機能:
- 社員マスター連動
- 部署マスター連動
- 教育種別マスター連動
- フォークリフト安全講習 100項目級
- ホイールローダー除雪作業 100項目級
- 除雪排雪ダンプ運転手 100項目級
- 警備員教育 100項目級
- AI総評
- リスク分析
- 再教育対象者自動登録
- 年間教育台帳自動更新
- ヒヤリハット登録
- 教育記録票HTML/PDF用
- 共通QR共有

Apps Script設定:
1. Googleスプレッドシートを開く
2. 拡張機能 → Apps Script
3. code.gs の中身を全部消す
4. このZIPの code.gs を貼り付け
5. 保存
6. デプロイ → 新しいデプロイ
7. 種類: ウェブアプリ
8. 実行ユーザー: 自分
9. アクセスできるユーザー: 全員
10. デプロイ
11. 表示されたウェブアプリURLをコピー

Streamlit Secrets:
GAS_WEBAPP_URL="ここにコピーしたURL"

GitHub:
app.py と requirements.txt を差し替えてCommit。
