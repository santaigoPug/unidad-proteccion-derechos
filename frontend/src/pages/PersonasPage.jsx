
import { useCallback, useEffect, useState } from 'react';

import Header from '../components/Header';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';

import '../styles/Layout.css';

const API_URL = '';

const FORMULARIO_INICIAL = {
  nombre_completo: '',
  curp: '',
  telefono: '',
  direccion: '',
  f_nacimiento: '',
  id_municipio: '',
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

function PersonasPage({ usuario, onCerrarSesion }) {
  const [formulario, setFormulario] = useState(FORMULARIO_INICIAL);
  const [personas, setPersonas] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [personaEditando, setPersonaEditando] = useState(null);
  const [mensaje, setMensaje] = useState('');
  const [tipoMensaje, setTipoMensaje] = useState('');

  function mostrarMensaje(texto, tipo = 'error') {
    setMensaje(texto);
    setTipoMensaje(tipo);
  }

  function limpiarMensaje() {
    setMensaje('');
    setTipoMensaje('');
  }

  const cargarPersonas = useCallback(async (termino = '') => {
    setCargando(true);

    try {
      const parametros = new URLSearchParams();

      if (termino.trim()) {
        parametros.set('q', termino.trim());
      }

      const query = parametros.toString();
      const ruta = query
        ? `${API_URL}/api/personas?${query}`
        : `${API_URL}/api/personas`;

      const respuesta = await fetch(ruta, {
        method: 'GET',
        credentials: 'include',
      });

      const datos = await leerRespuesta(respuesta);

      if (!respuesta.ok) {
        throw new Error(
          datos.message || 'No fue posible consultar las personas.'
        );
      }

      setPersonas(Array.isArray(datos.personas) ? datos.personas : []);
    } catch (error) {
      console.error('Error al consultar personas:', error);
      mostrarMensaje(error.message || 'No fue posible consultar las personas.');
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    cargarPersonas();
  }, [cargarPersonas]);

  function cambiarCampo(e) {
    const { name, value } = e.target;

    setFormulario((anterior) => ({
      ...anterior,
      [name]: value,
    }));
  }

  function iniciarEdicion(persona) {
    limpiarMensaje();

    setPersonaEditando(persona.id_persona);
    setFormulario({
      nombre_completo: persona.nombre_completo || '',
      curp: persona.curp || '',
      telefono: persona.telefono || '',
      direccion: persona.direccion || '',
      f_nacimiento: persona.f_nacimiento || '',
      id_municipio: persona.id_municipio ?? '',
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function cancelarEdicion() {
    setPersonaEditando(null);
    setFormulario(FORMULARIO_INICIAL);
    limpiarMensaje();
  }

  async function guardarPersona(e) {
    e.preventDefault();
    limpiarMensaje();
    setGuardando(true);

    try {
      const cuerpo = {
        ...formulario,
        curp: formulario.curp.trim().toUpperCase(),
        id_municipio: formulario.id_municipio
          ? Number(formulario.id_municipio)
          : null,
        f_nacimiento: formulario.f_nacimiento || null,
      };

      const editando = personaEditando !== null;
      const ruta = editando
        ? `${API_URL}/api/personas/${personaEditando}`
        : `${API_URL}/api/personas`;

      const respuesta = await fetch(ruta, {
        method: editando ? 'PUT' : 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cuerpo),
      });

      const datos = await leerRespuesta(respuesta);

      if (!respuesta.ok) {
        throw new Error(
          datos.message || 'No fue posible guardar la información.'
        );
      }

      setFormulario(FORMULARIO_INICIAL);
      setPersonaEditando(null);

      mostrarMensaje(
        datos.message ||
          (editando
            ? 'Persona actualizada correctamente.'
            : 'Persona registrada correctamente.'),
        'exito'
      );

      await cargarPersonas(busqueda);
    } catch (error) {
      console.error('Error al guardar persona:', error);
      mostrarMensaje(error.message || 'No fue posible guardar la información.');
    } finally {
      setGuardando(false);
    }
  }

  async function consultarDetalle(idPersona) {
    limpiarMensaje();

    try {
      const respuesta = await fetch(
        `${API_URL}/api/personas/${idPersona}`,
        {
          method: 'GET',
          credentials: 'include',
        }
      );

      const datos = await leerRespuesta(respuesta);

      if (!respuesta.ok) {
        throw new Error(
          datos.message || 'No fue posible consultar el detalle.'
        );
      }

      const persona = datos.persona;

      mostrarMensaje(
        `Registro ${persona.id_persona}: ${persona.nombre_completo}. CURP: ${persona.curp}. Teléfono: ${persona.telefono}. Dirección: ${persona.direccion}`,
        'exito'
      );
    } catch (error) {
      console.error('Error al consultar detalle:', error);
      mostrarMensaje(error.message || 'No fue posible consultar el detalle.');
    }
  }

  async function buscarPersonas(e) {
    e.preventDefault();
    await cargarPersonas(busqueda);
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
            <p className="etiqueta-seccion">GESTIÓN DE REGISTROS</p>
            <h2>Gestión de personas</h2>
            <p>
              Registra personas y consulta o actualiza sus datos.
              La información sensible se procesa en el backend.
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

          <section className="panel-formulario">
            <div className="encabezado-formulario">
              <div className="icono-formulario">+</div>
              <div>
                <h3>
                  {personaEditando !== null
                    ? `Editar persona #${personaEditando}`
                    : 'Registrar persona'}
                </h3>
                <p>Completa los campos de la persona.</p>
              </div>
            </div>

            <form onSubmit={guardarPersona}>
              <div className="campo-formulario">
                <label htmlFor="nombre_completo">Nombre completo</label>
                <input
                  id="nombre_completo"
                  name="nombre_completo"
                  value={formulario.nombre_completo}
                  onChange={cambiarCampo}
                  maxLength={200}
                  required
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="curp">CURP</label>
                <input
                  id="curp"
                  name="curp"
                  value={formulario.curp}
                  onChange={cambiarCampo}
                  maxLength={18}
                  minLength={18}
                  pattern="[A-Za-z0-9]{18}"
                  title="Ingresa una CURP de 18 caracteres alfanuméricos."
                  autoCapitalize="characters"
                  required
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="telefono">Teléfono</label>
                <input
                  id="telefono"
                  name="telefono"
                  type="tel"
                  value={formulario.telefono}
                  onChange={cambiarCampo}
                  maxLength={30}
                  required
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="direccion">Dirección</label>
                <textarea
                  id="direccion"
                  name="direccion"
                  value={formulario.direccion}
                  onChange={cambiarCampo}
                  maxLength={1000}
                  rows={3}
                  required
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="f_nacimiento">Fecha de nacimiento</label>
                <input
                  id="f_nacimiento"
                  name="f_nacimiento"
                  type="date"
                  value={formulario.f_nacimiento}
                  onChange={cambiarCampo}
                />
              </div>

              <div className="campo-formulario">
                <label htmlFor="id_municipio">ID del municipio (opcional)</label>
                <input
                  id="id_municipio"
                  name="id_municipio"
                  type="number"
                  min="1"
                  value={formulario.id_municipio}
                  onChange={cambiarCampo}
                  placeholder="Deja vacío si no aplica"
                />
              </div>

              <button
                className="boton-principal"
                type="submit"
                disabled={guardando}
              >
                {guardando
                  ? 'Guardando...'
                  : personaEditando !== null
                    ? 'Guardar cambios'
                    : 'Registrar persona'}
              </button>

              {personaEditando !== null && (
                <button
                  className="boton-secundario"
                  type="button"
                  onClick={cancelarEdicion}
                  disabled={guardando}
                >
                  Cancelar edición
                </button>
              )}
            </form>
          </section>

          <section className="panel-formulario">
            <div className="encabezado-formulario">
              <div className="icono-formulario">⌕</div>
              <div>
                <h3>Personas registradas</h3>
                <p>Busca por los datos que permita el endpoint.</p>
              </div>
            </div>

            <form onSubmit={buscarPersonas}>
              <div className="campo-formulario">
                <label htmlFor="busqueda">Buscar persona</label>
                <input
                  id="busqueda"
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  placeholder="Escribe un nombre, CURP o teléfono"
                />
              </div>
              <button className="boton-principal" type="submit">
                Buscar
              </button>
              <button
                className="boton-secundario"
                type="button"
                onClick={() => {
                  setBusqueda('');
                  cargarPersonas('');
                }}
              >
                Limpiar búsqueda
              </button>
            </form>

            {cargando ? (
              <p>Cargando personas...</p>
            ) : personas.length === 0 ? (
              <p>No se encontraron personas registradas.</p>
            ) : (
              <div className="tabla-contenedor">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Nombre completo</th>
                      <th>CURP</th>
                      <th>Teléfono</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {personas.map((persona) => (
                      <tr key={persona.id_persona}>
                        <td>{persona.id_persona}</td>
                        <td>{persona.nombre_completo}</td>
                        <td>{persona.curp}</td>
                        <td>{persona.telefono}</td>
                        <td>
                          <div className="acciones-tabla">
                            <button
                              type="button"
                              className="boton-secundario"
                              onClick={() => consultarDetalle(persona.id_persona)}
                            >
                              Ver detalle
                            </button>
                            <button
                              type="button"
                              className="boton-secundario"
                              onClick={() => iniciarEdicion(persona)}
                            >
                              Editar
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </main>
      </div>

      <Footer />
    </div>
  );
}

export default PersonasPage;
