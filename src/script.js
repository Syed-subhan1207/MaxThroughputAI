// script.js - Final Integrated NOC Control Operations Script

// ==================== GLOBAL NAVIGATION & UTILITIES ====================

function navigateTo(page) {
    document.querySelectorAll('#main-content > div').forEach(div => {
        div.classList.add('hidden');
    });
   
    const target = document.getElementById(page + '-page');
    if (target) target.classList.remove('hidden');
   
    // Update active nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(`'${page}'`)) {
            item.classList.add('active');
        }
    });

    if (page === 'analytics') {
        fetchAnalytics();
    }
}

function updateClock() {
    const timeEl = document.getElementById('current-time');
    if (!timeEl) return;
    
    const update = () => {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        let seconds = now.getSeconds();
        let ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        
        const hStr = hours < 10 ? '0' + hours : hours;
        const mStr = minutes < 10 ? '0' + minutes : minutes;
        const sStr = seconds < 10 ? '0' + seconds : seconds;
        
        timeEl.textContent = `${hStr}:${mStr}:${sStr} ${ampm}`;
    };
    
    update();
    setInterval(update, 1000);
}

function simulateConflict() {
    const map = document.getElementById('map');
    if (!map) return;
    
    map.style.borderColor = '#ef4444';
    map.style.boxShadow = '0 0 35px rgba(239, 68, 68, 0.4)';
   
    setTimeout(() => {
        alert("🚨 SPATIAL CONFLICT DETECTED\n\nRajdhani Express (130km/h) and Duronto Express (108km/h) approaching Section S3.\nAI Optimization Engine issued priority advisory.");
        navigateTo('conflict');
        map.style.borderColor = '';
        map.style.boxShadow = '';
    }, 800);
}

let currentSpeed = 118;

function acceptAdvisory() {
    alert("✅ Advisory accepted by Loco Pilot.\nSpeed reduction initiated to 82 km/h.");
    currentSpeed = 82;
    const speedEl = document.getElementById('current-speed');
    if (speedEl) speedEl.textContent = currentSpeed;
    triggerLiveToast("✅ Loco Pilot VA-224 accepted speed reduction advisory to 82 km/h");
}

function showAssistancePopup() {
    const popup = document.getElementById('assistance-popup');
    if (!popup) return;
    
    popup.classList.remove('hidden');
   
    const reasonsHTML = `
        <div onclick="selectReason(this)" class="reason-option p-4 hover:bg-slate-800/90 rounded-2xl cursor-pointer flex items-center gap-3 border border-slate-800 transition-all">
            <span class="text-xl">🛤️</span>
            <span class="font-medium text-slate-200">Obstacle on Track</span>
        </div>
        <div onclick="selectReason(this)" class="reason-option p-4 hover:bg-slate-800/90 rounded-2xl cursor-pointer flex items-center gap-3 border border-slate-800 transition-all">
            <span class="text-xl">🛑</span>
            <span class="font-medium text-slate-200">Brake Malfunction</span>
        </div>
        <div onclick="selectReason(this)" class="reason-option p-4 hover:bg-slate-800/90 rounded-2xl cursor-pointer flex items-center gap-3 border border-slate-800 transition-all">
            <span class="text-xl">🌫️</span>
            <span class="font-medium text-slate-200">Poor Visibility</span>
        </div>
        <div onclick="selectReason(this)" class="reason-option p-4 hover:bg-slate-800/90 rounded-2xl cursor-pointer flex items-center gap-3 border border-slate-800 transition-all">
            <span class="text-xl">🚦</span>
            <span class="font-medium text-slate-200">Signal Issue</span>
        </div>
    `;
    const container = document.getElementById('reason-options');
    if (container) container.innerHTML = reasonsHTML;
}

function selectReason(el) {
    document.querySelectorAll('.reason-option').forEach(opt => {
        opt.style.backgroundColor = '';
        opt.style.borderColor = 'rgba(31, 41, 55, 0.8)';
    });
    el.style.backgroundColor = '#1e293b';
    el.style.borderColor = '#06B6D4';
}

function hideAssistancePopup() {
    const popup = document.getElementById('assistance-popup');
    if (popup) popup.classList.add('hidden');
}

function submitAssistance() {
    hideAssistancePopup();
    setTimeout(() => {
        alert("✅ Assistance request sent to Central Controller.\nController notified. Support team dispatched.");
        triggerLiveToast("🚨 Emergency assistance dispatched to Section S3");
    }, 400);
}

