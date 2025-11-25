// app.js - client-side
const socket = io();

let myId = null;
let myName = null;
let myRole = null;

const pcConfig = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
};

let localStream = null;
let pc = null;
let currentCallTarget = null;

const loginScreen = document.getElementById('login-screen');
const mainScreen = document.getElementById('main-screen');
const nameInput = document.getElementById('name');
const btnLogin = document.getElementById('btnLogin');
const btnLogout = document.getElementById('btnLogout');
const meInfo = document.getElementById('meInfo');

const doctorsList = document.getElementById('doctorsList');
const patientsList = document.getElementById('patientsList');

const incomingPrompt = document.getElementById('incomingPrompt');
const incomingText = document.getElementById('incomingText');
const acceptBtn = document.getElementById('acceptBtn');
const declineBtn = document.getElementById('declineBtn');

const videoArea = document.getElementById('videoArea');
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const hangupBtn = document.getElementById('hangupBtn');

btnLogin.onclick = async () => {
  const name = nameInput.value.trim();
  const role = document.querySelector('input[name="role"]:checked').value;
  if (!name) return alert('Enter name');
  myName = name;
  myRole = role;
  socket.emit('login', { name, role });
  loginScreen.style.display = 'none';
  mainScreen.style.display = '';
  meInfo.innerText = `${name} (${role})`;
};

// logout simply reloads
btnLogout.onclick = () => location.reload();

// render lists: patients see only doctors; doctors see both
socket.on('users_update', ({ doctors, patients }) => {
  // store myId from socket
  myId = socket.id;
  renderUsers(doctors, patients);
});

function renderUsers(doctors, patients) {
  doctorsList.innerHTML = '';
  patientsList.innerHTML = '';

  function addTo(listEl, user) {
    const li = document.createElement('li');
    li.innerHTML = `<span>${escapeHtml(user.name)}</span>`;
    const btn = document.createElement('button');
    btn.className = 'call-btn';
    btn.innerHTML = '📹';
    btn.title = 'Call';
    btn.onclick = () => startCall(user.id);
    // disable calling self
    if (user.id === myId) btn.disabled = true;
    li.appendChild(btn);
    listEl.appendChild(li);
  }

  doctors.forEach(d => addTo(doctorsList, d));

  // patients list: only visible to doctors
  if (myRole === 'doctor') {
    patients.forEach(p => addTo(patientsList, p));
  } else {
    // keep list empty if patient (or show message)
    patientsList.innerHTML = '<li style="color:#777;padding:8px">(Patients are hidden)</li>';
  }
}

function startCall(targetId) {
  if (!targetId) return;
  // request the other side to show incoming call
  socket.emit('call_user', { targetId });
  // we'll wait for call accepted and then do WebRTC negotiation
  currentCallTarget = targetId;
  showToast('Calling...');
}

// incoming call prompt
let lastIncomingFrom = null;
socket.on('incoming_call', ({ from, fromName, fromRole }) => {
  lastIncomingFrom = from;
  incomingPrompt.style.display = '';
  incomingText.innerText = `Incoming call from ${fromName} (${fromRole})`;
});

// accept/decline handling
acceptBtn.onclick = async () => {
  incomingPrompt.style.display = 'none';
  if (!lastIncomingFrom) return;
  currentCallTarget = lastIncomingFrom;
  socket.emit('call_accept', { targetId: currentCallTarget });
  await startLocalMedia();
  await createPeerConnection();

  // as callee, wait for offer; we'll handle webrtc_offer event to setRemote and createAnswer
};

declineBtn.onclick = () => {
  incomingPrompt.style.display = 'none';
  if (!lastIncomingFrom) return;
  socket.emit('call_decline', { targetId: lastIncomingFrom });
  lastIncomingFrom = null;
};

socket.on('call_declined', ({ from }) => {
  if (from === currentCallTarget) {
    showToast('Call declined');
    currentCallTarget = null;
  }
});

socket.on('call_accepted', async ({ from }) => {
  // other side accepted, so caller should start WebRTC offer
  if (from === currentCallTarget) {
    await startLocalMedia();
    await createPeerConnection();
    // create offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    socket.emit('webrtc_offer', { targetId: currentCallTarget, sdp: offer });
  }
});

// Signaling: caller receives answer, callee receives offer
socket.on('webrtc_offer', async ({ from, sdp }) => {
  // only proceed if we are the callee (or if we accepted)
  if (from !== currentCallTarget) {
    // optionally set currentCallTarget = from
    currentCallTarget = from;
  }
  if (!pc) {
    await startLocalMedia();
    await createPeerConnection();
  }
  await pc.setRemoteDescription(new RTCSessionDescription(sdp));
  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);
  socket.emit('webrtc_answer', { targetId: from, sdp: answer });
});

socket.on('webrtc_answer', async ({ from, sdp }) => {
  if (!pc) return;
  await pc.setRemoteDescription(new RTCSessionDescription(sdp));
});

socket.on('ice_candidate', async ({ from, candidate }) => {
  if (pc && candidate) {
    try { await pc.addIceCandidate(candidate); } catch (e) { console.warn('ICE add err', e); }
  }
});

socket.on('hangup', ({ from }) => {
  endCall();
  showToast('Call ended');
});

hangupBtn.onclick = () => {
  if (currentCallTarget) {
    socket.emit('hangup', { targetId: currentCallTarget });
  }
  endCall();
};

// helper: get local media
async function startLocalMedia() {
  if (localStream) return;
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;
  } catch (e) {
    alert('Could not access camera/microphone: ' + e.message);
  }
}

// create PeerConnection and wire tracks + ICE
async function createPeerConnection() {
  pc = new RTCPeerConnection(pcConfig);

  // add local tracks
  if (localStream) {
    for (const t of localStream.getTracks()) pc.addTrack(t, localStream);
  }

  pc.onicecandidate = (ev) => {
    if (ev.candidate && currentCallTarget) {
      socket.emit('ice_candidate', { targetId: currentCallTarget, candidate: ev.candidate });
    }
  };

  pc.ontrack = (ev) => {
    // first track set remote stream
    remoteVideo.srcObject = ev.streams[0];
    showVideoArea();
  };

  pc.onconnectionstatechange = () => {
    if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed' || pc.connectionState === 'closed') {
      endCall();
    }
  };

  showVideoArea();
}

// teardown
function endCall() {
  if (pc) {
    try { pc.close(); } catch (e) {}
    pc = null;
  }
  if (localStream) {
    for (const t of localStream.getTracks()) t.stop();
    localStream = null;
    localVideo.srcObject = null;
  }
  remoteVideo.srcObject = null;
  videoArea.style.display = 'none';
  currentCallTarget = null;
}

// visuals
function showVideoArea() {
  videoArea.style.display = '';
  incomingPrompt.style.display = 'none';
}

// small toast
function showToast(msg) {
  console.log(msg);
  // simple in-page message (could be improved)
  const el = document.createElement('div');
  el.innerText = msg;
  el.style.position = 'fixed';
  el.style.bottom = '20px';
  el.style.right = '20px';
  el.style.background = '#111';
  el.style.color = '#fff';
  el.style.padding = '8px 12px';
  el.style.borderRadius = '6px';
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2500);
}

// escape HTML helper
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (m) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
}
