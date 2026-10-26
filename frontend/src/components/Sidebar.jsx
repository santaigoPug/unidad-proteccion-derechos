import { NavLink } from 'react-router-dom';

function Sidebar({ usuario }) {
  const esAdministrador = usuario?.rol === 'Administrador';

  return (
    <aside className="barra-lateral">
      <p className="barra-lateral-titulo">MENÚ PRINCIPAL</p>

      <nav className="navegacion">
        <NavLink to="/" end className="enlace-menu">
          <span>⌂</span>
          Inicio
        </NavLink>

        <NavLink to="/expedientes" className="enlace-menu">
          <span>▤</span>
          Expedientes
        </NavLink>

        <NavLink to="/personas" className="enlace-menu">
          <span>♙</span>
          Personas
        </NavLink>

        {esAdministrador && (
          <NavLink to="/usuarios" className="enlace-menu">
            <span>♙</span>
            Administrar usuarios
          </NavLink>
          
        )}
      </nav>


      <div className="barra-lateral-pie">
        Acceso autorizado
      </div>
    </aside>
  );
}

export default Sidebar;