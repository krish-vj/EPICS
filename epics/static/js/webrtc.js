const socket = io();
const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");
const loadingMsg = document.getElementById("loadingMsg");

let localStream;
let pc;
let isInitiator = false;

const config = {
    iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun1.l.google.com:19302" }
    ]
};

console.log("Initializing video call for room:", ROOM_ID);

// Get camera and microphone with proper error handling
async function initMedia() {
    try {
        console.log("Requesting camera and microphone access...");
        
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: true, 
            audio: true 
        });
        
        console.log("✅ Successfully got media stream");
        console.log("Video tracks:", stream.getVideoTracks().length);
        console.log("Audio tracks:", stream.getAudioTracks().length);
        
        localStream = stream;
        localVideo.srcObject = stream;
        
        // Join the room after getting media
        socket.emit("join", { room: ROOM_ID });
        console.log("✅ Joined room:", ROOM_ID);
        
        loadingMsg.textContent = "Waiting for other participant...";
        
    } catch (err) {
        console.error("❌ Error accessing media devices:", err);
        console.error("Error name:", err.name);
        console.error("Error message:", err.message);
        
        // Show specific error messages
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            loadingMsg.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Camera/Microphone Access Denied</h5>
                    <p>Please allow camera and microphone access in your browser settings and reload the page.</p>
                    <button class="btn btn-primary" onclick="location.reload()">Reload Page</button>
                </div>
            `;
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
            loadingMsg.innerHTML = `
                <div class="alert alert-warning">
                    <h5>No Camera/Microphone Found</h5>
                    <p>Please make sure your camera and microphone are connected.</p>
                </div>
            `;
        } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
            loadingMsg.innerHTML = `
                <div class="alert alert-warning">
                    <h5>Camera/Microphone Already in Use</h5>
                    <p>Please close other applications using your camera/microphone and reload.</p>
                    <button class="btn btn-primary" onclick="location.reload()">Reload Page</button>
                </div>
            `;
        } else {
            loadingMsg.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Media Error</h5>
                    <p>${err.message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">Reload Page</button>
                </div>
            `;
        }
    }
}

function createPeerConnection() {
    if (pc) {
        console.log("⚠️ Peer connection already exists");
        return;
    }
    
    console.log("🔗 Creating peer connection");
    pc = new RTCPeerConnection(config);

    // Add local tracks to peer connection
    localStream.getTracks().forEach(track => {
        console.log("➕ Adding track:", track.kind);
        pc.addTrack(track, localStream);
    });

    // Handle incoming tracks
    pc.ontrack = event => {
        console.log("📥 Received remote track:", event.track.kind);
        if (event.streams && event.streams[0]) {
            remoteVideo.srcObject = event.streams[0];
            loadingMsg.style.display = "none";
            console.log("✅ Remote video stream connected");
        }
    };

    // Handle ICE candidates
    pc.onicecandidate = event => {
        if (event.candidate) {
            console.log("🧊 Sending ICE candidate");
            socket.emit("ice_candidate", {
                room: ROOM_ID,
                candidate: event.candidate
            });
        } else {
            console.log("🧊 All ICE candidates sent");
        }
    };

    // Handle connection state changes
    pc.onconnectionstatechange = () => {
        console.log("🔌 Connection state:", pc.connectionState);
        if (pc.connectionState === "connected") {
            loadingMsg.style.display = "none";
            console.log("✅ WebRTC connection established!");
        } else if (pc.connectionState === "failed") {
            loadingMsg.innerHTML = `
                <div class="alert alert-danger">
                    Connection failed. Please try again.
                    <button class="btn btn-sm btn-primary" onclick="location.reload()">Reload</button>
                </div>
            `;
        } else if (pc.connectionState === "disconnected") {
            loadingMsg.textContent = "Connection lost. Reconnecting...";
            loadingMsg.style.display = "block";
        }
    };

    pc.oniceconnectionstatechange = () => {
        console.log("❄️ ICE connection state:", pc.iceConnectionState);
    };

    pc.onicegatheringstatechange = () => {
        console.log("🔍 ICE gathering state:", pc.iceGatheringState);
    };
}

// First user becomes the caller
socket.on("ready", async () => {
    console.log("📞 Received ready signal - becoming caller");
    isInitiator = true;
    createPeerConnection();
    
    try {
        // Create and send offer
        const offer = await pc.createOffer();
        console.log("📝 Created offer");
        await pc.setLocalDescription(offer);
        console.log("✅ Set local description (offer)");
        
        socket.emit("offer", { 
            room: ROOM_ID, 
            offer: pc.localDescription 
        });
        console.log("📤 Sent offer to room");
    } catch (err) {
        console.error("❌ Error creating offer:", err);
        loadingMsg.innerHTML = `
            <div class="alert alert-danger">
                Error establishing connection: ${err.message}
            </div>
        `;
    }
});

// Second user receives offer and sends answer
socket.on("offer", async data => {
    console.log("📥 Received offer");
    createPeerConnection();
    
    try {
        await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
        console.log("✅ Set remote description (offer)");
        
        const answer = await pc.createAnswer();
        console.log("📝 Created answer");
        await pc.setLocalDescription(answer);
        console.log("✅ Set local description (answer)");
        
        socket.emit("answer", { 
            room: ROOM_ID, 
            answer: pc.localDescription 
        });
        console.log("📤 Sent answer to room");
    } catch (err) {
        console.error("❌ Error handling offer:", err);
        loadingMsg.innerHTML = `
            <div class="alert alert-danger">
                Error establishing connection: ${err.message}
            </div>
        `;
    }
});

// Caller receives answer
socket.on("answer", async data => {
    console.log("📥 Received answer");
    try {
        await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
        console.log("✅ Set remote description (answer)");
    } catch (err) {
        console.error("❌ Error setting remote description:", err);
    }
});

// Handle ICE candidates from remote peer
socket.on("ice_candidate", async data => {
    console.log("📥 Received ICE candidate");
    try {
        if (pc && data.candidate) {
            await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
            console.log("✅ Added ICE candidate");
        }
    } catch (err) {
        console.error("❌ Error adding ICE candidate:", err);
    }
});

// Handle user left
socket.on("user_left", () => {
    console.log("👋 Remote user left");
    loadingMsg.textContent = "Remote user disconnected";
    loadingMsg.style.display = "block";
});

// End call function
function endCall() {
    console.log("📴 Ending call");
    socket.emit("end_call", { room: ROOM_ID });
    cleanup();
}

// Handle call ended by remote user
socket.on("call_ended", () => {
    console.log("📴 Call ended by remote user");
    cleanup();
});

function cleanup() {
    if (pc) {
        pc.close();
        pc = null;
    }
    if (localStream) {
        localStream.getTracks().forEach(track => {
            track.stop();
            console.log("🛑 Stopped track:", track.kind);
        });
    }
    setTimeout(() => {
        window.location.href = "/";
    }, 500);
}

// Handle socket connection events
socket.on("connect", () => {
    console.log("🔌 Socket connected:", socket.id);
});

socket.on("disconnect", () => {
    console.log("🔌 Socket disconnected");
});

socket.on("connect_error", (error) => {
    console.error("❌ Socket connection error:", error);
    loadingMsg.innerHTML = `
        <div class="alert alert-danger">
            Connection error. Please check your internet connection.
        </div>
    `;
});

// Start the initialization
console.log("🚀 Starting media initialization...");
initMedia();