function toggleNotifications() {
    alert("🛎️ 3 New NOC Notifications:\n• Speed Advisory accepted by VA-224\n• Ghaziabad (S4) junction cleared\n• Rain intensity reduced near Okhla (S3)");
}

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}

function showStationInfo(stationId, stationName, platform, weather, activeLoad) {
    const popup = document.getElementById('station-popup');
    const title = document.getElementById('popup-station-title');
    const pf = document.getElementById('popup-platform');
    const w = document.getElementById('popup-weather');
    const l = document.getElementById('popup-load');

    if (title) title.textContent = `${stationId}: ${stationName}`;
    if (pf) pf.textContent = platform;
    if (w) w.textContent = weather;
    if (l) l.textContent = activeLoad;

    if (popup) popup.classList.remove('hidden');
}

// ==================== LIVE TOAST ENGINE ====================

function triggerLiveToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast-item text-xs font-mono text-slate-200 flex items-center gap-3 mb-2 p-3 rounded-xl bg-slate-900/90 border border-cyan-500/40 shadow-xl';
    toast.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-sm shrink-0">
            <i class="fa-solid fa-satellite-dish"></i>
        </div>
        <div class="flex-1">${message}</div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 400);
    }, 5000);
}

function initLiveSimulation() {
    const sampleAlerts = [
        "🚆 Rajdhani Express (12627) entered Section S3 (Okhla)",
        "🚦 Signal restored near Ghaziabad Junction (S4)",
        "🌧 Weather update: Fog density reduced near Station S2",
        "⚡ AI Optimization advisory issued for Vande Bharat 22436",
        "✅ Spatial conflict resolved at Delhi Junction (S6)",
        "📡 GPS Telemetry ping received from Train T105 (Shatabdi)",
        "🚉 Platform 4 cleared at Nizamuddin Station (S2)"
    ];
    
    let alertIdx = 0;
    setInterval(() => {
        triggerLiveToast(sampleAlerts[alertIdx % sampleAlerts.length]);
        alertIdx++;
    }, 32000);
}

// ==================== DYNAMIC DATAINGESTION & STATIONS ====================

function loadDynamicStations() {
    fetch('http://127.0.0.1:8000/stations')
        .then(res => res.json())
        .then(data => {
            if (data.stations && data.stations.length) {
                const currentSelect = document.getElementById('pred-current-station');
                const nextSelect = document.getElementById('pred-next-station');
                if (currentSelect && nextSelect) {
                    currentSelect.innerHTML = '';
                    nextSelect.innerHTML = '';
                    data.stations.forEach((st, idx) => {
    const opt1 = document.createElement("option");
    opt1.value = st;
    opt1.textContent = st;
    currentSelect.appendChild(opt1);

    const opt2 = document.createElement("option");
    opt2.value = st;
    opt2.textContent = st;

    if (idx === 1) {
        opt2.selected = true;
    }

    nextSelect.appendChild(opt2);
});
                }
            }
        })
        .catch(() => {
            console.log("Using default station options.");
        });
}

function getPayloadFromDOM() {
    const getVal = (id, fallback) => {
        const el = document.getElementById(id);
        return el ? el.value : fallback;
    };
    const getNum = (id, fallback) => {
        const el = document.getElementById(id);
        return el ? Number(el.value) : fallback;
    };

    return {
        train_type: getVal('pred-train-type', 'Express'),
        current_station: getVal('pred-current-station', 'S1'),
        next_station: getVal('pred-next-station', 'S2'),
        speed: getNum('pred-speed', 95),
        current_delay: getNum('pred-current-delay', 8),
        weather: getVal('pred-weather', 'Clear'),
        signal_status: getVal('pred-signal-status', 'Green'),
        track_status: getVal('pred-track-status', 'Clear'),
        platform_available: getVal('pred-platform-available', 'Yes'),
        train_priority: getNum('pred-train-priority', 1),
        day_of_week: getVal('pred-day-of-week', 'Monday'),
        hour_of_day: getNum('pred-hour-of-day', 14),
        congestion_level: getVal('pred-congestion-level', 'Low')
    };
}

