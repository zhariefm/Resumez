// ==========================================================================
// RESUMEZ - APPLE CONTROLLER
// Minimalist, Clean, Fast
// ==========================================================================

const TECH_COUNTRIES = {
  "United States": {
    hubs: ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA", "Los Angeles, CA", "Remote (US)"],
    coords: [37.7749, -122.4194],
    city_coords: {
      "San Francisco, CA": [37.7749, -122.4194],
      "New York, NY": [40.7128, -74.0060],
      "Seattle, WA": [47.6062, -122.3321],
      "Austin, TX": [30.2672, -97.7431],
      "Boston, MA": [42.3601, -71.0589],
      "Los Angeles, CA": [34.0522, -118.2437],
      "Remote (US)": [39.8283, -98.5795],
    }
  },
  "United Kingdom": {
    hubs: ["London", "Cambridge", "Manchester", "Edinburgh", "Bristol", "Remote (UK)"],
    coords: [51.5074, -0.1278],
    city_coords: {
      "London": [51.5074, -0.1278],
      "Cambridge": [52.2053, 0.1218],
      "Manchester": [53.4808, -2.2426],
      "Edinburgh": [55.9533, -3.1883],
      "Bristol": [51.4545, -2.5879],
      "Remote (UK)": [54.5, -3.0],
    }
  },
  "Singapore": {
    hubs: ["Marina Bay", "One-North Tech Hub", "Jurong District", "Changi Park", "Remote (Singapore)"],
    coords: [1.3521, 103.8198],
    city_coords: {
      "Marina Bay": [1.2879, 103.8519],
      "One-North Tech Hub": [1.2988, 103.7874],
      "Jurong District": [1.3404, 103.6967],
      "Changi Park": [1.3347, 103.9634],
      "Remote (Singapore)": [1.3521, 103.8198],
    }
  },
  "Canada": {
    hubs: ["Toronto, ON", "Vancouver, BC", "Montreal, QC", "Waterloo, ON", "Ottawa, ON", "Remote (Canada)"],
    coords: [43.6532, -79.3832],
    city_coords: {
      "Toronto, ON": [43.6532, -79.3832],
      "Vancouver, BC": [49.2827, -123.1207],
      "Montreal, QC": [45.5017, -73.5673],
      "Waterloo, ON": [43.4643, -80.5204],
      "Ottawa, ON": [45.4215, -75.6972],
      "Remote (Canada)": [56.1304, -106.3468],
    }
  },
  "Germany": {
    hubs: ["Berlin", "Munich", "Frankfurt", "Hamburg", "Stuttgart", "Remote (Germany)"],
    coords: [52.5200, 13.4050],
    city_coords: {
      "Berlin": [52.5200, 13.4050],
      "Munich": [48.1351, 11.5820],
      "Frankfurt": [50.1109, 8.6821],
      "Hamburg": [53.5511, 9.9937],
      "Stuttgart": [48.7758, 9.1829],
      "Remote (Germany)": [51.1657, 10.4515],
    }
  },
  "Malaysia": {
    hubs: ["Kuala Lumpur", "Cyberjaya", "Penang", "Petaling Jaya", "Remote (Malaysia)"],
    coords: [3.1390, 101.6869],
    city_coords: {
      "Kuala Lumpur": [3.1118, 101.6669],
      "Cyberjaya": [2.9213, 101.6559],
      "Penang": [5.2974, 100.2831],
      "Petaling Jaya": [3.1073, 101.6067],
      "Remote (Malaysia)": [4.2105, 101.9758],
    }
  },
  "Australia": {
    hubs: ["Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD", "Perth, WA", "Remote (Australia)"],
    coords: [-33.8688, 151.2093],
    city_coords: {
      "Sydney, NSW": [-33.8688, 151.2093],
      "Melbourne, VIC": [-37.8136, 144.9631],
      "Brisbane, QLD": [-27.4698, 153.0251],
      "Perth, WA": [-31.9505, 115.8605],
      "Remote (Australia)": [-25.2744, 133.7751],
    }
  },
  "Global Remote": {
    hubs: ["Worldwide Remote", "North America", "Europe / UK", "Asia-Pacific"],
    coords: [20.0, 0.0],
    city_coords: {
      "Worldwide Remote": [20.0, 0.0],
      "North America": [39.8283, -98.5795],
      "Europe / UK": [54.5260, 15.2551],
      "Asia-Pacific": [1.3521, 103.8198],
    }
  }
};

