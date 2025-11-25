import React, { useState, useEffect, useRef } from 'react';
import { Video, Phone, PhoneOff, Users, UserCheck, Bell, Settings } from 'lucide-react';
import io from 'socket.io-client';

const App = () => {
  const [serverUrl, setServerUrl] = useState('https://f64e5baa7004.ngrok-free.app');
  const [showSettings, setShowSettings] = useState(false);
  const [connected, setConnected] = useState(false);
  const [userType, setUserType] = useState(null);
  const [userName, setName] = useState('');
  const [userId, setUserId] = useState(null);
  const [users, setUsers] = useState({ doctors: [], patients: [] });
  const [inCall, setInCall] = useState(false);
  const [callerId, setCallerId] = useState(null);
  const [callerName, setCallerName] = useState('');
  const [incomingCall, setIncomingCall] = useState(false);
  const [remoteUserId, setRemoteUserId] = useState(null);
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const localStreamRef = useRef(null);
  const socketRef = useRef(null);

  // Socket.io connection
  useEffect(() => {
    if (!userId) return;

    const socket = io(serverUrl, {
      transports: ['websocket', 'polling']
    });
    
    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
      
      socket.emit('register', {
        userId,
        userName,
        userType
      });
      
      // Request user list immediately
      socket.emit('getUserList');
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
    });

    socket.on('userList', (data) => {
      setUsers(data);
    });

    socket.on('incomingCall', (data) => {
      setIncomingCall(true);
      setCallerId(data.from);
      setCallerName(data.fromName);
    });

    socket.on('callAccepted', async (data) => {
      await createOffer(data.to);
    });

    socket.on('callRejected', () => {
      alert('Call was rejected');
      endCall();
    });

    socket.on('offer', async (data) => {
      await handleOffer(data);
    });

    socket.on('answer', async (data) => {
      await handleAnswer(data);
    });

    socket.on('iceCandidate', async (data) => {
      await handleIceCandidate(data);
    });

    socket.on('callEnded', () => {
      endCall();
    });

    // Request user list periodically
    const interval = setInterval(() => {
      if (socket.connected) {
        socket.emit('getUserList');
      }
    }, 3000);

    return () => {
      clearInterval(interval);
      socket.disconnect();
    };
  }, [userId, userName, userType, serverUrl]);

  const register = () => {
    if (!userName.trim()) {
      alert('Please enter your name');
      return;
    }
    const id = Math.random().toString(36).substr(2, 9);
    setUserId(id);
  };

  const initiateCall = async (targetUserId, targetName) => {
    setRemoteUserId(targetUserId);
    setCallerName(targetName);
    
    if (socketRef.current?.connected) {
      socketRef.current.emit('callUser', {
        from: userId,
        fromName: userName,
        to: targetUserId
      });
    }
    
    await setupMediaAndPeerConnection(targetUserId);
    setInCall(true);
  };

  const acceptCall = async () => {
    setIncomingCall(false);
    setRemoteUserId(callerId);
    setInCall(true);
    
    if (socketRef.current?.connected) {
      socketRef.current.emit('acceptCall', {
        from: userId,
        to: callerId
      });
    }
    
    await setupMediaAndPeerConnection(callerId);
  };

  const rejectCall = () => {
    setIncomingCall(false);
    
    if (socketRef.current?.connected) {
      socketRef.current.emit('rejectCall', {
        from: userId,
        to: callerId
      });
    }
    
    setCallerId(null);
    setCallerName('');
  };

  const setupMediaAndPeerConnection = async (targetId) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      localStreamRef.current = stream;
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }
      
      const config = {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      };
      
      const pc = new RTCPeerConnection(config);
      peerConnectionRef.current = pc;
      
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream);
      });
      
      pc.ontrack = (event) => {
        if (remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = event.streams[0];
        }
      };
      
      pc.onicecandidate = (event) => {
        if (event.candidate && socketRef.current?.connected) {
          socketRef.current.emit('iceCandidate', {
            candidate: event.candidate,
            to: targetId
          });
        }
      };
      
      pc.onconnectionstatechange = () => {
        console.log('Connection state:', pc.connectionState);
        if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
          endCall();
        }
      };
      
    } catch (error) {
      console.error('Error accessing media devices:', error);
      alert('Could not access camera/microphone. Please check permissions.');
      endCall();
    }
  };

  const createOffer = async (targetId) => {
    try {
      const pc = peerConnectionRef.current;
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      
      if (socketRef.current?.connected) {
        socketRef.current.emit('offer', {
          offer: offer,
          from: userId,
          to: targetId
        });
      }
    } catch (error) {
      console.error('Error creating offer:', error);
    }
  };

  const handleOffer = async (data) => {
    try {
      const pc = peerConnectionRef.current;
      await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
      
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      
      if (socketRef.current?.connected) {
        socketRef.current.emit('answer', {
          answer: answer,
          to: data.from
        });
      }
    } catch (error) {
      console.error('Error handling offer:', error);
    }
  };

  const handleAnswer = async (data) => {
    try {
      const pc = peerConnectionRef.current;
      await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
    } catch (error) {
      console.error('Error handling answer:', error);
    }
  };

  const handleIceCandidate = async (data) => {
    try {
      const pc = peerConnectionRef.current;
      if (pc && data.candidate) {
        await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
      }
    } catch (error) {
      console.error('Error handling ICE candidate:', error);
    }
  };

  const endCall = () => {
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
    
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }
    
    if (socketRef.current?.connected && remoteUserId) {
      socketRef.current.emit('endCall', {
        from: userId,
        to: remoteUserId
      });
    }
    
    setInCall(false);
    setRemoteUserId(null);
    setCallerName('');
  };

  // Settings Modal
  if (showSettings) {
    return (
      <div className="min-h-screen bg-gray-900 bg-opacity-90 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Server Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 font-medium mb-2">Server URL</label>
              <input
                type="text"
                value={serverUrl}
                onChange={(e) => setServerUrl(e.target.value)}
                placeholder="http://localhost:3001"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-500 mt-2">
                Use your ngrok URL here (e.g., https://abc123.ngrok.io)
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <button
              onClick={() => setShowSettings(false)}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Login Screen
  if (!userId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <button
          onClick={() => setShowSettings(true)}
          className="absolute top-4 right-4 p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition duration-200"
        >
          <Settings className="w-6 h-6 text-gray-700" />
        </button>
        
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <Video className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Telemedicine Platform</h1>
            <p className="text-gray-600">Connect with healthcare professionals</p>
            <div className="mt-4 flex items-center justify-center gap-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-500">
                {connected ? 'Connected to server' : 'Disconnected'}
              </span>
            </div>
          </div>
          
          {!userType ? (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-700 text-center mb-4">I am a:</h2>
              <button
                onClick={() => setUserType('doctor')}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-3"
              >
                <UserCheck className="w-6 h-6" />
                Doctor
              </button>
              <button
                onClick={() => setUserType('patient')}
                className="w-full bg-teal-600 hover:bg-teal-700 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-3"
              >
                <Users className="w-6 h-6" />
                Patient
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2">Your Name</label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your name"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  onKeyPress={(e) => e.key === 'Enter' && register()}
                />
              </div>
              <button
                onClick={register}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
              >
                Join as {userType === 'doctor' ? 'Doctor' : 'Patient'}
              </button>
              <button
                onClick={() => {setUserType(null); setName('');}}
                className="w-full text-gray-600 hover:text-gray-800 font-medium py-2"
              >
                Back
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Call Screen
  if (inCall) {
    return (
      <div className="min-h-screen bg-gray-900 flex flex-col">
        <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
          <div className="relative bg-gray-800 rounded-lg overflow-hidden">
            <video
              ref={remoteVideoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
            />
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-60 text-white px-4 py-2 rounded-lg">
              {callerName}
            </div>
            <div className="absolute top-4 right-4">
              <div className={`px-3 py-1 rounded-full text-sm ${connected ? 'bg-green-500' : 'bg-red-500'} text-white`}>
                {connected ? '● Live' : '● Disconnected'}
              </div>
            </div>
          </div>
          <div className="relative bg-gray-800 rounded-lg overflow-hidden">
            <video
              ref={localVideoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-60 text-white px-4 py-2 rounded-lg">
              You ({userName})
            </div>
          </div>
        </div>
        <div className="p-6 flex justify-center">
          <button
            onClick={endCall}
            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-4 px-8 rounded-full transition duration-200 flex items-center gap-3"
          >
            <PhoneOff className="w-6 h-6" />
            End Call
          </button>
        </div>
      </div>
    );
  }

  // Incoming Call Notification
  if (incomingCall) {
    return (
      <div className="min-h-screen bg-gray-900 bg-opacity-90 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
          <div className="text-center">
            <Bell className="w-20 h-20 text-indigo-600 mx-auto mb-4 animate-pulse" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Incoming Call</h2>
            <p className="text-gray-600 text-lg mb-8">{callerName} is calling you</p>
            <div className="flex gap-4">
              <button
                onClick={acceptCall}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2"
              >
                <Phone className="w-5 h-5" />
                Accept
              </button>
              <button
                onClick={rejectCall}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-4 px-6 rounded-lg transition duration-200 flex items-center justify-center gap-2"
              >
                <PhoneOff className="w-5 h-5" />
                Decline
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main Dashboard
  const displayUsers = userType === 'doctor' 
    ? [...users.patients, ...users.doctors.filter(d => d.id !== userId)]
    : users.doctors;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <button
        onClick={() => setShowSettings(true)}
        className="fixed top-4 right-4 p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition duration-200 z-50"
      >
        <Settings className="w-6 h-6 text-gray-700" />
      </button>
      
      <div className="container mx-auto p-6">
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                Welcome, {userName}
              </h1>
              <p className="text-gray-600">
                {userType === 'doctor' ? 'Doctor Dashboard' : 'Patient Dashboard'}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-500">
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className={`px-4 py-2 rounded-lg ${userType === 'doctor' ? 'bg-indigo-100 text-indigo-800' : 'bg-teal-100 text-teal-800'}`}>
                {userType === 'doctor' ? '👨‍⚕️ Doctor' : '🧑‍🦱 Patient'}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            {userType === 'doctor' ? 'Patients & Colleagues' : 'Available Doctors'}
          </h2>
          
          {displayUsers.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>No users online at the moment</p>
              <p className="text-sm mt-2">
                {connected ? 'Waiting for users to join...' : 'Please check your connection'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {displayUsers.map(user => (
                <div key={user.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition duration-200">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-800">{user.name}</h3>
                      <p className="text-sm text-gray-600">
                        {user.type === 'doctor' ? '👨‍⚕️ Doctor' : '🧑‍🦱 Patient'}
                      </p>
                    </div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                  <button
                    onClick={() => initiateCall(user.id, user.name)}
                    disabled={!connected}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center justify-center gap-2"
                  >
                    <Phone className="w-4 h-4" />
                    Call
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;