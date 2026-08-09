// Funnics Island B1-B20 behavior for the index-like drop-in.
(function(){
  const ROOT_SELECTOR = '[data-b-series]';
  const KEY_MODE = 'displayMode_unified';
  const POS_MAP = {
    adj:'形容詞', adv:'副詞', aux:'助動詞', conj:'接続詞', det:'限定詞',
    noun:'名詞', num:'数詞', phrase:'フレーズ', prep:'前置詞', pron:'代名詞', verb:'動詞', interj:'間投詞'
  };
  let currentAudio = null;
  let currentSpeech = null;
  let activeLine = null;
  let queue = [];
  let queueIndex = 0;
  let voicesCache = [];
  let initialized = false;
  const shadowState = new WeakMap();
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const USE_RECORDED_BEGINNER_AUDIO = true;
  const RECOGNITION_STOP_TIMEOUT_MS = 1000;
  const RECOGNITION_SETTLE_MS = 120;
  const PRELISTEN_MIN_WORDS = 4;
  const EARLY_RESULT_GRACE_MS = 320;
  const MOBILE_RECOGNITION_START_DELAY_MS = 650;
  const SH_PASS_THRESHOLDS = [0.7, 0.55, 0.4, 0.3, 0.2];

  function root(){ return document.querySelector(ROOT_SELECTOR); }
  function sharedShadowing(){
    return window.FunnicsPractice && window.FunnicsPractice.shadowing;
  }
  function sharedQuiz(){
    return window.FunnicsPractice && window.FunnicsPractice.quiz;
  }
  function requestPracticeEvent(name, detail){
    if(typeof CustomEvent !== 'function') return false;
    const event = new CustomEvent(name, { detail });
    document.dispatchEvent(event);
    return !!event.detail && event.detail.handled === true;
  }
  function requestSharedQuiz(book, lesson){
    return requestPracticeEvent('funnics:quiz', { book, lesson: String(lesson) });
  }
  function requestSharedShadow(action, book, userGesture){
    return requestPracticeEvent('funnics:shadowing', { action, book, userGesture: !!userGesture });
  }
  function requestSharedYoutube(book, lesson){
    return requestPracticeEvent('funnics:youtube', { book, lesson: String(lesson) });
  }
  function lessons(){
    const r = root();
    if(!r) return [];
    const out = [];
    r.querySelectorAll(':scope > section.lesson').forEach(s => out.push(s));
    // Lazy template wrappers: section is inside template.content DocumentFragment.
    r.querySelectorAll(':scope > template.lesson-tmpl').forEach(t => {
      const s = t.content.querySelector('section.lesson');
      if(s){ s.__lazyTmpl = t; out.push(s); }
    });
    out.sort((a,b)=>Number(a.dataset.lesson)-Number(b.dataset.lesson));
    return out;
  }
  function ensureLessonMaterialized(lesson){
    if(!lesson) return lesson;
    const tmpl = lesson.__lazyTmpl;
    if(!tmpl || !tmpl.parentNode) return lesson;
    tmpl.parentNode.appendChild(tmpl.content);
    tmpl.remove();
    lesson.__lazyTmpl = null;
    return lesson;
  }
  function currentLesson(){
    const r = root();
    return r ? r.querySelector(':scope > section.lesson:not(.hidden)') : null;
  }
  function makeRuby(text, rt){
    const ruby = document.createElement('ruby');
    ruby.appendChild(document.createTextNode(text));
    const rtEl = document.createElement('rt');
    rtEl.appendChild(document.createTextNode(rt));
    ruby.appendChild(rtEl);
    return ruby;
  }
  function saveWordDisplays(){
    // Walk each lesson so spans inside <template> wrappers (which root.querySelectorAll
    // cannot reach) still get their data-* baselines saved.
    lessons().forEach(lesson => {
      lesson.querySelectorAll('.w, .we').forEach(el => {
        const text = el.textContent.trim();
        if(!el.getAttribute('data-base-saved')) el.setAttribute('data-base-saved', el.getAttribute('data-base') || text.toLowerCase());
        if(!el.getAttribute('data-display')) el.setAttribute('data-display', text);
      });
    });
  }
  function markNewWords(){
    const seen = new Set();
    lessons().forEach(lesson => {
      const words = new Set();
      lesson.querySelectorAll('.w, .we').forEach(el => {
        const base = (el.getAttribute('data-base-saved') || el.getAttribute('data-base') || '').toLowerCase();
        if(base) words.add(base);
      });
      const newOnes = new Set();
      words.forEach(w => { if(!seen.has(w)) newOnes.add(w); });
      lesson.querySelectorAll('.w, .we').forEach(el => {
        const base = (el.getAttribute('data-base-saved') || el.getAttribute('data-base') || '').toLowerCase();
        el.classList.toggle('new-word', newOnes.has(base));
      });
      words.forEach(w => seen.add(w));
    });
  }
  function applyModeToLesson(mode, lesson){
    if(!lesson) return;
    ensureLessonMaterialized(lesson);
    lesson.querySelectorAll('.w').forEach(el => {
      const display = el.getAttribute('data-display') || el.textContent;
      const ipa = el.getAttribute('data-ipa') || '';
      const ja = el.getAttribute('data-ja') || '';
      el.replaceChildren(document.createTextNode(display));
      if(mode === 'ipa' && ipa) el.replaceChildren(makeRuby(display, ipa));
      else if(mode === 'ja' && ja) el.replaceChildren(makeRuby(display, ja));
    });
    lesson.querySelectorAll('.we').forEach(el => {
      const display = el.getAttribute('data-display') || el.textContent;
      const ja = el.getAttribute('data-ja') || '';
      el.replaceChildren(document.createTextNode(display));
      if(mode === 'en-ja' && ja) el.replaceChildren(makeRuby(display, ja));
    });
  }
  function applyMode(mode){
    const r = root();
    if(!r) return;
    localStorage.setItem(KEY_MODE, mode);
    r.querySelectorAll('.btn-mode').forEach(btn => btn.setAttribute('aria-pressed', String(btn.dataset.mode === mode)));
    lessons().forEach(lesson => {
      const jp = lesson.querySelector('.jp-body');
      const en = lesson.querySelector('.en-body');
      const jpf = lesson.querySelector('.jp-full');
      const pic = lesson.querySelector('.picturebook-body');
      if(mode === 'jp-full'){
        jp && jp.classList.add('hidden');
        en && en.classList.add('hidden');
        jpf && jpf.classList.remove('hidden');
        pic && pic.classList.add('hidden');
      } else if(mode === 'picturebook'){
        jp && jp.classList.add('hidden');
        en && en.classList.add('hidden');
        jpf && jpf.classList.add('hidden');
        pic && pic.classList.remove('hidden');
      } else if(mode === 'en' || mode === 'en-ja'){
        jp && jp.classList.add('hidden');
        en && en.classList.remove('hidden');
        jpf && jpf.classList.add('hidden');
        pic && pic.classList.add('hidden');
      } else {
        jp && jp.classList.remove('hidden');
        en && en.classList.add('hidden');
        jpf && jpf.classList.add('hidden');
        pic && pic.classList.add('hidden');
      }
    });
    applyModeToLesson(mode, currentLesson());
    hydratePicturebookImages(currentLesson());
  }
  function stopAudio(options){
    const keepQueue = options && options.keepQueue;
    if(currentAudio){
      const audio = currentAudio;
      currentAudio = null;
      audio.onended = null;
      audio.onerror = null;
      audio.onloadedmetadata = null;
      audio.ontimeupdate = null;
      audio.pause();
      audio.removeAttribute('src');
      audio.load();
    }
    if(currentSpeech){
      currentSpeech.onend = null;
      currentSpeech.onerror = null;
      currentSpeech = null;
    }
    if(window.speechSynthesis) window.speechSynthesis.cancel();
    if(activeLine) activeLine.classList.remove('is-playing');
    activeLine = null;
    if(!keepQueue){
      queue = [];
      queueIndex = 0;
    }
  }
  function rate(){
    const r = root();
    const sel = r && r.querySelector('.sel-tts-rate');
    return sel ? parseFloat(sel.value) || 0.85 : 0.85;
  }
  function resolveAudioUrl(url){
    if(!url) return '';
    if(/^(?:https?:|file:|data:|blob:|\/)/.test(url)) return url;
    if(document.body && document.body.dataset.bSeriesPreview === 'true' && url.startsWith('audio/')){
      return '../' + url;
    }
    return url;
  }
  function resolveThumbUrl(url){
    if(!url) return '';
    if(/^(?:https?:|file:|data:|blob:|\/)/.test(url)) return url;
    if(document.body && document.body.dataset.bSeriesPreview === 'true') return url;
    return 'funnics-beginner-assets/' + url;
  }
  function hydratePicturebookImages(scope){
    if(!scope) return;
    scope.querySelectorAll('img[data-thumb]').forEach(img => {
      if(!img.getAttribute('src')) img.setAttribute('src', resolveThumbUrl(img.getAttribute('data-thumb')));
    });
  }
  function textForPlayback(line){
    if(!line) return '';
    const pictureEnglish = line.querySelector && line.querySelector('.picture-english');
    if(pictureEnglish) return pictureEnglish.textContent.replace(/\s+/g, ' ').trim();
    return textFromLine(line);
  }
  function clearPlayingLine(line){
    if(line) line.classList.remove('is-playing');
    activeLine = null;
  }
  function speakElement(line, onend, options){
    const text = textForPlayback(line);
    stopAudio({ keepQueue: options && options.keepQueue });
    if(line){
      activeLine = line;
      line.classList.add('is-playing');
    }
    if(!window.speechSynthesis || !text){
      clearPlayingLine(line);
      if(onend) setTimeout(onend, 0);
      return;
    }
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US';
    u.rate = rate();
    const r = root();
    const sel = r && r.querySelector('.sel-tts-voice');
    if(sel && sel.value){
      const v = voicesCache.find(x => ((x.name || '') + '|' + (x.lang || '')) === sel.value);
      if(v){ u.voice = v; u.lang = v.lang; }
    }
    let done = false;
    const finish = () => {
      if(done) return;
      done = true;
      clearPlayingLine(line);
      currentSpeech = null;
      if(onend) onend();
    };
    u.onend = finish;
    u.onerror = finish;
    currentSpeech = u;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  }
  function playAudio(url, line, onend, options){
    if(!USE_RECORDED_BEGINNER_AUDIO || !url){
      speakElement(line, onend, options);
      return;
    }
    stopAudio({ keepQueue: options && options.keepQueue });
    if(line){
      activeLine = line;
      line.classList.add('is-playing');
    }
    const audio = new Audio(resolveAudioUrl(url));
    audio.playbackRate = rate();
    let done = false;
    let almostEndFired = false;
    const fireAlmostEnd = () => {
      if(almostEndFired || done) return;
      almostEndFired = true;
      if(options && options.onAlmostEnd) options.onAlmostEnd(audio);
    };
    const checkAlmostEnd = () => {
      if(!options || !options.onAlmostEnd || !Number.isFinite(audio.duration)) return;
      const lead = options.almostEndSeconds == null ? 0.55 : options.almostEndSeconds;
      if(audio.duration - audio.currentTime <= lead) fireAlmostEnd();
    };
    const finish = (ok) => {
      if(done || currentAudio !== audio) return;
      done = true;
      if(line) line.classList.remove('is-playing');
      activeLine = null;
      currentAudio = null;
      audio.onended = null;
      audio.onerror = null;
      audio.onloadedmetadata = null;
      audio.ontimeupdate = null;
      if(ok){
        if(onend) onend();
      } else {
        speakElement(line, onend, options);
      }
    };
    audio.onloadedmetadata = checkAlmostEnd;
    audio.ontimeupdate = checkAlmostEnd;
    audio.onended = () => finish(true);
    audio.onerror = () => finish(false);
    currentAudio = audio;
    audio.play().catch(() => finish(false));
  }
  function playQueue(lines){
    stopAudio();
    queue = lines.filter(Boolean);
    queueIndex = 0;
    function next(){
      if(queueIndex >= queue.length){ stopAudio(); return; }
      const line = queue[queueIndex++];
      const url = line.getAttribute('data-audio');
      playAudio(url, line, next, { keepQueue: true });
    }
    next();
  }
  function populateVoices(){
    voicesCache = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    const sorted = voicesCache.filter(v => (v.lang || '').toLowerCase().startsWith('en'));
    const r = root();
    if(!r) return;
    r.querySelectorAll('.sel-tts-voice').forEach(sel => {
      const prev = sel.value;
      sel.innerHTML = '';
      sorted.forEach(v => {
        const opt = document.createElement('option');
        opt.value = (v.name || '') + '|' + (v.lang || '');
        opt.textContent = `${v.name} [${v.lang}]`;
        sel.appendChild(opt);
      });
      if(prev) sel.value = prev;
    });
  }
  function speakWord(text){
    stopAudio();
    if(!window.speechSynthesis || !text) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US';
    u.rate = rate();
    const r = root();
    const sel = r && r.querySelector('.sel-tts-voice');
    if(sel && sel.value){
      const v = voicesCache.find(x => ((x.name || '') + '|' + (x.lang || '')) === sel.value);
      if(v){ u.voice = v; u.lang = v.lang; }
    }
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  }
  function renderVideo(){
    const r = root();
    const lesson = currentLesson();
    if(r && lesson && requestSharedYoutube(r, lesson.dataset.lesson)) return;
    const sec = r && r.querySelector('.yt-section');
    const container = sec && sec.querySelector('.yt-videos');
    if(!lesson || !container) return;
    const videoId = lesson.dataset.videoId;
    const label = lesson.dataset.videoLabel || ('Lesson B' + lesson.dataset.lesson);
    container.innerHTML = '';
    if(!videoId){ sec.hidden = true; return; }
    sec.hidden = false;
    container.innerHTML =
      '<div class="yt-video-item">' +
        '<span class="yt-video-label">' + label + '</span>' +
        '<div class="yt-embed-wrap"><iframe loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen src="https://www.youtube.com/embed/' + encodeURIComponent(videoId) + '?rel=0"></iframe></div>' +
        '<div style="text-align:center;"><a class="yt-watch-link" href="https://www.youtube.com/watch?v=' + encodeURIComponent(videoId) + '" target="_blank" rel="noopener">▶ YouTube で開く</a></div>' +
      '</div>';
  }
  function renderVocab(){
    const r = root();
    const lesson = currentLesson();
    if(!r || !lesson) return;
    const current = new Map();
    lesson.querySelectorAll('.jp-body .w').forEach(el => {
      const base = (el.getAttribute('data-base-saved') || el.getAttribute('data-base') || '').toLowerCase();
      if(!base || current.has(base)) return;
      current.set(base, {
        base,
        ipa: el.getAttribute('data-ipa') || '',
        ja: el.getAttribute('data-ja') || '',
        pos: POS_MAP[el.getAttribute('data-pos') || ''] || '',
        isNew: el.classList.contains('new-word')
      });
    });
    const cumulative = new Map();
    for(const l of lessons()){
      l.querySelectorAll('.jp-body .w').forEach(el => {
        const base = (el.getAttribute('data-base-saved') || el.getAttribute('data-base') || '').toLowerCase();
        if(!base || cumulative.has(base)) return;
        cumulative.set(base, {
          base,
          ipa: el.getAttribute('data-ipa') || '',
          ja: el.getAttribute('data-ja') || '',
          pos: POS_MAP[el.getAttribute('data-pos') || ''] || '',
          isNew: l === lesson && el.classList.contains('new-word')
        });
      });
      if(l === lesson) break;
    }
    function table(rows){
      const t = document.createElement('table');
      t.innerHTML = '<thead><tr><th>Word</th><th>IPA</th><th>日本語</th><th>品詞</th><th>区分</th></tr></thead>';
      const tb = document.createElement('tbody');
      rows.sort((a,b)=>a.base.localeCompare(b.base)).forEach(row => {
        const tr = document.createElement('tr');
        if(row.isNew) tr.classList.add('new-row');
        tr.classList.add('clickable-word');
        tr.innerHTML = '<td>' + row.base + '</td><td>' + row.ipa + '</td><td>' + row.ja + '</td><td>' + row.pos + '</td><td>' + (row.isNew ? '新出' : '既出') + '</td>';
        tr.addEventListener('click', () => speakWord(row.base));
        tb.appendChild(tr);
      });
      t.appendChild(tb);
      return t;
    }
    const vc = r.querySelector('.vocab-current');
    const cum = r.querySelector('.vocab-cumulative');
    if(vc) vc.replaceChildren(table(Array.from(current.values())));
    if(cum) cum.replaceChildren(table(Array.from(cumulative.values())));
  }
  function toggleSummaryControls(){
    const r = root();
    const lesson = currentLesson();
    if(!r || !lesson) return;
    const isSummary = lesson.dataset.summary === 'true';
    r.querySelectorAll('.b-series-hide-on-summary').forEach(el => {
      el.classList.toggle('hidden', isSummary);
    });
  }
  function showLesson(id){
    const r = root();
    if(!r) return;
    stopAudio();
    const all = lessons();
    // Materialize the target lesson before toggling visibility / running mode passes.
    const target = all.find(l => l.dataset.lesson === String(id));
    if(target) ensureLessonMaterialized(target);
    all.forEach(l => l.classList.toggle('hidden', l.dataset.lesson !== String(id)));
    const sel = r.querySelector('.lesson-select');
    if(sel && sel.value !== String(id)) sel.value = String(id);
    applyMode(localStorage.getItem(KEY_MODE) || 'plain');
    renderVideo();
    renderVocab();
    if(!requestSharedQuiz(r, id) && sharedQuiz()) sharedQuiz().build(r, String(id));
    toggleSummaryControls();
    resetShadowing();
  }
  function textFromLine(line){
    if(!line) return '';
    const clone = line.cloneNode(true);
    clone.querySelectorAll('rt').forEach(rt => rt.remove());
    return clone.textContent.replace(/^\([^)]+\)\s*/, '').replace(/\s+/g, ' ').trim();
  }
  function shadowLines(){
    const lesson = currentLesson();
    return lesson ? Array.from(lesson.querySelectorAll('.en-body p')) : [];
  }
  function stopShadowRecognition(sh, opts){
    const s = sh && shadowState.get(sh);
    if(!s) return Promise.resolve();
    if(s.stopRecognitionPromise) return s.stopRecognitionPromise;
    if(!s.recognition){
      if(!opts || !opts.silent) setShadowStatus(sh, '認識停止中', 'sh-status-idle');
      return Promise.resolve();
    }
    const rec = s.recognition;
    s.recognition = null;
    let done = false;
    let resolveStop;
    const promise = new Promise(resolve => { resolveStop = resolve; });
    s.stopRecognitionPromise = promise;
    const finish = () => {
      if(done) return;
      done = true;
      rec.onresult = null;
      rec.onerror = null;
      rec.onspeechend = null;
      rec.onspeechstart = null;
      rec.onaudioend = null;
      rec.onaudiostart = null;
      rec.onstart = null;
      rec.onend = null;
      if(shadowState.get(sh) === s && s.stopRecognitionPromise === promise) s.stopRecognitionPromise = null;
      if(!opts || !opts.silent) setShadowStatus(sh, '認識停止中', 'sh-status-idle');
      resolveStop();
    };
    rec.onend = finish;
    rec.onerror = finish;
    rec.onresult = null;
    rec.onspeechend = null;
    rec.onspeechstart = null;
    rec.onaudioend = null;
    rec.onaudiostart = null;
    rec.onstart = null;
    try { rec.abort(); } catch(e){ finish(); }
    setTimeout(finish, RECOGNITION_STOP_TIMEOUT_MS);
    return promise;
  }
  function resetShadowing(){
    const r = root();
    if(!r) return;
    if(requestSharedShadow('reset', r)){
      stopAudio();
      return;
    }
    if(sharedShadowing()){
      stopAudio();
      sharedShadowing().reset(r);
      return;
    }
    const sh = r.querySelector('.shadowing');
    if(!sh) return;
    const s = shadowState.get(sh);
    stopAudio();
    if(s && s.recognition) stopShadowRecognition(sh, { silent: true });
    releaseShadowMic(s);
    shadowState.delete(sh);
    sh.querySelector('.sh-intro')?.classList.remove('hidden');
    sh.querySelector('.sh-active')?.classList.add('hidden');
    sh.querySelector('.sh-done')?.classList.add('hidden');
    const fb = sh.querySelector('.sh-feedback');
    if(fb){ fb.textContent = ''; fb.className = 'sh-feedback'; }
  }
  const CONTRACTIONS = {
    "i'm":["i","am"],"you're":["you","are"],"he's":["he","is","has"],"she's":["she","is","has"],"it's":["it","is","has"],
    "we're":["we","are"],"they're":["they","are"],"that's":["that","is","has"],"what's":["what","is","has"],"who's":["who","is","has"],
    "can't":["can","not","cannot"],"don't":["do","not"],"doesn't":["does","not"],"isn't":["is","not"],"aren't":["are","not"],
    "won't":["will","not"],"couldn't":["could","not"],"wouldn't":["would","not"],"shouldn't":["should","not"],"let's":["let","us"]
  };
  const ALWAYS_MATCHED_NAMES = new Set(['tom','teacher','tacos','runner','rabbit','engineer','egg','pilot','panda','singer','snake','baker','bear','funnics']);
  function normWord(w){ return String(w).toLowerCase().replace(/[.,!?;:"“”'’()]/g, ''); }
  function norm(w){ return normWord(w); }
  function isLikelyProperNoun(word, index, allWords){
    const clean = normWord(word);
    if(ALWAYS_MATCHED_NAMES.has(clean)) return true;
    if(index === 0) return false;
    const prev = allWords[index - 1] || '';
    if(/[.!?]$/.test(prev)) return false;
    return /^[A-Z][a-z]+/.test(word);
  }
  function levenshtein(a, b){
    if(a === b) return 0;
    if(!a.length) return b.length;
    if(!b.length) return a.length;
    const dp = Array.from({length: b.length + 1}, (_, i) => i);
    for(let i = 1; i <= a.length; i++){
      let prev = dp[0];
      dp[0] = i;
      for(let j = 1; j <= b.length; j++){
        const tmp = dp[j];
        dp[j] = a[i - 1] === b[j - 1] ? prev : 1 + Math.min(prev, dp[j - 1], dp[j]);
        prev = tmp;
      }
    }
    return dp[b.length];
  }
  function fuzzyMatch(targetWord, recognizedSet){
    const t = normWord(targetWord);
    if(!t || t.length < 5) return false;
    const thr = Math.min(2, Math.floor(t.length / 4));
    for(const r of recognizedSet){
      if(!r || Math.abs(r.length - t.length) > thr) continue;
      if(levenshtein(t, r) <= thr) return true;
    }
    return false;
  }
  function createMatchSet(words){
    const s = new Set();
    for(const w of words){
      const n = normWord(w);
      if(!n) continue;
      s.add(n);
      s.add(n.replace(/'/g, ''));
      s.add(n.replace(/'s$/, ''));
      if(CONTRACTIONS[n]) CONTRACTIONS[n].forEach(x => s.add(x));
    }
    return s;
  }
  function wordMatched(target, set){
    const n = normWord(target);
    if(!n) return false;
    if(set.has(n) || set.has(n.replace(/'/g, '')) || set.has(n.replace(/'s$/, ''))) return true;
    if(CONTRACTIONS[n] && CONTRACTIONS[n].slice(0, 2).every(x => set.has(x))) return true;
    return fuzzyMatch(target, set);
  }
  function recognitionDelay(ms){ return new Promise(resolve => setTimeout(resolve, ms)); }
  function isMobileShadowDevice(){
    const ua = navigator.userAgent || '';
    return /Android|iPhone|iPad|iPod|Mobile|CriOS|FxiOS|EdgiOS/i.test(ua) ||
      (/Macintosh/i.test(ua) && navigator.maxTouchPoints > 1);
  }
  function shouldPrelistenShadow(){
    return !isMobileShadowDevice();
  }
  function shadowRecognitionStartDelay(){
    return shouldPrelistenShadow() ? EARLY_RESULT_GRACE_MS : MOBILE_RECOGNITION_START_DELAY_MS;
  }
  function canAcceptRecognitionResult(s){
    return !!s.acceptRecognitionResults && performance.now() >= (s.acceptResultsAfter || 0);
  }
  function releaseShadowMic(s){
    if(!s || !s.micWarmupStream) return;
    s.micWarmupStream.getTracks().forEach(track => track.stop());
    s.micWarmupStream = null;
  }
  function warmupShadowMic(sh){
    const s = shadowState.get(sh);
    if(isMobileShadowDevice()) return;
    if(!s || s.micWarmupStarted || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
    s.micWarmupStarted = true;
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        if(shadowState.get(sh) !== s || !s.active){
          stream.getTracks().forEach(track => track.stop());
          return;
        }
        s.micWarmupStream = stream;
      })
      .catch(err => {
        console.warn('shadowing mic warmup failed:', err && (err.name || err.message || err));
      });
  }
  function renderShadowTarget(sh){
    const s = shadowState.get(sh);
    if(!s) return;
    sh.querySelector('.sh-index').textContent = String(s.index + 1);
    sh.querySelector('.sh-total').textContent = String(s.lines.length);
    const target = sh.querySelector('.sh-target');
    target.innerHTML = '';
    const words = textFromLine(s.lines[s.index]).split(/\s+/).filter(Boolean);
    s.targetWords = words;
    s.recognizedWords = [];
    s.failedAttempts = 0;
    s.autoMatched = new Set();
    words.forEach((w, i) => {
      const span = document.createElement('span');
      span.className = 'sh-word';
      span.textContent = w;
      if(isLikelyProperNoun(w, i, words)){
        span.classList.add('matched', 'auto-matched');
        s.autoMatched.add(i);
      }
      target.appendChild(span);
      if(i < words.length - 1) target.appendChild(document.createTextNode(' '));
    });
    const fb = sh.querySelector('.sh-feedback');
    if(fb){ fb.textContent = ''; fb.className = 'sh-feedback'; }
  }
  function setShadowStatus(sh, text, cls){
    const el = sh.querySelector('.sh-status');
    if(!el) return;
    el.className = 'sh-status ' + (cls || '');
    el.textContent = text;
  }
  function updateShadowMatched(sh){
    const s = shadowState.get(sh);
    if(!s) return;
    const set = createMatchSet(s.recognizedWords || []);
    sh.querySelectorAll('.sh-target .sh-word').forEach((span, i) => {
      if(wordMatched(s.targetWords[i], set)) span.classList.add('matched');
    });
  }
  function shadowMatchStats(sh){
    const s = shadowState.get(sh);
    if(!s) return { hit: 0, total: 0, ratio: 0, targetLetters: 0, recognizedCount: 0 };
    const set = createMatchSet(s.recognizedWords || []);
    const targetWords = s.targetWords || [];
    if(!targetWords.length) return { hit: 0, total: 0, ratio: 0, targetLetters: 0, recognizedCount: 0 };
    let hit = 0;
    targetWords.forEach((w, i) => {
      if(s.autoMatched && s.autoMatched.has(i)) hit++;
      else if(wordMatched(w, set)) hit++;
    });
    const targetLetters = targetWords.map(normWord).filter(Boolean).join('').length;
    const recognizedCount = (s.recognizedWords || []).map(normWord).filter(Boolean).length;
    return { hit, total: targetWords.length, ratio: hit / targetWords.length, targetLetters, recognizedCount };
  }
  function shadowPassThreshold(s){
    return SH_PASS_THRESHOLDS[Math.min(s.failedAttempts || 0, SH_PASS_THRESHOLDS.length - 1)];
  }
  function shadowAllMatched(sh){
    const s = shadowState.get(sh);
    if(!s) return false;
    const stats = shadowMatchStats(sh);
    if(!stats.total) return false;
    if(stats.ratio >= shadowPassThreshold(s)) return true;
    if(stats.targetLetters <= 3 && stats.recognizedCount > 0) return true;
    if(stats.total <= 2 && stats.hit >= 1) return true;
    if(stats.total <= 4 && stats.hit >= 1 && (s.failedAttempts || 0) >= 1) return true;
    if(stats.recognizedCount > 0 && (s.failedAttempts || 0) >= 3) return true;
    return false;
  }
  async function listen(sh, options){
    const opts = options || {};
    const s = shadowState.get(sh);
    if(!s || !s.active) return;
    if(!SR){
      const fb = sh.querySelector('.sh-feedback');
      fb.textContent = '⚠️ このブラウザは音声認識に対応していません（ChromeかEdgeを使用してください）';
      fb.className = 'sh-feedback forward';
      return;
    }
    const listenToken = (s.listenToken || 0) + 1;
    s.listenToken = listenToken;
    await stopShadowRecognition(sh, { silent: true });
    await recognitionDelay(RECOGNITION_SETTLE_MS);
    if(shadowState.get(sh) !== s || !s.active || s.listenToken !== listenToken) return;
    const rec = new SR();
    rec.lang = 'en-US';
    rec.continuous = false;
    rec.interimResults = false;
    rec.maxAlternatives = 5;
    s.recognition = rec;
    s.resultHandled = false;
    s.errorOccurred = false;
    s.manualStop = false;
    s.ignoredEarlyResult = false;
    rec.onresult = ev => {
      if(s.recognition !== rec) return;
      if(!canAcceptRecognitionResult(s)){
        s.ignoredEarlyResult = true;
        try { rec.abort(); } catch(e){}
        return;
      }
      const spoken = ev.results[0][0].transcript.split(/\s+/).map(normWord).filter(Boolean);
      s.recognizedWords = (s.recognizedWords || []).concat(spoken);
      updateShadowMatched(sh);
      s.resultHandled = true;
      const fb = sh.querySelector('.sh-feedback');
      if(shadowAllMatched(sh)){
        s.failedAttempts = 0;
        fb.textContent = '◯';
        fb.className = 'sh-feedback ok';
        setTimeout(() => {
          if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken) advanceShadow(sh);
        }, 900);
      } else {
        s.failedAttempts++;
        if(s.failedAttempts < 5){
          fb.textContent = 'もう一度';
          fb.className = 'sh-feedback again';
          setTimeout(() => {
            if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken) listen(sh);
          }, 900);
        } else {
          s.failedAttempts = 0;
          fb.textContent = '先に進みます';
          fb.className = 'sh-feedback forward';
          setTimeout(() => {
            if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken) advanceShadow(sh);
          }, 1000);
        }
      }
    };
    rec.onspeechend = () => {
      setShadowStatus(sh, '⏳ 判別中', 'sh-status-processing');
    };
    rec.onerror = ev => {
      if(s.recognition !== rec) return;
      console.warn('shadowing recognition error:', ev.error);
      if(ev.error === 'no-speech'){
        s.errorOccurred = false;
        return;
      }
      if(ev.error === 'aborted') return;
      s.errorOccurred = true;
      if(ev.error === 'not-allowed' || ev.error === 'service-not-allowed'){
        const fb = sh.querySelector('.sh-feedback');
        fb.textContent = '⚠️ マイクの使用が許可されていません。ブラウザの設定で許可してください。';
        fb.className = 'sh-feedback forward';
      }
    };
    rec.onend = () => {
      if(s.recognition === rec){
        s.recognition = null;
        setShadowStatus(sh, '認識停止中', 'sh-status-idle');
        if(s.resultHandled || s.manualStop || s.errorOccurred) return;
        if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken && canAcceptRecognitionResult(s)){
          setTimeout(() => {
            if(shadowState.get(sh) === s && s.active && s.listenToken === listenToken) listen(sh);
          }, 300);
        }
      }
    };
    const startCurrentRecognition = (attempt) => {
      if(shadowState.get(sh) !== s || !s.active || s.recognition !== rec || s.listenToken !== listenToken) return;
      if(!opts.prelisten) setShadowStatus(sh, '🎤 英文を読み上げてください', 'sh-status-active');
      try { rec.start(); }
      catch(e){
        if(attempt < 2){
          setShadowStatus(sh, '⏳ 判別中', 'sh-status-processing');
          setTimeout(() => startCurrentRecognition(attempt + 1), 250 + attempt * 250);
          return;
        }
        console.warn('rec.start threw:', e);
        if(s.recognition === rec) s.recognition = null;
        const fb = sh.querySelector('.sh-feedback');
        fb.textContent = '⚠️ 認識を開始できませんでした: ' + (e.message || e);
        fb.className = 'sh-feedback forward';
        setShadowStatus(sh, '認識停止中', 'sh-status-idle');
      }
    };
    startCurrentRecognition(0);
  }
  async function playShadowCurrent(sh, thenListen){
    const s = shadowState.get(sh);
    if(!s) return;
    const playbackToken = (s.playbackToken || 0) + 1;
    s.playbackToken = playbackToken;
    s.listenToken = (s.listenToken || 0) + 1;
    s.playbackActive = true;
    s.acceptRecognitionResults = false;
    s.acceptResultsAfter = Infinity;
    s.ignoredEarlyResult = false;
    await stopShadowRecognition(sh, { silent: true });
    await recognitionDelay(RECOGNITION_SETTLE_MS);
    if(shadowState.get(sh) !== s || !s.active || s.playbackToken !== playbackToken) return;
    const line = s.lines[s.index];
    const url = line.getAttribute('data-audio');
    setShadowStatus(sh, '🔊 読み上げ中', 'sh-status-tts');
    let prelistenStarted = false;
    const beginPrelisten = () => {
      if(!shouldPrelistenShadow()) return;
      if(prelistenStarted || shadowState.get(sh) !== s || !s.active || s.playbackToken !== playbackToken) return;
      if((s.targetWords || []).length < PRELISTEN_MIN_WORDS) return;
      prelistenStarted = true;
      listen(sh, { prelisten: true });
    };
    const resumeListening = () => {
      if(shadowState.get(sh) !== s || !s.active || s.playbackToken !== playbackToken) return;
      s.playbackActive = false;
      if(!thenListen){
        setShadowStatus(sh, '認識停止中', 'sh-status-idle');
        return;
      }
      const startDelay = shadowRecognitionStartDelay();
      s.acceptResultsAfter = performance.now() + startDelay;
      setTimeout(() => {
        if(shadowState.get(sh) !== s || !s.active || s.playbackToken !== playbackToken) return;
        s.acceptRecognitionResults = true;
        if(s.recognition && s.ignoredEarlyResult){
          stopShadowRecognition(sh, { silent: true }).then(() => {
            if(shadowState.get(sh) === s && s.active && s.playbackToken === playbackToken) listen(sh);
          });
        } else if(s.recognition){
          setShadowStatus(sh, '🎤 英文を読み上げてください', 'sh-status-active');
        } else {
          listen(sh);
        }
      }, startDelay);
    };
    playAudio(url, line, resumeListening, {
      onAlmostEnd: beginPrelisten,
      almostEndSeconds: 0.65
    });
  }
  function startShadowing(){
    const r = root();
    const sh = r && r.querySelector('.shadowing');
    if(!sh) return;
    if(requestSharedShadow('start', r, true)){
      stopAudio();
      return;
    }
    if(sharedShadowing()){
      stopAudio();
      sharedShadowing().start(r);
      return;
    }
    const lines = shadowLines();
    if(!lines.length) return;
    shadowState.set(sh, {
      lines,
      index: 0,
      targetWords: [],
      recognizedWords: [],
      active: true,
      recognition: null,
      failedAttempts: 0,
      stopRecognitionPromise: null,
      listenToken: 0,
      playbackToken: 0,
      playbackActive: false,
      acceptRecognitionResults: false,
      acceptResultsAfter: Infinity,
      micWarmupStarted: false,
      micWarmupStream: null
    });
    sh.querySelector('.sh-intro')?.classList.add('hidden');
    sh.querySelector('.sh-active')?.classList.remove('hidden');
    sh.querySelector('.sh-done')?.classList.add('hidden');
    renderShadowTarget(sh);
    warmupShadowMic(sh);
    playShadowCurrent(sh, true);
  }
  async function advanceShadow(sh){
    const s = shadowState.get(sh);
    if(!s || s.advancing) return;
    s.advancing = true;
    s.listenToken = (s.listenToken || 0) + 1;
    await stopShadowRecognition(sh, { silent: true });
    if(shadowState.get(sh) !== s || !s.active) return;
    s.index++;
    if(s.index >= s.lines.length){
      s.active = false;
      s.advancing = false;
      releaseShadowMic(s);
      sh.querySelector('.sh-active')?.classList.add('hidden');
      sh.querySelector('.sh-done')?.classList.remove('hidden');
      stopAudio();
      return;
    }
    renderShadowTarget(sh);
    setTimeout(() => {
      if(shadowState.get(sh) !== s || !s.active) return;
      s.advancing = false;
      playShadowCurrent(sh, true);
    }, 180);
  }
  function init(){
    const r = root();
    if(!r) return;
    if(initialized) return;
    initialized = true;
    saveWordDisplays();
    markNewWords();
    populateVoices();
    if(window.speechSynthesis && typeof window.speechSynthesis.onvoiceschanged !== 'undefined') window.speechSynthesis.onvoiceschanged = populateVoices;
    if(document.body.dataset.bSeriesPreview === 'true') r.classList.remove('hidden');
    const sel = r.querySelector('.lesson-select');
    showLesson(sel && sel.value ? sel.value : '1');
  }
  function intercept(e){
    const r = root();
    if(!r) return;
    const target = e.target;
    if(!(target instanceof Element)) return;
    if(!r.contains(target)) return;
    if(!initialized) init();
    if(target.closest('.btn-mode')){
      e.preventDefault(); e.stopImmediatePropagation();
      applyMode(target.closest('.btn-mode').dataset.mode);
      return;
    }
    if(target.closest('.btn-tts-passage')){
      e.preventDefault(); e.stopImmediatePropagation();
      playQueue(shadowLines());
      return;
    }
    if(target.closest('.btn-tts-stop')){
      e.preventDefault(); e.stopImmediatePropagation();
      stopAudio();
      return;
    }
    if(target.closest('.btn-next-lesson')){
      e.preventDefault(); e.stopImmediatePropagation();
      const sel = r.querySelector('.lesson-select');
      if(sel && sel.selectedIndex < sel.options.length - 1){
        sel.selectedIndex += 1;
        showLesson(sel.value);
        r.scrollIntoView({behavior:'smooth', block:'start'});
      }
      return;
    }
    if(target.closest('.btn-sh-start') || target.closest('.btn-sh-retry')){
      e.preventDefault(); e.stopImmediatePropagation();
      startShadowing();
      return;
    }
    if(target.closest('.btn-sh-replay')){
      e.preventDefault(); e.stopImmediatePropagation();
      const sh = r.querySelector('.shadowing');
      if(requestSharedShadow('replay', r, true)){
        stopAudio();
      } else if(sharedShadowing()){
        stopAudio();
        sharedShadowing().replay(r);
      } else {
        stopShadowRecognition(sh, { silent: true }).then(() => playShadowCurrent(sh, true));
      }
      return;
    }
    if(target.closest('.btn-sh-stop')){
      e.preventDefault(); e.stopImmediatePropagation();
      const sh = r.querySelector('.shadowing');
      if(requestSharedShadow('stop', r, true)) stopAudio();
      else if(sharedShadowing()) sharedShadowing().stop(r);
      else {
        stopShadowRecognition(sh);
        stopAudio();
      }
      return;
    }
    if(target.closest('.btn-sh-skip')){
      e.preventDefault(); e.stopImmediatePropagation();
      if(requestSharedShadow('skip', r, true)) return;
      if(sharedShadowing()) sharedShadowing().skip(r);
      else advanceShadow(r.querySelector('.shadowing'));
      return;
    }
    if(target.closest('.btn-sh-end')){
      e.preventDefault(); e.stopImmediatePropagation();
      if(requestSharedShadow('end', r, true)) stopAudio();
      else if(sharedShadowing()) sharedShadowing().end(r);
      else {
        resetShadowing();
        stopAudio();
      }
      return;
    }
    const word = target.closest('.w, .we');
    if(word){
      e.preventDefault(); e.stopImmediatePropagation();
      speakWord(word.getAttribute('data-display') || word.textContent.trim());
    }
    const pictureLine = target.closest('.picture-line');
    if(pictureLine){
      e.preventDefault(); e.stopImmediatePropagation();
      playAudio(pictureLine.getAttribute('data-audio'), pictureLine);
    }
  }
  document.addEventListener('click', intercept, true);
  document.addEventListener('change', function(e){
    const r = root();
    const target = e.target;
    if(r && target instanceof Element && r.contains(target) && target.matches('.lesson-select')){
      e.preventDefault(); e.stopImmediatePropagation();
      if(!initialized) init();
      showLesson(target.value);
    }
  }, true);
  document.addEventListener('click', async function(e){
    const btn = e.target instanceof Element && e.target.closest('.btn-book[data-book="beginner"]');
    if(!btn) return;
    const r = root();
    if(!r) return;
    // Wait for the per-book lessons fragment to be fetched & injected (Phase 2 build).
    // Falls through immediately in dev mode where lessons are inline.
    if(typeof window.__loadBookLessons === 'function'){
      try { await window.__loadBookLessons(r); } catch(err){ return; }
    }
    const sel = r.querySelector('.lesson-select');
    if(sel){
      if(!initialized) init();
      showLesson(sel.value);
    }
  });
  document.addEventListener('visibilitychange', () => {
    if(document.hidden) resetShadowing();
  });
  function boot(){
    const r = root();
    if(!r) return;
    if(document.body.dataset.bSeriesPreview === 'true' || !r.classList.contains('hidden')) init();
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