const state = {
  currentStep: 1,
  careerLevel: "student",
  resumeText: "",
  targetCountry: "United States",
  targetHub: "San Francisco, CA",
  targetLocation: "San Francisco, CA, United States",
  recommendedCompanies: [],
  tailoredData: null,
  activeSavedId: null,
  resumePreviewMode: "pdf"
};

let mapInstance = null;
let mapMarker = null;

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  initLocationSelectors();
  initMap();
  initFileUpload();
  refreshSavedAppsCount();
  setupEventListeners();
});

function setupEventListeners() {
  // Step Navigation Pills
  document.querySelectorAll(".nav-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      const targetStep = parseInt(pill.dataset.step);
      if (targetStep === 1) goToStep(1);
      else if (targetStep === 2 && state.resumeText.trim()) goToStep(2);
      else if (targetStep === 3 && state.tailoredData) goToStep(3);
    });
  });

  // Career Segmented Switcher
  document.querySelectorAll("[data-career]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-career]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.careerLevel = btn.dataset.career;
    });
  });

  // Saved Applications Modal
  document.getElementById("btn-open-apps").addEventListener("click", openApplicationsModal);
  document.getElementById("btn-close-modal").addEventListener("click", closeApplicationsModal);

  // Custom Location Search
  const searchBtn = document.getElementById("btn-search-location");
  const customLocInput = document.getElementById("custom-location-input");
  if (searchBtn && customLocInput) {
    searchBtn.addEventListener("click", () => searchCustomLocation());
    customLocInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        searchCustomLocation();
      }
    });
  }
}

// --- NAVIGATION ---
function goToStep(stepNum) {
  state.currentStep = stepNum;
  document.querySelectorAll(".step-view").forEach(v => v.style.display = "none");
  document.getElementById(`step-${stepNum}`).style.display = "block";

  document.querySelectorAll(".nav-pill").forEach(pill => {
    const s = parseInt(pill.dataset.step);
    pill.classList.remove("active", "done");
    if (s === stepNum) pill.classList.add("active");
    else if (s < stepNum) pill.classList.add("done");
  });

  window.scrollTo({ top: 0, behavior: "smooth" });
}

// --- LOCATION & MAP ---
function initLocationSelectors() {
  const countrySelect = document.getElementById("select-country");
  const hubSelect = document.getElementById("select-hub");

  countrySelect.innerHTML = "";
  Object.keys(TECH_COUNTRIES).forEach(c => {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    if (c === state.targetCountry) opt.selected = true;
    countrySelect.appendChild(opt);
  });

  updateHubOptions();

  countrySelect.addEventListener("change", () => {
    state.targetCountry = countrySelect.value;
    updateHubOptions();
    updateLocationString();
    updateMap();
  });

  hubSelect.addEventListener("change", () => {
    state.targetHub = hubSelect.value;
    updateLocationString();
    updateMap();
  });
}

function updateHubOptions() {
  const hubSelect = document.getElementById("select-hub");
  const data = TECH_COUNTRIES[state.targetCountry] || TECH_COUNTRIES["United States"];
  hubSelect.innerHTML = "";
  data.hubs.forEach((h, idx) => {
    const opt = document.createElement("option");
    opt.value = h;
    opt.textContent = h;
    if (idx === 0) {
      opt.selected = true;
      state.targetHub = h;
    }
    hubSelect.appendChild(opt);
  });
  updateLocationString();
}

function updateLocationString() {
  if (state.targetCountry.includes("Remote") || state.targetHub.includes("Remote") || state.targetHub.includes("Worldwide")) {
    state.targetLocation = state.targetHub;
  } else {
    state.targetLocation = `${state.targetHub}, ${state.targetCountry}`;
  }
  const locDisp = document.getElementById("active-location-display");
  if (locDisp) locDisp.textContent = state.targetLocation;
}

