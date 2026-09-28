/**
 * Shared API client for the frontend.
 * Talks to the Flask REST API (backend/app.py). Update API_BASE when you
 * deploy the backend to the cloud (Render/Railway/EC2/etc.).
 */
const API_BASE = window.API_BASE_OVERRIDE ||
  ((location.hostname === "localhost" || location.hostname === "127.0.0.1")
    ? "http://localhost:5000"
    : "https://YOUR-RENDER-URL.onrender.com");

function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(token) {
  localStorage.setItem("access_token", token);
}

function clearSession() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("current_user");
}

function getCurrentUser() {
  const raw = localStorage.getItem("current_user");
  return raw ? JSON.parse(raw) : null;
}

function setCurrentUser(user) {
  localStorage.setItem("current_user", JSON.stringify(user));
}

function requireAuthOrRedirect() {
  if (!getToken()) {
    window.location.href = "login.html";
  }
}

/**
 * Core request helper. Automatically attaches the JWT and parses JSON.
 * Pass `isForm: true` + a FormData body for file uploads.
 */
async function apiRequest(path, { method = "GET", body = null, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isForm && body) headers["Content-Type"] = "application/json";

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    data = null;
  }

  if (response.status === 401) {
    clearSession();
    window.location.href = "login.html?expired=1";
    return null;
  }

  if (!response.ok) {
    const message = (data && data.error) || `Request failed (${response.status})`;
    throw new Error(message);
  }

  return data;
}

function showMessage(elementId, text, type = "error") {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = text;
  el.className = `msg ${type}`;
  el.style.display = "block";
}
