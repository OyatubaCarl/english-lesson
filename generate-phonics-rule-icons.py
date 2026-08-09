#!/usr/bin/env python3
"""Generate small SVG card icons for rule-based phonics cards."""
import json
from pathlib import Path


DATA_PATH = Path("phonics-audio-items.json")
OUT_DIR = Path("assets/card-icons")

MAGIC_E_LONG_A = {
    "cake": '<ellipse cx="96" cy="118" rx="48" ry="16" fill="#f59e0b"/><rect x="56" y="76" width="80" height="42" rx="10" fill="#fde68a"/><path d="M56 90h80" stroke="#f97316" stroke-width="6"/><circle cx="75" cy="69" r="4" fill="#ef4444"/><circle cx="96" cy="66" r="4" fill="#22c55e"/><circle cx="117" cy="69" r="4" fill="#3b82f6"/>',
    "make": '<path d="M59 110l55-55 20 20-55 55H59z" fill="#fbbf24"/><path d="M114 55l10-10 20 20-10 10z" fill="#64748b"/><path d="M59 110l-9 29 29-9z" fill="#fef3c7"/><circle cx="139" cy="134" r="8" fill="#2563eb"/>',
    "lake": '<path d="M32 116c24-19 46-19 70 0s47 19 70 0v34H32z" fill="#38bdf8"/><path d="M32 82l28-30 24 30 19-22 31 39" fill="none" stroke="#94a3b8" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/><path d="M42 134c24-9 45-9 68 0 18 7 36 7 55 0" fill="none" stroke="#e0f2fe" stroke-width="5" stroke-linecap="round"/>',
    "bake": '<rect x="46" y="60" width="100" height="86" rx="13" fill="#94a3b8"/><rect x="58" y="82" width="76" height="45" rx="8" fill="#1e293b"/><circle cx="70" cy="70" r="5" fill="#f97316"/><circle cx="92" cy="70" r="5" fill="#facc15"/><path d="M70 110c12-14 34-14 47 0" fill="none" stroke="#fbbf24" stroke-width="8" stroke-linecap="round"/>',
    "name": '<rect x="42" y="58" width="108" height="80" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="5"/><rect x="58" y="78" width="76" height="8" rx="4" fill="#2563eb"/><rect x="58" y="100" width="52" height="8" rx="4" fill="#60a5fa"/><circle cx="130" cy="118" r="9" fill="#f97316"/>',
    "game": '<rect x="47" y="64" width="48" height="48" rx="10" fill="#f8fafc" stroke="#64748b" stroke-width="5"/><rect x="99" y="84" width="48" height="48" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="5"/><circle cx="65" cy="82" r="4" fill="#1e293b"/><circle cx="78" cy="96" r="4" fill="#1e293b"/><circle cx="118" cy="103" r="4" fill="#1d4ed8"/><circle cx="129" cy="113" r="4" fill="#1d4ed8"/>',
    "gate": '<rect x="38" y="70" width="118" height="76" rx="8" fill="#fde68a"/><path d="M52 70v76M78 70v76M104 70v76M130 70v76M38 100h118" stroke="#92400e" stroke-width="7"/><path d="M97 70v76" stroke="#1f2937" stroke-width="4"/><circle cx="108" cy="111" r="4" fill="#1f2937"/>',
    "date": '<rect x="42" y="58" width="108" height="92" rx="12" fill="#fff" stroke="#2563eb" stroke-width="5"/><rect x="42" y="58" width="108" height="24" rx="12" fill="#60a5fa"/><rect x="60" y="100" width="22" height="18" rx="4" fill="#fde68a"/><rect x="88" y="100" width="22" height="18" rx="4" fill="#fde68a"/><rect x="116" y="100" width="22" height="18" rx="4" fill="#fca5a5"/>',
    "late": '<circle cx="96" cy="96" r="45" fill="#f8fafc" stroke="#2563eb" stroke-width="7"/><path d="M96 69v30l24 15" stroke="#1f2937" stroke-width="7" stroke-linecap="round"/><path d="M50 50l-14-14M142 50l14-14" stroke="#f97316" stroke-width="7" stroke-linecap="round"/>',
    "tape": '<circle cx="86" cy="100" r="42" fill="#e5e7eb" stroke="#64748b" stroke-width="6"/><circle cx="86" cy="100" r="16" fill="#fff"/><path d="M123 105h40v26h-54z" fill="#fde68a" stroke="#d97706" stroke-width="5"/><path d="M130 116h20" stroke="#f59e0b" stroke-width="4"/>',
    "cape": '<path d="M96 42c23 22 42 64 50 111H46c8-47 27-89 50-111z" fill="#ef4444"/><path d="M76 54h40l-8 22H84z" fill="#fee2e2"/><path d="M78 82c16 10 26 10 39 0" fill="none" stroke="#b91c1c" stroke-width="5" stroke-linecap="round"/>',
    "cane": '<path d="M80 54c0-22 42-22 42 4 0 19-26 20-26 2" fill="none" stroke="#92400e" stroke-width="11" stroke-linecap="round"/><path d="M96 61v86" stroke="#92400e" stroke-width="11" stroke-linecap="round"/><path d="M96 62v84" stroke="#fbbf24" stroke-width="4" stroke-linecap="round"/>',
    "lane": '<path d="M67 148l21-94h16l21 94z" fill="#64748b"/><path d="M96 58v18M96 94v20M96 132v12" stroke="#f8fafc" stroke-width="5" stroke-linecap="round"/><path d="M38 148h116" stroke="#22c55e" stroke-width="8" stroke-linecap="round"/>',
    "plane": '<path d="M30 105l132-48-45 54 42 25-27 11-40-18-31 27-13-7 19-36z" fill="#60a5fa" stroke="#1d4ed8" stroke-width="5" stroke-linejoin="round"/><path d="M67 113l49-2" stroke="#dbeafe" stroke-width="5" stroke-linecap="round"/>',
    "plate": '<circle cx="96" cy="100" r="52" fill="#f8fafc" stroke="#94a3b8" stroke-width="6"/><circle cx="96" cy="100" r="30" fill="#fff" stroke="#e5e7eb" stroke-width="5"/><circle cx="78" cy="96" r="7" fill="#ef4444"/><circle cx="99" cy="90" r="7" fill="#22c55e"/><circle cx="112" cy="111" r="7" fill="#f59e0b"/>',
    "snake": '<path d="M45 111c24-45 69-45 94-14 18 23-12 43-34 23-17-15-36-12-49 14" fill="none" stroke="#22c55e" stroke-width="19" stroke-linecap="round"/><circle cx="137" cy="97" r="3" fill="#052e16"/><path d="M146 104l14 2" stroke="#ef4444" stroke-width="3" stroke-linecap="round"/>',
    "brave": '<path d="M96 46l48 18v34c0 31-21 49-48 61-27-12-48-30-48-61V64z" fill="#facc15" stroke="#d97706" stroke-width="6"/><path d="M74 99l15 15 31-38" fill="none" stroke="#1f2937" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>',
    "cave": '<path d="M34 149c5-57 27-96 62-96s57 39 62 96z" fill="#78716c"/><path d="M70 149c1-35 12-57 26-57s25 22 26 57z" fill="#1f2937"/><path d="M52 145h88" stroke="#a8a29e" stroke-width="5" stroke-linecap="round"/>',
    "wave": '<path d="M34 119c20-31 47-35 72-8 20 22 34 20 52 0-8 31-35 49-66 44-31-4-48-18-58-36z" fill="#38bdf8"/><path d="M55 119c20 17 43 17 64 0" fill="none" stroke="#e0f2fe" stroke-width="6" stroke-linecap="round"/><path d="M68 139c19 7 39 7 58 0" fill="none" stroke="#e0f2fe" stroke-width="5" stroke-linecap="round"/>',
    "save": '<rect x="48" y="48" width="96" height="100" rx="10" fill="#2563eb"/><rect x="64" y="60" width="58" height="30" rx="3" fill="#dbeafe"/><rect x="70" y="111" width="52" height="37" rx="4" fill="#eff6ff"/><path d="M83 124h26M83 136h26" stroke="#64748b" stroke-width="4" stroke-linecap="round"/>',
}


def svg(word, drawing):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192" role="img" aria-label="{word}">
  <rect width="192" height="192" rx="24" fill="#f8fafc"/>
  <rect x="12" y="12" width="168" height="168" rx="20" fill="#ffffff" stroke="#dbeafe" stroke-width="4"/>
  {drawing}
</svg>
'''


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in data["words"]}
    generated = 0

    for word, drawing in MAGIC_E_LONG_A.items():
        out = OUT_DIR / f"{word}.svg"
        out.write_text(svg(word, drawing), encoding="utf-8")
        item = by_id.get(word)
        if item:
            item["image"] = f"assets/card-icons/{word}.svg"
        generated += 1

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {generated} Magic E long-a SVG icons")


if __name__ == "__main__":
    main()
