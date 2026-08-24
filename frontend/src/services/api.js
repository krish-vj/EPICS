import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const authService = {
  login: async (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const response = await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  }
};

export const patientService = {
  getDoctors: async (specialisation = '') => {
    const response = await api.get(`/patient/doctors${specialisation ? `?specialisation=${specialisation}` : ''}`);
    return response.data;
  },
  bookAppointment: async (appointmentData) => {
    const response = await api.post('/patient/appointments', appointmentData);
    return response.data;
  }
};

export const doctorService = {
  getAppointments: async () => {
    const response = await api.get('/doctor/appointments');
    return response.data;
  },
  submitNotes: async (appointmentId, notesData) => {
    const response = await api.post(`/doctor/appointments/${appointmentId}/complete`, notesData);
    return response.data;
  }
};

export const adminService = {
  createDoctorProfile: async (profileData) => {
    const response = await api.post('/admin/doctors', profileData);
    return response.data;
  },
  updateLeave: async (doctorId, leaveDays) => {
    const response = await api.put(`/admin/doctors/${doctorId}/leave`, { leave_days: leaveDays });
    return response.data;
  }
};

export default api;
