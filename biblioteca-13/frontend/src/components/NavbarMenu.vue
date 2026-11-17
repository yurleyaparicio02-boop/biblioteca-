<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const router = useRouter()
const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()
const menuAbierto = ref(false)
const rutaInicio = computed(() =>
  authStore.estaAutenticado
    ? authStore.esStaff
      ? '/gestion'
      : '/'
    : '/login'
)

function cerrarMenu() {
  menuAbierto.value = false
}

async function salir() {
  await authStore.cerrarSesion()
  notificaciones.info('Has cerrado sesión correctamente.')
  cerrarMenu()
  router.push('/')
}
</script>

<template>
  <header class="navbar-envoltura">
    <nav class="contenedor navbar" aria-label="Navegación principal">
      <RouterLink :to="rutaInicio" class="marca" @click="cerrarMenu">
        <span class="marca-icono" aria-hidden="true">
          <svg viewBox="0 0 42 32" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M3 5.5A2.5 2.5 0 0 1 5.5 3H20v24H5.5A2.5 2.5 0 0 0 3 29V5.5Z" fill="#F3DFEA" />
            <path d="M39 5.5A2.5 2.5 0 0 0 36.5 3H22v24h14.5A2.5 2.5 0 0 1 39 29V5.5Z" fill="#E2EBDD" />
            <path d="M21 6c-4-3-9-3-14-2v18c5-1 10-1 14 2 4-3 9-3 14-2V4c-5-1-10-1-14 2Z" />
            <path d="M21 6v18" />
          </svg>
        </span>
        <div>
          <span class="marca-titulo titulo-serif">Mi Biblioteca</span>
          <span class="marca-subtitulo">Lee · Descubre · Aprende</span>
        </div>
      </RouterLink>

      <button
        type="button"
        class="btn-hamburguesa"
        :aria-expanded="menuAbierto"
        :aria-label="menuAbierto ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'"
        @click="menuAbierto = !menuAbierto"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path v-if="!menuAbierto" d="M4 6h16M4 12h16M4 18h16" />
          <path v-else d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div class="nav-enlaces" :class="{ abierto: menuAbierto }">
        <RouterLink
          :to="rutaInicio"
          class="nav-link"
          exact-active-class="nav-link-activo"
          @click="cerrarMenu"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-6v-7h-4v7H4a1 1 0 0 1-1-1V10Z" />
          </svg>
          Inicio
        </RouterLink>
        <template v-if="authStore.estaAutenticado">
          <RouterLink v-if="authStore.esStaff" to="/" class="nav-link" exact-active-class="nav-link-activo" @click="cerrarMenu">
            Catálogo
          </RouterLink>
          <RouterLink to="/categorias" class="nav-link" exact-active-class="nav-link-activo" @click="cerrarMenu">
            Categorías
          </RouterLink>
          <RouterLink to="/autores" class="nav-link" exact-active-class="nav-link-activo" @click="cerrarMenu">
            Autores
          </RouterLink>
          <RouterLink v-if="!authStore.esStaff" to="/perfil" class="nav-link" exact-active-class="nav-link-activo" @click="cerrarMenu">
            Mi perfil
          </RouterLink>
        </template>
        <RouterLink v-else to="/registro" class="nav-link" exact-active-class="nav-link-activo" @click="cerrarMenu">
          Crear cuenta
        </RouterLink>

        <div class="nav-cuenta">
          <template v-if="authStore.estaAutenticado">
            <RouterLink
              to="/perfil"
              class="avatar-usuario"
              :aria-label="`Ver perfil de ${authStore.usuario?.nombre || 'usuario'}`"
              @click="cerrarMenu"
            >
              {{ authStore.usuario?.nombre?.charAt(0)?.toUpperCase() || 'U' }}
            </RouterLink>
            <button type="button" class="btn-salir" aria-label="Cerrar sesión" title="Cerrar sesión" @click="salir">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
                <path d="M10 17l5-5-5-5m5 5H3m9-9h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6" />
              </svg>
            </button>
          </template>
          <RouterLink v-else to="/login" class="btn btn-primario btn-nav" @click="cerrarMenu">
            Iniciar sesión
          </RouterLink>
        </div>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.navbar-envoltura {
  position: sticky;
  top: 0.45rem;
  z-index: 40;
  width: calc(100% - 1.5rem);
  max-width: 1380px;
  margin: 0.5rem auto 0;
  background-color: rgba(255, 253, 249, 0.94);
  backdrop-filter: blur(10px);
  border: 1px solid #f0e2e0;
  border-radius: 17px;
  box-shadow: 0 5px 18px rgba(79, 45, 59, 0.06);
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 60px;
  gap: 1rem;
  padding: 0 1.25rem;
}

