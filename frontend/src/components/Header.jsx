function Header({ usuario, onCerrarSesion }) {
  return (
    <header className="encabezado">
      <div className="encabezado-titulo">
        <span className="encabezado-escudo">U</span>
        <div>
          <h1>Unidad de Protección</h1>
          <p>Protección de Derechos Vulnerados</p>
        </div>
      </div>

      <div className="encabezado-usuario">
        <div>
          <strong>{usuario?.username || 'Usuario'}</strong>
          <span>{usuario?.rol || 'Sin rol'}</span>
        </div>

        <button
          type="button"
          className="boton-secundario"
          onClick={onCerrarSesion}
        >
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}

export default Header;