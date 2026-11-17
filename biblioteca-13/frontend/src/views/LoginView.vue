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
          <input
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
          />
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
