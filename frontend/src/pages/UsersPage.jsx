import { useCallback, useEffect, useState } from 'react';

import Header from '../components/Header';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';

import '../styles/Layout.css';

const API_URL = '';

const FORMULARIO_INICIAL = {
  username: '',
  password: '',
  rol: 'Operador',
};

const EDICION_INICIAL = {
  id_user: null,
  username: '',
  rol: 'Operador',
  estado: 1,
};

async function leerRespuesta(respuesta) {
  const tipoContenido = respuesta.headers.get('content-type') || '';

  if (!tipoContenido.includes('application/json')) {
    throw new Error(
      'El servidor no devolvió JSON. Comprueba que Flask esté funcionando y que la ruta sea correcta.'
    );
  }

  return respuesta.json();
}

function UsersPage({ usuario, onCerrarSesion }) {
  // Formulario de registro
  const [formulario, setFormulario] = useState(FORMULARIO_INICIAL);
  const [mostrarPassword, setMostrarPassword] = useState(false);

  // Lista de usuarios
  const [usuarios, setUsuarios] = useState([]);
  const [cargandoUsuarios, setCargandoUsuarios] = useState(true);

  // Formulario de edición
  const [edicion, setEdicion] = useState(EDICION_INICIAL);
  const [editando, setEditando] = useState(false);

  // Mensajes y estados
  const [mensaje, setMensaje] = useState('');
  const [tipoMensaje, setTipoMensaje] = useState('');
  const [guardando, setGuardando] = useState(false);

  function mostrarMensaje(texto, tipo = 'error') {
    setMensaje(texto);
    setTipoMensaje(tipo);
  }

  function limpiarMensaje() {
    setMensaje('');
    setTipoMensaje('');
  }

  // Consultar usuarios
  const cargarUsuarios = useCallback(async () => {
    setCargandoUsuarios(true);

    try {
      const respuesta = await fetch(`${API_URL}/api/usuarios`, {
        method: 'GET',
        credentials: 'include',
      });

      const datos = await leerRespuesta(respuesta);

      if (!respuesta.ok) {
        throw new Error(
          datos.message || 'No fue posible consultar los usuarios.'
        );
      }

      setUsuarios(Array.isArray(datos.usuarios) ? datos.usuarios : []);
    } catch (error) {
      console.error('Error al consultar usuarios:', error);

      mostrarMensaje(
        error.message || 'No fue posible conectar con el servidor.'
      );
    } finally {
      setCargandoUsuarios(false);
    }
  }, []);

  useEffect(() => {
    cargarUsuarios();
  }, [cargarUsuarios]);

  // Cambios en los campos de registro
  function cambiarCampoRegistro(e) {
    const { name, value } = e.target;

    setFormulario((anterior) => ({
      ...anterior,
      [name]: value,
    }));
  }

  // Registrar usuario
  async function registrarUsuario(e) {
    e.preventDefault();
    limpiarMensaje();
    setGuardando(true);

    try {
      const respuesta = await fetch(`${API_URL}/api/usuarios`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formulario),
      });

      const datos = await leerRespuesta(respuesta);

      if (!respuesta.ok) {
        throw new Error(
          datos.message || 'No fue posible registrar al usuario.'
        );
      }

      setFormulario(FORMULARIO_INICIAL);
      setMostrarPassword(false);

      mostrarMensaje(
        datos.message || 'Usuario registrado correctamente.',
        'exito'
      );

      await cargarUsuarios();
    } catch (error) {
      console.error('Error al registrar usuario:', error);

      mostrarMensaje(
        error.message || 'No fue posible registrar al usuario.'
      );
    } finally {
      setGuardando(false);
    }
  }

  // Abrir formulario de edición
  function iniciarEdicion(usuarioLista) {
    limpiarMensaje();

    setEdicion({
      id_user: usuarioLista.id_user,
      username: usuarioLista.username,
      rol: usuarioLista.rol,
      estado: Number(usuarioLista.estado) === 1 ? 1 : 0,
    });

    setEditando(true);
  }

  // Cambiar campos de edición
  function cambiarCampoEdicion(e) {
    const { name, value } = e.target;

    setEdicion((anterior) => ({
      ...anterior,
      [name]: value,
    }));
  }

  // Guardar modificaciones
  async function guardarEdicion(e) {
    e.preventDefault();
    limpiarMensaje();

    if (edicion.id_user === null) {
      mostrarMensaje('No se ha seleccionado un usuario.');
      return;
    }

    setGuardando(true);

    try {
      const respuesta = await fetch(
        `${API_URL}/api/usuarios/${edicion.id_user}`,
        {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: edicion.username,
            rol: edicion.rol,
            estado: Number(edicion.estado),
          }),
        }
      );

      const datos = await leerRespuesta(respuesta);

      if (!respuesta.ok) {
        throw new Error(
          datos.message || 'No fue posible modificar al usuario.'
        );
      }

      setEditando(false);
      setEdicion(EDICION_INICIAL);

      mostrarMensaje(
        datos.message || 'Usuario actualizado correctamente.',
        'exito'
      );

      await cargarUsuarios();
    } catch (error) {
      console.error('Error al modificar usuario:', error);

      mostrarMensaje(
        error.message || 'No fue posible modificar al usuario.'
      );
    } finally {
      setGuardando(false);
    }
  }

  function cancelarEdicion() {
    setEditando(false);
    setEdicion(EDICION_INICIAL);
    limpiarMensaje();
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

            <h2>Gestión de usuarios</h2>

            <p>
              Registra nuevas cuentas, consulta los usuarios existentes
              y modifica sus permisos.
            </p>
          </div>

          {mensaje && (
            <div
              className={`mensaje-formulario ${tipoMensaje}`}
              role="status"
              aria-live="polite"
            >
              {mensaje}
            </div>
          )}

          {/* FORMULARIO DE REGISTRO */}
          <section className="panel-formulario">
            <div className="encabezado-formulario">
              <div className="icono-formulario">+</div>

              <div>
                <h3>Registrar usuario</h3>
                <p>Completa los datos de la nueva cuenta.</p>
              </div>
            </div>

            <form onSubmit={registrarUsuario}>
              <div className="campo-formulario">
                <label htmlFor="nuevo-username">
                  Nombre de usuario
                </label>

                <input
                  id="nuevo-username"
                  name="username"
                  type="text"
                  value={formulario.username}
                  onChange={cambiarCampoRegistro}
                  placeholder="Ej. operador01"
                  maxLength={100}
                  autoComplete="off"
                  required
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="nuevo-password">
                  Contraseña
                </label>

                <input
                  id="nuevo-password"
                  name="password"
                  type={mostrarPassword ? 'text' : 'password'}
                  value={formulario.password}
                  onChange={cambiarCampoRegistro}
                  placeholder="Mínimo 8 caracteres"
                  minLength={8}
                  autoComplete="new-password"
                  required
                />

                <label className="opcion-mostrar-password">
                  <input
                    type="checkbox"
                    checked={mostrarPassword}
                    onChange={(e) =>
                      setMostrarPassword(e.target.checked)
                    }
                  />

                  Mostrar contraseña
                </label>
              </div>

              <div className="campo-formulario">
                <label htmlFor="nuevo-rol">
                  Rol del usuario
                </label>

                <select
                  id="nuevo-rol"
                  name="rol"
                  value={formulario.rol}
                  onChange={cambiarCampoRegistro}
                  required
                >
                  <option value="Operador">Operador</option>
                  <option value="Administrador">Administrador</option>
                </select>
              </div>

              <div className="acciones-formulario">
                <button
                  type="button"
                  className="boton-limpiar"
                  disabled={guardando}
                  onClick={() => {
                    setFormulario(FORMULARIO_INICIAL);
                    setMostrarPassword(false);
                    limpiarMensaje();
                  }}
                >
                  Limpiar
                </button>

                <button
                  type="submit"
                  className="boton-registrar"
                  disabled={guardando}
                >
                  {guardando ? 'Guardando...' : 'Registrar usuario'}
                </button>
              </div>
            </form>
          </section>
          {/* LISTA DE USUARIOS */}
          <section className="panel-formulario panel-lista-usuarios">
            <div className="encabezado-formulario">
              <div className="icono-formulario">
                ☷
              </div>

              <div>
                <h3>Usuarios registrados</h3>

                <p>
                  Consulta las cuentas existentes y modifica sus datos.
                </p>
              </div>
            </div>

            <div className="barra-lista-usuarios">
              <span>
                {cargandoUsuarios
                  ? 'Consultando usuarios...'
                  : `${usuarios.length} usuario(s)`}
              </span>

              <button
                type="button"
                className="boton-limpiar"
                onClick={cargarUsuarios}
                disabled={cargandoUsuarios}
              >
                {cargandoUsuarios ? 'Actualizando...' : 'Actualizar lista'}
              </button>
            </div>

            {cargandoUsuarios ? (
              <p className="estado-lista-usuarios">
                Cargando usuarios...
              </p>
            ) : usuarios.length === 0 ? (
              <p className="estado-lista-usuarios">
                No hay usuarios para mostrar.
              </p>
            ) : (
              <div className="contenedor-tabla-usuarios">
                <table className="tabla-usuarios">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Usuario</th>
                      <th>Rol</th>
                      <th>Estado</th>
                      <th>Fecha de creación</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>

                  <tbody>
                    {usuarios.map((usuarioLista) => (
                      <tr key={usuarioLista.id_user}>
                        <td>{usuarioLista.id_user}</td>

                        <td>{usuarioLista.username}</td>

                        <td>{usuarioLista.rol}</td>

                        <td>
                          <span
                            className={
                              Number(usuarioLista.estado) === 1
                                ? 'estado-usuario activo'
                                : 'estado-usuario inactivo'
                            }
                          >
                            {Number(usuarioLista.estado) === 1
                              ? 'Activo'
                              : 'Inactivo'}
                          </span>
                        </td>

                        <td>
                          {usuarioLista.f_creacion || 'No disponible'}
                        </td>

                        <td>
                          <button
                            type="button"
                            className="boton-editar-usuario"
                            onClick={() =>
                              iniciarEdicion(usuarioLista)
                            }
                          >
                            Editar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
          {/* FORMULARIO DE EDICIÓN */}
          {editando && (
            <section
              className="panel-formulario panel-edicion"
              aria-labelledby="titulo-edicion"
            >
              <div className="encabezado-formulario">
                <div className="icono-formulario">
                  ✎
                </div>

                <div>
                  <h3 id="titulo-edicion">
                    Modificar usuario
                  </h3>

                  <p>
                    ID de usuario: {edicion.id_user}
                  </p>
                </div>
              </div>

              <form onSubmit={guardarEdicion}>
                <div className="campo-formulario">
                  <label htmlFor="editar-username">
                    Nombre de usuario
                  </label>

                  <input
                    id="editar-username"
                    name="username"
                    type="text"
                    value={edicion.username}
                    onChange={cambiarCampoEdicion}
                    maxLength={100}
                    required
                  />
                </div>

                <div className="campo-formulario">
                  <label htmlFor="editar-rol">
                    Rol
                  </label>

                  <select
                    id="editar-rol"
                    name="rol"
                    value={edicion.rol}
                    onChange={cambiarCampoEdicion}
                    required
                  >
                    <option value="Operador">Operador</option>
                    <option value="Administrador">
                      Administrador
                    </option>
                  </select>
                </div>

                <div className="campo-formulario">
                  <label htmlFor="editar-estado">
                    Estado de la cuenta
                  </label>

                  <select
                    id="editar-estado"
                    name="estado"
                    value={String(edicion.estado)}
                    onChange={cambiarCampoEdicion}
                    required
                  >
                    <option value="1">Activo</option>
                    <option value="0">Inactivo</option>
                  </select>
                </div>

                <div className="acciones-formulario">
                  <button
                    type="button"
                    className="boton-limpiar"
                    onClick={cancelarEdicion}
                    disabled={guardando}
                  >
                    Cancelar
                  </button>

                  <button
                    type="submit"
                    className="boton-registrar"
                    disabled={guardando}
                  >
                    {guardando
                      ? 'Guardando cambios...'
                      : 'Guardar cambios'}
                  </button>
                </div>
              </form>
            </section>
          )}


        </main>
      </div>

      <Footer />
    </div>
  );
}

export default UsersPage;