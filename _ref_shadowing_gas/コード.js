function doGet() {
  recordAccess();
  const userAgent = HtmlService.getUserAgent();
  const htmlOutput = HtmlService.createTemplateFromFile("index").evaluate();
  htmlOutput.addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
  return htmlOutput;
}
// --- Deploy Tracker ---
function recordAccess() {
  const url = ScriptApp.getService().getUrl();
  if (!url || url.endsWith('/dev')) return url;
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = getOrCreateDeploySheet(ss);

  // 初回判定（Script Propertiesに識別コードがあるか）
  const props = PropertiesService.getScriptProperties();
  const instanceId = props.getProperty('instanceId');

  if (!instanceId) {
    // 初回アクセス（コピー直後 or 新規作成）
    // 前のオーナーのデータが残っていれば強制削除
    if (hasExistingData(ss)) {
      clearAllData(ss);
    }
    // 初期化済みフラグを保存
    props.setProperty('instanceId', '1');
  }

  const lastUrl = sheet.getRange(3, 2).getValue();
  if (lastUrl === url) return url;
  const lastVersion = sheet.getRange(3, 3).getValue();
  const newVersion = (typeof lastVersion === 'number') ? lastVersion + 1 : 1;
  sheet.insertRowAfter(2);
  sheet.getRange(3, 1, 1, 3).setValues([[new Date(), url, newVersion]]);
  sheet.getRange(3, 1).setNumberFormat('yyyy/MM/dd HH:mm:ss');
  return url;
}

function hasExistingData(ss) {
  const sheets = ss.getSheets();
  return sheets.some(sheet => {
    const name = sheet.getName();
    if (name.includes('score') && sheet.getLastRow() > 1) return true;
    if (name === 'デプロイ管理' && sheet.getRange(3, 2).getValue()) return true;
    return false;
  });
}

function clearAllData(ss) {
  // Script Propertiesの識別コードもクリア
  PropertiesService.getScriptProperties().deleteProperty('instanceId');

  const sheets = ss.getSheets();
  sheets.forEach(sheet => {
    const name = sheet.getName();
    if (name.includes('score')) {
      // _scoreを含むシートはデータ行を削除（ヘッダー保持）
      if (sheet.getLastRow() > 1) {
        sheet.deleteRows(2, sheet.getLastRow() - 1);
      }
    } else if (name === 'デプロイ管理') {
      // デプロイ管理シートはリセット（A1=警告文, 2行目=ヘッダーは再構築）
      sheet.clear();
      setupDeployHeader(sheet);
    }
  });
}

function getOrCreateDeploySheet(ss) {
  const SHEET_NAME = 'デプロイ管理';
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) { sheet = ss.insertSheet(SHEET_NAME); setupDeployHeader(sheet); }
  else if (!sheet.getRange(2, 1).getValue()) { setupDeployHeader(sheet); }
  return sheet;
}
function setupDeployHeader(sheet) {
  // A1に警告文を挿入
  sheet.getRange('A1').setValue('⚠ 再配布時にはデプロイ管理とscoreを記録したシートは削除してください')
    .setFontColor('#cc0000').setFontWeight('bold');
  sheet.getRange(2, 1, 1, 3).setValues([['日時', 'URL', 'Ver']]).setBackground('#4a86e8').setFontColor('#ffffff').setFontWeight('bold');
  sheet.setColumnWidth(1, 150); sheet.setColumnWidth(2, 450); sheet.setColumnWidth(3, 50); sheet.setFrozenRows(2);
}


// テスト用関数: APIが正常に動作するか確認
function testAPILookup() {
  var result = fetchFromDictionaryAPI('homework');
  Logger.log('Test result: ' + JSON.stringify(result));
  return result;
}

function getTexts() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("texts");
  const range = sheet.getDataRange();
  const values = range.getValues();
  const texts = values.slice(1).map(row => {
    let stageSuffix = '(英)';
    if (row[3] == 1) {
      stageSuffix = '(和)';
    } else if (row[0] !== (row[3] == 0 || row[3] == '' ? row[0] : row[1])) {
      stageSuffix = '(対話)';
    }

    return {
      english: row[0],
      japanese: row[1],
      hiddenIndices: row[2] ? row[2].split(',').map(Number) : [],
      readJapanese: row[3] == 1,
      readFirst: row[3] == 0 || row[3] == '' ? row[0] : (row[3] == 1 ? row[1] : row[3]),
      stageSuffix: stageSuffix
    };
  });
  return texts;
}

function getSpreadsheetName() {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  return spreadsheet.getName();
}

// アカウントを取得
function getAccount() {
  return Session.getActiveUser().getEmail();
}

function findAccountRow(account) {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName('shadowing_score');

  var data = sheet.getRange('A:A').getValues();

  for (var i = 0; i < data.length; i++) {
    if (data[i][0] === account) {
      return i + 1;
    }
  }

  var lastRow = sheet.getLastRow();
  sheet.getRange(lastRow + 1, 1).setValue(account);
  return lastRow + 1;
}

function getRowData(rowNum) {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName('shadowing_score')

  var rowData = sheet.getRange(rowNum, 1, 1, sheet.getLastColumn()).getValues();
  return rowData[0];
}

