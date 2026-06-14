
const SS = SpreadsheetApp.getActiveSpreadsheet();

const SHEETS = {
  EMP: "社員マスター",
  DEPT: "部署マスター",
  TYPE: "教育種別マスター",
  HISTORY: "教育履歴",
  ANNUAL: "年間教育台帳",
  RETRAIN: "再教育対象者",
  HIYARI: "ヒヤリハット",
  ITEMS: "教育項目マスター"
};

const HEADERS = {
  EMP: ["社員ID", "氏名", "部署", "資格", "在籍"],
  DEPT: ["部署"],
  TYPE: ["教育種別"],
  HISTORY: [
    "保存日時", "社員ID", "氏名", "部署", "教育種別", "実施日", "講師名",
    "点数", "減点合計", "判定", "ランク", "再教育要否",
    "AI総評", "改善指導", "重点確認事項", "リスク分析",
    "減点項目", "一発失格", "指導メモ",
    "写真ファイル名", "写真有無", "受講者署名", "講師署名"
  ],
  ANNUAL: [
    "年度", "社員ID", "氏名", "部署", "教育種別", "最終受講日",
    "最新点数", "最新判定", "最新ランク", "再教育要否", "更新日時"
  ],
  RETRAIN: [
    "登録日時", "社員ID", "氏名", "部署", "教育種別", "点数", "判定",
    "ランク", "理由", "対応状況", "対応メモ"
  ],
  HIYARI: ["登録日時", "発生日", "部署", "氏名", "分類", "内容", "原因", "対策", "重要度"],
  ITEMS: ["教育種別", "カテゴリ", "項目", "減点", "一発失格"]
};

const DEFAULT_DEPTS = [["容器請負"], ["アーム請負"], ["土木部"], ["警備"], ["派遣"]];
const DEFAULT_TYPES = [
  ["フォークリフト安全講習"],
  ["ホイールローダー除雪作業"],
  ["除雪排雪ダンプ運転手"],
  ["警備員教育"],
  ["玉掛け安全教育"],
  ["クレーン安全教育"],
  ["KY活動"],
  ["新入社員安全教育"],
  ["安全大会"],
  ["その他"]
];

function doGet(e) {
  setupSheets();
  const action = e.parameter.action || "ping";

  if (action === "ping") {
    return json({ ok: true, message: "Apps Script connected" });
  }

  if (action === "master") {
    return json({
      employees: sheetToObjects(SHEETS.EMP, HEADERS.EMP),
      departments: sheetToObjects(SHEETS.DEPT, HEADERS.DEPT),
      training_types: sheetToObjects(SHEETS.TYPE, HEADERS.TYPE)
    });
  }

  if (action === "history") return json(sheetToObjects(SHEETS.HISTORY, HEADERS.HISTORY));
  if (action === "annual") return json(sheetToObjects(SHEETS.ANNUAL, HEADERS.ANNUAL));
  if (action === "retrain") return json(sheetToObjects(SHEETS.RETRAIN, HEADERS.RETRAIN));
  if (action === "hiyari") return json(sheetToObjects(SHEETS.HIYARI, HEADERS.HIYARI));

  return json({ ok: false, error: "unknown action: " + action });
}

function doPost(e) {
  setupSheets();
  try {
    const body = JSON.parse(e.postData.contents || "{}");
    const action = body.action;
    const record = body.record || {};

    if (action === "add_employee") {
      appendRecord(SHEETS.EMP, HEADERS.EMP, record);
      return json({ ok: true });
    }

    if (action === "save_hiyari") {
      appendRecord(SHEETS.HIYARI, HEADERS.HIYARI, record);
      return json({ ok: true });
    }

    if (action === "save_training") {
      appendRecord(SHEETS.HISTORY, HEADERS.HISTORY, record);
      updateAnnual(record);

      if (record["再教育要否"] === "必要") {
        appendRecord(SHEETS.RETRAIN, HEADERS.RETRAIN, {
          "登録日時": record["保存日時"],
          "社員ID": record["社員ID"],
          "氏名": record["氏名"],
          "部署": record["部署"],
          "教育種別": record["教育種別"],
          "点数": record["点数"],
          "判定": record["判定"],
          "ランク": record["ランク"],
          "理由": record["改善指導"],
          "対応状況": "未対応",
          "対応メモ": ""
        });
      }
      return json({ ok: true });
    }

    return json({ ok: false, error: "unknown post action: " + action });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

function setupSheets() {
  ensureSheet(SHEETS.EMP, HEADERS.EMP);
  ensureSheet(SHEETS.DEPT, HEADERS.DEPT, DEFAULT_DEPTS);
  ensureSheet(SHEETS.TYPE, HEADERS.TYPE, DEFAULT_TYPES);
  ensureSheet(SHEETS.HISTORY, HEADERS.HISTORY);
  ensureSheet(SHEETS.ANNUAL, HEADERS.ANNUAL);
  ensureSheet(SHEETS.RETRAIN, HEADERS.RETRAIN);
  ensureSheet(SHEETS.HIYARI, HEADERS.HIYARI);
  ensureSheet(SHEETS.ITEMS, HEADERS.ITEMS);
}

function ensureSheet(name, headers, defaults) {
  let sh = SS.getSheetByName(name);
  if (!sh) sh = SS.insertSheet(name);

  const firstRow = sh.getRange(1, 1, 1, headers.length).getValues()[0];
  const hasHeader = firstRow.some(v => String(v).trim() !== "");

  if (!hasHeader) {
    sh.getRange(1, 1, 1, headers.length).setValues([headers]);
    sh.setFrozenRows(1);
    if (defaults && defaults.length > 0) {
      const values = defaults.map(r => headers.map((_, i) => r[i] || ""));
      sh.getRange(2, 1, values.length, headers.length).setValues(values);
    }
  } else {
    sh.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
}

function sheetToObjects(name, headers) {
  const sh = SS.getSheetByName(name);
  if (!sh) return [];
  const lastRow = sh.getLastRow();
  if (lastRow < 2) return [];
  const values = sh.getRange(2, 1, lastRow - 1, headers.length).getValues();

  return values
    .filter(row => row.some(v => String(v).trim() !== ""))
    .map(row => {
      const obj = {};
      headers.forEach((h, i) => obj[h] = row[i]);
      return obj;
    });
}

function appendRecord(sheetName, headers, record) {
  const sh = SS.getSheetByName(sheetName);
  const row = headers.map(h => record[h] !== undefined ? record[h] : "");
  sh.appendRow(row);
}

function updateAnnual(record) {
  const sh = SS.getSheetByName(SHEETS.ANNUAL);
  const headers = HEADERS.ANNUAL;
  const year = String(record["実施日"]).slice(0, 4);
  const empId = String(record["社員ID"]);
  const type = String(record["教育種別"]);

  const values = [
    year,
    record["社員ID"],
    record["氏名"],
    record["部署"],
    record["教育種別"],
    record["実施日"],
    record["点数"],
    record["判定"],
    record["ランク"],
    record["再教育要否"],
    Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyy-MM-dd HH:mm:ss")
  ];

  const lastRow = sh.getLastRow();
  if (lastRow >= 2) {
    const data = sh.getRange(2, 1, lastRow - 1, headers.length).getValues();
    for (let i = 0; i < data.length; i++) {
      const r = data[i];
      if (String(r[0]) === year && String(r[1]) === empId && String(r[4]) === type) {
        sh.getRange(i + 2, 1, 1, headers.length).setValues([values]);
        return;
      }
    }
  }
  sh.appendRow(values);
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
