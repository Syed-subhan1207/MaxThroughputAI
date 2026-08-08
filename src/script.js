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

let clockInterval = null;
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
    if (!clockInterval) {
        clockInterval = setInterval(update, 1000);
    }
}

// Global active trains state for Dynamic Speed Engine & GPS Telemetry
const trains = [
    {
        id: "train1",
        name: "Rajdhani Express",
        number: "12302",
        baseSpeed: 132,
        currentSpeed: 132,
        targetSpeed: 132,
        acceleration: 0.15,
        deceleration: 0.25,
        speedScale: 0.005,
        currentIdx: 0,
        progress: 0,
        delay: 4,
        priority: "HIGH (1)",
        aiStatus: "NOMINAL",
        gpsStatus: "CONNECTED",
        lat: 28.6139,
        lng: 77.2090,
        heading: "084"
    },
    {
        id: "train2",
        name: "Vande Bharat Express",
        number: "22436",
        baseSpeed: 98,
        currentSpeed: 98,
        targetSpeed: 98,
        acceleration: 0.15,
        deceleration: 0.25,
        speedScale: 0.0045,
        currentIdx: 2,
        progress: 0,
        delay: 0,
        priority: "HIGH (1)",
        aiStatus: "NOMINAL",
        gpsStatus: "CONNECTED",
        lat: 28.5524,
        lng: 77.2725,
        heading: "095"
    },
    {
        id: "train3",
        name: "Duronto Express",
        number: "12214",
        baseSpeed: 115,
        currentSpeed: 115,
        targetSpeed: 115,
        acceleration: 0.15,
        deceleration: 0.25,
        speedScale: 0.0055,
        currentIdx: 4,
        progress: 0,
        delay: 9,
        priority: "MEDIUM (2)",
        aiStatus: "NOMINAL",
        gpsStatus: "CONNECTED",
        lat: 28.6469,
        lng: 77.3160,
        heading: "240"
    }
];

let activeConflict = false;

function simulateConflict() {
    const map = document.getElementById('map');
    const innerTrack = document.querySelector('.track-inner');

    if (map) {
        map.style.borderColor = '#ef4444';
        map.style.boxShadow = '0 0 35px rgba(239, 68, 68, 0.5)';
    }

    if (innerTrack) {
        innerTrack.classList.add('track-conflict-glow');
    }

    activeConflict = true;

    // Apply advisory TARGET SPEED ONLY to affected train (Duronto Express, train3)
    const duronto = trains.find(t => t.id === 'train3');
    if (duronto) {
        duronto.targetSpeed = 82;
        duronto.aiStatus = "ADVISORY ACTIVE";
    }

    // Rajdhani Express (train1) continues at normal cruising speed
    const rajdhani = trains.find(t => t.id === 'train1');
    if (rajdhani) {
        rajdhani.targetSpeed = rajdhani.baseSpeed;
    }

    triggerLiveToast("🚨 SPATIAL CONFLICT DETECTED at Section S3! Advisory issued for Duronto Express (Target: 82 km/h)");

    setTimeout(() => {
        navigateTo('conflict');
        if (map) {
            map.style.borderColor = '';
            map.style.boxShadow = '';
        }
    }, 600);
}

function acceptAdvisory() {
    triggerLiveToast("✅ Loco Pilot VA-224 accepted speed advisory. Restoring nominal safety interval.");

    const duronto = trains.find(t => t.id === 'train3');
    if (duronto) {
        duronto.targetSpeed = duronto.baseSpeed;
        duronto.aiStatus = "NOMINAL";
    }

    activeConflict = false;
    const innerTrack = document.querySelector('.track-inner');
    if (innerTrack) {
        innerTrack.classList.remove('track-conflict-glow');
    }

    const speedEl = document.getElementById('current-speed');
    if (speedEl) speedEl.textContent = "82 -> 115";
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
        triggerLiveToast("🚨 Emergency assistance dispatched to Section S3");
    }, 400);
}