function initMap() {
  const mapElem = document.getElementById("leaflet-map");
  if (!mapElem || typeof L === "undefined") return;

  const countryData = TECH_COUNTRIES[state.targetCountry] || TECH_COUNTRIES["United States"];
  const coords = countryData.city_coords[state.targetHub] || countryData.coords;

  mapInstance = L.map("leaflet-map", { zoomControl: false }).setView(coords, 5);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap"
  }).addTo(mapInstance);

  mapMarker = L.circleMarker(coords, {
    radius: 6,
    fillColor: "#0071e3",
    color: "#ffffff",
    weight: 2,
    opacity: 1,
    fillOpacity: 0.95
  }).addTo(mapInstance);

  mapInstance.on("click", async (e) => {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    mapMarker.setLatLng([lat, lon]);

    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`, {
        headers: { "Accept-Language": "en" }
      });
      const data = await res.json();
      if (data && data.address) {
        const addr = data.address;
        const city = addr.city || addr.town || addr.village || addr.municipality || addr.state || "Location";
        const country = addr.country || "";
        const formatted = country ? `${city}, ${country}` : city;

        state.targetLocation = formatted;
        document.getElementById("custom-location-input").value = formatted;
        document.getElementById("active-location-display").textContent = formatted;
        showToast(`Pinned: ${formatted}`);
      } else {
        const fallback = `${lat.toFixed(2)}, ${lon.toFixed(2)}`;
        state.targetLocation = fallback;
        document.getElementById("active-location-display").textContent = fallback;
      }
    } catch (err) {
      const fallback = `${lat.toFixed(2)}, ${lon.toFixed(2)}`;
      state.targetLocation = fallback;
      document.getElementById("active-location-display").textContent = fallback;
    }
  });
}

function updateMap() {
  if (!mapInstance || !mapMarker) return;
  const countryData = TECH_COUNTRIES[state.targetCountry] || TECH_COUNTRIES["United States"];
  const coords = countryData.city_coords[state.targetHub] || countryData.coords;
  mapInstance.setView(coords, 7);
  mapMarker.setLatLng(coords);
}

async function searchCustomLocation() {
  const input = document.getElementById("custom-location-input");
  const query = input ? input.value.trim() : "";
  if (!query) return;

  showToast(`Searching...`);
  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`, {
      headers: { "Accept-Language": "en" }
    });
    const data = await res.json();
    if (data && data.length > 0) {
      const lat = parseFloat(data[0].lat);
      const lon = parseFloat(data[0].lon);
      const coords = [lat, lon];

      if (mapInstance && mapMarker) {
        mapInstance.flyTo(coords, 10);
        mapMarker.setLatLng(coords);
      }

      const parts = data[0].display_name.split(", ").filter(Boolean);
      const cleanLoc = parts.length > 2 ? `${parts[0]}, ${parts[parts.length - 1]}` : data[0].display_name;

      state.targetLocation = cleanLoc;
      document.getElementById("active-location-display").textContent = cleanLoc;
      showToast(`Location set: ${cleanLoc}`);
    } else {
      state.targetLocation = query;
      document.getElementById("active-location-display").textContent = query;
      showToast(`Location set: ${query}`);
    }
  } catch (err) {
    state.targetLocation = query;
    document.getElementById("active-location-display").textContent = query;
  }
}

// --- USER DETAILS & UPLOAD ---
function getUserDetails() {
  return {
    name: document.getElementById("user-name")?.value.trim() || "",
    target_role: document.getElementById("user-target-role")?.value.trim() || "",
    email: document.getElementById("user-email")?.value.trim() || "",
    phone: document.getElementById("user-phone")?.value.trim() || "",
    linkedin: document.getElementById("user-linkedin")?.value.trim() || "",
    github: document.getElementById("user-github")?.value.trim() || ""
  };
}

function initFileUpload() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const resumeTextarea = document.getElementById("resume-text");

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });

  resumeTextarea.addEventListener("input", (e) => {
    state.resumeText = e.target.value;
  });
}

