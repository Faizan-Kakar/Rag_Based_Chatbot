const chatBox = document.getElementById("chatBox");
let sessions = {}; // {sessionId: [messages]}
let currentSession = null;

// Switch between login & signup
function toggleAuth(type) {
  document.getElementById("authTitle").innerText = type === "login" ? "Login" : "Signup";
  document.getElementById("loginForm").style.display = type === "login" ? "block" : "none";
  document.getElementById("signupForm").style.display = type === "signup" ? "block" : "none";
}

//Websocket connection function
let socket;
function connectWebSocket(userId) {
  socket = new WebSocket(`ws://localhost:8000/ws/${userId}`);

  // 🔹 Handshake success
  socket.onopen = () => {
    console.log("✅ WebSocket connected");
    socket.send(JSON.stringify({
    event: "ping",
    payload: "Message from client"
  }));
  };

  // 🔹 Listen for events
  socket.onmessage = (event) => {

    const message = JSON.parse(event.data);
    if (message.event === "response") {

      if(message.payload.success){
        localStorage.setItem("session_id", message.payload.session_id);
      if (!message.payload.session_names == "") {
        const sessionList = document.getElementById("sessionList");
        const sessionDiv = document.createElement("div");
        sessionDiv.classList.add("session-item");
        sessionDiv.innerText = message.payload.session_names;
        sessionDiv.dataset.sessionId = message.payload.session_id;
        sessionDiv.onclick = () => loadSession(message.payload.session_id);
        sessionList.prepend(sessionDiv);
        highlightActiveSession(message.payload.session_id);
      }
      addMessage(message.payload.answer, "bot");
      console.log("💬 Bot:", message.payload.answer);
     }
     else{
      addMessage("⚠️ No response", "bot");
     }
    }
    else if (message.event === "ping") {
      console.log("💓 Pong from server");
}
  }
  // 🔹 When connection closes
  socket.onclose = () => {
    console.log("❌ WebSocket closed");
  };

  // 🔹 On error
  socket.onerror = (error) => {
    console.error("⚠️ WebSocket error:", error);
  };
}

// 🔹 Send an event (custom)
function sendQuestion(query, sessionId) {
  socket.send(JSON.stringify({
    event: "ask",
    payload: {
        querry: query,
        session_id: sessionId,
        userID: localStorage.getItem("userID")
      }
  }));
}


// Signup
async function signup() {
  const name = document.getElementById("signupName").value.trim();
  const userID = document.getElementById("signupEmail").value.trim();
  const password = document.getElementById("signupPassword").value.trim();

  if (!name || !userID || !password) {
    alert("Please fill all fields");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/auth/signUp", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ name, userID, password })
    });

    const data = await response.json();
    if (data.success) {
      alert("User Created Successfully");
      toggleAuth("login");
    } else {
      alert(data.message || "Signup failed");
    }
  } catch (error) {
    alert("⚠️ Error during signup");
  }
}

// Login
async function login() {
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value.trim();

  if (!email || !password) {
    alert("Please enter email and password");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/auth/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ userID: email, password })
    });

    const data = await response.json();
    if (data.success) {
      localStorage.setItem("authToken", data.token);
      localStorage.setItem("session_id", "");
      localStorage.setItem("userID", data.userID);

      document.getElementById("authContainer").style.display = "none";
      document.getElementById("mainContainer").style.display = "flex";

      loadSessionsFromAPI();
      // 🔹 Call this after login
      connectWebSocket(data.userID);

      // createNewSession();
    } else {
      alert(data.message || "Login failed");
    }
  } catch (error) {
    alert("⚠️ Error during login");
  }
}

// Fetch sessions from backend
async function loadSessionsFromAPI() {
  try {
    const response = await fetch(`http://127.0.0.1:8000/get_sessions?userID=${encodeURIComponent(localStorage.getItem("userID"))}`, {
      method: "GET",
      headers: {
        // "Authorization": "Bearer " + localStorage.getItem("authToken"),
        "Content-Type": "application/json"
      }
    });

    const data = await response.json();
    if (data.success) {
      const sessionList = document.getElementById("sessionList");
      sessionList.innerHTML = ""; // clear old list

      data.sessions.forEach(session => {
        const sessionDiv = document.createElement("div");
        sessionDiv.classList.add("session-item");
        sessionDiv.innerText = session.session_name;  // session name from API
        sessionDiv.dataset.sessionId = session.session_id;

        sessionDiv.onclick = () => loadSession(session.session_id);
        sessionList.appendChild(sessionDiv);

        // keep a local object reference too
        sessions[session.session_id] = [];
      });

      // highlight the first session if available
      // if (data.sessions.length > 0) {
      //   loadSession(data.sessions[0].session_id);
      // }
    } else {
      alert(data.message || "Failed to load sessions");
    }
  } catch (err) {
    console.error("⚠️ Error fetching sessions:", err);
  }
}

