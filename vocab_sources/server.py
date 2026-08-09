"""WordTacos 進捗ビューア + AI修正提案 + 直接保存サーバー.

usage: python3 server.py 8795

エンドポイント:
- GET /...                 静的ファイル(progress_viewer.html, json, m4a, mp3)
- POST /api/fix            Codex 経由で訂正案を生成 (返却JSON: {field, old_value, new_value, reason})
- POST /api/save           クイズデータを直接書き換え (body修正時は ruby/kana 自動再生成)

リクエスト/レスポンス:
- /api/fix:
    request: { id: "s5_xxxx", issue_type: "ruby|body|choices|explanation|other", user_note: "?" }
    response: { ok: bool, suggestion: { field: "...", old_value: "...", new_value: "...", reason: "..." }, raw: "Codex出力" }
- /api/save:
    request: { id: "s5_xxxx", updates: { body?: "...", body_ruby?: "...", choices?: [...], explanation?: "...", meaning_jp?: "..." } }
    response: { ok: bool, updated_fields: [...], regenerated_ruby: bool }
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODEX_DELEGATE = Path.home() / "Workspace" / "scripts" / "codex-delegate.sh"

STAGE_FILES = {
    "s5": ROOT / "stage5_quizzes_clean.json",
    "s6": ROOT / "stage6_quizzes_clean.json",
}

ISSUE_PROMPTS = {
    "ruby": "body_ruby のふりがな(青空文庫形式 漢字《よみ》)が間違っているか不自然です。正しいルビを推定して body_ruby を直してください。body本文と choices/explanation は変えないでください。",
    "body": "body の日本語文がおかしいか、<word>の品詞・文脈に合わない可能性があります。<word>タグはそのまま保持して body を40〜60字の自然な日本語に書き換えてください。",
    "choices": "choices(4択)に問題がある(重複、明らかな正解だらけ、紛らわしくない、長さ不均等など)。choices配列を見直して書き換えてください。correct_index も適切に。",
    "explanation": "explanation(語源・覚え方)が間違っているか不自然。正しい/わかりやすい一文(15〜30字)に書き換えてください。",
    "kana": "body_kana(読み上げ用ひらがな化)が不自然。VOICEPEAKで読み上げて違和感のないひらがな表記に直してください。<word>タグは保持。",
    "other": "下記 user_note の指示に従って必要なフィールドを修正してください。",
}


def find_quiz(qid: str) -> tuple[Path, dict, int] | None:
    prefix = qid.split("_")[0]
    fp = STAGE_FILES.get(prefix)
    if not fp:
        return None
    data = json.loads(fp.read_text(encoding="utf-8"))
    for i, q in enumerate(data["quizzes"]):
        if q.get("id") == qid:
            return fp, data, i
    return None


def build_codex_prompt(quiz: dict, issue_type: str, user_note: str) -> str:
    issue_desc = ISSUE_PROMPTS.get(issue_type, ISSUE_PROMPTS["other"])
    user_part = f"\n\n## ユーザーの追加指示\n{user_note}" if user_note else ""
    quiz_json = json.dumps(quiz, ensure_ascii=False, indent=2)
    return f"""あなたは WordTacos プロジェクト(日本語混じり文の英単語クイズ)の修正アシスタントです。

## 対象クイズ
```json
{quiz_json}
```

## 問題の種類
{issue_type}: {issue_desc}{user_part}

## あなたの仕事
下記の JSON だけを 1 つ出力してください。説明文や前置き、コードフェンスは付けないでください。
1 行目から最終行まで JSON のみを出力。

```
{{
  "field": "body" | "body_ruby" | "choices" | "explanation" | "meaning_jp",
  "old_value": "現状の値",
  "new_value": "提案する新しい値",
  "reason": "短い理由(30字以内)"
}}
```