function fetchOptimization(payload = null) {
    if (!payload) {
        payload = getPayloadFromDOM();
    }
    const url = 'http://127.0.0.1:8000/optimization';
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            const currentDec = document.getElementById('opt-current-decision');
            const optDec = document.getElementById('opt-optimized-decision');
            const timeSaved = document.getElementById('opt-time-saved');
            const throughput = document.getElementById('opt-throughput-gain');
            const conflictProb = document.getElementById('opt-conflict-prob');
            const route = document.getElementById('opt-route');
            const speed = document.getElementById('opt-speed');
            const priority = document.getElementById('opt-signal-priority');
            const strategy = document.getElementById('opt-strategy');

            if (currentDec) currentDec.textContent = data.current_decision;
            if (optDec) optDec.textContent = data.optimized_decision;
            if (timeSaved) timeSaved.textContent = `${data.expected_time_saved_min} min`;
            if (throughput) throughput.textContent = data.expected_throughput_improvement;
            if (conflictProb) conflictProb.textContent = `${data.conflict_probability_pct}%`;
            if (route) route.textContent = data.optimized_route;
            if (speed) speed.textContent = `${data.optimized_speed} km/h`;
            if (priority) priority.textContent = data.suggested_signal_priority;
            if (strategy) strategy.textContent = data.conflict_resolution_strategy;

            // Map Reinforcement Learning Telemetry
            const rlAction = document.getElementById('rl-recommended-action');
            const rlConfidence = document.getElementById('rl-confidence');
            const rlExpectedReward = document.getElementById('rl-expected-reward');
            const rlStability = document.getElementById('rl-policy-stability');
            const rlPolicy = document.getElementById('rl-policy');
            const rlEpisodes = document.getElementById('rl-episodes');
            const rlLr = document.getElementById('rl-learning-rate');
            const rlEpsilon = document.getElementById('rl-epsilon');
            const rlQSize = document.getElementById('rl-q-table-size');

            if (rlAction) rlAction.textContent = data.rl_recommended_action || data.rl_action || 'MOVE';
            if (rlConfidence) rlConfidence.textContent = data.rl_confidence || '85.0%';
            if (rlExpectedReward) rlExpectedReward.textContent = data.expected_reward || '+18.0';
            if (rlStability) rlStability.textContent = data.policy_stability || '80.0%';
            if (rlPolicy) rlPolicy.textContent = data.rl_policy || 'NOMINAL_DISPATCH';
            if (rlEpisodes) rlEpisodes.textContent = data.episodes_trained !== undefined ? data.episodes_trained : '0';
            if (rlLr) rlLr.textContent = data.learning_rate !== undefined ? data.learning_rate : '0.10';
            if (rlEpsilon) rlEpsilon.textContent = data.epsilon !== undefined ? data.epsilon : '0.20';
            if (rlQSize) rlQSize.textContent = data.q_table_size !== undefined ? `${data.q_table_size} states` : '0 states';
        })
        .catch(err => console.log("Optimization telemetry sync active."));
}

function fetchAnalytics() {
    fetch('http://127.0.0.1:8000/analytics')
        .then(res => res.json())
        .then(data => {
            console.log("Analytics data loaded successfully.");
        })
        .catch(err => console.log("Analytics metrics active."));
}

// ==================== CONTINUOUS 7-STATION TRAIN ANIMATION ENGINE ====================