function updateRowData(rowNum, newRowData) {
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = spreadsheet.getSheetByName('shadowing_score');

  sheet.getRange(rowNum, 1, 1, newRowData.length).setValues([newRowData]);
}

// 辞書データを取得する関数
function getDictionaryData(word) {
  try {
    var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = spreadsheet.getSheetByName('dictionary');

    if (!sheet) {
      Logger.log('Dictionary sheet not found');
      return null;
    }

    var data = sheet.getDataRange().getValues();
    var normalizedWord = word.toLowerCase().trim();

    // ヘッダー行をスキップして検索
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] && data[i][0].toLowerCase().trim() === normalizedWord) {
        return {
          word: data[i][0],
          pronunciation: data[i][1] || '',
          partOfSpeech: data[i][2] || '',
          meaning: data[i][3] || '',
          example: data[i][4] || '',
          source: 'local'
        };
      }
    }

    return null;
  } catch (error) {
    Logger.log('Error in getDictionaryData: ' + error);
    return null;
  }
}

// Google翻訳APIを使用して英語を日本語に翻訳
function translateToJapanese(text) {
  try {
    if (!text) return '';

    // Google Apps ScriptのLanguageAppを使用（無料）
    var translated = LanguageApp.translate(text, 'en', 'ja');
    return translated;
  } catch (error) {
    Logger.log('Translation error: ' + error);
    return text; // 翻訳失敗時は元のテキストを返す
  }
}

// 外部辞書APIを使用して単語を検索（英和辞典として機能）
function fetchFromDictionaryAPI(word) {
  try {
    Logger.log('Fetching from API for word: ' + word);

    // Free Dictionary API を使用
    var url = 'https://api.dictionaryapi.dev/api/v2/entries/en/' + encodeURIComponent(word);
    Logger.log('API URL: ' + url);

    var response = UrlFetchApp.fetch(url, {
      muteHttpExceptions: true,
      timeout: 10
    });

    var responseCode = response.getResponseCode();
    Logger.log('API Response Code: ' + responseCode);

    if (responseCode !== 200) {
      Logger.log('API returned non-200 status');
      return null;
    }

    var responseText = response.getContentText();
    Logger.log('API Response Text: ' + responseText.substring(0, 200));

    var data = JSON.parse(responseText);

    if (!data || data.length === 0) {
      Logger.log('API returned empty data');
      return null;
    }

    var entry = data[0];
    var phonetic = entry.phonetic || '';

    // phoneticsから発音記号を取得
    if (!phonetic && entry.phonetics && entry.phonetics.length > 0) {
      for (var i = 0; i < entry.phonetics.length; i++) {
        if (entry.phonetics[i].text) {
          phonetic = entry.phonetics[i].text;
          break;
        }
      }
    }

    var meaningsEn = [];
    var meaningsJa = [];
    var examples = [];

    if (entry.meanings && entry.meanings.length > 0) {
      for (var i = 0; i < Math.min(2, entry.meanings.length); i++) {
        var meaning = entry.meanings[i];
        var partOfSpeech = meaning.partOfSpeech || '';

        if (meaning.definitions && meaning.definitions.length > 0) {
          for (var j = 0; j < Math.min(2, meaning.definitions.length); j++) {
            var def = meaning.definitions[j];
            var englishDef = def.definition;

            // 英語の定義を日本語に翻訳
            var japaneseDef = translateToJapanese(englishDef);

            meaningsEn.push((partOfSpeech ? '[' + partOfSpeech + '] ' : '') + englishDef);
            meaningsJa.push((partOfSpeech ? '[' + partOfSpeech + '] ' : '') + japaneseDef);

            if (def.example && examples.length < 2) {
              examples.push(def.example);
            }
          }
        }
      }
    }

    var partOfSpeech = '';
    if (entry.meanings && entry.meanings.length > 0 && entry.meanings[0].partOfSpeech) {
      partOfSpeech = entry.meanings[0].partOfSpeech;
    }

    // 日本語訳をメインに、英語は括弧内に表示
    var combinedMeaning = '';
    for (var i = 0; i < meaningsJa.length; i++) {
      if (i > 0) combinedMeaning += '\n';
      combinedMeaning += meaningsJa[i];
    }

    return {
      word: entry.word || word,
      pronunciation: phonetic,
      partOfSpeech: partOfSpeech,
      meaning: combinedMeaning,
      example: examples.join('\n'),
      source: 'api'
    };

  } catch (error) {
    Logger.log('Error in fetchFromDictionaryAPI: ' + error);
    return null;
  }
}

// 辞書データを取得（ローカル→API の順で試行）
function lookupWord(word) {
  Logger.log('Looking up word: ' + word);

  // まずローカル辞書を検索
  var localResult = getDictionaryData(word);
  if (localResult) {
    Logger.log('Found in local dictionary');
    return localResult;
  }

  Logger.log('Not found in local dictionary, trying API...');

  // ローカルになければAPIを使用
  var apiResult = fetchFromDictionaryAPI(word);
  if (apiResult) {
    Logger.log('Found in API');
    return apiResult;
  }

  Logger.log('Not found in API either');

  // 見つからない場合
  return {
    word: word,
    pronunciation: '',
    partOfSpeech: '',
    meaning: '辞書に見つかりませんでした',
    example: '',
    source: 'none'
  };
}