async function handleFileUpload(file) {
  const formData = new FormData();
  formData.append("resume_file", file);

  showSpinner("Extracting text...");
  try {
    const res = await fetch("/api/upload-resume", { method: "POST", body: formData });
    const data = await res.json();
    hideSpinner();

    if (data.error) {
      showToast(data.error);
    } else {
      state.resumeText = data.text;
      document.getElementById("resume-text").value = data.text;

      // Auto-populate extracted contact info if empty
      const emailMatch = data.text.match(/[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}/);
      if (emailMatch && !document.getElementById("user-email").value) {
        document.getElementById("user-email").value = emailMatch[0];
      }
      const phoneMatch = data.text.match(/(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
      if (phoneMatch && !document.getElementById("user-phone").value) {
        document.getElementById("user-phone").value = phoneMatch[0];
      }
      const liMatch = data.text.match(/(linkedin\.com\/in\/[\w-]+)/i);
      if (liMatch && !document.getElementById("user-linkedin").value) {
        document.getElementById("user-linkedin").value = liMatch[0];
      }
      const ghMatch = data.text.match(/(github\.com\/[\w-]+)/i);
      if (ghMatch && !document.getElementById("user-github").value) {
        document.getElementById("user-github").value = ghMatch[0];
      }

      showToast("Resume parsed.");
    }
  } catch (err) {
    hideSpinner();
    showToast("Upload failed.");
  }
}

// --- STEP 1: CONTINUE ACTION ---
async function continueToCompanies() {
  const text = document.getElementById("resume-text").value.trim();
  if (!text) {
    showToast("Please provide resume background first.");
    return;
  }
  state.resumeText = text;
  const userDetails = getUserDetails();

  if (state.recommendedCompanies.length === 0) {
    showSpinner("Finding employers...");
    try {
      const res = await fetch("/api/recommend-companies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_text: state.resumeText,
          target_location: state.targetLocation,
          target_role: userDetails.target_role
        })
      });
      const data = await res.json();
      hideSpinner();

      if (data.error) {
        showToast(data.error);
        return;
      }
      state.recommendedCompanies = data.recommendations || [];
      renderRecommendedCompanies();
    } catch (err) {
      hideSpinner();
      showToast("Failed to fetch employers.");
      return;
    }
  } else {
    renderRecommendedCompanies();
  }

  goToStep(2);
}

// --- STEP 2: COMPANY SELECTION ---
function renderRecommendedCompanies() {
  const list = document.getElementById("recommended-list");
  list.innerHTML = "";

  if (state.recommendedCompanies.length === 0) {
    list.innerHTML = '<div style="color: #86868b; padding: 1rem;">No recommendations. Try the Custom Role tab.</div>';
    return;
  }

  state.recommendedCompanies.forEach((rec, idx) => {
    const card = document.createElement("div");
    card.className = "employer-card";
    card.innerHTML = `
      <div class="employer-head">
        <div>
          <span class="employer-name">${rec.company_name}</span>
          <a href="${rec.website_url}" target="_blank" class="external-link">Website ↗</a>
        </div>
        <span class="fit-pill">${rec.fit_score}% Match</span>
      </div>
      <div class="employer-role">${rec.role_title} &bull; <span style="color: #86868b;">${rec.target_locations || state.targetLocation}</span></div>
      <div class="employer-desc">${rec.company_overview}</div>
      <button class="action-btn action-btn-primary action-btn-block action-btn-sm" onclick="tailorForCompany(${idx})">Tailor for ${rec.company_name} →</button>
    `;
    list.appendChild(card);
  });
}

function switchStep2Tab(tabName) {
  document.querySelectorAll(".tab-s2").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-content-s2").forEach(c => c.classList.remove("active"));
  document.getElementById(`tab-s2-${tabName}`).classList.add("active");
  document.getElementById(`content-s2-${tabName}`).classList.add("active");
}

async function tailorForCompany(idx) {
  const rec = state.recommendedCompanies[idx];
  await runTailoring({
    company_name: rec.company_name,
    role_title: rec.role_title,
    website_url: rec.website_url,
    location: rec.target_locations || state.targetLocation,
    job_description: rec.job_description
  });
}

async function tailorCustomRole() {
  const company = document.getElementById("custom-company").value.trim();
  const role = document.getElementById("custom-role").value.trim();
  const jd = document.getElementById("custom-jd").value.trim();

  if (!company || !role || !jd) {
    showToast("Please provide company, role, and description.");
    return;
  }

  await runTailoring({
    company_name: company,
    role_title: role,
    location: state.targetLocation,
    job_description: jd
  });
}

async function runTailoring(payload) {
  showSpinner(`Tailoring for ${payload.company_name}...`);
  const userDetails = getUserDetails();
  try {
    const res = await fetch("/api/tailor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: state.resumeText,
        career_level: state.careerLevel,
        user_details: userDetails,
        ...payload
      })
    });
    const data = await res.json();
    hideSpinner();

    if (data.error) {
      showToast(data.error);
      return;
    }

    state.tailoredData = data.tailored_data;
    state.activeSavedId = data.saved_id;
    refreshSavedAppsCount();
    renderStep3();
    goToStep(3);
  } catch (err) {
    hideSpinner();
    showToast("Failed to tailor documents.");
  }
}

