import { useEffect, useState } from 'react';
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useNavigate,
} from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import UsersPage from './pages/UsersPage';
import './App.css';

const API_URL = 'http://127.0.0.1:5000';

function RutasAplicacion() {
  const [usuarioActual, setUsuarioActual] = useState(null);
  const [cargandoSesion, setCargandoSesion] = useState(true);

  useEffect(() => {
    let activo = true;

    async function consultarSesion() {
      try {
        
        const respuesta = await fetch(`${API_URL}/api/me`, {
          method: 'GET',
          credentials: 'include',
        });


        if (!respuesta.ok) {
          if (activo) {
            setUsuarioActual(null);
          }
          return;
        }

        const datos = await respuesta.json();

        if (activo) {
          setUsuarioActual(datos.usuario);
        }
      } catch (error) {
        console.error('Error al consultar la sesión:', error);

        if (activo) {
          setUsuarioActual(null);
        }
      } finally {
        if (activo) {
          setCargandoSesion(false);
        }
      }
    }

    consultarSesion();

    return () => {
      activo = false;
    };
  }, []);

  async function iniciarSesion(usuario, contrasena) {
    try {
      const respuesta = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: usuario,
          password: contrasena,
        }),
      });

      const datos = await respuesta.json();

      if (!respuesta.ok) {
        return {
          ok: false,
          message: datos.message || 'No fue posible iniciar sesión.',
        };
      }

      setUsuarioActual(datos.usuario);

      return { ok: true };
    } catch (error) {
      console.error('Error al iniciar sesión:', error);

      return {
        ok: false,
        message: 'No se pudo conectar con el servidor. Verifica que Flask esté ejecutándose.',
      };
    }
  }

  async function cerrarSesion() {
    try {
      await fetch(`${API_URL}/api/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Error al cerrar la sesión:', error);
    } finally {
      setUsuarioActual(null);
    }
  }

  if (cargandoSesion) {
    return (
      <main className="pagina-login">
        <p>Verificando sesión...</p>
      </main>
    );
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={
          usuarioActual
            ? <Navigate to="/" replace />
            : <LoginPage onLogin={iniciarSesion} />
        }
      />

      <Route
        path="/"
        element={
          usuarioActual
            ? (
              <HomePage
                usuario={usuarioActual}
                onCerrarSesion={cerrarSesion}
              />
            )
            : <Navigate to="/login" replace />
        }
      />

      <Route
        path="/usuarios"
        element={
          !usuarioActual
            ? <Navigate to="/login" replace />
            : usuarioActual.rol !== 'Administrador'
              ? <Navigate to="/" replace />
              : (
                <UsersPage
                  usuario={usuarioActual}
                  onCerrarSesion={cerrarSesion}
                />
              )
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <RutasAplicacion />
    </BrowserRouter>
  );
}

export default App;