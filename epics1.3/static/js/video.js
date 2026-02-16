const socket = io();

const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");

let pc;
let localStream;
let iceQueue = [];
let isCaller = false;

const config = {
    iceServers: [
        { urls: "stun:stun.l.google.com:19302" }
    ]
};

async function init() {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;
    socket.emit("join_call", { room_id: ROOM_ID });
}

socket.on("start_call", async (data) => {
    isCaller = socket.id === data.caller_sid;
    createPeer();

    if (isCaller) {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        socket.emit("webrtc_offer", { room: ROOM_ID, sdp: offer });
    }
});

socket.on("webrtc_offer", async (sdp) => {
    createPeer();
    await pc.setRemoteDescription(new RTCSessionDescription(sdp));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    socket.emit("webrtc_answer", { room: ROOM_ID, sdp: answer });
});

socket.on("webrtc_answer", async (sdp) => {
    await pc.setRemoteDescription(new RTCSessionDescription(sdp));
    flushIce();
});

socket.on("webrtc_ice", async (candidate) => {
    const ice = new RTCIceCandidate(candidate);
    if (pc.remoteDescription) {
        await pc.addIceCandidate(ice);
    } else {
        iceQueue.push(ice);
    }
});

function createPeer() {
    if (pc) return;

    pc = new RTCPeerConnection(config);

    localStream.getTracks().forEach(t => pc.addTrack(t, localStream));

    pc.ontrack = e => remoteVideo.srcObject = e.streams[0];

    pc.onicecandidate = e => {
        if (e.candidate) {
            socket.emit("webrtc_ice", { room: ROOM_ID, candidate: e.candidate });
        }
    };
}

function flushIce() {
    iceQueue.forEach(c => pc.addIceCandidate(c));
    iceQueue = [];
}

function endCall() {
    socket.emit("end_call", { room: ROOM_ID });
    window.location.href = "/";
}

socket.on("call_ended", () => {
    alert("Call ended");
    window.location.href = "/";
});

init();