.marca {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.marca-icono {
  width: 48px;
  height: 42px;
  color: #765879;
  display: grid;
  place-items: center;
}

.marca-icono svg {
  width: 44px;
  height: 34px;
}

.marca-titulo {
  display: block;
  font-size: 1.25rem;
  color: #321b2d;
  line-height: 1.15;
}

.marca-subtitulo {
  display: block;
  font-size: 0.75rem;
  color: var(--color-texto-suave);
}

.nav-enlaces {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  margin-left: auto;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  font-size: 0.81rem;
  font-weight: 500;
  color: var(--color-texto-suave);
  transition: background-color var(--transicion), color var(--transicion);
}

.nav-link svg {
  width: 17px;
  height: 17px;
}

.nav-link:hover {
  background-color: var(--color-beige);
  color: var(--color-texto);
}

.nav-link.nav-link-activo {
  background-color: #efdaf0;
  color: #482947;
}

.nav-cuenta {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-left: 0.55rem;
}

.avatar-usuario {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border: 2px solid #f1d7de;
  border-radius: 50%;
  background: linear-gradient(145deg, #f8e2e5, #e8d9ef);
  color: #58384e;
  font-family: var(--fuente-serif);
  font-size: 1.05rem;
  font-weight: 600;
}

.btn-salir {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--color-texto-suave);
  cursor: pointer;
  transition: background-color var(--transicion), color var(--transicion);
}

.btn-salir:hover {
  background: #f7e8eb;
  color: #8d526d;
}

.btn-salir svg {
  width: 17px;
  height: 17px;
}

.btn-nav {
  padding: 0.45rem 1rem;
  font-size: 0.8rem;
}

.btn-hamburguesa {
  display: none;
  background: var(--color-beige);
  border: 1px solid var(--color-borde);
  border-radius: var(--radio-sm);
  width: 40px;
  height: 40px;
  place-items: center;
  cursor: pointer;
}

.btn-hamburguesa svg {
  width: 22px;
  height: 22px;
}

@media (max-width: 768px) {
  .btn-hamburguesa {
    display: grid;
  }

  .nav-enlaces {
    display: none;
    position: absolute;
    top: calc(100% + 0.5rem);
    left: 0;
    right: 0;
    background-color: var(--color-blanco-calido);
    border: 1px solid var(--color-borde);
    border-radius: 14px;
    flex-direction: column;
    align-items: stretch;
    padding: 0.7rem;
    gap: 0.5rem;
    box-shadow: var(--sombra-suave);
  }

  .nav-enlaces.abierto {
    display: flex;
  }

  .nav-cuenta {
    justify-content: center;
    margin: 0.25rem 0 0;
    padding-top: 0.65rem;
    border-top: 1px solid var(--color-borde);
  }

  .nav-link,
  .btn-nav {
    text-align: center;
  }
}

@media (max-width: 420px) {
  .navbar-envoltura {
    width: calc(100% - 1rem);
  }

  .navbar {
    min-height: 56px;
    padding: 0 0.75rem;
  }

  .marca-icono {
    width: 40px;
  }

  .marca-icono svg {
    width: 38px;
  }

  .marca-titulo {
    font-size: 1.12rem;
  }

  .marca-subtitulo {
    font-size: 0.68rem;
  }
}
</style>
