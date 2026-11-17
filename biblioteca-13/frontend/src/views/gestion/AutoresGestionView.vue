<script setup>
import { onMounted, reactive, ref } from 'vue'
import { autoresApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import GestionTabla from '@/components/GestionTabla.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()
const autores = ref([])
const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const skip = ref(0)
const total = ref(0)
const limite = 20
const editandoId = ref(null)
const formularioElemento = ref(null)
const anioMaximo = new Date().getFullYear()
const formulario = reactive({ nombre: '', nacionalidad: '', anio_nacimiento: '' })
const columnas = [
  { clave: 'nombre', titulo: 'Nombre' },
  { clave: 'nacionalidad', titulo: 'Nacionalidad' },
  { clave: 'anio_nacimiento', titulo: 'Año de nacimiento' }
]

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const { data } = await autoresApi.listar({ skip: skip.value, limit: limite })
    autores.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudieron cargar los autores.')
  } finally {
    cargando.value = false
  }
}

function limpiarFormulario() {
  editandoId.value = null
  Object.assign(formulario, { nombre: '', nacionalidad: '', anio_nacimiento: '' })
}

function editar(autor) {
  editandoId.value = autor.id
  Object.assign(formulario, {
    nombre: autor.nombre,
    nacionalidad: autor.nacionalidad || '',
    anio_nacimiento: autor.anio_nacimiento ?? ''
  })
  formularioElemento.value?.scrollIntoView({ behavior: 'smooth' })
}

async function guardar() {
  guardando.value = true
  const datos = {
    nombre: formulario.nombre.trim(),
    nacionalidad: formulario.nacionalidad.trim() || null,
    anio_nacimiento: formulario.anio_nacimiento
      ? Number(formulario.anio_nacimiento)
      : null
  }
  try {
    if (editandoId.value) {
      await autoresApi.actualizar(editandoId.value, datos)
      notificaciones.exito('Autor actualizado correctamente.')
    } else {
      await autoresApi.crear(datos)
      notificaciones.exito('Autor creado correctamente.')
    }
    limpiarFormulario()
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo guardar el autor.'))
  } finally {
    guardando.value = false
  }
}

async function eliminar(autor) {
  if (!window.confirm(`¿Eliminar al autor ${autor.nombre}?`)) return
  try {
    await autoresApi.eliminar(autor.id)
    notificaciones.exito('Autor eliminado correctamente.')
    if (autores.value.length === 1 && skip.value > 0) skip.value -= limite
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo eliminar el autor.'))
  }
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
        <span class="badge badge-lila">Catálogo</span>
        <h1 class="titulo-serif">Autores</h1>
        <p>Registra y actualiza la información de los autores.</p>
      </div>
    </header>

    <form
      ref="formularioElemento"
      class="gestion-formulario tarjeta-base"
      @submit.prevent="guardar"
    >
      <h2 class="titulo-serif">{{ editandoId ? 'Editar autor' : 'Nuevo autor' }}</h2>
      <div class="gestion-form-grid">
        <label class="gestion-campo">
          <span>Nombre</span>
          <input v-model="formulario.nombre" required minlength="2" maxlength="100" />
        </label>
        <label class="gestion-campo">
          <span>Nacionalidad</span>
          <input v-model="formulario.nacionalidad" maxlength="60" />
        </label>
        <label class="gestion-campo">
          <span>Año de nacimiento</span>
          <input
            v-model="formulario.anio_nacimiento"
            type="number"
            min="1000"
            :max="anioMaximo"
          />
        </label>
      </div>
      <div class="gestion-form-acciones">
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Guardando...' : editandoId ? 'Guardar cambios' : 'Crear autor' }}
        </button>
        <button v-if="editandoId" type="button" class="btn btn-suave" @click="limpiarFormulario">
          Cancelar
        </button>
      </div>
    </form>

    <GestionTabla
      :columnas="columnas"
      :filas="autores"
      :cargando="cargando"
      :error="error"
      :total="total"
      :skip="skip"
      :limite="limite"
      mensaje-vacio="Todavía no hay autores registrados."
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