// --- STEP 3: RENDER SUITE ---
function renderStep3() {
  const d = state.tailoredData;
  if (!d) return;

  const assessment = d.ats_assessment || {};
  const score = assessment.match_score || 92;
  const breakdown = assessment.breakdown || {};

  document.getElementById("s3-company-name").textContent = assessment.target_company || "Company";
  document.getElementById("s3-role-loc").textContent = `${assessment.target_role || "Role"} • ${assessment.location || state.targetLocation}`;

  document.getElementById("metric-match").textContent = `${score}%`;
  document.getElementById("metric-skills").textContent = `${breakdown.skills_match_score || 95}%`;
  document.getElementById("metric-impact").textContent = `${breakdown.impact_metric_score || 90}%`;
  document.getElementById("metric-format").textContent = `${breakdown.format_compliance_score || 98}%`;
  document.getElementById("metric-length").textContent = `${breakdown.brevity_score || 92}%`;

  renderResumePaperView();
  renderKeywordMatrix();
  initBulletTuner();
  renderOutreachSuite();
  renderCoverLetterView();
  renderInterviewPrep();
  renderLinkedInView();

  loadPdfPreview();
}

function switchStep3Tab(tabName) {
  document.querySelectorAll(".tab-s3").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-content-s3").forEach(c => c.classList.remove("active"));
  document.getElementById(`tab-s3-${tabName}`).classList.add("active");
  document.getElementById(`content-s3-${tabName}`).classList.add("active");
}

function setPreviewMode(mode) {
  state.resumePreviewMode = mode;
  document.getElementById("btn-preview-pdf").classList.toggle("active", mode === "pdf");
  document.getElementById("btn-preview-paper").classList.toggle("active", mode === "paper");
  document.getElementById("resume-pdf-frame").style.display = mode === "pdf" ? "block" : "none";
  document.getElementById("resume-paper-view").style.display = mode === "paper" ? "block" : "none";
}

function loadPdfPreview() {
  const frame = document.getElementById("resume-pdf-frame");
  if (frame) {
    frame.src = `/preview/resume/pdf?t=${Date.now()}`;
  }
}

// --- KEYWORD MATRIX ---
function renderKeywordMatrix() {
  const assessment = state.tailoredData.ats_assessment || {};
  const matched = assessment.key_matched_keywords || [];
  const missing = assessment.missing_or_recommended_keywords || [];

  const total = matched.length + missing.length;
  const coverage = total > 0 ? Math.round((matched.length / total) * 100) : 88;

  document.getElementById("kw-coverage-num").textContent = `${coverage}%`;
  document.getElementById("kw-coverage-bar").style.width = `${coverage}%`;

  document.getElementById("matched-keywords-container").innerHTML = matched.map(k => `<span class="tag-match">✓ ${k}</span>`).join("");
  document.getElementById("missing-keywords-container").innerHTML = missing.map(k => `<span class="tag-miss">⚠️ ${k}</span>`).join("");
}

// --- BULLET TUNER ---
function initBulletTuner() {
  const d = state.tailoredData;
  const select = document.getElementById("tuner-bullet-select");
  select.innerHTML = "";

  const items = [];
  (d.experience || []).forEach((exp, expIdx) => {
    (exp.bullets || []).forEach((b, bIdx) => {
      items.push({
        label: `Work: ${exp.company || 'Role'} - Bullet ${bIdx + 1}`,
        text: b,
        type: "exp",
        parentIdx: expIdx,
        bulletIdx: bIdx
      });
    });
  });

  (d.projects || []).forEach((proj, pIdx) => {
    (proj.bullets || []).forEach((b, bIdx) => {
      items.push({
        label: `Project: ${proj.title || proj.name || 'Project'} - Bullet ${bIdx + 1}`,
        text: b,
        type: "proj",
        parentIdx: pIdx,
        bulletIdx: bIdx
      });
    });
  });

  items.forEach((item, idx) => {
    const opt = document.createElement("option");
    opt.value = idx;
    opt.textContent = item.label;
    select.appendChild(opt);
  });

  window._bulletItems = items;

  if (items.length > 0) {
    document.getElementById("tuner-current-bullet").value = items[0].text;
  }

  select.onchange = () => {
    const chosen = items[select.value];
    if (chosen) document.getElementById("tuner-current-bullet").value = chosen.text;
  };
}

