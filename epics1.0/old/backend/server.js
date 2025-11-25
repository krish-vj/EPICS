const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);

// Configure CORS for both Express and Socket.io
app.use(cors());
app.use(express.json());

const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Store connected users
const users = {
  doctors: new Map(),
  patients: new Map()
};

// Helper to get user list
const getUserList = () => ({
  doctors: Array.from(users.doctors.values()),
  patients: Array.from(users.patients.values())
});

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log('New client connected:', socket.id);

  // Register user
  socket.on('register', (data) => {
    const { userId, userName, userType } = data;
    
    const userInfo = {
      id: userId,
      name: userName,
      type: userType,
      socketId: socket.id
    };

    // Store user in appropriate pool
    if (userType === 'doctor') {
      users.doctors.set(userId, userInfo);
    } else {
      users.patients.set(userId, userInfo);
    }

    socket.userId = userId;
    socket.userType = userType;

    console.log(`User registered: ${userName} (${userType})`);
    
    // Broadcast updated user list to all clients
    io.emit('userList', getUserList());
  });

  // Request user list
  socket.on('getUserList', () => {
    socket.emit('userList', getUserList());
  });

  // Call user
  socket.on('callUser', (data) => {
    const { from, fromName, to } = data;
    
    // Find target user's socket
    const targetUser = users.doctors.get(to) || users.patients.get(to);
    
    if (targetUser) {
      io.to(targetUser.socketId).emit('incomingCall', {
        from,
        fromName
      });
      console.log(`Call initiated: ${fromName} -> ${targetUser.name}`);
    }
  });

  // Accept call
  socket.on('acceptCall', (data) => {
    const { from, to } = data;
    
    const targetUser = users.doctors.get(to) || users.patients.get(to);
    
    if (targetUser) {
      io.to(targetUser.socketId).emit('callAccepted', {
        from,
        to
      });
      console.log(`Call accepted: ${from} <-> ${to}`);
    }
  });

  // Reject call
  socket.on('rejectCall', (data) => {
    const { from, to } = data;
    
    const targetUser = users.doctors.get(to) || users.patients.get(to);
    
    if (targetUser) {
      io.to(targetUser.socketId).emit('callRejected', {
        from
      });
      console.log(`Call rejected: ${from} -> ${to}`);
    }
  });

  // WebRTC signaling: offer
  socket.on('offer', (data) => {
    const { offer, from, to } = data;
    
    const targetUser = users.doctors.get(to) || users.patients.get(to);
    
    if (targetUser) {
      io.to(targetUser.socketId).emit('offer', {
        offer,
        from
      });
      console.log(`Offer sent: ${from} -> ${to}`);
    }
  });

  // WebRTC signaling: answer
  socket.on('answer', (data) => {
    const { answer, to } = data;
    
    const targetUser = users.doctors.get(to) || users.patients.get(to);
    
    if (targetUser) {
      io.to(targetUser.socketId).emit('answer', {
        answer
      });
      console.log(`Answer sent to: ${to}`);
    }
  });

  // WebRTC signaling: ICE candidate
  socket.on('iceCandidate', (data) => {
    const { candidate, to } = data;
    
    const targetUser = users.doctors.get(to) || users.patients.get(to);
    
    if (targetUser) {
      io.to(targetUser.socketId).emit('iceCandidate', {
        candidate
      });
    }
  });

  // End call
  socket.on('endCall', (data) => {
    const { from, to } = data;
    
    const targetUser = users.doctors.get(to) || users.patients.get(to);
    
    if (targetUser) {
      io.to(targetUser.socketId).emit('callEnded', {
        from
      });
      console.log(`Call ended: ${from} -> ${to}`);
    }
  });

  // Handle disconnect
  socket.on('disconnect', () => {
    if (socket.userId) {
      // Remove user from appropriate pool
      users.doctors.delete(socket.userId);
      users.patients.delete(socket.userId);
      
      console.log(`User disconnected: ${socket.userId}`);
      
      // Broadcast updated user list
      io.emit('userList', getUserList());
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    users: {
      doctors: users.doctors.size,
      patients: users.patients.size
    }
  });
});

// Get users endpoint (optional REST API)
app.get('/api/users', (req, res) => {
  res.json(getUserList());
});

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Access via: http://localhost:${PORT}`);
});