function initTrainAnimationEngine() {
    // 7 Station node coordinates along the track path
    const stationCoords = [
        { id: "S1", x: 120, y: 180, name: "S1: NDLS" },
        { id: "S2", x: 350, y: 160, name: "S2: NZM" },
        { id: "S3", x: 620, y: 170, name: "S3: OKA" },
        { id: "S4", x: 850, y: 220, name: "S4: GZB" },
        { id: "S5", x: 780, y: 390, name: "S5: ANVT" },
        { id: "S6", x: 480, y: 440, name: "S6: DLI" },
        { id: "S7", x: 200, y: 410, name: "S7: DEC" }
    ];

    const trains = [
        { id: "train1", currentIdx: 0, progress: 0, speed: 0.003 },
        { id: "train2", currentIdx: 2, progress: 0, speed: 0.0025 },
        { id: "train3", currentIdx: 4, progress: 0, speed: 0.0035 }
    ];

    function animate() {
        trains.forEach(t => {
            const el = document.getElementById(t.id);
            if (!el) return;

            const fromSt = stationCoords[t.currentIdx];
            const toSt = stationCoords[(t.currentIdx + 1) % stationCoords.length];

            t.progress += t.speed;

            if (t.progress >= 1) {
                t.progress = 0;
                t.currentIdx = (t.currentIdx + 1) % stationCoords.length;
                
                // Station stop trigger: highlight node briefly
                showStationInfo(toSt.id, toSt.name, "PF-1", "Clear Signal", "Active Corridor");
            }

            // Easing position calculation
            const currentX = fromSt.x + (toSt.x - fromSt.x) * t.progress;
            const currentY = fromSt.y + (toSt.y - fromSt.y) * t.progress;

            const circle = el.querySelector('circle');
            const text = el.querySelector('text');

            if (circle) {
                circle.setAttribute('cx', currentX);
                circle.setAttribute('cy', currentY);
            }
            if (text) {
                text.setAttribute('x', currentX - 10);
                text.setAttribute('y', currentY + 4);
            }
        });

        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
}

// ==================== AUTH & INITIALIZATION ====================

function checkAuth() {
    const username = localStorage.getItem("controllerName");
    if (!username) {
        window.location.href = "login.html";
        return false;
    } else {
        const controllerNameEl = document.getElementById("controller-name");
        if (controllerNameEl) controllerNameEl.textContent = username.toUpperCase();
        return true;
    }
}

function showLoadingScreen() {
    const loadingScreen = document.getElementById("loading-screen");
    if (!loadingScreen) return;
    
    loadingScreen.classList.remove("hidden");
   
    const messages = [
        "✓ Authenticating Controller Credentials...",
        "✓ Connecting to FastAPI Backend Hub...",
        "✓ Ingesting Real Railway Operational Data (train_info.csv)...",
        "✓ Initializing LSTM Neural Network Engine...",
        "✓ Loading Reinforcement Learning Optimizer...",
        "✓ Initializing 7-Station Spatial Corridor Map...",
        "✓ NOC Control Dashboard Ready"
    ];
   
    let i = 0;
    const msgContainer = document.getElementById("loading-messages");
    const progressBar = document.getElementById("progress-bar");
    
    if (!msgContainer || !progressBar) return;
    
    msgContainer.innerHTML = '';
    
    const interval = setInterval(() => {
        if (i < messages.length) {
            const div = document.createElement("div");
            div.textContent = messages[i];
            msgContainer.appendChild(div);
            setTimeout(() => { div.style.opacity = 1; div.style.transform = 'translateY(0)'; }, 50);
            i++;
            progressBar.style.width = `${(i / messages.length) * 100}%`;
        } else {
            clearInterval(interval);
            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 800);
        }
    }, 380);
}

// ==================== PAGE LOAD ENTRYPOINTS ====================

if (window.location.pathname.endsWith("login.html") || 
    window.location.pathname === "/" || 
    window.location.pathname.endsWith("/")) {
    
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", function(e) {
            e.preventDefault();
            
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            const errorMsg = document.getElementById("error-msg");
            
            let isValidAuth = false;
            let displayName = username;
            
            if (username === "admin" && password === "admin123") {
                isValidAuth = true;
                displayName = "CHIEF NOC CONTROLLER";
            } else {
                const savedUserStr = localStorage.getItem("registeredUser");
                if (savedUserStr) {
                    try {
                        const savedUser = JSON.parse(savedUserStr);
                        if (savedUser.username === username && savedUser.password === password) {
                            isValidAuth = true;
                            displayName = savedUser.fullname || username;
                        }
                    } catch (e) {}
                }
            }
            
            if (isValidAuth) {
                localStorage.setItem("controllerName", displayName);
                showLoadingScreen();
            } else {
                errorMsg.textContent = "Invalid Username or Password";
                errorMsg.classList.remove("hidden");
                setTimeout(() => errorMsg.classList.add("hidden"), 3500);
            }
        });
    }
}

if (window.location.pathname.endsWith("register.html")) {
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", function(e) {
            e.preventDefault();
            
            const fullname = document.getElementById("reg-fullname") ? document.getElementById("reg-fullname").value.trim() : "";
            const username = document.getElementById("reg-username") ? document.getElementById("reg-username").value.trim() : "";
            const password = document.getElementById("reg-password") ? document.getElementById("reg-password").value : "";
            const confirmPassword = document.getElementById("reg-confirm-password") ? document.getElementById("reg-confirm-password").value : "";
            const errorMsg = document.getElementById("reg-error-msg");
            const errorText = document.getElementById("reg-error-text");
            const successModal = document.getElementById("reg-success-modal");
            
            if (password !== confirmPassword) {
                if (errorText && errorMsg) {
                    errorText.textContent = "Passwords do not match";
                    errorMsg.classList.remove("hidden");
                    setTimeout(() => errorMsg.classList.add("hidden"), 3500);
                }
                return;
            }
            
            const userObj = {
                username: username,
                password: password,
                fullname: fullname
            };
            localStorage.setItem("registeredUser", JSON.stringify(userObj));
            
            if (successModal) {
                successModal.classList.remove("hidden");
                setTimeout(() => {
                    window.location.href = "login.html";
                }, 1800);
            } else {
                alert("Account created successfully!");
                window.location.href = "login.html";
            }
        });
    }
}