async function tuneBulletAction(mode) {
  const select = document.getElementById("tuner-bullet-select");
  const items = window._bulletItems || [];
  const chosen = items[select.value];
  if (!chosen) return;

  showSpinner("Refining bullet...");
  try {
    const res = await fetch("/api/tune-bullet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        bullet_text: chosen.text,
        mode: mode,
        target_role: state.tailoredData.ats_assessment?.target_role || "Software Engineer"
      })
    });
    const data = await res.json();
    hideSpinner();

    if (data.error) {
      showToast(data.error);
      return;
    }

    const tuned = data.tuned_bullet;
    chosen.text = tuned;
    document.getElementById("tuner-current-bullet").value = tuned;

    if (chosen.type === "exp") {
      state.tailoredData.experience[chosen.parentIdx].bullets[chosen.bulletIdx] = tuned;
    } else {
      state.tailoredData.projects[chosen.parentIdx].bullets[chosen.bulletIdx] = tuned;
    }

    renderResumePaperView();
    loadPdfPreview();
    showToast("Bullet updated.");
  } catch (err) {
    hideSpinner();
    showToast("Error tuning bullet.");
  }
}

// --- JAKE'S PAPER VIEW ---
function renderResumePaperView() {
  const d = state.tailoredData;
  const p = d.personal_info || {};
  const contact = [p.phone, p.email, p.linkedin, p.github, p.portfolio].filter(Boolean).join("  |  ");

  let html = `
    <div class="paper-name">${p.name || 'Candidate'}</div>
    <div class="paper-contacts">${contact}</div>
  `;

  const eduHtml = `
    <div class="paper-divider-title">Education</div>
    ${(d.education || []).map(e => `
      <div class="paper-line">
        <span class="paper-bold">${e.institution}</span>
        <span>${e.location || ''}</span>
      </div>
      <div class="paper-line">
        <span class="paper-italic">${e.degree}${e.gpa ? ` (GPA: ${e.gpa})` : ''}</span>
        <span class="paper-italic">${e.dates || ''}</span>
      </div>
    `).join('')}
  `;

  const expHtml = `
    <div class="paper-divider-title">Experience</div>
    ${(d.experience || []).map(exp => `
      <div class="paper-line">
        <span class="paper-bold">${exp.role}</span>
        <span>${exp.dates || ''}</span>
      </div>
      <div class="paper-line">
        <span class="paper-italic">${exp.company}</span>
        <span class="paper-italic">${exp.location || ''}</span>
      </div>
      <ul class="paper-list">
        ${(exp.bullets || []).map(b => `<li>${b}</li>`).join('')}
      </ul>
    `).join('')}
  `;

  const projHtml = `
    <div class="paper-divider-title">Projects</div>
    ${(d.projects || []).map(pr => `
      <div class="paper-line">
        <span><span class="paper-bold">${pr.title || pr.name}</span>${pr.tech_stack || pr.tools ? ` | <i>${pr.tech_stack || pr.tools}</i>` : ''}</span>
        <span class="paper-italic">${pr.dates || ''}</span>
      </div>
      <ul class="paper-list">
        ${(pr.bullets || []).map(b => `<li>${b}</li>`).join('')}
      </ul>
    `).join('')}
  `;

  const skillsObj = d.skills || d.technical_skills || {};
  let skillsHtml = '<div class="paper-divider-title">Technical Skills</div>';
  if (Array.isArray(skillsObj)) {
    skillsHtml += `<div style="font-size: 0.86rem;"><b>Skills:</b> ${skillsObj.join(', ')}</div>`;
  } else {
    Object.keys(skillsObj).forEach(cat => {
      const items = skillsObj[cat];
      skillsHtml += `<div style="font-size: 0.86rem; margin-bottom: 2px;"><b>${cat.replace(/_/g, ' ')}:</b> ${Array.isArray(items) ? items.join(', ') : items}</div>`;
    });
  }

  if (state.careerLevel === "experienced") {
    html += expHtml + projHtml + skillsHtml + eduHtml;
  } else {
    html += eduHtml + expHtml + projHtml + skillsHtml;
  }

  document.getElementById("resume-paper-view").innerHTML = html;
}

