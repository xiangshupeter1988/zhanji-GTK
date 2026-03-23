import textwrap

# Read the original to get the CSS (lines 1-409 of the HTML)
with open('/workspace/output/index.html', 'r') as f:
    original = f.read()

# Extract everything from <!DOCTYPE to </style>\n</head> (all CSS)
css_end = original.find('</style>\n</head>')
css_section = original[:css_end]

# We need to add login page CSS and syncing indicator CSS
additional_css = """
/* === LOGIN PAGE === */
.login-page{
  position:fixed;inset:0;z-index:500;
  background:linear-gradient(180deg,var(--primary-dark) 0%,var(--primary) 60%,var(--primary-light) 100%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:32px;
}
.login-page.hidden{display:none}
.login-logo{color:var(--accent);font-size:48px;font-weight:800;letter-spacing:2px;margin-bottom:8px}
.login-subtitle{color:rgba(255,255,255,.6);font-size:14px;margin-bottom:40px}
.login-form{width:100%;max-width:360px}
.login-input{
  width:100%;padding:14px 16px;margin-bottom:12px;
  background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.15);
  border-radius:12px;color:#fff;font-size:16px;
}
.login-input::placeholder{color:rgba(255,255,255,.4)}
.login-input:focus{border-color:var(--accent);background:rgba(255,255,255,.15)}
.login-btn{
  width:100%;padding:14px;border-radius:14px;
  font-size:16px;font-weight:600;margin-bottom:10px;
  transition:opacity .2s,transform .15s;cursor:pointer;border:none;
}
.login-btn:active{opacity:.85;transform:scale(.98)}
.login-btn-primary{background:linear-gradient(135deg,var(--accent),var(--accent-glow));color:var(--primary-dark)}
.login-btn-secondary{background:rgba(255,255,255,.12);color:#fff;border:1px solid rgba(255,255,255,.2)}
.login-error{
  color:#ff6b6b;font-size:13px;text-align:center;
  margin-top:12px;min-height:20px;
}
.login-divider{
  display:flex;align-items:center;gap:12px;
  margin:16px 0;color:rgba(255,255,255,.3);font-size:12px;
}
.login-divider::before,.login-divider::after{content:'';flex:1;height:1px;background:rgba(255,255,255,.15)}

/* === SYNCING INDICATOR === */
.sync-indicator{
  position:fixed;top:calc(var(--safe-top) + 4px);right:12px;z-index:110;
  display:flex;align-items:center;gap:6px;
  background:rgba(52,199,89,.9);color:#fff;
  padding:4px 10px;border-radius:8px;
  font-size:11px;font-weight:600;
  opacity:0;transition:opacity .3s;pointer-events:none;
}
.sync-indicator.show{opacity:1}
.sync-indicator .sync-spinner{
  width:12px;height:12px;border:2px solid rgba(255,255,255,.3);
  border-top-color:#fff;border-radius:50%;
  animation:spin .6s linear infinite;
}

/* === LOGOUT BUTTON === */
.header-logout{
  color:rgba(255,255,255,.6);font-size:12px;font-weight:500;
  padding:4px 10px;border-radius:8px;
  background:rgba(255,255,255,.1);
}

/* === CREATOR EMAIL === */
.expo-card-creator{
  font-size:11px;color:var(--text3);padding-left:8px;margin-top:4px;
}
"""

