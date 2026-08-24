import React, { useState, useEffect } from 'react';
import { authService, patientService, doctorService } from './services/api';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [view, setView] = useState('patient_dashboard');

  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [symptoms, setSymptoms] = useState('');
  const [startTime, setStartTime] = useState('');
  const [bookingMessage, setBookingMessage] = useState(null);

  const [appointments, setAppointments] = useState([]);
  const [activeAppointment, setActiveAppointment] = useState(null);
  const [postNotes, setPostNotes] = useState('');
  const [medicationName, setMedicationName] = useState('');
  const [dosage, setDosage] = useState('');
  const [frequency, setFrequency] = useState('');
  const [medicationsList, setMedicationsList] = useState([]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await authService.login(email, password);
      setToken(localStorage.getItem('token'));
      alert('Login successful!');
    } catch (err) {
      alert('Login failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleBook = async (e) => {
    e.preventDefault();
    try {
      const res = await patientService.bookAppointment({
        doctor_id: selectedDoctor,
        start_time: new Date(startTime).toISOString(),
        symptoms: symptoms
      });
      setBookingMessage(`Appointment booked successfully! AI Urgency: ${res.pre_visit_summary?.urgency}`);
    } catch (err) {
      alert('Booking failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  useEffect(() => {
    if (token) {
      patientService.getDoctors().then(setDoctors).catch(console.error);
      doctorService.getAppointments().then(setAppointments).catch(console.error);
    }
  }, [token]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-6">
      <header className="max-w-4xl mx-auto mb-8 flex justify-between items-center border-b pb-4">
        <h1 className="text-2xl font-bold text-blue-600">Healthcare Appointment & Follow-up Manager</h1>
        {token && (
          <button 
            onClick={() => { authService.logout(); setToken(null); }}
            className="bg-red-500 text-white px-4 py-2 rounded text-sm hover:bg-red-600"
          >
            Logout
          </button>
        )}
      </header>

      <main className="max-w-4xl mx-auto">
        {!token ? (
          <div className="bg-white p-6 rounded-lg shadow max-w-md mx-auto">
            <h2 className="text-xl font-semibold mb-4">Sign In</h2>
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium">Email Address</label>
                <input 
                  type="email" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  className="w-full border p-2 rounded mt-1" 
                  required 
                />
              </div>
              <div>
                <label className="block text-sm font-medium">Password</label>
                <input 
                  type="password" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  className="w-full border p-2 rounded mt-1" 
                  required 
                />
              </div>
              <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
                Sign In
              </button>
            </form>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex space-x-4 border-b pb-2">
              <button onClick={() => setView('patient_dashboard')} className={`font-medium ${view === 'patient_dashboard' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}>
                Patient Portal
              </button>
              <button onClick={() => setView('doctor_dashboard')} className={`font-medium ${view === 'doctor_dashboard' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}>
                Doctor Portal
              </button>
            </div>

            {view === 'patient_dashboard' && (
              <div className="bg-white p-6 rounded-lg shadow space-y-4">
                <h2 className="text-xl font-semibold">Book an Appointment & Submit Symptoms</h2>
                {bookingMessage && <div className="p-3 bg-green-100 text-green-700 rounded">{bookingMessage}</div>}
                <form onSubmit={handleBook} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium">Select Doctor Profile</label>
                    <select 
                      onChange={(e) => setSelectedDoctor(e.target.value)} 
                      className="w-full border p-2 rounded mt-1"
                      required
                    >
                      <option value="">-- Choose Doctor --</option>
                      {doctors.map(doc => (
                        <option key={doc.id} value={doc.id}>ID: {doc.id} - {doc.specialisation} (Slot: {doc.slot_duration_mins}m)</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Appointment Date & Time</label>
                    <input 
                      type="datetime-local" 
                      value={startTime} 
                      onChange={(e) => setStartTime(e.target.value)} 
                      className="w-full border p-2 rounded mt-1" 
                      required 
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium">Describe Your Symptoms (AI Pre-visit Analysis)</label>
                    <textarea 
                      value={symptoms} 
                      onChange={(e) => setSymptoms(e.target.value)} 
                      className="w-full border p-2 rounded mt-1" 
                      rows="3"
                      placeholder="e.g., Severe migraine with sensitivity to light..."
                      required 
                    />
                  </div>
                  <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Confirm Booking & Run AI Summary
                  </button>
                </form>
              </div>
            )}

            {view === 'doctor_dashboard' && (
              <div className="bg-white p-6 rounded-lg shadow space-y-4">
                <h2 className="text-xl font-semibold">Doctor Appointment Queue & Post-Visit Summary</h2>
                <div className="space-y-2">
                  {appointments.map(app => (
                    <div key={app.id} className="border p-4 rounded flex justify-between items-center">
                      <div>
                        <p className="font-semibold">Patient ID: {app.patient_id} | Time: {new Date(app.start_time).toLocaleString()}</p>
                        <p className="text-sm text-gray-600">Symptoms: {app.symptoms}</p>
                        {app.pre_visit_summary && (
                          <div className="mt-2 text-xs bg-yellow-50 p-2 rounded border border-yellow-200">
                            <span className="font-bold text-yellow-800">AI Urgency: {app.pre_visit_summary.urgency}</span> | 
                            <span> Chief Complaint: {app.pre_visit_summary.chief_complaint}</span>
                          </div>
                        )}
                      </div>
                      <button 
                        onClick={() => setActiveAppointment(app.id)}
                        className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                      >
                        Complete Visit
                      </button>
                    </div>
                  ))}
                </div>

                {activeAppointment && (
                  <div className="border-t pt-4 mt-4 space-y-3">
                    <h3 className="font-medium text-lg">Submit Clinical Notes for Appointment #{activeAppointment}</h3>
                    <textarea 
                      value={postNotes} 
                      onChange={(e) => setPostNotes(e.target.value)} 
                      placeholder="Enter clinical observations and advice..."
                      className="w-full border p-2 rounded" 
                      rows="3"
                    />
                    <div className="flex space-x-2">
                      <input type="text" placeholder="Medication Name" value={medicationName} onChange={(e) => setMedicationName(e.target.value)} className="border p-2 rounded flex-1" />
                      <input type="text" placeholder="Dosage" value={dosage} onChange={(e) => setDosage(e.target.value)} className="border p-2 rounded w-28" />
                      <input type="text" placeholder="Frequency" value={frequency} onChange={(e) => setFrequency(e.target.value)} className="border p-2 rounded w-36" />
                      <button 
                        type="button" 
                        onClick={() => {
                          setMedicationsList([...medicationsList, { name: medicationName, dosage, frequency }]);
                          setMedicationName(''); setDosage(''); setFrequency('');
                        }}
                        className="bg-gray-200 px-3 rounded"
                      >
                        Add Med
                      </button>
                    </div>
                    <ul className="list-disc pl-5 text-sm">
                      {medicationsList.map((m, idx) => <li key={idx}>{m.name} - {m.dosage} ({m.frequency})</li>)}
                    </ul>
                    <button 
                      onClick={async () => {
                        try {
                          await doctorService.submitNotes(activeAppointment, {
                            post_visit_notes: postNotes,
                            medications: medicationsList,
                            next_follow_up_date: new Date(Date.now() + 7*24*60*60*1000).toISOString().split('T')[0]
                          });
                          alert('Post-visit notes and summary generated successfully!');
                          setActiveAppointment(null);
                        } catch (err) {
                          alert('Error: ' + (err.response?.data?.detail || err.message));
                        }
                      }}
                      className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                      Finalize & Generate Patient-Friendly Summary
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
