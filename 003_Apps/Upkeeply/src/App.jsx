import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Chat from './pages/Chat';
import Tasks from './pages/Tasks';
import Assets from './pages/Assets';
import Login from './pages/Login';
import Profile from './pages/Profile';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import DevicePreview from './components/DevicePreview';

function PrivateRoute({ children }) {
  const { currentUser } = useAuth();
  return currentUser ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <DevicePreview>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }>
              <Route path="/" element={<Chat />} />
              <Route path="/tasks" element={<Tasks />} />
              <Route path="/assets" element={<Assets />} />
              <Route path="/profile" element={<Profile />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </DevicePreview>
  )
}

export default App
