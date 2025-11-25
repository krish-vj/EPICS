// server.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// serve static frontend from /public
app.use(express.static('public'));

// simple REST endpoints (optional) — return current lists
app.get('/api/users', (req, res) => {
  res.json({
    doctors: Object.values(users).filter(u => u.role === 'doctor').map(u => ({ id: u.id, name: u.name })),
    patients: Object.values(users).filter(u => u.role === 'patient').map(u => ({ id: u.id, name: u.name }))
  });
});

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

const users = {}; // socketId -> { id: socketId, name, role }

// Socket.io signaling and presence
io.on('connection', socket => {
  console.log('socket connected', socket.id);

  socket.on('login', ({ name, role }) => {
    users[socket.id] = { id: socket.id, name, role };
    // send updated lists to everyone
    io.emit('users_update', { doctors: listByRole('doctor'), patients: listByRole('patient') });
    console.log('login', name, role, socket.id);
  });

  socket.on('call_user', ({ targetId }) => {
    const caller = users[socket.id];
    const target = users[targetId];
    if (!caller || !target) {
      socket.emit('call_error', { message: 'User not available' });
      return;
    }
    // send incoming call notification to target with caller info
    io.to(targetId).emit('incoming_call', {
      from: socket.id,
      fromName: caller.name,
      fromRole: caller.role
    });
  });

  // Signaling messages for WebRTC
  socket.on('webrtc_offer', ({ targetId, sdp }) => {
    io.to(targetId).emit('webrtc_offer', { from: socket.id, sdp });
  });

  socket.on('webrtc_answer', ({ targetId, sdp }) => {
    io.to(targetId).emit('webrtc_answer', { from: socket.id, sdp });
  });

  socket.on('ice_candidate', ({ targetId, candidate }) => {
    io.to(targetId).emit('ice_candidate', { from: socket.id, candidate });
  });

  socket.on('call_decline', ({ targetId }) => {
    io.to(targetId).emit('call_declined', { from: socket.id });
  });

  socket.on('call_accept', ({ targetId }) => {
    io.to(targetId).emit('call_accepted', { from: socket.id });
  });

  socket.on('hangup', ({ targetId }) => {
    io.to(targetId).emit('hangup', { from: socket.id });
  });

  socket.on('disconnect', () => {
    console.log('disconnect', socket.id);
    delete users[socket.id];
    io.emit('users_update', { doctors: listByRole('doctor'), patients: listByRole('patient') });
  });
});

function listByRole(role) {
  return Object.values(users)
    .filter(u => u.role === role)
    .map(u => ({ id: u.id, name: u.name }));
}

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
