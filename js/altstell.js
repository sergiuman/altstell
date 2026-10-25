/**
 * AltStell — Alternative Storytelling · Stellar Minds
 * Core Frontend Controller (Feed, Alternative Storytelling Overlays, Graph Bridge,
 * 17-Book Bilingual Reader, Mindful Screen Guard, and 10-QA / 10-Day Evolution Telemetry).
 */
(function () {
  window.AltStellLang = localStorage.getItem('altstell_lang') || 'en';

  const state = {
    lang: window.AltStellLang,
    activeView: 'feed',
    activeCategory: 'all',
    valuePathFilter: null,
    soundUnlocked: false,
    episodes: [],
    graph: { nodes: [], edges: [], learned_bridges: [], meta: {} },
    books: [],
    qaHistory: [],
    evolution: { completed_days: 0, max_days: 10, daily_runs: [] },
    principles: { rules: [], learned_heuristics: [] },
    sparks: parseInt(localStorage.getItem('altstell_sparks') || '12', 10),
    completedDilemmas: JSON.parse(localStorage.getItem('altstell_dilemmas') || '{}'),
    completedQuests: JSON.parse(localStorage.getItem('altstell_quests') || '{}'),
    sessionWatchedIds: new Set(),
    mindfulShownAtCount: 0,
    observer: null,
    currentReaderBook: null,
    currentReaderChapter: 0
  };

  const UI_STRINGS = {
    en: {
      feed: 'Shorts',
      constellation: 'Constellation',
      library: '17 Books',
      pulse: 'Mindful & QA',
      all: '✦ All Sparks',
      brain_systems: '🧠 Brain & Systems',
      focus_grit: '🔥 Focus & Grit',
      friends_empathy: '🤝 Friends & Empathy',
      inner_calm: '🌙 Calm & Sleep',
      graph_fusion: '🧬 Graph Fusions',
      flipLens: 'Flip Lens',
      dilemma: 'Choose Path',
      quest: 'Real Life',
      graphBtn: 'Graph',
      readBook: 'Full Book',
      tapSound: '🔊 Tap for Voice & Music',
      soundOn: '🔊 Voice On',
      close: 'Back to Story ▶',
      tryQuestBtn: 'I Tried This Offline! (+5 ✦)',
      questDone: '✓ Completed in Real Life!'
    },
    ro: {
      feed: 'Povești Scurte',
      constellation: 'Constelație',
      library: '17 Cărți',
      pulse: 'Echilibru & QA',
      all: '✦ Toate Scânteile',
      brain_systems: '🧠 Minte & Sisteme',
      focus_grit: '🔥 Focus & Răbdare',
      friends_empathy: '🤝 Prieteni & Empatie',
      inner_calm: '🌙 Liniște & Somn',
      graph_fusion: '🧬 Fuziuni din Graf',
      flipLens: 'Perspectivă',
      dilemma: 'Alege Calea',
      quest: 'Viața Reală',
      graphBtn: 'Graf',
      readBook: 'Cartea',
      tapSound: '🔊 Activează Vocea',
      soundOn: '🔊 Voce Activă',
      close: 'Înapoi la Poveste ▶',
      tryQuestBtn: 'Am Încercat Asta Offline! (+5 ✦)',
      questDone: '✓ Îndeplinit în Viața Reală!'
    }
  };

  function t(key) {
    return (UI_STRINGS[state.lang] && UI_STRINGS[state.lang][key]) || UI_STRINGS.en[key] || key;
  }

  async function fetchJsonSafe(url, fallback) {
    try {
      const r = await fetch(url + '?v=' + Date.now());
      if (!r.ok) return fallback;
      return await r.json();
    } catch (_) {
      return fallback;
    }
  }

  async function boot() {
    const [feedDoc, graphDoc, booksDoc, qaDoc, evoDoc, prinDoc] = await Promise.all([
      fetchJsonSafe('data/feed.json', { episodes: [] }),
      fetchJsonSafe('data/knowledge_graph.json', { nodes: [], edges: [], learned_bridges: [], meta: {} }),
      fetchJsonSafe('assets/books_json/books_library.json', { books: [] }),
      fetchJsonSafe('qa/qa_sessions_history.json', []),
      fetchJsonSafe('data/evolution_state.json', { completed_days: 0, max_days: 10, daily_runs: [] }),
      fetchJsonSafe('data/storytelling_principles.json', { rules: [], learned_heuristics: [] })
    ]);

    state.episodes = Array.isArray(feedDoc) ? feedDoc : (feedDoc.episodes || []);
    state.graph = graphDoc || { nodes: [], edges: [] };
    state.books = (booksDoc && booksDoc.books) ? booksDoc.books : [];
    state.qaHistory = Array.isArray(qaDoc) ? qaDoc : [];
    state.evolution = evoDoc || { completed_days: 0, max_days: 10, daily_runs: [] };
    state.principles = prinDoc || { rules: [], learned_heuristics: [] };

    bindGlobalControls();
    applyLanguageLabels();
    renderFilterBar();
    renderFeed();
    renderLibrary();
    renderPulseDashboard();
    updateSparksBadge();
  }

  function bindGlobalControls() {
    document.querySelectorAll('.nav-tab').forEach(btn => {
      btn.addEventListener('click', () => switchView(btn.dataset.view));
    });

    const langBtn = document.getElementById('lang-switch-btn');
    if (langBtn) {
      langBtn.addEventListener('click', () => {
        state.lang = state.lang === 'en' ? 'ro' : 'en';
        window.AltStellLang = state.lang;
        localStorage.setItem('altstell_lang', state.lang);
        applyLanguageLabels();
        renderFilterBar();
        renderFeed();
        renderLibrary();
        renderPulseDashboard();
        if (state.activeView === 'constellation') initGraphView();
      });
    }

    // Keyboard navigation for accessibility & desktop smoothness
    window.addEventListener('keydown', (e) => {
      const readerOpen = document.getElementById('book-reader-backdrop')?.classList.contains('open');
      if (readerOpen) {
        if (e.key === 'Escape') closeBookReader();
        return;
      }
      if (state.activeView !== 'feed') return;
      const stream = document.getElementById('shorts-stream');
      if (!stream) return;
      if (e.key === 'ArrowDown' || e.key === 'PageDown') {
        e.preventDefault();
        stream.scrollBy({ top: stream.clientHeight, behavior: 'smooth' });
      } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
        e.preventDefault();
        stream.scrollBy({ top: -stream.clientHeight, behavior: 'smooth' });
      } else if (e.key === ' ') {
        if (document.activeElement && document.activeElement.tagName === 'BUTTON') return;
        e.preventDefault();
        const activeVid = document.querySelector('.short-slide.in-view video');
        if (activeVid) {
          if (activeVid.paused) activeVid.play().catch(() => {});
          else activeVid.pause();
        }
      }
    });
  }

  function applyLanguageLabels() {
    const langBtn = document.getElementById('lang-switch-btn');
    if (langBtn) langBtn.textContent = state.lang === 'en' ? '🇬🇧 EN → 🇷🇴 RO' : '🇷🇴 RO → 🇬🇧 EN';

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = t(key);
    });
    document.querySelectorAll('[data-en][data-ro]').forEach(el => {
      el.textContent = state.lang === 'ro' ? el.getAttribute('data-ro') : el.getAttribute('data-en');
    });
  }

  function switchView(viewName) {
    state.activeView = viewName;
    document.querySelectorAll('.nav-tab').forEach(b => {
      b.classList.toggle('active', b.dataset.view === viewName);
    });
    document.querySelectorAll('.view-panel').forEach(p => {
      p.classList.toggle('active', p.id === `view-${viewName}`);
    });

    if (viewName !== 'feed') {
      document.querySelectorAll('.short-video').forEach(v => v.pause());
    } else {
      const activeVid = document.querySelector('.short-slide.in-view video');
      if (activeVid) activeVid.play().catch(() => {});
    }

    if (viewName === 'constellation') {
      setTimeout(initGraphView, 40);
    }
  }

  function addSparks(n) {
    state.sparks += n;
    localStorage.setItem('altstell_sparks', String(state.sparks));
    updateSparksBadge();
  }

  function updateSparksBadge() {
    const el = document.getElementById('sparks-count');
    if (el) el.textContent = state.sparks;
  }

  /* =========================================================
     SHORT-VIDEO FEED & ALTERNATIVE STORYTELLING CONTROLS
     ========================================================= */
  function renderFilterBar() {
    const bar = document.getElementById('feed-filter-bar');
    if (!bar) return;
    const cats = ['all', 'brain_systems', 'focus_grit', 'friends_empathy', 'inner_calm', 'graph_fusion'];
    bar.innerHTML = '';

    if (state.valuePathFilter) {
      const clearChip = document.createElement('button');
      clearChip.className = 'filter-chip active';
      clearChip.textContent = `🕸️ ${state.valuePathFilter.label} ✕`;
      clearChip.onclick = () => {
        state.valuePathFilter = null;
        renderFilterBar();
        renderFeed();
      };
      bar.appendChild(clearChip);
      return;
    }

    cats.forEach(c => {
      const btn = document.createElement('button');
      btn.className = 'filter-chip' + (state.activeCategory === c ? ' active' : '');
      btn.textContent = t(c);
      btn.onclick = () => {
        state.activeCategory = c;
        renderFilterBar();
        renderFeed();
      };
      bar.appendChild(btn);
    });
  }

  function getFilteredEpisodes() {
    if (state.valuePathFilter) {
      const targetId = state.valuePathFilter.id;
      return state.episodes.filter(ep =>
        (ep.value_ids || []).includes(targetId) ||
        (ep.book_ids || []).includes(targetId) ||
        ep.id === targetId
      );
    }
    if (state.activeCategory === 'all') return state.episodes;
    if (state.activeCategory === 'graph_fusion') {
      return state.episodes.filter(ep => ep.is_graph_fusion || ep.category === 'graph_fusion');
    }
    return state.episodes.filter(ep => ep.category === state.activeCategory);
  }

  function getValueLabel(valId) {
    const node = (state.graph.nodes || []).find(n => n.id === valId);
    if (!node) return valId.replace('val_', '').replace(/_/g, ' ');
    return state.lang === 'ro' ? (node.label_ro || node.label_en) : node.label_en;
  }

  function renderFeed() {
    const stream = document.getElementById('shorts-stream');
    if (!stream) return;
    if (state.observer) state.observer.disconnect();
    stream.innerHTML = '';

    const list = getFilteredEpisodes();
    list.forEach((ep) => {
      const slide = document.createElement('article');
      slide.className = 'short-slide';
      slide.dataset.epid = ep.id;

      const vidSrc = state.lang === 'ro'
        ? (ep.video_ro || `assets/videos/${ep.id}_ro.mp4`)
        : (ep.video_en || `assets/videos/${ep.id}_en.mp4`);
      const posterSrc = ep.poster || `assets/thumbs/${ep.id}.jpg`;
      const dilemmaDone = Boolean(state.completedDilemmas[ep.id]);
      const questDone = Boolean(state.completedQuests[ep.id]);
      const valChipsHtml = (ep.value_ids || []).slice(0, 2).map(vid =>
        `<span class="value-badge" data-val-jump="${vid}">✦ ${escapeHtml(getValueLabel(vid))}</span>`
      ).join('');

      const beatTimestamps = state.lang === 'ro'
        ? (ep.beat_timestamps_ro || ep.beat_timestamps_en || [0, 7, 14, 21, 28, 35])
        : (ep.beat_timestamps_en || [0, 7, 14, 21, 28, 35]);
      const beatDotsHtml = (ep.beats || []).map((b, bIdx) =>
        `<button class="beat-dot ${bIdx === 0 ? 'active' : ''}" data-beat-idx="${bIdx}" title="Beat ${bIdx + 1}: ${escapeHtml((state.lang === 'ro' ? b.caption_ro : b.caption_en) || '').slice(0, 60)}…">${bIdx + 1}</button>`
      ).join('');

      slide.innerHTML = `
        <div class="short-stage">
          <video class="short-video"
            src="${vidSrc}"
            poster="${posterSrc}"
            playsinline
            loop
            preload="metadata"
            ${state.soundUnlocked ? '' : 'muted'}
            aria-label="${escapeHtml(ep.title[state.lang] || ep.title.en)}">
          </video>

          <div class="beat-sync-bar" role="group" aria-label="Synced Story Beats">
            ${beatDotsHtml}
          </div>

          <button class="sound-unlock-banner" aria-label="Toggle Audio">
            ${state.soundUnlocked ? t('soundOn') : t('tapSound')}
          </button>

          <div class="action-rail">
            <button class="rail-btn act-flip" aria-label="${t('flipLens')}">🔀</button>
            <div class="rail-label">${t('flipLens')}</div>

            <button class="rail-btn act-dilemma ${dilemmaDone ? 'completed' : ''}" aria-label="${t('dilemma')}">⚡</button>
            <div class="rail-label">${t('dilemma')}</div>

            <button class="rail-btn act-quest ${questDone ? 'completed' : ''}" aria-label="${t('quest')}">🎯</button>
            <div class="rail-label">${t('quest')}</div>

            <button class="rail-btn act-graph" aria-label="${t('graphBtn')}">🕸️</button>
            <div class="rail-label">${t('graphBtn')}</div>

            <button class="rail-btn act-book" aria-label="${t('readBook')}">📖</button>
            <div class="rail-label">${t('readBook')}</div>
          </div>

          <div class="stage-footer-chips">
            ${valChipsHtml}
            <button class="interactive-cta-btn act-dilemma-inline">⚡ ${state.lang === 'ro' ? 'Ce ai face tu?' : 'What Would You Do?'}</button>
          </div>

          <div class="stage-overlay" data-overlay-for="${ep.id}"></div>
        </div>
      `;

      const videoEl = slide.querySelector('video');
      const soundBtn = slide.querySelector('.sound-unlock-banner');
      const overlayEl = slide.querySelector('.stage-overlay');
      const beatDots = slide.querySelectorAll('.beat-dot');

      // Live millisecond-locked Story Beat synchronization via beat_timestamps
      videoEl.addEventListener('timeupdate', () => {
        const ct = videoEl.currentTime || 0;
        let activeIdx = 0;
        for (let i = 0; i < beatTimestamps.length; i++) {
          if (ct >= beatTimestamps[i] - 0.08) activeIdx = i;
        }
        beatDots.forEach((dot, idx) => dot.classList.toggle('active', idx === activeIdx));
      });

      beatDots.forEach(dot => {
        dot.addEventListener('click', (e) => {
          e.stopPropagation();
          const idx = parseInt(dot.getAttribute('data-beat-idx') || '0', 10);
          if (beatTimestamps[idx] !== undefined) {
            videoEl.currentTime = beatTimestamps[idx] + 0.05;
            videoEl.play().catch(() => {});
          }
        });
      });

      videoEl.addEventListener('click', () => {
        if (!state.soundUnlocked) {
          unlockAllAudio();
          videoEl.play().catch(() => {});
          return;
        }
        if (videoEl.paused) videoEl.play().catch(() => {});
        else videoEl.pause();
      });

      soundBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        state.soundUnlocked = !state.soundUnlocked;
        document.querySelectorAll('.short-video').forEach(v => { v.muted = !state.soundUnlocked; });
        document.querySelectorAll('.sound-unlock-banner').forEach(b => {
          b.textContent = state.soundUnlocked ? t('soundOn') : t('tapSound');
        });
      });

      slide.querySelector('.act-flip').onclick = () => openFlipOverlay(ep, overlayEl, videoEl);
      slide.querySelector('.act-dilemma').onclick = () => openDilemmaOverlay(ep, overlayEl, videoEl, slide);
      slide.querySelector('.act-dilemma-inline').onclick = () => openDilemmaOverlay(ep, overlayEl, videoEl, slide);
      slide.querySelector('.act-quest').onclick = () => openQuestOverlay(ep, overlayEl, videoEl, slide);
      slide.querySelector('.act-graph').onclick = () => {
        switchView('constellation');
        setTimeout(() => window.AltStellConstellation.focusNodeById(ep.id), 90);
      };
      slide.querySelector('.act-book').onclick = () => {
        const bid = (ep.book_ids && ep.book_ids[0]) || 'book_01';
        openBookReader(bid);
      };

      slide.querySelectorAll('[data-val-jump]').forEach(chip => {
        chip.onclick = () => {
          const vid = chip.getAttribute('data-val-jump');
          switchView('constellation');
          setTimeout(() => window.AltStellConstellation.focusNodeById(vid), 90);
        };
      });

      stream.appendChild(slide);
    });

    setupIntersectionObserver();
  }

  function unlockAllAudio() {
    state.soundUnlocked = true;
    document.querySelectorAll('.short-video').forEach(v => { v.muted = false; });
    document.querySelectorAll('.sound-unlock-banner').forEach(b => { b.textContent = t('soundOn'); });
  }

  function setupIntersectionObserver() {
    const slides = document.querySelectorAll('.short-slide');
    state.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const slide = entry.target;
        const vid = slide.querySelector('video');
        if (entry.isIntersecting && entry.intersectionRatio >= 0.65) {
          slide.classList.add('in-view');
          if (vid && state.activeView === 'feed') {
            vid.muted = !state.soundUnlocked;
            vid.play().catch(() => {});
          }
          trackMindfulWatch(slide.dataset.epid);
        } else {
          slide.classList.remove('in-view');
          if (vid) vid.pause();
        }
      });
    }, { threshold: [0.25, 0.7] });

    slides.forEach(s => state.observer.observe(s));
  }

  function trackMindfulWatch(epId) {
    if (!epId || state.sessionWatchedIds.has(epId)) return;
    state.sessionWatchedIds.add(epId);
    const count = state.sessionWatchedIds.size;
    // Ethical Anti-Doomscroll Check-In every 6 distinct shorts watched!
    if (count > 0 && count % 6 === 0 && state.mindfulShownAtCount !== count) {
      state.mindfulShownAtCount = count;
      setTimeout(openMindfulPauseModal, 1800);
    }
  }

  function openFlipOverlay(ep, overlayEl, videoEl) {
    videoEl.pause();
    const pf = ep.perspective_flip || {};
    const la = (pf.lens_a_label && pf.lens_a_label[state.lang]) || 'Lens A';
    const ta = (pf.lens_a_thought && pf.lens_a_thought[state.lang]) || '';
    const lb = (pf.lens_b_label && pf.lens_b_label[state.lang]) || 'Lens B';
    const tb = (pf.lens_b_thought && pf.lens_b_thought[state.lang]) || '';
    const calmCue = ep.mindful_cue ? (ep.mindful_cue[state.lang] || ep.mindful_cue.en) : '';

    overlayEl.innerHTML = `
      <div class="overlay-kicker">🔀 ${state.lang === 'ro' ? 'Dublă Perspectivă (Antrenament de Empatie)' : 'Dual-Lens Perspective Flip'}</div>
      <div class="overlay-title">${escapeHtml(ep.title[state.lang] || ep.title.en)}</div>
      <div class="lens-card">
        <h4>⚡ ${escapeHtml(la)}</h4>
        <p>“${escapeHtml(ta)}”</p>
      </div>
      <div class="lens-card lens-growth">
        <h4>🌟 ${escapeHtml(lb)}</h4>
        <p>“${escapeHtml(tb)}”</p>
      </div>
      ${calmCue ? `<p style="font-size:0.8rem;color:#94a3b8;">🧘 ${escapeHtml(calmCue)}</p>` : ''}
      <button class="overlay-close">${t('close')}</button>
    `;
    overlayEl.classList.add('open');
    overlayEl.querySelector('.overlay-close').onclick = () => {
      overlayEl.classList.remove('open');
      videoEl.play().catch(() => {});
    };
  }

  function openDilemmaOverlay(ep, overlayEl, videoEl, slideEl) {
    videoEl.pause();
    const dil = ep.interactive_dilemma || {};
    const sit = (dil.situation && dil.situation[state.lang]) || '';
    const ca = (dil.choice_a && dil.choice_a.label && dil.choice_a.label[state.lang]) || 'Option A';
    const cb = (dil.choice_b && dil.choice_b.label && dil.choice_b.label[state.lang]) || 'Option B';
    const somaticCue = ep.mindful_cue ? (ep.mindful_cue[state.lang] || ep.mindful_cue.en) : '';

    overlayEl.innerHTML = `
      <div class="overlay-kicker">⚡ ${state.lang === 'ro' ? 'Poveste Interactivă · Tu Decizi' : 'Interactive Story · What Would You Do?'}</div>
      <div class="overlay-title">${escapeHtml(sit)}</div>
      ${somaticCue ? `<p style="font-size:0.79rem;color:#93c5fd;">🧘 ${escapeHtml(somaticCue)}</p>` : ''}
      <button class="choice-btn" data-choice="a">🅰️ ${escapeHtml(ca)}</button>
      <button class="choice-btn" data-choice="b">🅱️ ${escapeHtml(cb)}</button>
      <div class="dilemma-feedback" id="dil-fb-${ep.id}" style="display:none;"></div>
      <button class="overlay-close">${t('close')}</button>
    `;
    overlayEl.classList.add('open');

    overlayEl.querySelectorAll('.choice-btn').forEach(btn => {
      btn.onclick = () => {
        const key = btn.dataset.choice === 'a' ? 'choice_a' : 'choice_b';
        const ch = dil[key] || {};
        const ripple = (ch.ripple && ch.ripple[state.lang]) || '';
        const takeaway = (dil.psych_takeaway && dil.psych_takeaway[state.lang]) || '';
        const fb = overlayEl.querySelector(`#dil-fb-${ep.id}`);
        fb.style.display = 'block';
        fb.innerHTML = `
          <strong>${ch.is_growth_choice ? '🌟 Growth Ripple:' : '🔍 Notice What Happens:'}</strong>
          <p style="margin-top:5px;">${escapeHtml(ripple)}</p>
          <p style="margin-top:8px;color:#fbbf24;font-weight:700;">💡 ${escapeHtml(takeaway)}</p>
        `;
        if (!state.completedDilemmas[ep.id]) {
          state.completedDilemmas[ep.id] = true;
          localStorage.setItem('altstell_dilemmas', JSON.stringify(state.completedDilemmas));
          addSparks(3);
          slideEl.querySelector('.act-dilemma')?.classList.add('completed');
        }
      };
    });

    overlayEl.querySelector('.overlay-close').onclick = () => {
      overlayEl.classList.remove('open');
      videoEl.play().catch(() => {});
    };
  }

  function openQuestOverlay(ep, overlayEl, videoEl, slideEl) {
    videoEl.pause();
    const q = ep.offline_quest || {};
    const qTitle = (q.title && q.title[state.lang]) || 'Real-World Spark';
    const qInst = (q.instruction && q.instruction[state.lang]) || '';
    const isDone = Boolean(state.completedQuests[ep.id]);

    overlayEl.innerHTML = `
      <div class="overlay-kicker">🎯 ${state.lang === 'ro' ? 'Din Ecran în Viața Reală (2 Minute)' : 'Screen-to-Life Transfer Quest (2 Min)'}</div>
      <div class="overlay-title">${escapeHtml(qTitle)}</div>
      <div class="lens-card lens-growth">
        <p>${escapeHtml(qInst)}</p>
      </div>
      <button class="interactive-cta-btn" id="complete-quest-${ep.id}" style="padding:11px 18px;font-size:0.88rem;">
        ${isDone ? t('questDone') : t('tryQuestBtn')}
      </button>
      <button class="overlay-close">${t('close')}</button>
    `;
    overlayEl.classList.add('open');

    overlayEl.querySelector(`#complete-quest-${ep.id}`).onclick = (e) => {
      if (!state.completedQuests[ep.id]) {
        state.completedQuests[ep.id] = true;
        localStorage.setItem('altstell_quests', JSON.stringify(state.completedQuests));
        addSparks(5);
        e.target.textContent = t('questDone');
        slideEl.querySelector('.act-quest')?.classList.add('completed');
        renderPulseDashboard();
      }
    };

    overlayEl.querySelector('.overlay-close').onclick = () => {
      overlayEl.classList.remove('open');
      videoEl.play().catch(() => {});
    };
  }

  /* =========================================================
     CONSTELLATION KNOWLEDGE GRAPH VIEW
     ========================================================= */
  function initGraphView() {
    const canvas = document.getElementById('constellation-canvas');
    if (!canvas) return;
    window.AltStellConstellation.init(canvas, state.graph, renderGraphInspector);
  }

  function renderGraphInspector(node, neighbors) {
    const box = document.getElementById('graph-inspector-content');
    if (!box || !node) return;
    const lbl = state.lang === 'ro' ? (node.label_ro || node.title_ro || node.label_en) : (node.label_en || node.title_en);
    const desc = state.lang === 'ro'
      ? (node.superpower_ro || node.summary_ro || node.scenario_ro || '')
      : (node.superpower_en || node.summary_en || node.scenario_en || '');

    const connectedChips = neighbors.slice(0, 10).map(({ node: nb, relation }) => {
      const nLbl = state.lang === 'ro' ? (nb.label_ro || nb.title_ro || nb.label_en) : (nb.label_en || nb.title_en);
      return `<button class="btn-pill" style="font-size:0.75rem;margin:3px;" data-focus-node="${nb.id}">
        ${nb.type === 'book' ? '📘' : nb.type === 'value' ? '✦' : nb.type === 'episode' ? '🎬' : '🧩'} ${escapeHtml(nLbl)}
      </button>`;
    }).join('');

    box.innerHTML = `
      <span class="overlay-kicker">${escapeHtml(node.type.toUpperCase())} NODE · PAGERANK ${(node.centrality || 0.015).toFixed(4)}</span>
      <h3 style="font-family:var(--font-display);font-size:1.3rem;">${escapeHtml(lbl)}</h3>
      ${desc ? `<p style="font-size:0.9rem;color:#cbd5e1;line-height:1.5;">${escapeHtml(desc)}</p>` : ''}
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px;">
        <button class="interactive-cta-btn" id="launch-value-path-btn" style="padding:8px 14px;">
          ▶ ${state.lang === 'ro' ? 'Vezi Poveștile Conectate' : 'Watch Connected Shorts'}
        </button>
        ${node.type === 'book' ? `<button class="btn-pill" id="open-graph-book-btn">📖 ${state.lang === 'ro' ? 'Citește Cartea' : 'Read 11yo Book'}</button>` : ''}
      </div>
      <div style="margin-top:12px;">
        <h4 style="font-size:0.78rem;color:var(--text-muted);margin-bottom:8px;">
          ${state.lang === 'ro' ? 'CONEXIUNI ÎN CONSTELAȚIE' : 'GRAPH CONNECTIONS'} (${neighbors.length})
        </h4>
        <div>${connectedChips}</div>
      </div>
    `;

    box.querySelector('#launch-value-path-btn').onclick = () => {
      state.valuePathFilter = { id: node.id, label: lbl };
      switchView('feed');
      renderFilterBar();
      renderFeed();
    };

    const bkBtn = box.querySelector('#open-graph-book-btn');
    if (bkBtn) bkBtn.onclick = () => openBookReader(node.id);

    box.querySelectorAll('[data-focus-node]').forEach(b => {
      b.onclick = () => window.AltStellConstellation.focusNodeById(b.getAttribute('data-focus-node'));
    });
  }

  /* =========================================================
     17-BOOK BILINGUAL CONSOLIDATED LIBRARY & READER
     ========================================================= */
  function filterBooks(query) {
    const q = String(query || '').trim().toLowerCase();
    if (!q) return state.books;
    return state.books.filter(bk =>
      (bk.title_en || '').toLowerCase().includes(q) ||
      (bk.title_ro || '').toLowerCase().includes(q) ||
      (bk.source_book || '').toLowerCase().includes(q) ||
      (bk.source_author || '').toLowerCase().includes(q)
    );
  }

  function renderLibrary() {
    const grid = document.getElementById('books-grid');
    if (!grid) return;
    const searchInput = document.getElementById('bookSearchInput');
    if (searchInput && !searchInput.dataset.bound) {
      searchInput.dataset.bound = '1';
      searchInput.addEventListener('input', () => renderLibrary());
    }
    if (searchInput) {
      searchInput.placeholder = state.lang === 'ro'
        ? '🔍 Caută printre cele 17 cărți, autori sau teme...'
        : '🔍 Search 17 books, authors, or themes...';
    }
    const filtered = filterBooks(searchInput ? searchInput.value : '');
    grid.innerHTML = '';

    filtered.forEach(bk => {
      const card = document.createElement('div');
      card.className = 'book-card';
      const title = state.lang === 'ro' ? bk.title_ro : bk.title_en;
      const wc = state.lang === 'ro' ? bk.word_count_ro : bk.word_count_en;
      const pdfUrl = state.lang === 'ro' ? (bk.pdf_ro || bk.pdf_en) : (bk.pdf_en || bk.pdf_ro);

      card.innerHTML = `
        <div class="book-num" style="color:${bk.color || '#38bdf8'};">VOL. ${bk.num} · ${escapeHtml(bk.source_book)}</div>
        <h3>${escapeHtml(title)}</h3>
        <div class="book-meta">Inspired by ${escapeHtml(bk.source_author)} · ~${wc.toLocaleString()} words (Age 11 Edition)</div>
        <div class="book-actions">
          <button class="interactive-cta-btn read-in-app-btn" style="padding:7px 14px;">📖 ${state.lang === 'ro' ? 'Citește în Aplicație' : 'Read In-App'}</button>
          ${pdfUrl ? `<a class="btn-pill" href="${pdfUrl}" target="_blank" rel="noopener" style="text-decoration:none;">⬇ PDF</a>` : ''}
        </div>
      `;
      card.querySelector('.read-in-app-btn').onclick = () => openBookReader(bk.id);
      grid.appendChild(card);
    });
  }

  function openBookReader(bookId) {
    const bk = state.books.find(b => b.id === bookId) || state.books[0];
    if (!bk) return;
    state.currentReaderBook = bk;
    state.currentReaderChapter = 0;
    document.querySelectorAll('.short-video').forEach(v => v.pause());
    renderReaderModalContent();
    document.getElementById('book-reader-backdrop')?.classList.add('open');
  }

  function closeBookReader() {
    document.getElementById('book-reader-backdrop')?.classList.remove('open');
  }
  window.closeBookReader = closeBookReader;
  window.openBookReader = openBookReader;

  function renderReaderModalContent() {
    const bk = state.currentReaderBook;
    if (!bk) return;
    const chapters = state.lang === 'ro' ? (bk.chapters_ro || []) : (bk.chapters_en || []);
    const titleEl = document.getElementById('reader-book-title');
    const barEl = document.getElementById('reader-chapters-bar');
    const bodyEl = document.getElementById('reader-body');

    if (titleEl) titleEl.textContent = state.lang === 'ro' ? bk.title_ro : bk.title_en;
    if (barEl) {
      barEl.innerHTML = '';
      chapters.forEach((ch, idx) => {
        const b = document.createElement('button');
        b.className = 'filter-chip' + (idx === state.currentReaderChapter ? ' active' : '');
        b.textContent = ch.heading.length > 26 ? ch.heading.slice(0, 24) + '…' : ch.heading;
        b.onclick = () => {
          state.currentReaderChapter = idx;
          renderReaderModalContent();
        };
        barEl.appendChild(b);
      });
    }

    if (bodyEl) {
      const ch = chapters[state.currentReaderChapter] || { heading: '', body: '' };
      const paragraphs = ch.body.split(/\n\n+/).map(p => {
        const clean = escapeHtml(p.trim())
          .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.+?)\*/g, '<em>$1</em>');
        return `<p>${clean}</p>`;
      }).join('');
      bodyEl.innerHTML = `<h2 style="font-family:var(--font-display);margin-bottom:18px;color:#38bdf8;">${escapeHtml(ch.heading)}</h2>${paragraphs}`;
      bodyEl.scrollTop = 0;
    }
  }

  /* =========================================================
     MINDFUL PULSE, QA 10-SESSION TABLE & 10-DAY EVOLUTION LOG
     ========================================================= */
  function openMindfulPauseModal() {
    document.querySelectorAll('.short-video').forEach(v => v.pause());
    const bd = document.getElementById('mindful-pause-backdrop');
    if (bd) bd.classList.add('open');
  }

  window.closeMindfulPause = function () {
    document.getElementById('mindful-pause-backdrop')?.classList.remove('open');
  };

  function renderPulseDashboard() {
    const qCount = Object.keys(state.completedQuests).length;
    const dCount = Object.keys(state.completedDilemmas).length;
    const latestQa = state.qaHistory.length ? state.qaHistory[state.qaHistory.length - 1] : null;
    const gMeta = state.graph.meta || {};

    const statGrid = document.getElementById('pulse-stats');
    if (statGrid) {
      statGrid.innerHTML = `
        <div class="stat-card">
          <div class="book-meta">${state.lang === 'ro' ? 'Scântei câștigate' : 'Stellar Sparks Earned'}</div>
          <div class="stat-val">✦ ${state.sparks}</div>
          <div class="book-meta">${dCount} dilemmas · ${qCount} offline quests</div>
        </div>
        <div class="stat-card">
          <div class="book-meta">${state.lang === 'ro' ? 'Povești Video & Cărți' : 'Short Videos & Books'}</div>
          <div class="stat-val">${state.episodes.length} / 17</div>
          <div class="book-meta">Bilingual EN + RO (Age 11)</div>
        </div>
        <div class="stat-card">
          <div class="book-meta">${state.lang === 'ro' ? 'Noduri & Muchii în Graf' : 'Knowledge Graph Size'}</div>
          <div class="stat-val">${gMeta.total_nodes || (state.graph.nodes || []).length} / ${gMeta.total_edges || (state.graph.edges || []).length}</div>
          <div class="book-meta">NetworkX + Ollama gemma2</div>
        </div>
        <div class="stat-card">
          <div class="book-meta">${state.lang === 'ro' ? 'Scor QA Verificat (10 Sesiuni)' : 'Verified 10-QA Score'}</div>
          <div class="stat-val" style="color:#10b981;">${latestQa ? latestQa.composite_score.toFixed(1) : '—'}/100</div>
          <div class="book-meta">${state.qaHistory.length} QA sessions passed</div>
        </div>
      `;
    }

    const qaBody = document.getElementById('qa-history-tbody');
    if (qaBody) {
      qaBody.innerHTML = state.qaHistory.map(h => {
        const d = h.dimensions || {};
        const sign = h.delta_from_previous >= 0 ? '+' : '';
        return `<tr>
          <td><strong>QA #${h.session}</strong></td>
          <td style="color:#10b981;font-weight:700;">${h.composite_score.toFixed(2)}</td>
          <td><span class="value-badge">${sign}${h.delta_from_previous.toFixed(2)}</span></td>
          <td>${(d.age_11_readability_fit || 0).toFixed(1)}</td>
          <td>${(d.child_psych_safety_growth || 0).toFixed(1)}</td>
          <td>${(d.alt_storytelling_richness || 0).toFixed(1)}</td>
          <td>${(d.media_video_audio_integrity || 0).toFixed(1)}</td>
          <td>${(d.graph_connectivity_expansion || 0).toFixed(1)}</td>
          <td style="color:#cbd5e1;">${escapeHtml(h.changelog_note || '')}</td>
        </tr>`;
      }).join('');
    }

    const evoBox = document.getElementById('evolution-log-list');
    if (evoBox) {
      const runs = state.evolution.daily_runs || [];
      const heuristics = (state.principles && state.principles.learned_heuristics) || [];
      evoBox.innerHTML = `
        <p style="color:#cbd5e1;font-size:0.9rem;margin-bottom:10px;">
          <strong>10-Day Autonomous Workflow Status:</strong> Active via macOS <code>launchd</code> + <code>Ollama (${escapeHtml(state.evolution.ollama_model || 'gemma2:latest')})</code> · Day ${state.evolution.completed_days || 0} / ${state.evolution.max_days || 10}
        </p>
        <div style="display:flex;flex-direction:column;gap:8px;">
          ${heuristics.slice(-4).map(h => `<div class="lens-card lens-growth"><p>🧠 <strong>Learned Principle:</strong> ${escapeHtml(h)}</p></div>`).join('')}
          ${runs.map(r => `<div class="lens-card"><p>🚀 <strong>Day ${r.day}:</strong> Generated <code>${escapeHtml(r.episode_id)}</code> — <em>${escapeHtml(r.title_en)}</em> (Graph Nodes: ${r.graph_nodes}, Guard Score: ${r.guard_score})</p></div>`).join('')}
        </div>
      `;
    }
  }

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  document.addEventListener('DOMContentLoaded', boot);
})();
