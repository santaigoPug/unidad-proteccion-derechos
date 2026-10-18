import Header from '../components/Header';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';
import '../styles/Layout.css';

function HomePage({ usuario, onCerrarSesion }) {
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
            <p className="etiqueta-seccion">PANEL DE CONTROL</p>
            <h2>Bienvenido al sistema</h2>
            <p>
              Desde esta pantalla podrás acceder a los módulos
              de la Unidad de Protección de Derechos Vulnerados.
            </p>
          </div>

          <section className="tarjetas-resumen">
            <article className="tarjeta-resumen">
              <span className="icono-resumen">▤</span>
              <h3>Expedientes</h3>
              <p>Consulta y seguimiento de expedientes.</p>
              <span className="estado-modulo">Módulo en preparación</span>
            </article>

            <article className="tarjeta-resumen">
              <span className="icono-resumen">♙</span>
              <h3>Personas</h3>
              <p>Información de las personas relacionadas con los casos.</p>
              <span className="estado-modulo">Módulo en preparación</span>
            </article>

            <article className="tarjeta-resumen">
              <span className="icono-resumen">▥</span>
              <h3>Reportes</h3>
              <p>Consulta futura de información y estadísticas.</p>
              <span className="estado-modulo">Módulo en preparación</span>
            </article>
          </section>

          {usuario?.rol === 'Administrador' && (
            <section className="aviso-administrador">
              <h3>Administración del sistema</h3>
              <p>
                Tienes el rol de administrador. Desde el menú lateral
                podrás acceder a la sección de usuarios.
              </p>
            </section>
          )}
        </main>
      </div>

      <Footer />
    </div>
  );
}

export default HomePage;