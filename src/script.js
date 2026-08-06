// script.js - Final Combined & Enhanced Operations Center Script

// ==================== GLOBAL FUNCTIONS ====================

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
        alert("🚨 CONFLICT SIMULATED\n\nRajdhani Express (130km/h) and Duronto Express (108km/h) approaching same section.\nAI has already issued advisory.");
        navigateTo('conflict');
        map.style.borderColor = '';
        map.style.boxShadow = '';
    }, 800);
}

let currentSpeed = 118;

function acceptAdvisory() {
    alert("✅ Advisory accepted by Loco Pilot.\nSpeed reduction initiated.");
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
    alert("🛎️ 3 New Notifications:\n• Advisory accepted by VA-224\n• Ghaziabad junction clear\n• Weather update: Rain intensity reduced");
}

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}

function triggerSSOMessage(provider) {
    alert(`ℹ️ ${provider} Single Sign-On (SSO) integration is scheduled for Future Release v2.5.`);
}

// ==================== LIVE TOAST NOTIFICATION ENGINE ====================

function triggerLiveToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast-item text-xs font-mono text-slate-200 flex items-center gap-3';
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
        "🚆 Rajdhani Express (12627) entered Section S3",
        "🚦 Signal restored near Ghaziabad Junction",
        "🌧 Weather update: Fog density reduced near Delhi NCR",
        "⚡ AI Advisory issued for Express 22109",
        "✅ Spatial conflict resolved at Delhi Junction",
        "📡 GPS Telemetry ping received from Vande Bharat 22436",
        "🚉 Platform 4 cleared at Nizamuddin Station"
    ];
    
    let alertIdx = 0;
    setInterval(() => {
        triggerLiveToast(sampleAlerts[alertIdx % sampleAlerts.length]);
        alertIdx++;
    }, 38000);
    
    const weatherStates = [
        { temp: "28°C", vis: "4.8km", wind: "14km/h", hum: "62%", text: "28°C • Delhi NCR", icon: "fa-cloud-sun text-amber-400" },
        { temp: "26°C", vis: "3.5km", wind: "18km/h", hum: "74%", text: "26°C • Light Rain", icon: "fa-cloud-rain text-blue-400" },
        { temp: "24°C", vis: "2.1km", wind: "10km/h", hum: "88%", text: "24°C • Heavy Fog", icon: "fa-smog text-cyan-400" },
        { temp: "29°C", vis: "6.0km", wind: "12km/h", hum: "55%", text: "29°C • Clear Sky", icon: "fa-sun text-amber-300" }
    ];
    
    let wIdx = 0;
    setInterval(() => {
        wIdx = (wIdx + 1) % weatherStates.length;
        const ws = weatherStates[wIdx];
        
        const topText = document.getElementById('top-weather-text');
        const topIcon = document.getElementById('top-weather-icon');
        const sideTemp = document.getElementById('side-weather-temp');
        const sideVis = document.getElementById('side-vis');
        const sideWind = document.getElementById('side-wind');
        const sideHum = document.getElementById('side-hum');
        
        if (topText) topText.textContent = ws.text;
        if (topIcon) topIcon.className = `fa-solid ${ws.icon}`;
        if (sideTemp) sideTemp.textContent = ws.temp;
        if (sideVis) sideVis.textContent = ws.vis;
        if (sideWind) sideWind.textContent = ws.wind;
        if (sideHum) sideHum.textContent = ws.hum;
    }, 45000);

    setInterval(() => {
        const activeEl = document.getElementById('active-trains');
        if (activeEl) {
            const val = 44 + Math.floor(Math.random() * 9);
            activeEl.textContent = val;
        }
    }, 15000);
}

// ==================== AUTH & LOADING ====================

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
        "✓ Authenticating Loco Pilot Credentials...",
        "✓ Connecting to Railway Control Centre FastAPI Backend...",
        "✓ Loading Live Train GPS Telemetry...",
        "✓ Initializing LSTM AI Neural Decision Engine...",
        "✓ Synchronizing Station Signal Matrices...",
        "✓ Starting Live Spatial Monitoring...",
        "✓ Railway NOC Control Dashboard Ready"
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
    }, 420);
}

// ==================== PAGE SPECIFIC INITIALIZATION ====================

