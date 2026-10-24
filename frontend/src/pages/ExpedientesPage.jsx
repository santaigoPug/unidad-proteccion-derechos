
import { useCallback, useEffect, useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';
import '../styles/Layout.css';

const API_URL = '';

async function leerRespuesta(respuesta) {
  const datos = await respuesta.json();

  if (!respuesta.ok) {
    throw new Error(
      datos.message || 'Ocurrió un error al consultar el servidor.'
    );
  }

  return datos;
}

function ExpedientesPage({ usuario, onCerrarSesion }) {
  const [expedientes, setExpedientes] = useState([]);
  const [expedienteSeleccionado, setExpedienteSeleccionado] = useState('');
  const [personas, setPersonas] = useState([]);
  const [personasVinculadas, setPersonasVinculadas] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [personaSeleccionada, setPersonaSeleccionada] = useState('');
  const [rol, setRol] = useState('Solicitante');

  const [cargandoExpedientes, setCargandoExpedientes] = useState(true);
  const [cargandoPersonas, setCargandoPersonas] = useState(false);
  const [cargandoVinculadas, setCargandoVinculadas] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  const cargarExpedientes = useCallback(async () => {
    setCargandoExpedientes(true);

    try {
      const respuesta = await fetch(`${API_URL}/api/expedientes`, {
        credentials: 'include',
      });

      const datos = await leerRespuesta(respuesta);
      const lista = datos.expedientes || [];

      setExpedientes(lista);

      setExpedienteSeleccionado((actual) => {
        if (actual && lista.some(
          (expediente) => String(expediente.id_expediente) === actual
        )) {
          return actual;
        }

        return lista.length ? String(lista[0].id_expediente) : '';
      });
    } catch (error) {
      setMensaje({ tipo: 'error', texto: error.message });
    } finally {
      setCargandoExpedientes(false);
    }
  }, []);

  const cargarPersonasVinculadas = useCallback(async (idExpediente) => {
    if (!idExpediente) {
      setPersonasVinculadas([]);
      return;
    }

    setCargandoVinculadas(true);

    try {
      const respuesta = await fetch(
        `${API_URL}/api/expedientes/${idExpediente}/personas`,
        { credentials: 'include' }
      );

      const datos = await leerRespuesta(respuesta);
      setPersonasVinculadas(datos.personas || []);
    } catch (error) {
      setPersonasVinculadas([]);
      setMensaje({ tipo: 'error', texto: error.message });
    } finally {
      setCargandoVinculadas(false);
    }
  }, []);

  useEffect(() => {
    cargarExpedientes();
  }, [cargarExpedientes]);

  useEffect(() => {
    cargarPersonasVinculadas(expedienteSeleccionado);
    setPersonaSeleccionada('');
  }, [expedienteSeleccionado, cargarPersonasVinculadas]);

  useEffect(() => {
    let activo = true;

    async function buscarPersonas() {
      const termino = busqueda.trim();

      if (termino.length < 2) {
        setPersonas([]);
        setPersonaSeleccionada('');
        setCargandoPersonas(false);
        return;
      }

      setCargandoPersonas(true);

      try {
        const respuesta = await fetch(
          `${API_URL}/api/expedientes/personas?q=${encodeURIComponent(termino)}`,
          { credentials: 'include' }
        );

        const datos = await leerRespuesta(respuesta);

        if (activo) {
          setPersonas(datos.personas || []);
          setPersonaSeleccionada('');
        }
      } catch (error) {
        if (activo) {
          setPersonas([]);
          setMensaje({ tipo: 'error', texto: error.message });
        }
      } finally {
        if (activo) setCargandoPersonas(false);
      }
    }

    buscarPersonas();

    return () => {
      activo = false;
    };
  }, [busqueda]);

  async function vincularPersona(evento) {
    evento.preventDefault();
    setMensaje(null);

    if (!expedienteSeleccionado) {
      setMensaje({
        tipo: 'error',
        texto: 'Selecciona un expediente antes de continuar.',
      });
      return;
    }

    if (!personaSeleccionada) {
      setMensaje({
        tipo: 'error',
        texto: 'Busca y selecciona una persona.',
      });
      return;
    }

    if (!rol.trim()) {
      setMensaje({
        tipo: 'error',
        texto: 'Selecciona el rol de la persona.',
      });
      return;
    }

    const yaVinculada = personasVinculadas.some(
      (persona) =>
        String(persona.id_persona) === String(personaSeleccionada)
    );

    if (yaVinculada) {
      setMensaje({
        tipo: 'error',
        texto: 'Esta persona ya está vinculada al expediente seleccionado.',
      });
      return;
    }

    setGuardando(true);

    try {
      const respuesta = await fetch(
        `${API_URL}/api/expedientes/${expedienteSeleccionado}/personas`,
        {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id_persona: Number(personaSeleccionada),
            rol_en_caso: rol.trim(),
          }),
        }
      );

      const datos = await leerRespuesta(respuesta);

      setMensaje({
        tipo: 'exito',
        texto: datos.message || 'Persona vinculada correctamente.',
      });

      setBusqueda('');
      setPersonas([]);
      setPersonaSeleccionada('');

      await cargarPersonasVinculadas(expedienteSeleccionado);
    } catch (error) {
      setMensaje({ tipo: 'error', texto: error.message });
    } finally {
      setGuardando(false);
    }
  }

  const expedienteActual = expedientes.find(
    (expediente) =>
      String(expediente.id_expediente) === expedienteSeleccionado
  );

  return (
    <div className="estructura-app">
      <Header usuario={usuario} onCerrarSesion={onCerrarSesion} />

      <div className="cuerpo-app">
        <Sidebar usuario={usuario} />

        <main className="contenido-principal">
          <div className="encabezado-formulario">
            <div>
              <h1>Expedientes</h1>
              <p>Consulta expedientes y administra las personas vinculadas.</p>
            </div>

            <button
              type="button"
              className="boton-principal"
              onClick={cargarExpedientes}
              disabled={cargandoExpedientes}
            >
              {cargandoExpedientes ? 'Actualizando...' : 'Actualizar'}
            </button>
          </div>

          {mensaje && (
            <div
              className={`mensaje-formulario ${mensaje.tipo}`}
              role="status"
            >
              {mensaje.texto}
              <button
                type="button"
                onClick={() => setMensaje(null)}
                aria-label="Cerrar mensaje"
              >
                ×
              </button>
            </div>
          )}

          <section className="panel-formulario">
            <h2>Expedientes registrados</h2>

            {cargandoExpedientes ? (
              <p>Cargando expedientes...</p>
            ) : expedientes.length === 0 ? (
              <p>No hay expedientes registrados.</p>
            ) : (
              <div className="tabla-contenedor">
                <table>
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Motivo de atención</th>
                      <th>Fecha de apertura</th>
                      <th>Responsable</th>
                      <th>Estado</th>
                      <th>Acción</th>
                    </tr>
                  </thead>

                  <tbody>
                    {expedientes.map((expediente) => (
                      <tr key={expediente.id_expediente}>
                        <td>{expediente.codigo_unico}</td>
                        <td>{expediente.motivo_atencion}</td>
                        <td>{expediente.fecha_apertura}</td>
                        <td>{expediente.responsable}</td>
                        <td>{expediente.estado}</td>
                        <td>
                          <button
                            type="button"
                            className="boton-principal"
                            onClick={() =>
                              setExpedienteSeleccionado(
                                String(expediente.id_expediente)
                              )
                            }
                          >
                            {expedienteSeleccionado ===
                            String(expediente.id_expediente)
                              ? 'Seleccionado'
                              : 'Seleccionar'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {expedienteActual && (
            <>
              <section className="panel-formulario">
                <div className="encabezado-formulario">
                  <div>
                    <h2>Vincular persona</h2>
                    <p>
                      Expediente seleccionado:{' '}
                      <strong>{expedienteActual.codigo_unico}</strong>
                    </p>
                  </div>
                </div>

                <form onSubmit={vincularPersona}>
                  <div className="campo-formulario">
                    <label htmlFor="buscar-persona">
                      Buscar persona por nombre
                    </label>
                    <input
                      id="buscar-persona"
                      type="search"
                      value={busqueda}
                      onChange={(evento) => setBusqueda(evento.target.value)}
                      placeholder="Escribe al menos 2 caracteres..."
                      autoComplete="off"
                    />
                  </div>

                  {cargandoPersonas && <p>Buscando personas...</p>}

                  {!cargandoPersonas &&
                    busqueda.trim().length >= 2 &&
                    personas.length === 0 && (
                      <p>No se encontraron personas con ese nombre.</p>
                    )}

                  {personas.length > 0 && (
                    <div className="campo-formulario">
                      <label htmlFor="persona-seleccionada">
                        Seleccionar persona
                      </label>
                      <select
                        id="persona-seleccionada"
                        value={personaSeleccionada}
                        onChange={(evento) =>
                          setPersonaSeleccionada(evento.target.value)
                        }
                        required
                      >
                        <option value="">Selecciona una persona</option>
                        {personas.map((persona) => (
                          <option
                            key={persona.id_persona}
                            value={persona.id_persona}
                          >
                            {persona.nombre_completo}
                            {persona.nombre_municipio
                              ? ` — ${persona.nombre_municipio}`
                              : ''}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div className="campo-formulario">
                    <label htmlFor="rol-persona">Rol en el expediente</label>
                    <select
                      id="rol-persona"
                      value={rol}
                      onChange={(evento) => setRol(evento.target.value)}
                      required
                    >
                      <option value="Solicitante">Solicitante</option>
                      <option value="Beneficiario">Beneficiario</option>
                      <option value="Víctima">Víctima</option>
                      <option value="Familiar">Familiar</option>
                      <option value="Representante">Representante</option>
                      <option value="Testigo">Testigo</option>
                      <option value="Otro">Otro</option>
                    </select>
                  </div>

                  <div className="acciones-formulario">
                    <button
                      type="submit"
                      className="boton-registrar"
                      disabled={guardando || !personaSeleccionada}
                    >
                      {guardando ? 'Vinculando...' : 'Vincular persona'}
                    </button>

                    <button
                      type="button"
                      className="boton-limpiar"
                      onClick={() => {
                        setBusqueda('');
                        setPersonas([]);
                        setPersonaSeleccionada('');
                        setMensaje(null);
                      }}
                    >
                      Limpiar
                    </button>
                  </div>
                </form>
              </section>

              <section className="panel-formulario">
                <h2>Personas vinculadas</h2>
                <p>
                  Expediente: <strong>{expedienteActual.codigo_unico}</strong>
                </p>

                {cargandoVinculadas ? (
                  <p>Cargando personas vinculadas...</p>
                ) : personasVinculadas.length === 0 ? (
                  <p>Este expediente todavía no tiene personas vinculadas.</p>
                ) : (
                  <div className="tabla-contenedor">
                    <table>
                      <thead>
                        <tr>
                          <th>Nombre completo</th>
                          <th>Fecha de nacimiento</th>
                          <th>Municipio</th>
                          <th>Rol en el expediente</th>
                        </tr>
                      </thead>

                      <tbody>
                        {personasVinculadas.map((persona) => (
                          <tr key={persona.id_persona}>
                            <td>{persona.nombre_completo}</td>
                            <td>{persona.f_nacimiento || 'No disponible'}</td>
                            <td>{persona.nombre_municipio || 'No disponible'}</td>
                            <td>{persona.rol_en_caso}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>
            </>
          )}
        </main>
      </div>

      <Footer />
    </div>
  );
}

export default ExpedientesPage;
