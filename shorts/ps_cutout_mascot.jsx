// Teacher Tacos welcoming.png を Select Subject で切り抜き、透過PNG出力。
#target photoshop
(function () {
  var SRC = "/Users/masaki/Documents/ClaudeCode/FunnicsIsland/characters/T_teacher_tacos/reference_pack/actions/welcoming.png";
  var OUT = "/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/assets/tt_welcoming_ps.png";
  var doc = app.open(File(SRC));
  app.activeDocument = doc;
  if (doc.activeLayer.isBackgroundLayer) doc.activeLayer.isBackgroundLayer = false;

  var selected = false;
  // Select Subject
  try { executeAction(stringIDToTypeID("selectSubject"), undefined, DialogModes.NO); selected = true; } catch (e) {}
  if (!selected) {
    doc.close(SaveOptions.DONOTSAVECHANGES);
    throw new Error("selectSubject failed");
  }
  // 被写体選択を反転→背景削除
  doc.selection.invert();
  doc.selection.clear();
  doc.selection.deselect();
  doc.trim(TrimType.TRANSPARENT, true, true, true, true);

  var opts = new PNGSaveOptions();
  opts.interlaced = false;
  doc.saveAs(File(OUT), opts, true, Extension.LOWERCASE);
  doc.close(SaveOptions.DONOTSAVECHANGES);
})();
