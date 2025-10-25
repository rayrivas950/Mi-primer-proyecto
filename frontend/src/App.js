import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ContactForm from './components/ContactForm';
import LoginForm from './components/LoginForm';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Verificar si hay un token al cargar la aplicación
    if (localStorage.getItem('access_token')) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsLoggedIn(false);
  };

  return (
    <div>
      <Header />
      <h1>Hello, React!</h1>
      {isLoggedIn ? (
        <div>
          <button onClick={handleLogout}>Cerrar Sesión</button>
          <ContactForm />
        </div>
      ) : (
        <LoginForm onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;