// --- COVER LETTER VIEW ---
function renderCoverLetterView() {
  const l = state.tailoredData.application_letter || {};
  const p = state.tailoredData.personal_info || {};
  const targetComp = state.tailoredData.ats_assessment?.target_company || "Company";

  document.getElementById("cover-letter-view").innerHTML = `
    <div style="font-size: 0.92rem; margin-bottom: 0.6rem;">${l.date || 'Current Date'}</div>
    <div style="font-size: 0.92rem; margin-bottom: 0.85rem;"><b>To:</b> Hiring Team, ${targetComp}</div>
    <div style="font-size: 0.92rem; margin-bottom: 0.85rem;">${l.greeting || 'Dear Hiring Team,'}</div>
    <div style="font-size: 0.92rem; margin-bottom: 0.85rem;">${l.opening_hook || l.opening || ''}</div>
    <div style="font-size: 0.92rem; margin-bottom: 0.85rem;">${l.why_company || l.body_paragraph_1 || ''}</div>
    <div style="font-size: 0.92rem; margin-bottom: 0.85rem;">${l.student_value_add || l.body_paragraph_2 || ''}</div>
    <div style="font-size: 0.92rem; margin-bottom: 1.25rem;">${l.closing_and_call_to_action || l.closing || ''}</div>
    <div style="font-size: 0.92rem;">${l.sign_off || 'Sincerely,'}<br><b>${p.name || 'Candidate'}</b></div>
  `;
}

// --- OUTREACH SUITE ---
function renderOutreachSuite() {
  const o = state.tailoredData.recruiter_outreach || {};
  const liNote = o.linkedin_connection_note || "Hi [Name], I'd love to connect!";
  document.getElementById("outreach-li-note").value = liNote;
  document.getElementById("outreach-li-count").textContent = `${liNote.length}/300`;

  document.getElementById("outreach-email-subject").value = o.cold_email_subject || "Candidate Application";
  document.getElementById("outreach-email-body").value = o.cold_email_body || "";
  document.getElementById("outreach-thank-you").value = o.thank_you_note || "";
}

// --- INTERVIEW PREP & LINKEDIN ---
function renderInterviewPrep() {
  const prep = state.tailoredData.interview_prep || {};
  const tech = prep.technical_questions || [];
  const behav = prep.behavioral_questions || [];

  const tHtml = tech.map(t => `
    <div style="background: #f5f5f7; border-left: 3px solid #0071e3; border-radius: 8px; padding: 0.65rem 0.85rem; margin-bottom: 0.5rem;">
      <div style="font-weight: 600; font-size: 0.88rem;">${t.question}</div>
      <div style="color: #86868b; font-size: 0.82rem; margin-top: 0.2rem;">${t.answer_strategy}</div>
    </div>
  `).join("");

  const bHtml = behav.map(b => `
    <div style="background: #f5f5f7; border-left: 3px solid #34c759; border-radius: 8px; padding: 0.65rem 0.85rem; margin-bottom: 0.5rem;">
      <div style="font-weight: 600; font-size: 0.88rem;">${b.question}</div>
      <div style="color: #86868b; font-size: 0.82rem; margin-top: 0.2rem;">${b.answer_strategy}</div>
    </div>
  `).join("");

  document.getElementById("tech-scenarios-container").innerHTML = tHtml || '<div style="color:#86868b;">None.</div>';
  document.getElementById("behav-scenarios-container").innerHTML = bHtml || '<div style="color:#86868b;">None.</div>';
}

function renderLinkedInView() {
  const li = state.tailoredData.linkedin_suite || {};
  document.getElementById("li-headline-input").value = li.headline || "";
  document.getElementById("li-about-input").value = li.about_summary || "";
}