複数フィールドを同時に直したい場合は、最も重要な 1 つを選んでください。
field が body の場合、文字数は 40〜60字、`<{quiz['word']}>` タグを必ず保持。
field が body_ruby の場合、青空文庫ルビ形式(漢字《よみ》)を保ち、`<{quiz['word']}>` タグもそのまま。
field が choices の場合 new_value は4要素の配列、すべて文字列。
"""


def call_codex(prompt: str, timeout: int = 90) -> tuple[bool, str]:
    """codex-delegate.sh を呼んで出力を返す."""
    if not CODEX_DELEGATE.exists():
        return False, f"codex-delegate.sh not found at {CODEX_DELEGATE}"
    try:
        proc = subprocess.run(
            ["bash", str(CODEX_DELEGATE), "-", str(ROOT)],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = proc.stdout + ("\n" + proc.stderr if proc.stderr else "")
        if proc.returncode != 0:
            return False, out
        return True, out
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"


def extract_json(text: str) -> dict | None:
    """Codex 出力から 'field' キーを持つJSONを探す。複数あれば後出を優先."""
    candidates = []
    depth = 0
    start = -1
    in_str = False
    esc = False
    for i, c in enumerate(text):
        if esc:
            esc = False
            continue
        if c == "\\":
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                cand = text[start : i + 1]
                try:
                    obj = json.loads(cand)
                    candidates.append(obj)
                except json.JSONDecodeError:
                    pass
                start = -1
    if not candidates:
        return None
    # 「field」キーを持つものを優先(Codex最終出力)。後ろから探す
    for obj in reversed(candidates):
        if isinstance(obj, dict) and "field" in obj and "new_value" in obj:
            return obj
    return candidates[-1]


def regenerate_ruby(qid: str) -> bool:
    """特定問題のみ ruby を再生成 (該当ファイル全体に add_furigana.py を再実行)."""
    prefix = qid.split("_")[0]
    fp = STAGE_FILES.get(prefix)
    if not fp:
        return False
    try:
        proc = subprocess.run(
            ["python3", str(ROOT / "add_furigana.py"), str(fp)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(ROOT),
        )
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        # 静かに
        sys.stderr.write("%s - %s\n" % (self.client_address[0], fmt % args))

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict | None:
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n <= 0:
            return None
        raw = self.rfile.read(n)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/fix":
            self._handle_fix()
        elif self.path == "/api/save":
            self._handle_save()
        else:
            self._send_json(404, {"ok": False, "error": "unknown endpoint"})

    def _handle_fix(self) -> None:
        req = self._read_json()
        if not req:
            self._send_json(400, {"ok": False, "error": "invalid json"})
            return
        qid = req.get("id", "")
        issue_type = req.get("issue_type", "other")
        user_note = req.get("user_note", "")
        found = find_quiz(qid)
        if not found:
            self._send_json(404, {"ok": False, "error": f"quiz not found: {qid}"})
            return
        _, data, idx = found
        quiz = data["quizzes"][idx]
        prompt = build_codex_prompt(quiz, issue_type, user_note)
        ok, out = call_codex(prompt, timeout=120)
        if not ok:
            self._send_json(500, {"ok": False, "error": "codex failed", "raw": out[-2000:]})
            return
        suggestion = extract_json(out)
        if not suggestion:
            self._send_json(500, {"ok": False, "error": "no JSON in codex output", "raw": out[-2000:]})
            return
        self._send_json(200, {"ok": True, "suggestion": suggestion, "raw": out[-2000:]})

    def _handle_save(self) -> None:
        req = self._read_json()
        if not req:
            self._send_json(400, {"ok": False, "error": "invalid json"})
            return
        qid = req.get("id", "")
        updates = req.get("updates", {})
        if not isinstance(updates, dict) or not updates:
            self._send_json(400, {"ok": False, "error": "updates required"})
            return
        found = find_quiz(qid)
        if not found:
            self._send_json(404, {"ok": False, "error": f"quiz not found: {qid}"})
            return
        fp, data, idx = found
        quiz = data["quizzes"][idx]
        allowed = {"body", "body_ruby", "choices", "choices_ruby", "correct_index", "explanation", "explanation_ruby", "meaning_jp", "pos"}
        updated_fields = []
        body_changed = False
        for k, v in updates.items():
            if k not in allowed:
                continue
            quiz[k] = v
            updated_fields.append(k)
            if k == "body":
                body_changed = True
        # body変更時は ruby/kana を消して再生成対象に
        if body_changed:
            for k in ("body_ruby", "choices_ruby", "explanation_ruby", "body_kana"):
                if k not in updates:
                    quiz.pop(k, None)
        # 保存
        fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        regen = False
        if body_changed:
            regen = regenerate_ruby(qid)
        self._send_json(200, {"ok": True, "updated_fields": updated_fields, "regenerated_ruby": regen})


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8795
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"WordTacos server: http://127.0.0.1:{port}/progress_viewer.html")
    print(f"  - GET /<file>     静的ファイル")
    print(f"  - POST /api/fix   AI訂正案 (Codex)")
    print(f"  - POST /api/save  保存(JSON書き換え+ルビ再生成)")
    server.serve_forever()


if __name__ == "__main__":
    main()