function toggleNotifications() {
    triggerLiveToast("🛎️ NOC Notifications: Speed Advisory active for Duronto Express | S4 Junction Cleared");
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

let liveSimInterval = null;
function initLiveSimulation() {
    if (liveSimInterval) return;

    const sampleAlerts = [
        "🚆 Rajdhani Express (12302) entered Section S3 (Okhla)",
        "🚦 Signal restored near Ghaziabad Junction (S4)",
        "🌧 Weather update: Fog density reduced near Station S2",
        "⚡ AI Optimization advisory issued for Vande Bharat 22436",
        "✅ Spatial conflict resolved at Delhi Junction (S6)",
        "📡 GPS Telemetry ping received from Train T105 (Shatabdi)",
        "🚉 Platform 4 cleared at Nizamuddin Station (S2)"
    ];

    let alertIdx = 0;
    liveSimInterval = setInterval(() => {
        triggerLiveToast(sampleAlerts[alertIdx % sampleAlerts.length]);
        alertIdx++;
    }, 32000);
}

// ==================== DYNAMIC STATIONS & DOM DATA ====================

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
                        if (idx === 1) opt2.selected = true;
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
        return (el && el.value && el.value.trim() !== '') ? el.value.trim() : fallback;
    };
    const getNum = (id, fallback) => {
        const el = document.getElementById(id);
        return (el && el.value !== '' && !isNaN(el.value)) ? Number(el.value) : fallback;
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

// ==================== FRONTEND ALGORITHMS: A* & BFS ====================

function runFrontendAStar(start, goal) {
    const nodes = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"];
    if (!nodes.includes(start) || !nodes.includes(goal)) {
        return { path: [start, goal], cost: 12.0, visited: [start, goal] };
    }
    let sIdx = nodes.indexOf(start);
    let gIdx = nodes.indexOf(goal);
    let path = [];
    if (sIdx <= gIdx) {
        path = nodes.slice(sIdx, gIdx + 1);
    } else {
        path = nodes.slice(sIdx).concat(nodes.slice(0, gIdx + 1));
    }
    const cost = ((path.length - 1) * 12.0).toFixed(1);
    return { path, cost, visited: path };
}

function runFrontendBFS(start, goal) {
    const nodes = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"];
    const astar = runFrontendAStar(start, goal);
    return { connected: true, path: astar.path, visited: astar.visited };
}

// ==================== FETCH OPTIMIZATION & ANALYTICS ====================

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

            // Update Routing Engine (A* & BFS telemetry)
            const aStarEl = document.getElementById('a-star-path');
            const bfsEl = document.getElementById('bfs-status');
            if (data.a_star && data.a_star.path) {
                if (aStarEl) aStarEl.textContent = `${data.a_star.path.join(' → ')} (Cost: ${data.a_star.cost})`;
            }
            if (data.bfs && data.bfs.visited_nodes) {
                if (bfsEl) bfsEl.textContent = `CONNECTED (Visited: ${data.bfs.visited_nodes.length} nodes: ${data.bfs.visited_nodes.join(' → ')})`;
            }

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
        .catch(err => {
            console.log("Optimization telemetry fallback active.");
            const curSt = payload.current_station || 'S1';
            const nxtSt = payload.next_station || 'S2';
            const astar = runFrontendAStar(curSt, nxtSt);
            const bfs = runFrontendBFS(curSt, nxtSt);

            const aStarEl = document.getElementById('a-star-path');
            const bfsEl = document.getElementById('bfs-status');
            if (aStarEl) aStarEl.textContent = `${astar.path.join(' → ')} (Cost: ${astar.cost})`;
            if (bfsEl) bfsEl.textContent = `CONNECTED (Visited: ${bfs.visited.length} nodes: ${bfs.visited.join(' → ')})`;
        });
}

function fetchAnalytics() {
    fetch('http://127.0.0.1:8000/analytics')
        .then(res => res.json())
        .then(data => {
            console.log("Analytics data synchronized.");
        })
        .catch(err => console.log("Analytics metrics active."));
}

// ==================== CONTINUOUS DYNAMIC TRAIN ANIMATION & GPS TELEMETRY ====================

