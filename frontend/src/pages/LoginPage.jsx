import { useState } from 'react';
import '../App.css';

function LoginPage({ onLogin }) {
  const [usuario, setUsuario] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [mostrarContrasena, setMostrarContrasena] = useState(false);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  async function iniciarSesion(e) {
    e.preventDefault();
    setError('');
    setCargando(true);

    try {
      const resultado = await onLogin(usuario, contrasena);

      if (!resultado.ok) {
        setError(resultado.message);
      }
    } catch {
      setError('No se pudo conectar con el servidor.');
    } finally {
      setCargando(false);
    }
  }

  return (
    <main className="pagina-login">
      <section className="tarjeta-login">
        <div className="escudo">U</div>

        <p className="etiqueta">SISTEMA DE GESTIÓN</p>
        <h1>Unidad de Protección</h1>
        <p className="descripcion">
          Sistema de Protección de Derechos Vulnerados
        </p>

        <form onSubmit={iniciarSesion}>
          <div className="campo">
            <label htmlFor="usuario">Usuario</label>
            <input
              id="usuario"
              type="text"
              placeholder="Ingresa tu usuario"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
              autoComplete="username"
              required
            />
          </div>

          <div className="campo">
            <label htmlFor="contrasena">Contraseña</label>
            <input
              id="contrasena"
              type={mostrarContrasena ? 'text' : 'password'}
              placeholder="Ingresa tu contraseña"
              value={contrasena}
              onChange={(e) => setContrasena(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          <label className="opcion-contrasena">
            <input
              type="checkbox"
              checked={mostrarContrasena}
              onChange={(e) => setMostrarContrasena(e.target.checked)}
            />
            Mostrar contraseña
          </label>

          {error && (
            <p className="mensaje-error" role="alert">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="boton-principal"
            disabled={cargando}
          >
            {cargando ? 'Verificando...' : 'Iniciar sesión'}
          </button>
        </form>

        <p className="pie-login">
          Acceso exclusivo para usuarios autorizados
        </p>
      </section>
    </main>
  );
}

export default LoginPage;