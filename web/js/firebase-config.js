// js/firebase-config.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.9.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/12.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/12.9.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyDS_J4dULPj4zQ0644QNcFsZLxefda2kx4",
  authDomain: "geometrykirk.firebaseapp.com",
  projectId: "geometrykirk",
  storageBucket: "geometrykirk.firebasestorage.app",
  messagingSenderId: "299744997160",
  appId: "1:299744997160:web:ec32cdcd26cc41e683ea1d",
  measurementId: "G-BHSGNPT9MY"
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

