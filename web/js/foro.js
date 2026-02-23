// js/foro.js
import { auth, db } from "./firebase-config.js";
import {
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/12.9.0/firebase-auth.js";
import {
  collection,
  addDoc,
  serverTimestamp,
  query,
  orderBy,
  onSnapshot,
  doc,
  collectionGroup
} from "https://www.gstatic.com/firebasejs/12.9.0/firebase-firestore.js";

const foroMsg = document.getElementById("foro-msg");
const postsContainer = document.getElementById("posts-container");
const newPostForm = document.getElementById("new-post-form");

let currentUser = null;

// Solo usuarios logueados pueden ver el foro
onAuthStateChanged(auth, (user) => {
  if (!user) {
    window.location.href = "perfil.html";
  } else {
    currentUser = user;
    foroMsg.textContent = "Sesión iniciada como: " + user.email;
    foroMsg.classList.add("success");
    listenPosts();
  }
});

async function createPost(title, body) {
  await addDoc(collection(db, "posts"), {
    title,
    body,
    author: currentUser.email,
    createdAt: serverTimestamp()
  });
}

async function createReply(postId, body) {
  const postRef = doc(db, "posts", postId);
  await addDoc(collection(postRef, "replies"), {
    body,
    author: currentUser.email,
    createdAt: serverTimestamp()
  });
}

function listenPosts() {
  const q = query(collection(db, "posts"), orderBy("createdAt", "desc"));
  onSnapshot(q, async (snapshot) => {
    postsContainer.innerHTML = "";
    snapshot.forEach((docSnap) => {
      const data = docSnap.data();
      const postId = docSnap.id;

      const postDiv = document.createElement("div");
      postDiv.className = "post-card";

      const header = document.createElement("div");
      header.className = "post-header";
      const titleSpan = document.createElement("span");
      titleSpan.textContent = data.title;
      const metaSpan = document.createElement("span");
      metaSpan.className = "post-meta";
      metaSpan.textContent = data.author || "Anónimo";
      header.appendChild(titleSpan);
      header.appendChild(metaSpan);

      const bodyDiv = document.createElement("div");
      bodyDiv.className = "post-body";
      bodyDiv.textContent = data.body;

      const repliesDiv = document.createElement("div");
      repliesDiv.className = "reply-list";
      repliesDiv.id = `replies-${postId}`;

      const replyForm = document.createElement("form");
      replyForm.className = "reply-form";
      replyForm.innerHTML = `
        <input type="text" placeholder="Responder..." required>
        <button type="submit" class="btn" style="padding:6px 10px;font-size:12px;">Enviar</button>
      `;
      replyForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const input = replyForm.querySelector("input");
        const text = input.value.trim();
        if (!text) return;
        try {
          await createReply(postId, text);
          input.value = "";
        } catch (err) {
          foroMsg.textContent = "Error al responder: " + err.message;
          foroMsg.classList.add("error");
        }
      });

      postDiv.appendChild(header);
      postDiv.appendChild(bodyDiv);
      postDiv.appendChild(repliesDiv);
      postDiv.appendChild(replyForm);

      postsContainer.appendChild(postDiv);

      listenReplies(postId, repliesDiv);
    });
  });
}

function listenReplies(postId, container) {
  const postRef = doc(db, "posts", postId);
  const q = query(collection(postRef, "replies"), orderBy("createdAt", "asc"));
  onSnapshot(q, (snapshot) => {
    container.innerHTML = "";
    snapshot.forEach((replySnap) => {
      const data = replySnap.data();
      const div = document.createElement("div");
      div.className = "reply-item";
      const meta = document.createElement("div");
      meta.className = "reply-meta";
      meta.textContent = data.author || "Anónimo";
      const body = document.createElement("div");
      body.textContent = data.body;
      div.appendChild(meta);
      div.appendChild(body);
      container.appendChild(div);
    });
  });
}

newPostForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("post-title").value.trim();
  const body = document.getElementById("post-body").value.trim();
  if (!title || !body) return;
  try {
    await createPost(title, body);
    newPostForm.reset();
  } catch (err) {
    foroMsg.textContent = "Error al publicar: " + err.message;
    foroMsg.classList.add("error");
  }
});