// Login Page
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
            
            // 1. Check default admin credentials
            if (username === "admin" && password === "admin123") {
                isValidAuth = true;
                displayName = "ADMINISTRATOR";
            } else {
                // 2. Check registered user in localStorage
                const savedUserStr = localStorage.getItem("registeredUser");
                if (savedUserStr) {
                    try {
                        const savedUser = JSON.parse(savedUserStr);
                        if (savedUser.username === username && savedUser.password === password) {
                            isValidAuth = true;
                            displayName = savedUser.fullname || savedUser.name || username;
                        }
                    } catch (e) {
                        console.error("Error parsing registered user:", e);
                    }
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

// Register Page
if (window.location.pathname.endsWith("register.html")) {
    const regForm = document.getElementById("register-form");
    if (regForm) {
        regForm.addEventListener("submit", function(e) {
            e.preventDefault();
            
            const errContainer = document.getElementById("reg-error-msg");
            const errText = document.getElementById("reg-error-text");
            
            const fullname = document.getElementById("reg-fullname").value.trim();
            const employeeId = document.getElementById("reg-employee-id").value.trim();
            const email = document.getElementById("reg-email").value.trim();
            const mobile = document.getElementById("reg-mobile").value.trim();
            const dob = document.getElementById("reg-dob").value;
            const gender = document.getElementById("reg-gender").value;
            const zone = document.getElementById("reg-zone").value;
            const division = document.getElementById("reg-division").value;
            const depot = document.getElementById("reg-depot").value;
            const station = document.getElementById("reg-station").value;
            const designation = document.getElementById("reg-designation").value;
            const joiningDate = document.getElementById("reg-joining-date").value;
            const experience = document.getElementById("reg-experience").value;
            const license = document.getElementById("reg-license").value.trim();
            const medical = document.getElementById("reg-medical").value.trim();
            const bloodGroup = document.getElementById("reg-blood-group").value;
            const emergencyName = document.getElementById("reg-emergency-name").value.trim();
            const emergencyPhone = document.getElementById("reg-emergency-phone").value.trim();
            const username = document.getElementById("reg-username").value.trim();
            const password = document.getElementById("reg-password").value;
            const confirmPassword = document.getElementById("reg-confirm-password").value;
            const agree = document.getElementById("reg-agree").checked;

            // Reset error
            errContainer.classList.add("hidden");

            // Email Regex Validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (!fullname || !employeeId || !username) {
                errText.textContent = "Please fill in all mandatory fields.";
                errContainer.classList.remove("hidden");
                return;
            }

            if (!emailRegex.test(email)) {
                errText.textContent = "Please enter a valid Railway Email Address.";
                errContainer.classList.remove("hidden");
                return;
            }

            if (mobile.length !== 10 || isNaN(mobile)) {
                errText.textContent = "Please enter a valid 10-digit Mobile Number.";
                errContainer.classList.remove("hidden");
                return;
            }

            if (password.length < 6) {
                errText.textContent = "Password must be at least 6 characters long.";
                errContainer.classList.remove("hidden");
                return;
            }

            if (password !== confirmPassword) {
                errText.textContent = "Password and Confirm Password do not match.";
                errContainer.classList.remove("hidden");
                return;
            }

            if (!agree) {
                errText.textContent = "You must agree to the Railway Security Policy.";
                errContainer.classList.remove("hidden");
                return;
            }

            // Save to localStorage
            const userData = {
                fullname,
                employeeId,
                email,
                mobile,
                dob,
                gender,
                zone,
                division,
                depot,
                station,
                designation,
                joiningDate,
                experience,
                license,
                medical,
                bloodGroup,
                emergencyName,
                emergencyPhone,
                username,
                password
            };

            localStorage.setItem("registeredUser", JSON.stringify(userData));

            // Show Success Modal Popup
            const successModal = document.getElementById("reg-success-modal");
            if (successModal) successModal.classList.remove("hidden");

            setTimeout(() => {
                window.location.href = "login.html";
            }, 2000);
        });
    }
}

// Dashboard Page
if (window.location.pathname.endsWith("dashboard.html")) {
    if (checkAuth()) {
        window.onload = function() {
            updateClock();
            initLiveSimulation();
            
            // Default to dashboard
            navigateTo('dashboard');
            
            // Simulate live train movement glow
            setInterval(() => {
                const trains = document.querySelectorAll('#railway-svg circle');
                if (trains.length) {
                    trains.forEach((train) => {
                        if (Math.random() > 0.65) {
                            train.style.filter = 'brightness(1.8) drop-shadow(0 0 12px #06B6D4)';
                            setTimeout(() => {
                                train.style.filter = '';
                            }, 600);
                        }
                    });
                }
            }, 3000);
            
            // Keyboard shortcut
            document.addEventListener('keydown', function(e) {
                if (e.key === "/" && !document.getElementById('map-page').classList.contains('hidden')) {
                    simulateConflict();
                }
            });
            
            console.log('%cSmart Rail AI Control Center Loaded ✅', 'color:#06B6D4; font-family:monospace; font-weight:bold; font-size:14px');
        };
    }
}


// ==================== AI DELAY PREDICTION ====================

function predictDelay() {
    const btn = document.getElementById('predict-btn');
    const btnText = document.getElementById('predict-btn-text');
    const spinner = document.getElementById('predict-spinner');
    const errorBox = document.getElementById('predict-error');
    const resultCard = document.getElementById('predict-result');

    if (!btn) return;

    // Reset state
    errorBox.classList.add('hidden');
    resultCard.classList.add('hidden');

    // Loading state
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
            if (!response.ok) throw new Error('Server responded with an error');
            return response.json();
        })
        .then(data => showPredictionResult(data))
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

    // Calculate dynamic ETA
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