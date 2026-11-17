<script setup>
import { onMounted, reactive, ref } from 'vue'
import { authApi, sociosApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import EstadoCarga from '@/components/EstadoCarga.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()
const prestamos = ref([])
const multas = ref([])
const socioPerfil = ref(null)
const totalAdeudado = ref(0)
const cargando = ref(true)
const guardandoPerfil = ref(false)
const cambiandoPassword = ref(false)
const error = ref('')
const errorPrestamos = ref('')
const errorPassword = ref('')
const perfilForm = reactive({ nombre: '', telefono: '' })
const passwordForm = reactive({ password_actual: '', password_nueva: '' })

async function cargarPerfil() {
  cargando.value = true
  error.value = ''
  errorPrestamos.value = ''
  try {
    await authStore.cargarPerfil()
    if (!authStore.usuario) {
      error.value = 'No se pudo validar la sesión. Inicia sesión nuevamente.'
      return
    }

    if (authStore.usuario.rol === 'socio') {
      const perfil = await sociosApi.miPerfil()
      socioPerfil.value = perfil.data
      Object.assign(perfilForm, {
        nombre: perfil.data.nombre,
        telefono: perfil.data.telefono || ''
      })
      const [respuestaPrestamos, respuestaMultas] = await Promise.allSettled([
        sociosApi.misPrestamos({ skip: 0, limit: 20 }),
        sociosApi.misMultas()
      ])
      if (respuestaPrestamos.status === 'fulfilled') {
        prestamos.value = respuestaPrestamos.value.data.items || []
      } else {
        errorPrestamos.value = extraerMensajeError(
          respuestaPrestamos.reason,
          'No se pudieron cargar tus préstamos.'
        )
      }
      if (respuestaMultas.status === 'fulfilled') {
        multas.value = respuestaMultas.value.data.items || []
        totalAdeudado.value = Number(respuestaMultas.value.data.total_adeudado || 0)
      } else {
        errorPrestamos.value = [
          errorPrestamos.value,
          extraerMensajeError(respuestaMultas.reason, 'No se pudieron cargar tus multas.')
        ]
          .filter(Boolean)
          .join(' ')
      }
    }
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudo cargar tu cuenta.')
  } finally {
    cargando.value = false
  }
}

async function guardarPerfil() {
  guardandoPerfil.value = true
  try {
    const { data } = await sociosApi.actualizarMiPerfil({
      nombre: perfilForm.nombre.trim(),
      telefono: perfilForm.telefono.trim() || null
    })
    socioPerfil.value = data
    notificaciones.exito('Tu perfil se actualizó correctamente.')
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo actualizar tu perfil.'))
  } finally {
    guardandoPerfil.value = false
  }
}

async function cambiarPassword() {
  errorPassword.value = ''
  cambiandoPassword.value = true
  try {
    const { data } = await authApi.cambiarPassword(
      passwordForm.password_actual,
      passwordForm.password_nueva
    )
    authStore.usuario = data
    Object.assign(passwordForm, { password_actual: '', password_nueva: '' })
    notificaciones.exito('Tu contraseña se actualizó correctamente.')
  } catch (err) {
    errorPassword.value = extraerMensajeError(err, 'No se pudo cambiar la contraseña.')
    notificaciones.error(errorPassword.value)
  } finally {
    cambiandoPassword.value = false
  }
}

onMounted(cargarPerfil)
</script>

<template>
  <main class="contenedor perfil-pagina">
    <EstadoCarga v-if="cargando" mensaje="Cargando tu perfil..." :tarjetas="2" />

    <div v-else-if="error" class="tarjeta-base perfil-error" role="alert">
      <p>{{ error }}</p>
      <RouterLink to="/login" class="btn btn-primario">Iniciar sesión</RouterLink>
    </div>

    <section v-else-if="authStore.usuario" class="perfil-contenido">
      <header class="perfil-cabecera">
        <div>
          <span class="badge badge-lila" style="text-transform: capitalize">
            {{ authStore.usuario.rol }}
          </span>
          <h1 class="titulo-serif perfil-titulo">
            {{ socioPerfil?.nombre || authStore.usuario.nombre }}
          </h1>
          <p class="perfil-email">{{ authStore.usuario.email }}</p>
        </div>
        <RouterLink v-if="authStore.esStaff" to="/gestion" class="btn btn-primario">
          Ir a gestión
        </RouterLink>
      </header>

      <div class="perfil-grid">
        <form
          v-if="authStore.usuario.rol === 'socio'"
          class="tarjeta-base perfil-card"
          @submit.prevent="guardarPerfil"
        >
          <h2 class="titulo-serif">Mis datos</h2>
          <label class="perfil-campo">
            <span>Nombre</span>
            <input v-model="perfilForm.nombre" required minlength="2" maxlength="100" />
          </label>
          <label class="perfil-campo">
            <span>Teléfono</span>
            <input v-model="perfilForm.telefono" type="tel" minlength="7" maxlength="15" />
          </label>
          <button type="submit" class="btn btn-primario" :disabled="guardandoPerfil">
            {{ guardandoPerfil ? 'Guardando...' : 'Guardar perfil' }}
          </button>
        </form>

        <form class="tarjeta-base perfil-card" @submit.prevent="cambiarPassword">
          <h2 class="titulo-serif">Cambiar contraseña</h2>
          <label class="perfil-campo">
            <span>Contraseña actual</span>
            <input
              v-model="passwordForm.password_actual"
              type="password"
              required
              autocomplete="current-password"
            />
          </label>
          <label class="perfil-campo">
            <span>Nueva contraseña</span>
            <input
              v-model="passwordForm.password_nueva"
              type="password"
              required
              minlength="8"
              maxlength="64"
              autocomplete="new-password"
            />
          </label>
          <p class="perfil-ayuda">Debe incluir mayúscula, minúscula y número.</p>
          <p v-if="errorPassword" class="perfil-error-texto" role="alert">{{ errorPassword }}</p>
          <button type="submit" class="btn btn-secundario" :disabled="cambiandoPassword">
            {{ cambiandoPassword ? 'Actualizando...' : 'Actualizar contraseña' }}
          </button>
        </form>
      </div>

      <section v-if="authStore.usuario.rol === 'socio'" class="tarjeta-base prestamos-card">
        <div class="prestamos-cabecera">
          <div>
            <h2 class="titulo-serif">Mis préstamos recientes</h2>
            <p v-if="errorPrestamos" class="perfil-error-texto" role="alert">{{ errorPrestamos }}</p>
            <p v-else-if="prestamos.length === 0" class="sin-prestamos">
              No tienes préstamos registrados por el momento.
            </p>
          </div>
          <div class="multa-resumen">
            <span>Multas pendientes</span>
            <strong>{{ totalAdeudado.toLocaleString('es-CO') }}</strong>
          </div>
        </div>
        <ul v-if="prestamos.length" class="lista-prestamos">
          <li v-for="p in prestamos" :key="p.id" class="item-prestamo">
            <div>
              <strong>Préstamo #{{ p.id }} · Libro #{{ p.libro_id }}</strong>
              <span class="fecha-prestamo">
                Límite: {{ String(p.fecha_limite).slice(0, 10) }}
              </span>
            </div>
            <span
              class="badge"
              :class="p.estado === 'devuelto' ? 'badge-salvia' : p.estado === 'vencido' ? 'badge-rosa' : 'badge-beige'"
            >
              {{ p.estado }}
            </span>
          </li>
        </ul>
        <div v-if="multas.length" class="multas-pendientes">
          <h3>Multas por pagar</h3>
          <p v-for="multa in multas" :key="multa.id">
            Préstamo #{{ multa.id }} · {{ Number(multa.multa).toLocaleString('es-CO') }}
          </p>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.perfil-pagina {
  padding-top: 1.5rem;
  padding-bottom: 3.5rem;
}

.perfil-contenido {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.perfil-cabecera,
.perfil-card,
.prestamos-card {
  padding: 1.35rem;
}

.perfil-cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 1px solid var(--color-borde);
  border-radius: var(--radio-md);
  background: linear-gradient(120deg, #f8e6e9, #f4edf6 60%, #eef3eb);
}

.perfil-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 1rem;
}

.perfil-grid .perfil-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.8rem;
}

