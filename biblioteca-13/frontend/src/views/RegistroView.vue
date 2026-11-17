<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const router = useRouter()
const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()

const form = reactive({
  nombre: '',
  email: '',
  telefono: '',
  password: '',
  confirmar_password: ''
})

const errorForm = ref('')

async function enviar() {
  errorForm.value = ''
  if (form.password !== form.confirmar_password) {
    errorForm.value = 'Las contraseñas no coinciden.'
    return
  }

  const payload = {
    nombre: form.nombre,
    email: form.email,
    password: form.password,
    confirmar_password: form.confirmar_password
  }
  if (form.telefono.trim()) {
    payload.telefono = form.telefono.trim()
  }

  const res = await authStore.registrar(payload)
  if (res.ok) {
    notificaciones.exito('Cuenta creada con éxito. Ahora puedes iniciar sesión.')
    router.push('/login')
  } else {
    errorForm.value = res.mensaje
    notificaciones.error(res.mensaje)
  }
}
</script>

<template>
  <main class="contenedor auth-pagina">
    <section class="auth-tarjeta tarjeta-base">
      <span class="badge badge-lila">Nuevo socio</span>
      <h1 class="titulo-serif auth-titulo">Crear cuenta</h1>
      <p class="auth-subtitulo">
        Regístrate para consultar tus préstamos y multas en la biblioteca.
      </p>

      <div v-if="errorForm" class="auth-error" role="alert">
        {{ errorForm }}
      </div>

      <form class="auth-form" @submit.prevent="enviar">
        <label class="campo">
          <span>Nombre completo</span>
          <input v-model="form.nombre" type="text" required minlength="3" placeholder="María Pérez" />
        </label>

        <label class="campo">
          <span>Correo electrónico</span>
          <input v-model="form.email" type="email" required placeholder="tu@correo.com" />
        </label>

        <label class="campo">
          <span>Teléfono (opcional)</span>
          <input v-model="form.telefono" type="tel" minlength="7" maxlength="15" placeholder="3001234567" />
        </label>

        <label class="campo">
          <span>Contraseña</span>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="8"
            placeholder="Mín. 8 caracteres, mayúscula, minúscula y número"
          />
        </label>

        <label class="campo">
          <span>Confirmar contraseña</span>
          <input
            v-model="form.confirmar_password"
            type="password"
            required
            minlength="8"
            placeholder="Repite tu contraseña"
          />
        </label>

        <button
          type="submit"
          class="btn btn-primario btn-ancho"
          :disabled="authStore.cargando"
        >
          {{ authStore.cargando ? 'Registrando...' : 'Crear mi cuenta' }}
        </button>
      </form>

      <p class="auth-pie">
        ¿Ya tienes cuenta?
        <RouterLink to="/login" class="enlace">Inicia sesión</RouterLink>
      </p>
    </section>
  </main>
</template>

<style scoped>
.auth-pagina {
  padding: 2.5rem 1.25rem;
  display: flex;
  justify-content: center;
}

.auth-tarjeta {
  width: 100%;
  max-width: 450px;
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
  gap: 0.9rem;
}

.campo {
  display: flex;
  flex-direction: column;
  gap: 0.32rem;
  font-size: 0.88rem;
  font-weight: 500;
}

.campo input {
  padding: 0.65rem 0.9rem;
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
