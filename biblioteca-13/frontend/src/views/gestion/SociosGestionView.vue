<script setup>
import { onMounted, reactive, ref } from 'vue'
import { sociosApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import GestionTabla from '@/components/GestionTabla.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()
const socios = ref([])
const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const skip = ref(0)
const total = ref(0)
const limite = 20
const editandoId = ref(null)
const formularioElemento = ref(null)
const filtroActivo = ref('')
const formulario = reactive({
  nombre: '',
  email: '',
  telefono: '',
  activo: true
})
const columnas = [
  { clave: 'nombre', titulo: 'Nombre' },
  { clave: 'email', titulo: 'Correo' },
  { clave: 'telefono', titulo: 'Teléfono' },
  { clave: 'estado', titulo: 'Estado' },
  { clave: 'fecha_alta_texto', titulo: 'Fecha de alta' }
]

async function cargar() {
  cargando.value = true
  error.value = ''
  const params = { skip: skip.value, limit: limite }
  if (filtroActivo.value !== '') params.activo = filtroActivo.value
  try {
    const { data } = await sociosApi.listar(params)
    socios.value = (data.items || []).map((socio) => ({
      ...socio,
      estado: socio.activo ? 'Activo' : 'Inactivo',
      fecha_alta_texto: new Date(socio.fecha_alta).toLocaleDateString('es-CO')
    }))
    total.value = data.total || 0
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudieron cargar los socios.')
  } finally {
    cargando.value = false
  }
}

function limpiarFormulario() {
  editandoId.value = null
  Object.assign(formulario, {
    nombre: '',
    email: '',
    telefono: '',
    activo: true
  })
}

function editar(socio) {
  editandoId.value = socio.id
  Object.assign(formulario, {
    nombre: socio.nombre,
    email: socio.email,
    telefono: socio.telefono || '',
    activo: socio.activo
  })
  formularioElemento.value?.scrollIntoView({ behavior: 'smooth' })
}

async function guardar() {
  guardando.value = true
  const datos = {
    nombre: formulario.nombre.trim(),
    email: formulario.email.trim(),
    telefono: formulario.telefono.trim() || null
  }
  if (editandoId.value) datos.activo = formulario.activo

  try {
    if (editandoId.value) {
      await sociosApi.actualizar(editandoId.value, datos)
      notificaciones.exito('Socio actualizado correctamente.')
    } else {
      await sociosApi.crear(datos)
      notificaciones.exito('Socio creado correctamente.')
    }
    limpiarFormulario()
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo guardar el socio.'))
  } finally {
    guardando.value = false
  }
}

async function eliminar(socio) {
  if (!window.confirm(`¿Eliminar al socio ${socio.nombre}?`)) return
  try {
    await sociosApi.eliminar(socio.id)
    notificaciones.exito('Socio eliminado correctamente.')
    if (socios.value.length === 1 && skip.value > 0) skip.value -= limite
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo eliminar el socio.'))
  }
}

function aplicarFiltros() {
  skip.value = 0
  cargar()
}

function paginaAnterior() {
  skip.value = Math.max(0, skip.value - limite)
  cargar()
}

function paginaSiguiente() {
  skip.value += limite
  cargar()
}

onMounted(cargar)
</script>

<template>
  <div class="gestion-vista">
    <header class="gestion-cabecera">
      <div>
        <span class="badge badge-lila">Miembros</span>
        <h1 class="titulo-serif">Socios</h1>
        <p>Administra los datos y el estado de los socios de la biblioteca.</p>
      </div>
    </header>

    <form
      ref="formularioElemento"
      class="gestion-formulario tarjeta-base"
      @submit.prevent="guardar"
    >
      <h2 class="titulo-serif">{{ editandoId ? 'Editar socio' : 'Registrar socio' }}</h2>
      <div class="gestion-form-grid">
        <label class="gestion-campo">
          <span>Nombre completo</span>
          <input v-model="formulario.nombre" required minlength="2" maxlength="100" />
        </label>
        <label class="gestion-campo">
          <span>Correo electrónico</span>
          <input v-model="formulario.email" type="email" required maxlength="150" />
        </label>
        <label class="gestion-campo">
          <span>Teléfono</span>
          <input v-model="formulario.telefono" type="tel" minlength="7" maxlength="15" />
        </label>
        <label v-if="editandoId" class="gestion-campo gestion-checkbox">
          <span>Cuenta activa</span>
          <input v-model="formulario.activo" type="checkbox" />
        </label>
      </div>
      <p class="gestion-ayuda">
        Este formulario registra el perfil de socio. El acceso a la cuenta se administra por separado.
      </p>
      <div class="gestion-form-acciones">
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Guardando...' : editandoId ? 'Guardar cambios' : 'Crear socio' }}
        </button>
        <button v-if="editandoId" type="button" class="btn btn-suave" @click="limpiarFormulario">
          Cancelar
        </button>
      </div>
    </form>

    <div class="gestion-filtros tarjeta-base">
      <label class="gestion-campo">
        <span>Estado</span>
        <select v-model="filtroActivo" @change="aplicarFiltros">
          <option value="">Todos los socios</option>
          <option :value="true">Activos</option>
          <option :value="false">Inactivos</option>
        </select>
      </label>
    </div>

    <GestionTabla
      :columnas="columnas"
      :filas="socios"
      :cargando="cargando"
      :error="error"
      :total="total"
      :skip="skip"
      :limite="limite"
      mensaje-vacio="No hay socios que coincidan con el filtro."
      @reintentar="cargar"
      @anterior="paginaAnterior"
      @siguiente="paginaSiguiente"
    >
      <template #acciones="{ fila }">
        <div class="gestion-acciones-fila">
          <button type="button" class="btn-tabla" @click="editar(fila)">Editar</button>
          <button
            v-if="authStore.usuario?.rol === 'admin'"
            type="button"
            class="btn-tabla btn-tabla-peligro"
            @click="eliminar(fila)"
          >
            Eliminar
          </button>
        </div>
      </template>
    </GestionTabla>
  </div>
</template>