html_content = css_section + additional_css + """</style>
</head>
<body>

<!-- LOGIN PAGE -->
<div class="login-page" id="loginPage">
  <div class="login-logo">展记</div>
  <div class="login-subtitle">参展记录云同步工具</div>
  <div class="login-form">
    <input class="login-input" type="email" id="loginEmail" placeholder="邮箱地址" autocomplete="email">
    <input class="login-input" type="password" id="loginPassword" placeholder="密码" autocomplete="current-password">
    <button class="login-btn login-btn-primary" onclick="doLogin()">登录</button>
    <div class="login-divider">或</div>
    <button class="login-btn login-btn-secondary" onclick="doRegister()">注册新账户</button>
    <div class="login-error" id="loginError"></div>
  </div>
</div>

<!-- SYNCING INDICATOR -->
<div class="sync-indicator" id="syncIndicator"><div class="sync-spinner"></div>同步中...</div>

<!-- HEADER -->
<header class="app-header">
  <div class="header-inner">
    <button class="header-btn" id="headerLeft" style="visibility:hidden" onclick="goBack()">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
    </button>
    <div style="flex:1;overflow:hidden">
      <div class="header-title" id="headerTitle">展记</div>
      <div class="header-expo-name" id="headerExpoName"></div>
    </div>
    <button class="header-logout" id="logoutBtn" style="display:none" onclick="doLogout()">退出</button>
    <button class="header-btn" id="headerRight" style="visibility:hidden"></button>
  </div>
</header>

<!-- PAGES -->
<div class="page-container">
  <!-- HOME -->
  <div class="page active" id="pageHome">
    <div class="page-pad" id="expoListContainer"></div>
  </div>
  <!-- EXPO DETAIL -->
  <div class="page" id="pageDetail">
    <div class="page-pad" id="detailContent"></div>
  </div>
  <!-- PHOTO -->
  <div class="page" id="pagePhoto">
    <div class="page-pad">
      <div class="media-viewport"><video id="photoPreview" autoplay playsinline muted></video><canvas id="photoCanvas" style="display:none"></canvas></div>
      <div class="media-controls">
        <button class="media-ctrl-btn" onclick="switchPhotoCamera()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M21 3l-7 7"/><path d="M8 21H3v-5"/><path d="M3 21l7-7"/></svg></button>
        <button class="capture-btn" onclick="takePhoto()"><div class="capture-btn-inner"></div></button>
        <div style="width:44px"></div>
      </div>
      <div id="photoList"></div>
    </div>
  </div>
  <!-- AUDIO -->
  <div class="page" id="pageAudio">
    <div class="page-pad">
      <div class="audio-recorder">
        <div class="audio-timer" id="audioTimer">00:00</div>
        <div class="audio-status" id="audioStatus">点击开始录音</div>
        <div class="audio-wave" id="audioWave"></div>
        <div class="audio-controls">
          <button class="media-ctrl-btn" id="audioPauseBtn" style="display:none" onclick="pauseAudio()"><svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg></button>
          <button class="capture-btn" id="audioRecBtn" onclick="toggleAudio()"><div class="capture-btn-inner"></div></button>
          <div style="width:44px"></div>
        </div>
      </div>
      <div class="transcript-box idle" id="audioTranscript"></div>
      <div id="audioList"></div>
    </div>
  </div>
  <!-- VIDEO -->
  <div class="page" id="pageVideo">
    <div class="page-pad">
      <div class="media-viewport"><video id="videoPreview" autoplay playsinline muted></video></div>
      <div class="media-controls">
        <button class="media-ctrl-btn" onclick="switchVideoCamera()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M21 3l-7 7"/><path d="M8 21H3v-5"/><path d="M3 21l7-7"/></svg></button>
        <button class="capture-btn" id="videoRecBtn" onclick="toggleVideo()"><div class="capture-btn-inner"></div></button>
        <div class="media-ctrl-btn" id="videoTimerDisplay" style="font-size:13px;font-weight:600;color:var(--danger);opacity:0">00:00</div>
      </div>
      <div class="transcript-box idle" id="videoTranscript"></div>
      <div id="videoList"></div>
    </div>
  </div>
  <!-- CONTACTS -->
  <div class="page" id="pageContact">
    <div class="page-pad" id="contactListContainer"></div>
  </div>
</div>

<!-- TAB BAR -->
<nav class="tab-bar">
  <div class="tab-bar-inner">
    <button class="tab-item active" data-tab="home" onclick="switchTab('home')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/><path d="M9 21V12h6v9"/></svg>
      <span>展会</span>
    </button>
    <button class="tab-item" data-tab="photo" onclick="switchTab('photo')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
      <span>拍照</span>
    </button>
    <button class="tab-item" data-tab="audio" onclick="switchTab('audio')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
      <span>录音</span>
    </button>
    <button class="tab-item" data-tab="video" onclick="switchTab('video')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
      <span>录像</span>
    </button>
    <button class="tab-item" data-tab="contact" onclick="switchTab('contact')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
      <span>对话</span>
    </button>
  </div>
</nav>

<!-- FAB (on home) -->
<button class="fab" id="homeFab" onclick="showNewExpoModal()">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
</button>

<!-- MODALS -->
<div class="modal-overlay" id="modalOverlay">
  <div class="modal-sheet">
    <div class="modal-handle"></div>
    <div class="modal-header">
      <h3 id="modalTitle">新建展会</h3>
      <button class="modal-close" onclick="closeModal()">关闭</button>
    </div>
    <div class="modal-body" id="modalBody"></div>
  </div>
</div>

<!-- PHOTO PREVIEW -->
<div class="preview-overlay" id="previewOverlay">
  <img id="previewImage" src="">
  <div class="preview-actions">
    <button class="cancel" onclick="cancelPreview()">重拍</button>
    <button class="confirm" onclick="confirmPhoto()">保存</button>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<!-- MEDIA FULL PREVIEW -->
<div class="preview-overlay" id="mediaViewOverlay" onclick="closeMediaView()">
  <img id="mediaViewImg" style="display:none" src="">
  <video id="mediaViewVideo" style="display:none" controls playsinline></video>
  <audio id="mediaViewAudio" style="display:none" controls></audio>
</div>

<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script src="https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/file-saver@2.0.5/dist/FileSaver.min.js"></script>
<script>
// ============================================================
// CONFIG - Edit these values with your Supabase project details
// ============================================================
const SUPABASE_URL = 'https://YOUR_PROJECT_ID.supabase.co';
const SUPABASE_ANON_KEY = 'YOUR_ANON_KEY_HERE';

// ============ SUPABASE CLIENT ============
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// ============ CURRENT USER ============
let currentUser = null; // set after auth

// ============ SYNCING INDICATOR ============
let syncCount = 0;
function showSync() {
  syncCount++;
  document.getElementById('syncIndicator').classList.add('show');
}
function hideSync() {
  syncCount = Math.max(0, syncCount - 1);
  if (syncCount === 0) document.getElementById('syncIndicator').classList.remove('show');
}

// ============ SUPABASE DB HELPERS ============
async function dbAdd(table, data) {
  showSync();
  try {
    const { data: result, error } = await supabase.from(table).upsert(data).select();
    if (error) throw error;
    return result && result[0] ? result[0] : null;
  } finally { hideSync(); }
}

async function dbInsert(table, data) {
  showSync();
  try {
    const { data: result, error } = await supabase.from(table).insert(data).select();
    if (error) throw error;
    return result && result[0] ? result[0] : null;
  } finally { hideSync(); }
}

async function dbGetAll(table) {
  const { data, error } = await supabase.from(table).select('*').order('created_at', { ascending: false });
  if (error) throw error;
  return data || [];
}

async function dbGetByExpo(table, expoId) {
  const { data, error } = await supabase.from(table).select('*').eq('expo_id', expoId).order('created_at', { ascending: false });
  if (error) throw error;
  return data || [];
}

async function dbDelete(table, id) {
  showSync();
  try {
    const { error } = await supabase.from(table).delete().eq('id', id);
    if (error) throw error;
  } finally { hideSync(); }
}

async function dbUpdate(table, id, updates) {
  showSync();
  try {
    const { data, error } = await supabase.from(table).update(updates).eq('id', id).select();
    if (error) throw error;
    return data && data[0] ? data[0] : null;
  } finally { hideSync(); }
}

// ============ STORAGE HELPERS ============
async function uploadMedia(blob, type, ext) {
  if (!currentUser) throw new Error('Not logged in');
  const ts = Date.now();
  const path = currentUser.id + '/' + type + '_' + ts + '.' + ext;
  showSync();
  try {
    const { error } = await supabase.storage.from('media').upload(path, blob, { contentType: blob.type || 'application/octet-stream' });
    if (error) throw error;
    return path;
  } finally { hideSync(); }
}

function getMediaUrl(filePath) {
  if (!filePath) return '';
  const { data } = supabase.storage.from('media').getPublicUrl(filePath);
  return data.publicUrl;
}

async function fetchMediaBlob(filePath) {
  const url = getMediaUrl(filePath);
  const resp = await fetch(url);
  return resp.blob();
}

async function deleteMediaFile(filePath) {
  if (!filePath) return;
  try {
    await supabase.storage.from('media').remove([filePath]);
  } catch (e) { console.warn('Failed to delete storage file:', e); }
}

// ============ AUTH ============
async function doLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  const errEl = document.getElementById('loginError');
  errEl.textContent = '';
  if (!email || !password) { errEl.textContent = '请输入邮箱和密码'; return; }
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) { errEl.textContent = '登录失败: ' + error.message; return; }
  currentUser = data.user;
  onAuthSuccess();
}

async function doRegister() {
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  const errEl = document.getElementById('loginError');
  errEl.textContent = '';
  if (!email || !password) { errEl.textContent = '请输入邮箱和密码'; return; }
  if (password.length < 6) { errEl.textContent = '密码至少6个字符'; return; }
  const { data, error } = await supabase.auth.signUp({ email, password });
  if (error) { errEl.textContent = '注册失败: ' + error.message; return; }
  if (data.user && !data.session) {
    errEl.textContent = '注册成功！请查收验证邮件后登录。';
    errEl.style.color = '#34c759';
    return;
  }
  currentUser = data.user;
  onAuthSuccess();
}

async function doLogout() {
  await supabase.auth.signOut();
  currentUser = null;
  currentExpo = null;
  allExpos = [];
  document.getElementById('loginPage').classList.remove('hidden');
  document.getElementById('logoutBtn').style.display = 'none';
}

function onAuthSuccess() {
  document.getElementById('loginPage').classList.add('hidden');
  document.getElementById('logoutBtn').style.display = 'block';
  init();
}

// ============ CHECK OWNERSHIP ============
function isOwner(item) {
  return currentUser && item.user_id === currentUser.id;
}

// Helper to get user email from cache
const userEmailCache = {};
async function getUserEmail(userId) {
  if (userEmailCache[userId]) return userEmailCache[userId];
  if (currentUser && userId === currentUser.id) {
    userEmailCache[userId] = currentUser.email;
    return currentUser.email;
  }
  // We can't query other users' emails from client side easily,
  // so we store creator email in a simple way
  return userId.substring(0, 8) + '...';
}

// ============ STATE ============
let currentTab = 'home';
let currentExpo = null;
let allExpos = [];
let photoStream = null, photoFacing = 'environment';
let audioRecorder = null, audioStream = null, audioChunks = [], audioState = 'idle', audioInterval = null, audioSeconds = 0;
let videoRecorder = null, videoStream = null, videoChunks = [], videoState = 'idle', videoInterval = null, videoSeconds = 0, videoFacing = 'environment';
let pendingPhotoBlob = null;
let audioSpeechRec = null, audioTranscript = '', videoSpeechRec = null, videoTranscript = '';
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function createSpeechRec(onResult) {
  if (!SpeechRecognition) return null;
  const rec = new SpeechRecognition();
  rec.continuous = true; rec.interimResults = true; rec.lang = 'zh-CN';
  rec.onresult = e => {
    let final = '', interim = '';
    for (let i = 0; i < e.results.length; i++) {
      if (e.results[i].isFinal) final += e.results[i][0].transcript;
      else interim += e.results[i][0].transcript;
    }
    onResult(final, interim);
  };
  rec.onerror = () => {};
  rec.onend = function() { if (this._keepAlive) try { this.start() } catch(e) {} };
  return rec;
}

// ============ INIT ============
async function init() {
  allExpos = await dbGetAll('expos');
  if (allExpos.length > 0 && !currentExpo) currentExpo = allExpos[0];
  initAudioWave();
  renderHome();
  updateHeaderExpo();
}

// ============ AUTH INIT ON LOAD ============
(async function() {
  const { data: { session } } = await supabase.auth.getSession();
  if (session && session.user) {
    currentUser = session.user;
    onAuthSuccess();
  }
  // Listen for auth changes
  supabase.auth.onAuthStateChange((event, session) => {
    if (session && session.user) {
      currentUser = session.user;
    } else {
      currentUser = null;
    }
  });
})();

// ============ TAB SWITCHING ============
function switchTab(tab) {
  if (currentTab === tab) return;
  if (currentTab === 'photo') stopPhotoStream();
  if (currentTab === 'audio' && audioState !== 'idle') stopAudioRecording();
  if (currentTab === 'video' && videoState !== 'idle') stopVideoRecording();
  if (currentTab === 'video') stopVideoStream();

  document.querySelectorAll('.tab-item').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

  currentTab = tab;
  const pageMap = { home: 'pageHome', photo: 'pagePhoto', audio: 'pageAudio', video: 'pageVideo', contact: 'pageContact' };
  document.getElementById(pageMap[tab]).classList.add('active');

  document.getElementById('homeFab').style.display = tab === 'home' ? 'flex' : 'none';

  const headerLeft = document.getElementById('headerLeft');
  headerLeft.style.visibility = 'hidden';

  if (tab === 'home') {
    document.getElementById('headerTitle').textContent = '展记';
    document.getElementById('headerRight').style.visibility = 'hidden';
    renderHome();
  } else {
    if (!currentExpo) { showToast('请先选择或创建一个展会'); switchTab('home'); return; }
    document.getElementById('headerTitle').textContent = { photo: '拍照', audio: '录音', video: '录像', contact: '对话记录' }[tab];
    updateHeaderExpo();
    if (tab === 'photo') startPhotoStream();
    if (tab === 'audio') renderAudioList();
    if (tab === 'video') startVideoStream();
    if (tab === 'contact') renderContactList();
  }
  if (tab === 'contact') {
    document.getElementById('homeFab').style.display = 'flex';
    document.getElementById('homeFab').onclick = () => showNewContactModal();
  } else {
    document.getElementById('homeFab').onclick = () => showNewExpoModal();
  }
}

// ============ HEADER ============
function updateHeaderExpo() {
  const el = document.getElementById('headerExpoName');
  el.textContent = currentExpo ? ('当前展会: ' + currentExpo.name) : '';
}
function goBack() {
  const headerLeft = document.getElementById('headerLeft');
  headerLeft.style.visibility = 'hidden';
  document.getElementById('headerRight').style.visibility = 'hidden';
  document.getElementById('pageDetail').classList.remove('active');
  document.getElementById('pageHome').classList.add('active');
  document.getElementById('headerTitle').textContent = '展记';
  document.getElementById('homeFab').style.display = 'flex';
  currentTab = 'home';
  document.querySelectorAll('.tab-item').forEach(t => t.classList.toggle('active', t.dataset.tab === 'home'));
}

// ============ TOAST ============
function showToast(msg) {
  const t = document.getElementById('toast'); t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2200);
}

// ============ MODAL ============
function showModal(title, html) {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalBody').innerHTML = html;
  document.getElementById('modalOverlay').classList.add('show');
}
function closeModal() { document.getElementById('modalOverlay').classList.remove('show') }

// ============ HOME / EXPO LIST ============
async function renderHome() {
  allExpos = await dbGetAll('expos');
  const c = document.getElementById('expoListContainer');
  if (allExpos.length === 0) {
    c.innerHTML = '<div class="empty-state"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="18" rx="2"/><path d="M8 7h8M8 11h5"/></svg><h3>还没有展会记录</h3><p>点击右下角 + 按钮创建你的第一个展会</p></div>';
    return;
  }
  // count records per expo
  const photos = await dbGetAll('photos'), audios = await dbGetAll('audios'), videos = await dbGetAll('videos'), contacts = await dbGetAll('contacts');
  const count = (arr, eid) => arr.filter(r => r.expo_id === eid).length;

  let html = '<div class="section-header"><h2>我的展会</h2></div>';
  for (const ex of allExpos) {
    const sel = currentExpo && currentExpo.id === ex.id;
    const pc = count(photos, ex.id), ac = count(audios, ex.id), vc = count(videos, ex.id), cc = count(contacts, ex.id);
    const creatorEmail = currentUser && ex.user_id === currentUser.id ? currentUser.email : (ex.user_id ? ex.user_id.substring(0, 8) + '...' : '');
    const canEdit = isOwner(ex);
    html += '<div class="expo-card" onclick="selectExpo(\\'' + ex.id + '\\')">' +
      (sel ? '<div class="selected-indicator">当前</div>' : '') +
      '<div class="expo-card-name">' + esc(ex.name) + '</div>' +
      '<div class="expo-card-info"><span>' + (ex.date || '') + '</span>' + (ex.location ? '<span>\\u00b7</span><span>' + esc(ex.location) + '</span>' : '') + '</div>' +
      '<div class="expo-card-creator">创建者: ' + esc(creatorEmail) + '</div>' +
      '<div class="expo-card-stats">' +
        '<span class="stat-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>' + pc + '</span>' +
        '<span class="stat-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/></svg>' + ac + '</span>' +
        '<span class="stat-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>' + vc + '</span>' +
        '<span class="stat-chip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>' + cc + '</span>' +
      '</div></div>';
  }
  c.innerHTML = html;
}

function selectExpo(id) {
  currentExpo = allExpos.find(e => e.id === id) || null;
  updateHeaderExpo();
  showExpoDetail(id);
}

async function showExpoDetail(id) {
  const ex = allExpos.find(e => e.id === id); if (!ex) return;
  currentTab = 'detail';
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('pageDetail').classList.add('active');
  document.getElementById('headerTitle').textContent = ex.name;
  document.getElementById('headerExpoName').textContent = (ex.date || '') + (ex.location ? ' \\u00b7 ' + ex.location : '');
  document.getElementById('headerLeft').style.visibility = 'visible';
  document.getElementById('homeFab').style.display = 'none';
  document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));

  const photos = await dbGetByExpo('photos', id);
  const audios = await dbGetByExpo('audios', id);
  const videos = await dbGetByExpo('videos', id);
  const contacts = await dbGetByExpo('contacts', id);

  const canEdit = isOwner(ex);
  let html = '';

  // Info section
  html += '<div class="detail-section">' +
    '<div style="display:flex;gap:8px;margin-bottom:16px">' +
      '<button class="export-btn" onclick="exportExpo(\\'' + id + '\\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>导出Word报告</button>' +
    '</div>';
  if (canEdit) {
    html += '<div style="display:flex;gap:8px">' +
      '<button class="form-btn" style="flex:1;font-size:13px;padding:10px" onclick="showEditExpoModal(\\'' + id + '\\')">编辑展会</button>' +
      '<button class="form-btn danger" style="flex:1;font-size:13px;padding:10px" onclick="deleteExpo(\\'' + id + '\\')">删除展会</button>' +
    '</div>';
  }
  html += '</div>';

  if (ex.description) {
    html += '<div class="detail-section"><div class="contact-notes">' + esc(ex.description) + '</div></div>';
  }

  // Photos
  html += '<div class="detail-section"><div class="detail-section-title">照片 (' + photos.length + ')</div>';
  if (photos.length > 0) {
    html += '<div class="detail-grid">';
    photos.forEach(p => {
      const url = getMediaUrl(p.file_path);
      const imp = p.important ? true : false;
      const canEditP = isOwner(p);
      html += '<div class="detail-grid-item' + (imp ? ' photo-important' : '') + '" onclick="viewMedia(\\'image\\',\\'' + p.id + '\\')">' +
        '<img src="' + url + '">' +
        (canEditP ? '<button class="photo-star' + (imp ? ' important' : '') + '" onclick="event.stopPropagation();togglePhotoStarDetail(\\'' + p.id + '\\',\\'' + id + '\\')"><svg viewBox="0 0 24 24" fill="' + (imp ? 'currentColor' : 'none') + '" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></button>' : '') +
      '</div>';
    });
    html += '</div>';
  } else html += '<div style="color:var(--text3);font-size:13px;padding:8px 0">暂无照片</div>';
  html += '</div>';

  // Audios
  html += '<div class="detail-section"><div class="detail-section-title">录音 (' + audios.length + ')</div>';
  audios.forEach(a => {
    const hasT = a.transcript && a.transcript.trim();
    html += '<div class="record-item" onclick="viewMedia(\\'audio\\',\\'' + a.id + '\\')" style="flex-wrap:wrap">' +
      '<div class="record-item-thumb"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/></svg></div>' +
      '<div class="record-item-info"><div class="record-item-title">录音 ' + fmtDuration(a.duration || 0) + (hasT ? '<span class="transcript-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>已转写</span>' : '') + '</div><div class="record-item-meta">' + fmtDate(a.created_at) + '</div>' + (hasT ? '<div class="record-item-transcript">' + esc(a.transcript) + '</div>' : '') + '</div>' +
    '</div>';
  });
  if (audios.length === 0) html += '<div style="color:var(--text3);font-size:13px;padding:8px 0">暂无录音</div>';
  html += '</div>';

  // Videos
  html += '<div class="detail-section"><div class="detail-section-title">录像 (' + videos.length + ')</div>';
  if (videos.length > 0) {
    html += '<div class="detail-grid">';
    videos.forEach(v => {
      const url = getMediaUrl(v.file_path);
      html += '<div class="detail-grid-item" onclick="viewMedia(\\'video\\',\\'' + v.id + '\\')">' +
        '<video src="' + url + '" muted></video>' +
        '<div class="play-badge"><svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg></div></div>';
    });
    html += '</div>';
  } else html += '<div style="color:var(--text3);font-size:13px;padding:8px 0">暂无录像</div>';
  html += '</div>';

  // Contacts
  html += '<div class="detail-section"><div class="detail-section-title">对话记录 (' + contacts.length + ')</div>';
  contacts.forEach(ct => { html += renderContactCard(ct); });
  if (contacts.length === 0) html += '<div style="color:var(--text3);font-size:13px;padding:8px 0">暂无对话记录</div>';
  html += '</div>';

  document.getElementById('detailContent').innerHTML = html;
}

// ============ EXPO CRUD ============
function showNewExpoModal() {
  showModal('新建展会',
    '<div class="form-group"><label class="form-label">展会名称 *</label><input class="form-input" id="expoName" placeholder="如：2026 CES 消费电子展"></div>' +
    '<div class="form-group"><label class="form-label">日期</label><input class="form-input" id="expoDate" type="date"></div>' +
    '<div class="form-group"><label class="form-label">地点</label><input class="form-input" id="expoLocation" placeholder="如：上海新国际博览中心"></div>' +
    '<div class="form-group"><label class="form-label">描述</label><textarea class="form-input" id="expoDesc" placeholder="展会简介、关注重点等"></textarea></div>' +
    '<button class="form-btn" onclick="saveNewExpo()">创建展会</button>'
  );
}
async function saveNewExpo() {
  const name = document.getElementById('expoName').value.trim();
  if (!name) { showToast('请输入展会名称'); return; }
  const row = await dbInsert('expos', {
    user_id: currentUser.id,
    name,
    date: document.getElementById('expoDate').value,
    location: document.getElementById('expoLocation').value.trim(),
    description: document.getElementById('expoDesc').value.trim()
  });
  currentExpo = row;
  closeModal(); showToast('展会已创建');
  updateHeaderExpo(); renderHome();
}
function showEditExpoModal(id) {
  const ex = allExpos.find(e => e.id === id); if (!ex) return;
  showModal('编辑展会',
    '<div class="form-group"><label class="form-label">展会名称</label><input class="form-input" id="editExpoName" value="' + esc(ex.name) + '"></div>' +
    '<div class="form-group"><label class="form-label">日期</label><input class="form-input" id="editExpoDate" type="date" value="' + (ex.date || '') + '"></div>' +
    '<div class="form-group"><label class="form-label">地点</label><input class="form-input" id="editExpoLocation" value="' + esc(ex.location || '') + '"></div>' +
    '<div class="form-group"><label class="form-label">描述</label><textarea class="form-input" id="editExpoDesc">' + esc(ex.description || '') + '</textarea></div>' +
    '<button class="form-btn" onclick="saveEditExpo(\\'' + id + '\\')">保存</button>'
  );
}
async function saveEditExpo(id) {
  const updated = await dbUpdate('expos', id, {
    name: document.getElementById('editExpoName').value.trim(),
    date: document.getElementById('editExpoDate').value,
    location: document.getElementById('editExpoLocation').value.trim(),
    description: document.getElementById('editExpoDesc').value.trim()
  });
  closeModal(); showToast('已保存');
  allExpos = await dbGetAll('expos');
  if (currentExpo && currentExpo.id === id) currentExpo = updated || allExpos.find(e => e.id === id);
  showExpoDetail(id);
}
async function deleteExpo(id) {
  if (!confirm('确定删除该展会及所有相关记录？')) return;
  // delete related media files first
  for (const table of ['photos', 'audios', 'videos']) {
    const items = await dbGetByExpo(table, id);
    for (const item of items) {
      await deleteMediaFile(item.file_path);
      await dbDelete(table, item.id);
    }
  }
  const contactItems = await dbGetByExpo('contacts', id);
  for (const item of contactItems) await dbDelete('contacts', item.id);
  await dbDelete('expos', id);
  if (currentExpo && currentExpo.id === id) currentExpo = null;
  showToast('已删除'); goBack(); renderHome();
}

// ============ PHOTO ============
async function startPhotoStream() {
  try {
    if (photoStream) stopPhotoStream();
    photoStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: photoFacing, width: { ideal: 1920 }, height: { ideal: 1080 } }, audio: false });
    document.getElementById('photoPreview').srcObject = photoStream;
    renderPhotoList();
  } catch(e) { showToast('无法访问摄像头: ' + e.message); }
}
function stopPhotoStream() {
  if (photoStream) { photoStream.getTracks().forEach(t => t.stop()); photoStream = null; }
  document.getElementById('photoPreview').srcObject = null;
}
function switchPhotoCamera() {
  photoFacing = photoFacing === 'environment' ? 'user' : 'environment';
  startPhotoStream();
}
function takePhoto() {
  if (!photoStream) return;
  const video = document.getElementById('photoPreview');
  const canvas = document.getElementById('photoCanvas');
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  canvas.toBlob(blob => {
    pendingPhotoBlob = blob;
    document.getElementById('previewImage').src = URL.createObjectURL(blob);
    document.getElementById('previewOverlay').classList.add('show');
  }, 'image/jpeg', 0.92);
}
function cancelPreview() {
  pendingPhotoBlob = null;
  document.getElementById('previewOverlay').classList.remove('show');
}
async function confirmPhoto() {
  if (!pendingPhotoBlob || !currentExpo) return;
  const filePath = await uploadMedia(pendingPhotoBlob, 'photo', 'jpg');
  await dbInsert('photos', {
    expo_id: currentExpo.id,
    user_id: currentUser.id,
    file_path: filePath,
    important: false
  });
  pendingPhotoBlob = null;
  document.getElementById('previewOverlay').classList.remove('show');
  showToast('照片已保存'); renderPhotoList();
}
async function renderPhotoList() {
  if (!currentExpo) return;
  const photos = await dbGetByExpo('photos', currentExpo.id);
  const c = document.getElementById('photoList');
  if (photos.length === 0) { c.innerHTML = '<div style="text-align:center;color:var(--text3);font-size:13px;padding:16px 0">该展会暂无照片</div>'; return; }
  let html = '<div style="margin-top:8px;font-size:13px;font-weight:600;color:var(--text2);margin-bottom:8px">已拍摄 (' + photos.length + ') \\u00b7 点击\\u2b50标记重要照片用于导出</div>';
  photos.forEach(p => {
    const url = getMediaUrl(p.file_path);
    const imp = p.important ? true : false;
    const canEditP = isOwner(p);
    html += '<div class="record-item' + (imp ? ' photo-important' : '') + '">' +
      '<div class="record-item-thumb" style="position:relative"><img src="' + url + '">' +
      (canEditP ? '<button class="photo-star' + (imp ? ' important' : '') + '" onclick="event.stopPropagation();togglePhotoStar(\\'' + p.id + '\\')"><svg viewBox="0 0 24 24" fill="' + (imp ? 'currentColor' : 'none') + '" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></button>' : '') +
      '</div>' +
      '<div class="record-item-info"><div class="record-item-title">照片' + (imp ? ' \\u2b50' : '') + '</div><div class="record-item-meta">' + fmtDate(p.created_at) + '</div></div>' +
      (canEditP ? '<button class="record-item-del" onclick="event.stopPropagation();deleteRecord(\\'photos\\',\\'' + p.id + '\\',\\'photo\\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg></button>' : '') +
    '</div>';
  });
  c.innerHTML = html;
}
async function deleteRecord(table, id, type) {
  if (!confirm('确定删除？')) return;
  // Delete associated media file
  if (table === 'photos' || table === 'audios' || table === 'videos') {
    const items = await dbGetAll(table);
    const item = items.find(x => x.id === id);
    if (item && item.file_path) await deleteMediaFile(item.file_path);
  }
  await dbDelete(table, id); showToast('已删除');
  if (type === 'photo') renderPhotoList();
  else if (type === 'audio') renderAudioList();
  else if (type === 'video') renderVideoList();
  else if (type === 'contact') renderContactList();
}

// ============ AUDIO ============
function initAudioWave() {
  const w = document.getElementById('audioWave'); let html = '';
  for (let i = 0; i < 30; i++) {
    const d = (Math.random() * 0.8 + 0.2).toFixed(2);
    html += '<div class="audio-wave-bar" style="animation-delay:' + d + 's"></div>';
  }
  w.innerHTML = html;
}
async function toggleAudio() {
  if (audioState === 'idle') startAudioRecording();
  else stopAudioRecording();
}
async function startAudioRecording() {
  try {
    audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioRecorder = new MediaRecorder(audioStream);
    audioChunks = []; audioTranscript = '';
    document.getElementById('audioTranscript').textContent = '';
    document.getElementById('audioTranscript').classList.remove('idle');
    audioRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
    audioRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      if (currentExpo) {
        const filePath = await uploadMedia(blob, 'audio', 'webm');
        await dbInsert('audios', {
          expo_id: currentExpo.id,
          user_id: currentUser.id,
          file_path: filePath,
          duration: audioSeconds,
          transcript: audioTranscript
        });
        showToast('录音已保存'); renderAudioList();
      }
      audioStream.getTracks().forEach(t => t.stop());
      audioStream = null; audioRecorder = null; audioChunks = [];
    };
    audioRecorder.start(1000);
    audioSpeechRec = createSpeechRec((final, interim) => {
      audioTranscript = final;
      document.getElementById('audioTranscript').textContent = final + interim;
      document.getElementById('audioTranscript').scrollTop = 99999;
    });
    if (audioSpeechRec) { audioSpeechRec._keepAlive = true; try { audioSpeechRec.start() } catch(e) {} }
    audioState = 'recording'; audioSeconds = 0;
    document.getElementById('audioRecBtn').classList.add('recording');
    document.getElementById('audioPauseBtn').style.display = 'flex';
    document.getElementById('audioWave').classList.add('active');
    document.getElementById('audioStatus').textContent = '录音中...';
    audioInterval = setInterval(() => { audioSeconds++; document.getElementById('audioTimer').textContent = fmtDuration(audioSeconds); }, 1000);
  } catch(e) { showToast('无法访问麦克风: ' + e.message); }
}
function pauseAudio() {
  if (!audioRecorder) return;
  if (audioState === 'recording') {
    audioRecorder.pause(); audioState = 'paused';
    clearInterval(audioInterval);
    document.getElementById('audioStatus').textContent = '已暂停';
    document.getElementById('audioWave').classList.remove('active');
    document.getElementById('audioPauseBtn').innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
  } else if (audioState === 'paused') {
    audioRecorder.resume(); audioState = 'recording';
    document.getElementById('audioStatus').textContent = '录音中...';
    document.getElementById('audioWave').classList.add('active');
    document.getElementById('audioPauseBtn').innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>';
    audioInterval = setInterval(() => { audioSeconds++; document.getElementById('audioTimer').textContent = fmtDuration(audioSeconds); }, 1000);
  }
}
function stopAudioRecording() {
  if (audioRecorder && audioRecorder.state !== 'inactive') audioRecorder.stop();
  if (audioSpeechRec) { audioSpeechRec._keepAlive = false; try { audioSpeechRec.stop() } catch(e) {} audioSpeechRec = null; }
  clearInterval(audioInterval);
  audioState = 'idle'; audioSeconds = 0;
  document.getElementById('audioTimer').textContent = '00:00';
  document.getElementById('audioStatus').textContent = '点击开始录音';
  document.getElementById('audioRecBtn').classList.remove('recording');
  document.getElementById('audioPauseBtn').style.display = 'none';
  document.getElementById('audioWave').classList.remove('active');
  document.getElementById('audioTranscript').classList.add('idle');
}
async function renderAudioList() {
  if (!currentExpo) return;
  const audios = await dbGetByExpo('audios', currentExpo.id);
  const c = document.getElementById('audioList');
  if (audios.length === 0) { c.innerHTML = '<div style="text-align:center;color:var(--text3);font-size:13px;padding:16px 0">该展会暂无录音</div>'; return; }
  let html = '<div style="margin-top:16px;font-size:13px;font-weight:600;color:var(--text2);margin-bottom:8px">录音列表 (' + audios.length + ')</div>';
  audios.forEach(a => {
    const hasT = a.transcript && a.transcript.trim();
    const canEditA = isOwner(a);
    html += '<div class="record-item" onclick="playAudio(\\'' + a.id + '\\')" style="flex-wrap:wrap">' +
      '<div class="record-item-thumb"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg></div>' +
      '<div class="record-item-info"><div class="record-item-title">录音 ' + fmtDuration(a.duration || 0) + (hasT ? '<span class="transcript-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>已转写</span>' : '') + '</div><div class="record-item-meta">' + fmtDate(a.created_at) + '</div>' + (hasT ? '<div class="record-item-transcript">' + esc(a.transcript) + '</div>' : '') + '</div>' +
      (canEditA ? '<button class="edit-transcript-btn" onclick="event.stopPropagation();editTranscript(\\'audios\\',\\'' + a.id + '\\')" title="编辑转写"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg></button>' : '') +
      (canEditA ? '<button class="record-item-del" onclick="event.stopPropagation();deleteRecord(\\'audios\\',\\'' + a.id + '\\',\\'audio\\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg></button>' : '') +
    '</div>';
  });
  c.innerHTML = html;
}
async function playAudio(id) {
  const audios = await dbGetByExpo('audios', currentExpo.id);
  const a = audios.find(x => x.id === id); if (!a) return;
  const url = getMediaUrl(a.file_path);
  const overlay = document.getElementById('mediaViewOverlay');
  document.getElementById('mediaViewImg').style.display = 'none';
  document.getElementById('mediaViewVideo').style.display = 'none';
  const aud = document.getElementById('mediaViewAudio');
  aud.src = url; aud.style.display = 'block'; aud.play();
  overlay.classList.add('show');
}

// ============ VIDEO ============
async function startVideoStream() {
  try {
    if (videoStream) stopVideoStream();
    videoStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: videoFacing, width: { ideal: 1920 }, height: { ideal: 1080 } }, audio: true });
    document.getElementById('videoPreview').srcObject = videoStream;
    renderVideoList();
  } catch(e) { showToast('无法访问摄像头: ' + e.message); }
}
function stopVideoStream() {
  if (videoStream) { videoStream.getTracks().forEach(t => t.stop()); videoStream = null; }
  document.getElementById('videoPreview').srcObject = null;
}
function switchVideoCamera() {
  videoFacing = videoFacing === 'environment' ? 'user' : 'environment';
  if (videoState !== 'idle') return;
  startVideoStream();
}
function toggleVideo() {
  if (videoState === 'idle') startVideoRecording();
  else stopVideoRecording();
}
function startVideoRecording() {
  if (!videoStream) return;
  try {
    videoRecorder = new MediaRecorder(videoStream, { mimeType: 'video/webm;codecs=vp8,opus' });
  } catch(e) {
    try { videoRecorder = new MediaRecorder(videoStream); } catch(e2) { showToast('不支持视频录制'); return; }
  }
  videoChunks = []; videoTranscript = '';
  document.getElementById('videoTranscript').textContent = '';
  document.getElementById('videoTranscript').classList.remove('idle');
  videoRecorder.ondataavailable = e => { if (e.data.size > 0) videoChunks.push(e.data); };
  videoRecorder.onstop = async () => {
    const blob = new Blob(videoChunks, { type: videoRecorder.mimeType || 'video/webm' });
    if (currentExpo) {
      const filePath = await uploadMedia(blob, 'video', 'webm');
      await dbInsert('videos', {
        expo_id: currentExpo.id,
        user_id: currentUser.id,
        file_path: filePath,
        duration: videoSeconds,
        transcript: videoTranscript
      });
      showToast('录像已保存'); renderVideoList();
    }
    videoChunks = []; videoRecorder = null;
  };
  videoRecorder.start(1000);
  videoSpeechRec = createSpeechRec((final, interim) => {
    videoTranscript = final;
    document.getElementById('videoTranscript').textContent = final + interim;
    document.getElementById('videoTranscript').scrollTop = 99999;
  });
  if (videoSpeechRec) { videoSpeechRec._keepAlive = true; try { videoSpeechRec.start() } catch(e) {} }
  videoState = 'recording'; videoSeconds = 0;
  document.getElementById('videoRecBtn').classList.add('recording');
  document.getElementById('videoTimerDisplay').style.opacity = '1';
  videoInterval = setInterval(() => { videoSeconds++; document.getElementById('videoTimerDisplay').textContent = fmtDuration(videoSeconds); }, 1000);
}
function stopVideoRecording() {
  if (videoRecorder && videoRecorder.state !== 'inactive') videoRecorder.stop();
  if (videoSpeechRec) { videoSpeechRec._keepAlive = false; try { videoSpeechRec.stop() } catch(e) {} videoSpeechRec = null; }
  clearInterval(videoInterval);
  videoState = 'idle'; videoSeconds = 0;
  document.getElementById('videoRecBtn').classList.remove('recording');
  document.getElementById('videoTimerDisplay').style.opacity = '0';
  document.getElementById('videoTimerDisplay').textContent = '00:00';
  document.getElementById('videoTranscript').classList.add('idle');
}
async function renderVideoList() {
  if (!currentExpo) return;
  const videos = await dbGetByExpo('videos', currentExpo.id);
  const c = document.getElementById('videoList');
  if (videos.length === 0) { c.innerHTML = '<div style="text-align:center;color:var(--text3);font-size:13px;padding:16px 0">该展会暂无录像</div>'; return; }
  let html = '<div style="margin-top:8px;font-size:13px;font-weight:600;color:var(--text2);margin-bottom:8px">录像列表 (' + videos.length + ')</div>';
  videos.forEach(v => {
    const hasT = v.transcript && v.transcript.trim();
    const canEditV = isOwner(v);
    html += '<div class="record-item" onclick="playVideo(\\'' + v.id + '\\')" style="flex-wrap:wrap">' +
      '<div class="record-item-thumb"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg></div>' +
      '<div class="record-item-info"><div class="record-item-title">录像 ' + fmtDuration(v.duration || 0) + (hasT ? '<span class="transcript-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>已转写</span>' : '') + '</div><div class="record-item-meta">' + fmtDate(v.created_at) + '</div>' + (hasT ? '<div class="record-item-transcript">' + esc(v.transcript) + '</div>' : '') + '</div>' +
      (canEditV ? '<button class="edit-transcript-btn" onclick="event.stopPropagation();editTranscript(\\'videos\\',\\'' + v.id + '\\')" title="编辑转写"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg></button>' : '') +
      (canEditV ? '<button class="record-item-del" onclick="event.stopPropagation();deleteRecord(\\'videos\\',\\'' + v.id + '\\',\\'video\\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg></button>' : '') +
    '</div>';
  });
  c.innerHTML = html;
}
async function playVideo(id) {
  const videos = await dbGetByExpo('videos', currentExpo.id);
  const v = videos.find(x => x.id === id); if (!v) return;
  const url = getMediaUrl(v.file_path);
  const overlay = document.getElementById('mediaViewOverlay');
  document.getElementById('mediaViewImg').style.display = 'none';
  document.getElementById('mediaViewAudio').style.display = 'none';
  const vid = document.getElementById('mediaViewVideo');
  vid.src = url; vid.style.display = 'block'; vid.play();
  overlay.classList.add('show');
}

// ============ CONTACTS ============
function showNewContactModal() {
  showModal('新增对话记录',
    '<div class="form-group"><label class="form-label">姓名 *</label><input class="form-input" id="contactName" placeholder="对方姓名"></div>' +
    '<div class="form-group"><label class="form-label">公司</label><input class="form-input" id="contactCompany" placeholder="所属公司/机构"></div>' +
    '<div class="form-group"><label class="form-label">职位</label><input class="form-input" id="contactPosition" placeholder="职位/头衔"></div>' +
    '<div class="form-group"><label class="form-label">联系方式</label><input class="form-input" id="contactPhone" placeholder="电话/微信/邮箱"></div>' +
    '<div class="form-group"><label class="form-label">交流要点</label><textarea class="form-input" id="contactNotes" placeholder="交流内容、合作意向、关注点等" rows="4"></textarea></div>' +
    '<button class="form-btn" onclick="saveNewContact()">保存</button>'
  );
}
async function saveNewContact() {
  const name = document.getElementById('contactName').value.trim();
  if (!name) { showToast('请输入姓名'); return; }
  if (!currentExpo) { showToast('请先选择展会'); return; }
  await dbInsert('contacts', {
    expo_id: currentExpo.id,
    user_id: currentUser.id,
    name,
    company: document.getElementById('contactCompany').value.trim(),
    position: document.getElementById('contactPosition').value.trim(),
    phone: document.getElementById('contactPhone').value.trim(),
    notes: document.getElementById('contactNotes').value.trim()
  });
  closeModal(); showToast('对话记录已保存'); renderContactList();
}
async function renderContactList() {
  if (!currentExpo) return;
  const contacts = await dbGetByExpo('contacts', currentExpo.id);
  const c = document.getElementById('contactListContainer');
  if (contacts.length === 0) {
    c.innerHTML = '<div class="empty-state"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg><h3>暂无对话记录</h3><p>点击右下角 + 按钮记录与展商/嘉宾的交流</p></div>';
    return;
  }
  let html = '<div class="section-header"><h2>对话记录</h2><span style="font-size:13px;color:var(--text3)">' + contacts.length + '条</span></div>';
  contacts.forEach(ct => { html += renderContactCard(ct); });
  c.innerHTML = html;
}
function renderContactCard(c) {
  const initials = c.name.charAt(0);
  const canEditC = isOwner(c);
  return '<div class="contact-card">' +
    '<div class="contact-card-header">' +
      '<div class="contact-avatar">' + initials + '</div>' +
      '<div><div class="contact-name">' + esc(c.name) + '</div>' + (c.company ? '<div class="contact-company">' + esc(c.company) + (c.position ? ' \\u00b7 ' + esc(c.position) : '') + '</div>' : '') + '</div>' +
    '</div>' +
    (c.phone ? '<div class="contact-details"><div class="contact-detail"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg><span>' + esc(c.phone) + '</span></div></div>' : '') +
    (c.notes ? '<div class="contact-notes">' + esc(c.notes).replace(/\\n/g, '<br>') + '</div>' : '') +
    (canEditC ? '<div class="contact-card-actions"><button style="background:var(--bg);color:var(--danger)" onclick="deleteRecord(\\'contacts\\',\\'' + c.id + '\\',\\'contact\\')">删除</button></div>' : '') +
  '</div>';
}

// ============ PHOTO STAR TOGGLE ============
async function togglePhotoStar(id) {
  const photos = await dbGetByExpo('photos', currentExpo.id);
  const p = photos.find(x => x.id === id); if (!p) return;
  await dbUpdate('photos', id, { important: !p.important });
  renderPhotoList();
}
async function togglePhotoStarDetail(pid, expoId) {
  const photos = await dbGetByExpo('photos', expoId);
  const p = photos.find(x => x.id === pid); if (!p) return;
  await dbUpdate('photos', pid, { important: !p.important });
  showExpoDetail(expoId);
}

// ============ TRANSCRIPT EDIT ============
async function editTranscript(table, id) {
  const items = await dbGetAll(table);
  const item = items.find(x => x.id === id); if (!item) return;
  showModal('编辑转写文本',
    '<div class="form-group"><label class="form-label">转写内容</label><textarea class="form-input" id="editTranscriptText" rows="8" placeholder="在此输入或编辑语音转写文本">' + esc(item.transcript || '') + '</textarea></div>' +
    '<button class="form-btn" onclick="saveTranscript(\\'' + table + '\\',\\'' + id + '\\')">保存</button>'
  );
}
async function saveTranscript(table, id) {
  await dbUpdate(table, id, { transcript: document.getElementById('editTranscriptText').value });
  closeModal(); showToast('转写已更新');
  if (table === 'audios') renderAudioList();
  else renderVideoList();
}

// ============ MEDIA VIEW ============
async function viewMedia(type, id) {
  const overlay = document.getElementById('mediaViewOverlay');
  document.getElementById('mediaViewImg').style.display = 'none';
  document.getElementById('mediaViewVideo').style.display = 'none';
  document.getElementById('mediaViewAudio').style.display = 'none';
  if (type === 'image') {
    const photos = await dbGetAll('photos');
    const p = photos.find(x => x.id === id); if (!p) return;
    const img = document.getElementById('mediaViewImg');
    img.src = getMediaUrl(p.file_path); img.style.display = 'block';
  } else if (type === 'video') {
    const videos = await dbGetAll('videos');
    const v = videos.find(x => x.id === id); if (!v) return;
    const vid = document.getElementById('mediaViewVideo');
    vid.src = getMediaUrl(v.file_path); vid.style.display = 'block'; vid.play();
  } else if (type === 'audio') {
    const audios = await dbGetAll('audios');
    const a = audios.find(x => x.id === id); if (!a) return;
    const aud = document.getElementById('mediaViewAudio');
    aud.src = getMediaUrl(a.file_path); aud.style.display = 'block'; aud.play();
  }
  overlay.classList.add('show');
}
function closeMediaView() {
  const overlay = document.getElementById('mediaViewOverlay');
  overlay.classList.remove('show');
  document.getElementById('mediaViewVideo').pause();
  document.getElementById('mediaViewAudio').pause();
}

// ============ EXPORT TO WORD ============
function showExportProgress(msg) {
  let el = document.getElementById('exportProgress');
  if (!el) { el = document.createElement('div'); el.id = 'exportProgress'; el.className = 'export-progress'; document.body.appendChild(el); }
  el.innerHTML = '<div class="export-progress-spinner"></div><div class="export-progress-text">' + msg + '</div>';
  el.style.display = 'flex';
}
function hideExportProgress() { const el = document.getElementById('exportProgress'); if (el) el.style.display = 'none'; }

function blobToArrayBuffer(blob) { return new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsArrayBuffer(blob); }); }

const STOP_WORDS = new Set('的了是在我有和就不人都一个上也这到说要会可以你那我们他她它为对从而与被让给把比更很已所又或者之其如果因为但是然而虽然如何什么怎么哪里什么时候为什么可能应该需要能够这个那个这些那些自己他们我们你们大家没有不是已经正在可以还是以及关于通过进行表示'.split(''));

function extractKeywords(texts) {
  const combined = texts.join(' ');
  const segments = combined.replace(/[，。！？、；：""''（）\\[\\]【】\\s\\n\\r,.!?;:'"()\\-]/g, ' ').split(/\\s+/).filter(w => w.length >= 2 && w.length <= 8 && !STOP_WORDS.has(w));
  const freq = {};
  segments.forEach(w => { freq[w] = (freq[w] || 0) + 1; });
  return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 15).map(e => ({ word: e[0], count: e[1] }));
}

async function exportExpo(id) {
  const ex = allExpos.find(e => e.id === id); if (!ex) return;
  showExportProgress('正在准备数据...');

  try {
    const photos = await dbGetByExpo('photos', id);
    const audios = await dbGetByExpo('audios', id);
    const videos = await dbGetByExpo('videos', id);
    const contacts = await dbGetByExpo('contacts', id);

    const impPhotos = photos.filter(p => p.important);
    const exportPhotos = impPhotos.length > 0 ? impPhotos : photos;

    const allTexts = [];
    audios.forEach(a => { if (a.transcript) allTexts.push(a.transcript); });
    videos.forEach(v => { if (v.transcript) allTexts.push(v.transcript); });
    contacts.forEach(c => { if (c.notes) allTexts.push(c.notes); if (c.company) allTexts.push(c.company); });

    const timeline = [];
    exportPhotos.forEach(p => timeline.push({ type: 'photo', data: p, time: new Date(p.created_at).getTime() }));
    audios.forEach(a => timeline.push({ type: 'audio', data: a, time: new Date(a.created_at).getTime() }));
    videos.forEach(v => timeline.push({ type: 'video', data: v, time: new Date(v.created_at).getTime() }));
    contacts.forEach(c => timeline.push({ type: 'contact', data: c, time: new Date(c.created_at).getTime() }));
    timeline.sort((a, b) => a.time - b.time);

    const keywords = extractKeywords(allTexts);
    const companies = [...new Set(contacts.filter(c => c.company).map(c => c.company))];

    showExportProgress('正在生成Word文档...');

    const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle, ImageRun, TableOfContents } = docx;

    const PRIMARY = '1a365d';
    const ACCENT = 'e8a838';

    const heading = (text, level = HeadingLevel.HEADING_1) => new Paragraph({ heading: level, spacing: { before: 300, after: 150 }, children: [new TextRun({ text, bold: true, color: PRIMARY, font: 'Microsoft YaHei', size: level === HeadingLevel.HEADING_1 ? 32 : level === HeadingLevel.HEADING_2 ? 26 : 22 })] });

    const bodyText = (text, opts = {}) => new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text, font: 'Microsoft YaHei', size: 21, ...opts })] });

    const bulletPoint = (text, opts = {}) => new Paragraph({ bullet: { level: 0 }, spacing: { after: 80 }, children: [new TextRun({ text, font: 'Microsoft YaHei', size: 21, ...opts })] });

    const sections = [];

    // COVER PAGE
    const coverChildren = [
      new Paragraph({ spacing: { before: 2400 }, alignment: AlignmentType.CENTER, children: [] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: ex.name, bold: true, color: PRIMARY, font: 'Microsoft YaHei', size: 52 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: (ex.date || '') + (ex.location ? ' \\u00b7 ' + ex.location : ''), color: '666666', font: 'Microsoft YaHei', size: 24 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300, after: 100 }, children: [new TextRun({ text: '参 展 记 录 报 告', bold: true, color: ACCENT, font: 'Microsoft YaHei', size: 36 })] }),
    ];
    if (ex.description) {
      coverChildren.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [new TextRun({ text: ex.description, color: '888888', font: 'Microsoft YaHei', size: 20, italics: true })] }));
    }
    coverChildren.push(
      new Paragraph({ spacing: { before: 800 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '生成日期: ' + new Date().toLocaleString('zh-CN'), color: '999999', font: 'Microsoft YaHei', size: 18 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: '照片 ' + exportPhotos.length + ' | 录音 ' + audios.length + ' | 录像 ' + videos.length + ' | 对话 ' + contacts.length, color: '999999', font: 'Microsoft YaHei', size: 18 })] })
    );

    // SECTION 1: TREND SUMMARY
    const trendChildren = [heading('一、趋势总结与核心洞察')];
    trendChildren.push(bodyText('本次参展共记录 ' + contacts.length + ' 场对话交流，涉及 ' + companies.length + ' 家企业/机构，拍摄照片 ' + exportPhotos.length + ' 张，录制音频 ' + audios.length + ' 段、视频 ' + videos.length + ' 段。', { bold: true }));

    if (companies.length > 0) {
      trendChildren.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [new TextRun({ text: '接触企业/机构:', bold: true, font: 'Microsoft YaHei', size: 21, color: PRIMARY })] }));
      companies.forEach(c => trendChildren.push(bulletPoint(c)));
    }

    if (keywords.length > 0) {
      trendChildren.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [new TextRun({ text: '高频关键词:', bold: true, font: 'Microsoft YaHei', size: 21, color: PRIMARY })] }));
      const kwText = keywords.map(k => k.word + '(' + k.count + '次)').join('、');
      trendChildren.push(bodyText(kwText));
    }

    if (contacts.length > 0) {
      trendChildren.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [new TextRun({ text: '主要交流议题:', bold: true, font: 'Microsoft YaHei', size: 21, color: PRIMARY })] }));
      contacts.forEach(c => {
        if (c.notes) {
          const summary = c.notes.length > 80 ? c.notes.substring(0, 80) + '...' : c.notes;
          trendChildren.push(bulletPoint(c.name + (c.company ? ' (' + c.company + ')' : '') + '：' + summary));
        }
      });
    }

    // SECTION 2: TIMELINE
    showExportProgress('正在处理时间线...');
    const timelineChildren = [heading('二、参展时间线')];
    timelineChildren.push(bodyText('以下按时间顺序记录本次参展的所有活动内容。'));

    for (const entry of timeline) {
      const timeStr = new Date(entry.time).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });

      if (entry.type === 'photo') {
        timelineChildren.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [
          new TextRun({ text: '\\ud83d\\udcf7 [' + timeStr + '] 照片', bold: true, font: 'Microsoft YaHei', size: 22, color: PRIMARY })
        ] }));
        try {
          const photoBlob = await fetchMediaBlob(entry.data.file_path);
          const ab = await blobToArrayBuffer(photoBlob);
          timelineChildren.push(new Paragraph({ spacing: { after: 120 }, children: [
            new ImageRun({ data: ab, transformation: { width: 400, height: 300 }, type: 'jpg' })
          ] }));
        } catch(e) {
          timelineChildren.push(bodyText('[照片嵌入失败]'));
        }
      } else if (entry.type === 'audio') {
        const a = entry.data;
        timelineChildren.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [
          new TextRun({ text: '\\ud83c\\udf99\\ufe0f [' + timeStr + '] 录音 (' + fmtDuration(a.duration || 0) + ')', bold: true, font: 'Microsoft YaHei', size: 22, color: PRIMARY })
        ] }));
        if (a.transcript && a.transcript.trim()) {
          timelineChildren.push(bodyText('转写内容:', { bold: true, color: '555555' }));
          timelineChildren.push(bodyText(a.transcript));
        } else {
          timelineChildren.push(bodyText('[未转写]', { color: '999999', italics: true }));
        }
      } else if (entry.type === 'video') {
        const v = entry.data;
        timelineChildren.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [
          new TextRun({ text: '\\ud83c\\udfac [' + timeStr + '] 录像 (' + fmtDuration(v.duration || 0) + ')', bold: true, font: 'Microsoft YaHei', size: 22, color: PRIMARY })
        ] }));
        if (v.transcript && v.transcript.trim()) {
          timelineChildren.push(bodyText('转写内容:', { bold: true, color: '555555' }));
          timelineChildren.push(bodyText(v.transcript));
        } else {
          timelineChildren.push(bodyText('[未转写]', { color: '999999', italics: true }));
        }
      } else if (entry.type === 'contact') {
        const ct = entry.data;
        timelineChildren.push(new Paragraph({ spacing: { before: 200, after: 60 }, children: [
          new TextRun({ text: '\\ud83d\\udcac [' + timeStr + '] 对话 — ' + ct.name, bold: true, font: 'Microsoft YaHei', size: 22, color: PRIMARY }),
          ...(ct.company ? [new TextRun({ text: ' (' + ct.company + (ct.position ? ' \\u00b7 ' + ct.position : '') + ')', font: 'Microsoft YaHei', size: 20, color: '666666' })] : [])
        ] }));
        if (ct.phone) timelineChildren.push(bodyText('联系方式: ' + ct.phone, { color: '555555' }));
        if (ct.notes) {
          timelineChildren.push(bodyText('交流要点:', { bold: true, color: '555555' }));
          ct.notes.split('\\n').forEach(line => {
            if (line.trim()) timelineChildren.push(bodyText(line));
          });
        }
      }
    }

    // SECTION 3: COOPERATION & TODO
    showExportProgress('正在生成合作机会...');
    const todoChildren = [heading('三、合作机会筛选与TODO')];

    if (contacts.length === 0) {
      todoChildren.push(bodyText('本次参展暂无对话记录。'));
    } else {
      const sorted = [...contacts].sort((a, b) => (b.notes || '').length - (a.notes || '').length);
      const highPriority = sorted.filter(c => (c.notes || '').length > 30);
      const normalPriority = sorted.filter(c => (c.notes || '').length <= 30);

      if (highPriority.length > 0) {
        todoChildren.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [new TextRun({ text: '\\ud83d\\udd34 重点跟进 (交流内容详细)', bold: true, font: 'Microsoft YaHei', size: 22, color: PRIMARY })] }));
        highPriority.forEach(c => {
          const keyPoint = c.notes ? (c.notes.length > 60 ? c.notes.substring(0, 60) + '...' : c.notes) : '待确认';
          todoChildren.push(bulletPoint('\\u2610 跟进 ' + c.name + (c.company ? ' (' + c.company + ')' : '') + ' — ' + keyPoint));
          if (c.phone) todoChildren.push(bodyText('    联系方式: ' + c.phone, { color: '666666', size: 19 }));
        });
      }

      if (normalPriority.length > 0) {
        todoChildren.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [new TextRun({ text: '\\ud83d\\udfe1 一般跟进', bold: true, font: 'Microsoft YaHei', size: 22, color: PRIMARY })] }));
        normalPriority.forEach(c => {
          const keyPoint = c.notes || '保持联系';
          todoChildren.push(bulletPoint('\\u2610 跟进 ' + c.name + (c.company ? ' (' + c.company + ')' : '') + ' — ' + keyPoint));
          if (c.phone) todoChildren.push(bodyText('    联系方式: ' + c.phone, { color: '666666', size: 19 }));
        });
      }

      todoChildren.push(new Paragraph({ spacing: { before: 300, after: 80 }, children: [new TextRun({ text: '\\ud83d\\udccb 后续行动清单', bold: true, font: 'Microsoft YaHei', size: 22, color: PRIMARY })] }));
      todoChildren.push(bulletPoint('\\u2610 整理所有名片并录入CRM系统'));
      todoChildren.push(bulletPoint('\\u2610 24小时内发送跟进邮件/微信给重点联系人'));
      todoChildren.push(bulletPoint('\\u2610 整理录音/录像转写内容，提取关键信息'));
      todoChildren.push(bulletPoint('\\u2610 撰写参展总结报告提交团队'));
      todoChildren.push(bulletPoint('\\u2610 制定后续合作推进计划及时间表'));
    }

    // BUILD DOCUMENT
    showExportProgress('正在打包文档...');
    const doc = new Document({
      sections: [
        { children: coverChildren },
        { children: trendChildren },
        { children: timelineChildren },
        { children: todoChildren }
      ]
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, '参展记录_' + ex.name + '_' + (ex.date || '未知日期') + '.docx');
    hideExportProgress();
    showToast('Word文档已导出');
  } catch(e) {
    hideExportProgress();
    console.error('Export error:', e);
    showToast('导出失败: ' + e.message);
  }
}

// ============ UTILS ============
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function fmtDuration(sec) { const m = Math.floor(sec / 60).toString().padStart(2, '0'); const s = (sec % 60).toString().padStart(2, '0'); return m + ':' + s; }
function fmtDate(ts) { return new Date(ts).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }); }

// ============ SERVICE WORKER ============
if ('serviceWorker' in navigator) {
  const swCode = "const CACHE='expo-recorder-v1';const ASSETS=['/'];self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))});self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim())});self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{if(resp.status===200){const clone=resp.clone();caches.open(CACHE).then(c=>c.put(e.request,clone))}return resp}).catch(()=>caches.match('/')))});";
  const swBlob = new Blob([swCode], { type: 'application/javascript' });
  const swUrl = URL.createObjectURL(swBlob);
  navigator.serviceWorker.register(swUrl).catch(() => {});
}

// ============ ANDROID INSTALL PROMPT ============
let deferredInstallPrompt = null;
window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  deferredInstallPrompt = e;
  const banner = document.createElement('div');
  banner.id = 'installBanner';
  banner.style.cssText = 'position:fixed;top:calc(var(--safe-top) + var(--header-h) + 8px);left:12px;right:12px;z-index:150;background:linear-gradient(135deg,var(--primary),var(--primary-light));color:#fff;padding:14px 16px;border-radius:14px;display:flex;align-items:center;gap:12px;box-shadow:0 4px 20px rgba(0,0,0,.25);animation:slideDown .4s ease';
  banner.innerHTML = '<div style="flex:1"><div style="font-size:15px;font-weight:600">安装「展记」到桌面</div><div style="font-size:12px;opacity:.8;margin-top:2px">离线可用，体验更流畅</div></div><button id="installBtn" style="background:var(--accent);color:var(--primary-dark);padding:8px 16px;border-radius:10px;font-size:14px;font-weight:600;white-space:nowrap">安装</button><button id="dismissInstall" style="color:rgba(255,255,255,.6);padding:4px;font-size:20px;line-height:1">&times;</button>';
  document.body.appendChild(banner);
  document.getElementById('installBtn').onclick = async () => {
    deferredInstallPrompt.prompt();
    const result = await deferredInstallPrompt.userChoice;
    if (result.outcome === 'accepted') showToast('安装成功');
    banner.remove(); deferredInstallPrompt = null;
  };
  document.getElementById('dismissInstall').onclick = () => banner.remove();
});

// ============ PLATFORM DETECTION & HINTS ============
function detectPlatform() {
  const ua = navigator.userAgent;
  const isIOS = /iPad|iPhone|iPod/.test(ua);
  const isAndroid = /Android/.test(ua);
  const isStandalone = window.matchMedia('(display-mode:standalone)').matches || navigator.standalone;
  if ((isIOS || isAndroid) && !isStandalone && !localStorage.getItem('installHintDismissed')) {
    setTimeout(() => {
      if (isIOS && !deferredInstallPrompt) {
        showToast('点击分享按钮 \\u2192 添加到主屏幕');
      }
      localStorage.setItem('installHintDismissed', '1');
    }, 3000);
  }
}
detectPlatform();
</script>
<style>
@keyframes slideDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
</style>
</body>
</html>"""

with open('/workspace/output/index.html', 'w') as f:
    f.write(html_content)

print(f"Written {len(html_content)} chars")
