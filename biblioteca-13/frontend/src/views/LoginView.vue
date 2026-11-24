<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()

const email = ref('')
const password = ref('')
const errorForm = ref('')
const mostrarPassword = ref(false)

async function enviar() {
  errorForm.value = ''
  const res = await authStore.iniciarSesion(email.value, password.value)
  if (res.ok) {
    notificaciones.exito('¡Bienvenido de nuevo!')
    const destinoSolicitado = route.query.redirect
    const destinoValido =
      typeof destinoSolicitado === 'string' &&
      destinoSolicitado.startsWith('/') &&
      !destinoSolicitado.startsWith('//') &&
      !['/login', '/registro'].includes(destinoSolicitado.split('?')[0])
    const destinoPorRol = authStore.esStaff ? '/gestion' : '/perfil'
    const destinoInicial = destinoSolicitado === '/' && authStore.esStaff
    router.replace(destinoValido && !destinoInicial ? destinoSolicitado : destinoPorRol)
  } else {
    errorForm.value = res.mensaje
    notificaciones.error(res.mensaje)
  }
}
</script>

<template>
  <main class="contenedor auth-pagina">
    <section class="auth-tarjeta tarjeta-base">
      <span class="badge badge-rosa">Acceso</span>
      <h1 class="titulo-serif auth-titulo">Iniciar sesión</h1>
      <p class="auth-subtitulo">
        Ingresa con tu correo electrónico y contraseña para consultar tu cuenta.
      </p>

      <div v-if="errorForm" class="auth-error" role="alert">
        {{ errorForm }}
      </div>

      <form class="auth-form" @submit.prevent="enviar">
        <label class="campo">
          <span>Correo electrónico</span>
          <input
            v-model="email"
            type="email"
            required
            autocomplete="email"
            placeholder="tu@correo.com"
          />
        </label>

        <label class="campo">
          <span>Contraseña</span>
          <div class="campo-password">
            <input
              v-model="password"
              :type="mostrarPassword ? 'text' : 'password'"
              required
              autocomplete="current-password"
              placeholder="••••••••"
            />
            <button
              type="button"
              class="boton-password"
              :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              :title="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              @click="mostrarPassword = !mostrarPassword"
            >
              <svg
                v-if="!mostrarPassword"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              <svg
                v-else
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="m3 3 18 18M10.6 6.1A10.7 10.7 0 0 1 12 6c6.5 0 10 6 10 6a16.5 16.5 0 0 1-2.1 2.7M6.2 6.2C3.5 8 2 12 2 12s3.5 6 10 6a9.7 9.7 0 0 0 4-.8M9.9 9.9a3 3 0 0 0 4.2 4.2" />
              </svg>
            </button>
          </div>
        </label>

        <button
          type="submit"
          class="btn btn-primario btn-ancho"
          :disabled="authStore.cargando"
        >
          {{ authStore.cargando ? 'Ingresando...' : 'Entrar a mi cuenta' }}
        </button>
      </form>

      <p class="auth-pie">
        ¿Aún no eres socio?
        <RouterLink to="/registro" class="enlace">Regístrate aquí</RouterLink>
      </p>
    </section>
  </main>
</template>

<style scoped>
.auth-pagina {
  padding: 3rem 1.25rem;
  display: flex;
  justify-content: center;
}

.auth-tarjeta {
  width: 100%;
  max-width: 430px;
  padding: 2.1rem;
}

.auth-titulo {
  font-size: 1.7rem;
  margin: 0.55rem 0 0.3rem;
}

.auth-subtitulo {
  font-size: 0.92rem;
  color: var(--color-texto-suave);
  margin-bottom: 1.4rem;
}

.auth-error {
  background-color: var(--color-error-bg);
  color: var(--color-error-txt);
  padding: 0.75rem 0.95rem;
  border-radius: var(--radio-sm);
  font-size: 0.88rem;
  margin-bottom: 1rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.88rem;
  font-weight: 500;
}

.campo input {
  padding: 0.68rem 0.9rem;
  border-radius: var(--radio-sm);
  border: 1px solid var(--color-borde);
  background-color: var(--color-crema);
  outline: none;
}

.campo input:focus {
  border-color: var(--color-lila-oscuro);
  background-color: var(--color-blanco-calido);
}

.campo-password {
  position: relative;
}

.campo-password input {
  width: 100%;
  padding-right: 3rem;
}

.boton-password {
  position: absolute;
  top: 50%;
  right: 0.65rem;
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  padding: 0;
  transform: translateY(-50%);
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--color-texto-suave);
  cursor: pointer;
}

.boton-password:hover {
  background: var(--color-lila);
  color: var(--color-lila-oscuro);
}

.boton-password svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.btn-ancho {
  width: 100%;
  margin-top: 0.35rem;
}

.auth-pie {
  text-align: center;
  font-size: 0.88rem;
  color: var(--color-texto-suave);
  margin-top: 1.25rem;
}

.enlace {
  color: var(--color-lila-oscuro);
  font-weight: 600;
  text-decoration: underline;
}
</style>