.perfil-titulo {
  font-size: 1.7rem;
  margin: 0.45rem 0 0.1rem;
}

.perfil-email {
  color: var(--color-texto-suave);
}

.perfil-card h2,
.prestamos-card h2 {
  font-size: 1.3rem;
  margin-bottom: 0.25rem;
}

.perfil-campo {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  color: var(--color-texto-suave);
  font-size: 0.84rem;
}

.perfil-campo input {
  width: 100%;
  padding: 0.62rem 0.75rem;
  border: 1px solid var(--color-borde);
  border-radius: var(--radio-sm);
  background: var(--color-crema);
}

.perfil-ayuda,
.fecha-prestamo {
  color: var(--color-texto-tenue);
  font-size: 0.8rem;
}

.perfil-error,
.perfil-error-texto {
  color: var(--color-error-txt);
}

.perfil-error {
  padding: 1.5rem;
}

.perfil-error .btn {
  margin-top: 0.8rem;
}

.perfil-error-texto {
  font-size: 0.84rem;
}

.prestamos-cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.multa-resumen {
  display: flex;
  flex-direction: column;
  padding: 0.65rem 0.9rem;
  border-radius: var(--radio-sm);
  background: var(--color-alerta-bg);
  color: var(--color-alerta-txt);
  font-size: 0.75rem;
}

.multa-resumen strong {
  font-size: 1.05rem;
}

.sin-prestamos {
  color: var(--color-texto-suave);
}

.lista-prestamos {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.item-prestamo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  border-radius: var(--radio-sm);
  background-color: var(--color-crema);
  border: 1px solid var(--color-borde);
}

.fecha-prestamo {
  display: block;
  margin-top: 0.15rem;
}

.multas-pendientes {
  display: grid;
  gap: 0.3rem;
  margin-top: 1rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--color-borde);
  color: var(--color-alerta-txt);
  font-size: 0.84rem;
}

@media (max-width: 560px) {
  .perfil-cabecera,
  .prestamos-cabecera {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