// --- PIPELINE STATUS UPDATE ---
async function updateActiveStatus(newStatus) {
  if (!state.activeSavedId) return;
  try {
    await fetch(`/api/applications/${state.activeSavedId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    showToast(`Status: ${newStatus}`);
  } catch (err) {
    showToast("Failed to update status.");
  }
}

// --- APPLICATIONS MODAL ---
async function openApplicationsModal() {
  const modal = document.getElementById("apps-modal");
  modal.classList.add("active");
  loadApplicationsList();
}

function closeApplicationsModal() {
  document.getElementById("apps-modal").classList.remove("active");
}

async function loadApplicationsList() {
  const container = document.getElementById("saved-apps-list");
  container.innerHTML = '<div style="color: #86868b; padding: 1rem;">Loading...</div>';

  try {
    const res = await fetch("/api/applications");
    const data = await res.json();
    const apps = data.applications || [];

    if (apps.length === 0) {
      container.innerHTML = '<div style="color: #86868b; padding: 1rem;">No saved applications.</div>';
      return;
    }

    container.innerHTML = "";
    apps.forEach(app => {
      const card = document.createElement("div");
      card.style = "background: #f5f5f7; border: 1px solid #d2d2d7; border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 0.65rem;";
      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
          <div>
            <span style="font-weight: 700; font-size: 1rem; color: #1d1d1f;">${app.company_name}</span>
            <span style="color: #86868b; font-size: 0.84rem; margin-left: 0.35rem;">${app.role_title} &bull; ${app.location}</span>
          </div>
          <span class="fit-pill">${app.match_score}%</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem;">
          <div style="font-size: 0.78rem; color: #86868b;">${app.created_at.substring(0, 10)} &bull; ${app.status}</div>
          <div style="display: flex; gap: 0.35rem;">
            <button class="action-btn action-btn-primary action-btn-sm" onclick="loadSavedApp(${app.id})">Open →</button>
            <button class="action-btn action-btn-secondary action-btn-sm" onclick="deleteSavedApp(${app.id})">Delete</button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = '<div style="color: #ff3b30; padding: 1rem;">Error loading applications.</div>';
  }
}

async function loadSavedApp(appId) {
  showSpinner("Loading...");
  try {
    const res = await fetch(`/api/applications/${appId}`);
    const data = await res.json();
    hideSpinner();

    if (data.error) {
      showToast(data.error);
      return;
    }

    state.tailoredData = data.data;
    state.activeSavedId = data.id;
    state.careerLevel = data.career_level || "student";
    state.targetLocation = data.location || state.targetLocation;

    const p = data.data?.personal_info || {};
    if (p.name && document.getElementById("user-name")) document.getElementById("user-name").value = p.name;
    if (p.email && document.getElementById("user-email")) document.getElementById("user-email").value = p.email;
    if (p.phone && document.getElementById("user-phone")) document.getElementById("user-phone").value = p.phone;
    if (p.linkedin && document.getElementById("user-linkedin")) document.getElementById("user-linkedin").value = p.linkedin;
    if (p.github && document.getElementById("user-github")) document.getElementById("user-github").value = p.github;

    closeApplicationsModal();
    renderStep3();
    goToStep(3);
    showToast(`Loaded ${data.company_name}.`);
  } catch (err) {
    hideSpinner();
    showToast("Error loading application.");
  }
}

async function deleteSavedApp(appId) {
  if (!confirm("Delete this saved application?")) return;
  try {
    await fetch(`/api/applications/${appId}`, { method: "DELETE" });
    showToast("Deleted.");
    loadApplicationsList();
    refreshSavedAppsCount();
  } catch (err) {
    showToast("Error deleting.");
  }
}

async function refreshSavedAppsCount() {
  try {
    const res = await fetch("/api/applications");
    const data = await res.json();
    const count = data.applications?.length || 0;
    const btn = document.getElementById("btn-open-apps");
    if (btn) btn.textContent = `Applications (${count})`;
  } catch (err) {}
}

// --- UTILITIES ---
function copyText(elemId) {
  const elem = document.getElementById(elemId);
  if (!elem) return;
  navigator.clipboard.writeText(elem.value || elem.innerText).then(() => {
    showToast("Copied.");
  });
}

function showSpinner(text = "Processing...") {
  const sp = document.getElementById("spinner-overlay");
  const txt = document.getElementById("spinner-text");
  if (txt) txt.textContent = text;
  if (sp) sp.classList.add("active");
}

function hideSpinner() {
  const sp = document.getElementById("spinner-overlay");
  if (sp) sp.classList.remove("active");
}

function showToast(msg) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.style.display = "block";
  setTimeout(() => { t.style.display = "none"; }, 2500);
}
