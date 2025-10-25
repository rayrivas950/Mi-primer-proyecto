import React, { useState } from 'react';

function ContactForm() {
  // 1. Un solo objeto de estado para todos los campos del formulario
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });

  // 2. Manejador de cambio genérico para todos los campos
  const handleChange = (e) => {
    const { id, value } = e.target; // 'id' del input corresponde a la clave en formData
    setFormData(prevFormData => ({
      ...prevFormData, // Mantiene los otros campos sin cambios
      [id]: value       // Actualiza solo el campo que cambió
    }));
  };

  // 3. Manejador del envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault(); // Evita que la página se recargue
    
    try {
      const response = await fetch('http://127.0.0.1:5000/contactos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al agregar contacto');
      }

      const result = await response.json();
      console.log('Contacto agregado con éxito:', result);
      alert('Contacto agregado con éxito!');

      // Limpiar campos después del envío
      setFormData({
        name: '',
        email: '',
        phone: ''
      });

    } catch (error) {
      console.error('Error al enviar el formulario:', error.message);
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Añadir Nuevo Contacto</h2>
      <div>
        <label htmlFor="name">Nombre:</label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label htmlFor="phone">Teléfono:</label>
        <input
          type="tel"
          id="phone"
          value={formData.phone}
          onChange={handleChange}
        />
      </div>
      <button type="submit">Guardar Contacto</button>
    </form>
  );
}

export default ContactForm;