if (window.location.pathname.endsWith("dashboard.html")) {
    if (checkAuth()) {
        window.onload = function() {
            updateClock();
            initLiveSimulation();
            loadDynamicStations();
            fetchOptimization();
            initTrainAnimationEngine();
            
            navigateTo('dashboard');
            
            document.addEventListener('keydown', function(e) {
                if (e.key === "/" && !document.getElementById('map-page').classList.contains('hidden')) {
                    simulateConflict();
                }
            });
            
            console.log('%cSmart Rail AI Operations Platform Loaded ✅', 'color:#06B6D4; font-family:monospace; font-weight:bold; font-size:14px');
        };
    }
}

// ==================== AI PREDICTION INTEGRATION ====================

function predictDelay() {
    const btn = document.getElementById('predict-btn');
    const btnText = document.getElementById('predict-btn-text');
    const spinner = document.getElementById('predict-spinner');
    const errorBox = document.getElementById('predict-error');
    const resultCard = document.getElementById('predict-result');

    if (!btn) return;

    errorBox.classList.add('hidden');
    resultCard.classList.add('hidden');

    btn.disabled = true;
    btnText.textContent = 'RUNNING LSTM MODEL & RECEIVING PREDICTION...';
    spinner.classList.remove('hidden');

    const payload = {
        train_type: document.getElementById('pred-train-type').value,
        current_station: document.getElementById('pred-current-station').value,
        next_station: document.getElementById('pred-next-station').value,
        speed: Number(document.getElementById('pred-speed').value),
        current_delay: Number(document.getElementById('pred-current-delay').value),
        weather: document.getElementById('pred-weather').value,
        signal_status: document.getElementById('pred-signal-status').value,
        track_status: document.getElementById('pred-track-status').value,
        platform_available: document.getElementById('pred-platform-available').value,
        train_priority: Number(document.getElementById('pred-train-priority').value),
        day_of_week: document.getElementById('pred-day-of-week').value,
        hour_of_day: Number(document.getElementById('pred-hour-of-day').value),
        congestion_level: document.getElementById('pred-congestion-level').value
    };

    fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(response => {
            if (!response.ok) throw new Error('Server responded with error');
            return response.json();
        })
       .then(data => {
    showPredictionResult(data);

    // Pass LSTM prediction to optimizer
    payload.predicted_delay = data.predicted_delay;

    fetchOptimization(payload);
    fetchAnalytics();
})
        .catch(() => {
            errorBox.classList.remove('hidden');
        })
        .finally(() => {
            btn.disabled = false;
            btnText.textContent = 'RUN LSTM AI DELAY PREDICTION';
            spinner.classList.add('hidden');
        });
}

function showPredictionResult(data) {
    const resultCard = document.getElementById('predict-result');
    const delayValue = document.getElementById('result-delay-value');
    const statusEl = document.getElementById('result-status');
    const recList = document.getElementById('result-recommendations');
    const etaVal = document.getElementById('result-eta-val');

    const predictedDelay = Number(data.predicted_delay);
    delayValue.textContent = predictedDelay.toFixed(2);

    statusEl.textContent = data.delay_status;
    statusEl.className = 'text-xl font-bold font-tech ' + getStatusColorClass(data.delay_status);

    const now = new Date();
    now.setMinutes(now.getMinutes() + Math.round(predictedDelay) + 15);
    let hours = now.getHours();
    let minutes = now.getMinutes();
    let ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    if (etaVal) etaVal.textContent = `${hours}:${minutes < 10 ? '0' : ''}${minutes} ${ampm}`;

    recList.innerHTML = '';
    (data.recommendations || []).forEach(item => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-3 p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-200';
        li.innerHTML = '<span class="text-cyan-400 font-bold mt-0.5">✓</span><span>' + item + '</span>';
        recList.appendChild(li);
    });

    resultCard.classList.remove('hidden');
    triggerLiveToast(`🔮 AI Prediction Completed: ${data.delay_status} (${predictedDelay.toFixed(1)} mins)`);
}

function getStatusColorClass(status) {
    const s = (status || '').toUpperCase();
    if (s.includes('SEVERE') || s.includes('CRITICAL') || s.includes('HIGH')) return 'text-red-400';
    if (s.includes('MODERATE')) return 'text-amber-400';
    if (s.includes('MINOR') || s.includes('LOW') || s.includes('ON TIME')) return 'text-emerald-400';
    return 'text-white';
}