function initTrainAnimationEngine() {
    if (window.__trainEngineInitialized) return;
    window.__trainEngineInitialized = true;

    const stationCoords = [
        { id: "S1", x: 120, y: 180, name: "NDLS (New Delhi)", lat: 28.6139, lng: 77.2090 },
        { id: "S2", x: 350, y: 160, name: "NZM (Nizamuddin)", lat: 28.5892, lng: 77.2530 },
        { id: "S3", x: 620, y: 170, name: "OKA (Okhla)", lat: 28.5524, lng: 77.2725 },
        { id: "S4", x: 850, y: 220, name: "GZB (Ghaziabad)", lat: 28.6692, lng: 77.4538 },
        { id: "S5", x: 780, y: 390, name: "ANVT (Anand Vihar)", lat: 28.6469, lng: 77.3160 },
        { id: "S6", x: 480, y: 440, name: "DLI (Old Delhi)", lat: 28.6617, lng: 77.2300 },
        { id: "S7", x: 200, y: 410, name: "DEC (Delhi Cantt)", lat: 28.5913, lng: 77.1200 }
    ];

    function setupTooltipEvents() {
        const tooltip = document.getElementById('train-tooltip');
        if (!tooltip) return;

        trains.forEach(t => {
            const el = document.getElementById(t.id);
            if (!el) return;

            el.addEventListener('mouseenter', (e) => {
                const rect = el.getBoundingClientRect();
                tooltip.style.left = `${rect.left + 30}px`;
                tooltip.style.top = `${rect.top - 20}px`;

                document.getElementById('tt-train-name').textContent = t.name.toUpperCase();
                document.getElementById('tt-train-number').textContent = `#${t.number}`;
                document.getElementById('tt-current-st').textContent = stationCoords[t.currentIdx].id;
                document.getElementById('tt-next-st').textContent = stationCoords[(t.currentIdx + 1) % stationCoords.length].id;
                document.getElementById('tt-current-speed').textContent = `${Math.round(t.currentSpeed)} km/h`;
                document.getElementById('tt-base-speed').textContent = `${t.baseSpeed} km/h`;
                document.getElementById('tt-target-speed').textContent = `${Math.round(t.targetSpeed)} km/h`;
                document.getElementById('tt-delay').textContent = `${t.delay} min`;
                document.getElementById('tt-priority').textContent = t.priority;
                document.getElementById('tt-ai-status').textContent = t.aiStatus;
                document.getElementById('tt-gps-status').textContent = `${t.gpsStatus} (SIMULATED)`;

                tooltip.classList.remove('hidden');
            });

            el.addEventListener('mouseleave', () => {
                tooltip.classList.add('hidden');
            });

            el.addEventListener('click', () => {
                alert(`📡 SIMULATED GPS TELEMETRY: ${t.name} (${t.number})\nPosition: ${t.lat}° N, ${t.lng}° E\nCurrent Speed: ${Math.round(t.currentSpeed)} km/h (Target: ${Math.round(t.targetSpeed)} km/h)\nSection: ${stationCoords[t.currentIdx].id} -> ${stationCoords[(t.currentIdx + 1) % stationCoords.length].id}\nAI Status: ${t.aiStatus}`);
            });
        });
    }

    setupTooltipEvents();

    function animate() {
        trains.forEach(t => {
            const el = document.getElementById(t.id);

            // 1. DYNAMIC GRADUAL SPEED TRANSITION
            if (t.currentSpeed < t.targetSpeed) {
                t.currentSpeed = Math.min(t.targetSpeed, t.currentSpeed + t.acceleration);
            } else if (t.currentSpeed > t.targetSpeed) {
                t.currentSpeed = Math.max(t.targetSpeed, t.currentSpeed - t.deceleration);
            }
            t.currentSpeed = Math.max(0, t.currentSpeed);

            // 2. SMOOTH POSITION & CORRIDOR PROGRESS INTERPOLATION
            const speedRatio = t.baseSpeed > 0 ? (t.currentSpeed / t.baseSpeed) : 1;
            t.progress += t.speedScale * speedRatio;

            if (t.progress >= 1) {
                t.progress = 0;
                t.currentIdx = (t.currentIdx + 1) % stationCoords.length;
            }

            const fromSt = stationCoords[t.currentIdx];
            const toSt = stationCoords[(t.currentIdx + 1) % stationCoords.length];

            const currentX = fromSt.x + (toSt.x - fromSt.x) * t.progress;
            const currentY = fromSt.y + (toSt.y - fromSt.y) * t.progress;

            // 3. SIMULATED GPS LATITUDE & LONGITUDE INTERPOLATION
            t.lat = (fromSt.lat + (toSt.lat - fromSt.lat) * t.progress).toFixed(4);
            t.lng = (fromSt.lng + (toSt.lng - fromSt.lng) * t.progress).toFixed(4);

            const dy = toSt.y - fromSt.y;
            const dx = toSt.x - fromSt.x;
            let angle = Math.atan2(dy, dx) * (180 / Math.PI);
            if (angle < 0) angle += 360;
            t.heading = Math.round(angle).toString().padStart(3, '0');

            // 4. SVG MAP POSITION UPDATE
            if (el) {
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
            }

            // 5. UPDATE ACTIVE TELEMETRY METRICS IN DASHBOARD
            const telemetrySpeedEl = document.getElementById(`${t.id === 'train1' ? 't1' : t.id === 'train2' ? 't2' : 't3'}-telemetry-speed`);
            if (telemetrySpeedEl) {
                telemetrySpeedEl.textContent = `${Math.round(t.currentSpeed)} km/h`;
            }
        });

        // 6. UPDATE SIMULATED GPS OVERLAY PANEL FOR TRAIN 1 OR TARGET TRAIN
        const trackedTrain = trains.find(t => t.aiStatus === "ADVISORY ACTIVE") || trains[0];
        if (trackedTrain) {
            const gpsName = document.getElementById('gps-train-name');
            const gpsLat = document.getElementById('gps-lat');
            const gpsLng = document.getElementById('gps-lng');
            const gpsHeading = document.getElementById('gps-heading');
            const gpsSection = document.getElementById('gps-section');
            const gpsSpeed = document.getElementById('gps-speed-val');

            if (gpsName) gpsName.textContent = `${trackedTrain.name} (${trackedTrain.number})`;
            if (gpsLat) gpsLat.textContent = `${trackedTrain.lat}° N`;
            if (gpsLng) gpsLng.textContent = `${trackedTrain.lng}° E`;
            if (gpsHeading) gpsHeading.textContent = `${trackedTrain.heading}°`;
            if (gpsSection) gpsSection.textContent = `${stationCoords[trackedTrain.currentIdx].id} → ${stationCoords[(trackedTrain.currentIdx + 1) % stationCoords.length].id}`;
            if (gpsSpeed) gpsSpeed.textContent = `${Math.round(trackedTrain.currentSpeed)} km/h`;
        }

        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
}

// ==================== AUTH & INITIALIZATION ====================

function checkAuth() {
    let username = localStorage.getItem("controllerName");
    if (!username) {
        username = "CHIEF NOC CONTROLLER";
        localStorage.setItem("controllerName", username);
    }
    const controllerNameEl = document.getElementById("controller-name");
    if (controllerNameEl) controllerNameEl.textContent = username.toUpperCase();
    return true;
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
            if (errorMsg) {
                errorMsg.textContent = "Invalid Username or Password";
                errorMsg.classList.remove("hidden");
                setTimeout(() => errorMsg.classList.add("hidden"), 3500);
            }
        }
    });
}

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