// Sessions
function createNewSession() {
  // const sessionId = Date.now().toString();
  // sessions[sessionId] = [];
  // currentSession = sessionId;

  // const sessionList = document.getElementById("sessionList");
  // const sessionDiv = document.createElement("div");
  // sessionDiv.classList.add("session-item");
  // sessionDiv.innerText = "Session " + Object.keys(sessions).length;
  // sessionDiv.dataset.sessionId = sessionId;

  // sessionDiv.onclick = () => loadSession(sessionId);
  // sessionList.appendChild(sessionDiv);

  // highlightActiveSession(sessionId);
  // loadSession(sessionId);
  // 1. Clear chatbox
    const chatBox = document.getElementById("chatBox"); // replace with your chat container id
    chatBox.innerHTML = "";

    // 2. Remove active highlight from all sessions
    const allSessions = document.querySelectorAll(".session-item"); // adjust class name
    allSessions.forEach(session => session.classList.remove("active"));

    // 3. Reset session_id in localStorage
    localStorage.setItem("session_id", "");

    console.log("New chat started: chatbox cleared, no session highlighted, session_id reset");
}

// function loadSession(sessionId) {
//   currentSession = sessionId;
//   chatBox.innerHTML = "";
//   sessions[sessionId].forEach(msg => {
//     addMessage(msg.text, msg.sender, false);
//   });
//   highlightActiveSession(sessionId);
// }

async function loadSession(sessionId) {
  currentSession = sessionId;
  localStorage.setItem("session_id", sessionId);
  chatBox.innerHTML = ""; // clear old chat

  try {
    const response = await fetch(`http://127.0.0.1:8000/get_session_chats?session_id=${sessionId}`, {
      method: "GET",
      headers: {
        // "Authorization": "Bearer " + localStorage.getItem("authToken"),
        "Content-Type": "application/json"
      }
    });

    const data = await response.json();
    if (data.success) {
      // Display each chat
      data.chats.forEach(chat => {
        addMessage(chat.content, chat.role === "user" ? "user" : "bot", false);
      });
    } else {
      addMessage("⚠️ No chats found for this session", "bot");
    }
  } catch (err) {
    console.error("⚠️ Error fetching chats:", err);
    addMessage("⚠️ Error loading chats", "bot");
  }

  highlightActiveSession(sessionId);
}


function highlightActiveSession(sessionId) {
  document.querySelectorAll(".session-item").forEach(item => {
    item.classList.remove("active");
    if (item.dataset.sessionId === sessionId) {
      item.classList.add("active");
    }
  });
}

// Messages
function addMessage(text, sender, save = true) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
  messageDiv.innerText = text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (save && currentSession) {
    sessions[currentSession].push({ text, sender });
  }
}

// Send Message
async function sendMessage() {
  const userInput = document.getElementById("userInput");
  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  userInput.value = "";

  try {
    // const response = await fetch("http://127.0.0.1:8000/ask", {
    //   method: "POST",
    //   headers: {"Content-Type": "application/json"},
    //   body: JSON.stringify({
    //     querry: text,
    //     session_id: localStorage.getItem("session_id"),
    //     userID: localStorage.getItem("userID")
    //   })
    // });
    console.log("This is running");
    sendQuestion(text, localStorage.getItem("session_id"))

    // const data = await response.json();
    // if (data.success) {
      // localStorage.setItem("session_id", data.session_id);
      // if (!data.session_names == "") {
      //   const sessionList = document.getElementById("sessionList");
      //   const sessionDiv = document.createElement("div");
      //   sessionDiv.classList.add("session-item");
      //   sessionDiv.innerText = data.session_names;
      //   sessionDiv.dataset.sessionId = data.session_id;
      //   sessionDiv.onclick = () => loadSession(data.session_id);
      //   sessionList.prepend(sessionDiv);
      //   highlightActiveSession(data.session_id);
      // }
      // addMessage(data.answer, "bot");
    // } else {
    //   addMessage("⚠️ No response", "bot");
    // }
    // }
  } catch (err) {
    addMessage("⚠️ Error connecting to backend", "bot");
  }
}

// Upload Document
async function uploadDoc() {
  const fileInput = document.getElementById("docInput");
  if (fileInput.files.length === 0) {
    alert("Please select a file to upload.");
    return;
  }
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://127.0.0.1:8000/upload_doc", {
      method: "POST",
      headers: { "Authorization": "Bearer " + localStorage.getItem("authToken") },
      body: formData
    });

    const data = await response.json();
    alert("File Successfully uploaded: " + data.filename);
  } catch (error) {
    alert("⚠️ Upload failed");
  }
}
