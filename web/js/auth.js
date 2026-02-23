// js/auth.js
import { auth } from "./firebase-config.js";
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut
} from "https://www.gstatic.com/firebasejs/12.9.0/firebase-auth.js";

const path = window.location.pathname;

// Páginas protegidas: requieren sesión
const protectedPages = [
  "/descarga-windows.html",
  "/descarga-android.html",
  "/foro.html"
];

onAuthStateChanged(auth, (user) => {
  // Proteger páginas
  if (protectedPages.some(p => path.endsWith(p))) {
    if (!user) {
      window.location.href = "perfil.html";
      return;
    }
  }

  // Perfil: mostrar info de usuario
  if (path.endsWith("perfil.html")) {
    const userInfo = document.getElementById("user-info");
    const logoutBtn = document.getElementById("logout-btn");
    if (user) {
      userInfo.textContent = `Sesión iniciada como: ${user.email}`;
      logoutBtn.style.display = "inline-block";
    } else {
      userInfo.textContent = "No has iniciado sesión.";
      logoutBtn.style.display = "none";
    }
  }

  // Descarga Windows
  if (path.endsWith("descarga-windows.html")) {
    const msg = document.getElementById("windows-msg");
    const link = document.getElementById("windows-link");
    if (user) {
      msg.textContent = "Sesión iniciada. Puedes descargar el juego.";
      msg.classList.add("success");
      link.style.display = "inline-block";
    } else {
      msg.textContent = "Debes iniciar sesión para descargar.";
      msg.classList.add("error");
      link.style.display = "none";
    }
  }

  // Descarga Android
  if (path.endsWith("descarga-android.html")) {
    const msg = document.getElementById("android-msg");
    const link = document.getElementById("android-link");
    if (user) {
      msg.textContent = "Sesión iniciada. Puedes descargar el juego.";
      msg.classList.add("success");
      link.style.display = "inline-block";
    } else {
      msg.textContent = "Debes iniciar sesión para descargar.";
      msg.classList.add("error");
      link.style.display = "none";
    }
  }
});

// Solo en perfil.html: manejar formularios
if (path.endsWith("perfil.html")) {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const loginMsg = document.getElementById("login-msg");
  const registerMsg = document.getElementById("register-msg");
  const logoutBtn = document.getElementById("logout-btn");

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginMsg.textContent = "";
    loginMsg.className = "msg";
    const email = document.getElementById("login-email").value;
    const pass = document.getElementById("login-password").value;
    try {
      await signInWithEmailAndPassword(auth, email, pass);
      loginMsg.textContent = "Sesión iniciada correctamente.";
      loginMsg.classList.add("success");
      setTimeout(() => window.location.href = "index.html", 800);
    } catch (err) {
      loginMsg.textContent = "Error al iniciar sesión: " + err.message;
      loginMsg.classList.add("error");
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    registerMsg.textContent = "";
    registerMsg.className = "msg";
    const email = document.getElementById("register-email").value;
    const pass = document.getElementById("register-password").value;
    try {
      await createUserWithEmailAndPassword(auth, email, pass);
      registerMsg.textContent = "Cuenta creada correctamente. Ya puedes iniciar sesión.";
      registerMsg.classList.add("success");
    } catch (err) {
      registerMsg.textContent = "Error al registrarse: " + err.message;
      registerMsg.classList.add("error");
    }
  });

  logoutBtn.addEventListener("click", async () => {
    await signOut(auth);
    window.location.reload();
  });
}
