(function () {
  var log = new File("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/_ae_work/ae_log.txt");
  log.parent.create(); log.open("w");
  function L(m){ log.writeln(m); }
  try {
    L("start ver=" + app.version);
    // 現在のプロジェクトを保存せず閉じる(newProjectの保存確認モーダル回避)
    try { if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); } catch (ce) { L("close:" + ce); }
    app.newProject();
    var proj = app.project;
    L("proj ok");
    var comp = proj.items.addComp("main", 1080, 1920, 1.0, 3, 30);
    L("comp ok");
    comp.layers.addSolid([1,1,1], "bg", 1080, 1920, 1.0);
    L("solid ok");
    var t = comp.layers.addText("WordTacos");
    L("text ok");
    var td = t.property("Source Text").value;
    td.resetCharStyle(); td.fontSize = 140; td.fillColor = [0.84,0.26,0.10];
    t.property("Source Text").setValue(td);
    L("style ok");
    var f = new File("/Users/masaki/Documents/ClaudeCode/英語学習教材作成/shorts/_ae_work/ae_test.aep");
    proj.save(f);
    L("saved " + f.exists);
  } catch(e) {
    L("ERROR line " + (e.line||"?") + ": " + e.toString());
  }
  log.close();
})();