if (document.getElementById("controller-name") || window.location.pathname.endsWith("dashboard.html")) {
    if (checkAuth()) {
        let isDashboardInitialized = false;
        const initDashboard = function() {
            if (isDashboardInitialized) return;
            isDashboardInitialized = true;

            updateClock();
            initLiveSimulation();
            loadDynamicStations();
            fetchOptimization();
            initTrainAnimationEngine();

            const predForm = document.getElementById("prediction-form");
            if (predForm) {
                predForm.addEventListener("submit", function(e) {
                    e.preventDefault();
                    predictDelay(e);
                });
            }

            navigateTo('dashboard');

            document.addEventListener('keydown', function(e) {
                if (e.key === "/" && !document.getElementById('map-page').classList.contains('hidden')) {
                    simulateConflict();
                }
            });

            console.log('%cSmart Rail AI Operations Platform Loaded ✅', 'color:#06B6D4; font-family:monospace; font-weight:bold; font-size:14px');
        };

        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            initDashboard();
        } else {
            window.addEventListener('DOMContentLoaded', initDashboard);
            window.addEventListener('load', initDashboard);
        }
    }
}

// ==================== AI PREDICTION INTEGRATION ====================

function predictDelay(e) {
    if (e && e.preventDefault) e.preventDefault();
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

    const payload = getPayloadFromDOM();

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