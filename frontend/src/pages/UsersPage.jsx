import { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';
import '../styles/Layout.css';

const API_URL = '';

function UsersPage({ usuario, onCerrarSesion }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rol, setRol] = useState('Operador');
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [tipoMensaje, setTipoMensaje] = useState('');
  const [cargando, setCargando] = useState(false);

  async function registrarUsuario(e) {
    e.preventDefault();
    setMensaje('');
    setTipoMensaje('');
    setCargando(true);

    try {
      const respuesta = await fetch(`${API_URL}/api/usuarios`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
          rol,
        }),
      });

      const datos = await respuesta.json();

      if (!respuesta.ok) {
        setTipoMensaje('error');
        setMensaje(datos.message || 'No fue posible registrar al usuario.');
        return;
      }

      setTipoMensaje('exito');
      setMensaje(`El usuario "${datos.usuario.username}" se registró correctamente.`);
      setUsername('');
      setPassword('');
      setRol('Operador');
      setMostrarPassword(false);

    } catch (error) {
      console.error('Error al registrar usuario:', error);
      setTipoMensaje('error');
      setMensaje(
        'No se pudo conectar con el servidor. Verifica que Flask esté ejecutándose.'
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="estructura-app">
      <Header
        usuario={usuario}
        onCerrarSesion={onCerrarSesion}
      />

      <div className="cuerpo-app">
        <Sidebar usuario={usuario} />

        <main className="contenido-principal">
          <div className="titulo-seccion">
            <p className="etiqueta-seccion">ADMINISTRACIÓN</p>
            <h2>Agregar nuevo usuario</h2>
            <p>
              Registra una cuenta y asigna el rol que tendrá dentro del sistema.
            </p>
          </div>

          <section className="panel-formulario">
            <div className="encabezado-formulario">
              <div className="icono-formulario">+</div>
              <div>
                <h3>Datos de la cuenta</h3>
                <p>Completa los campos para registrar al usuario.</p>
              </div>
            </div>

            <form onSubmit={registrarUsuario}>
              <div className="campo-formulario">
                <label htmlFor="nuevo-username">Nombre de usuario</label>
                <input
                  id="nuevo-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Ej. operador01"
                  maxLength={100}
                  autoComplete="off"
                  required
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="nuevo-password">Contraseña</label>
                <input
                  id="nuevo-password"
                  type={mostrarPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Mínimo 8 caracteres"
                  minLength={8}
                  autoComplete="new-password"
                  required
                />

                <label className="opcion-mostrar-password">
                  <input
                    type="checkbox"
                    checked={mostrarPassword}
                    onChange={(e) => setMostrarPassword(e.target.checked)}
                  />
                  Mostrar contraseña
                </label>
              </div>

              <div className="campo-formulario">
                <label htmlFor="nuevo-rol">Rol del usuario</label>
                <select
                  id="nuevo-rol"
                  value={rol}
                  onChange={(e) => setRol(e.target.value)}
                  required
                >
                  <option value="Operador">Operador</option>
                  <option value="Administrador">Administrador</option>
                </select>
                <p className="ayuda-campo">
                  Los administradores pueden registrar otras cuentas.
                </p>
              </div>

              {mensaje && (
                <div
                  className={`mensaje-formulario ${tipoMensaje}`}
                  role="status"
                >
                  {mensaje}
                </div>
              )}

              <div className="acciones-formulario">
                <button
                  type="button"
                  className="boton-limpiar"
                  onClick={() => {
                    setUsername('');
                    setPassword('');
                    setRol('Operador');
                    setMensaje('');
                    setTipoMensaje('');
                    setMostrarPassword(false);
                  }}
                  disabled={cargando}
                >
                  Limpiar
                </button>

                <button
                  type="submit"
                  className="boton-registrar"
                  disabled={cargando}
                >
                  {cargando ? 'Registrando...' : 'Registrar usuario'}
                </button>
              </div>
            </form>
          </section>
        </main>
      </div>

      <Footer />
    </div>
  );
}

export default UsersPage;