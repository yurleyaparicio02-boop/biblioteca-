<script setup>
import { onMounted, reactive, ref } from 'vue'
import { categoriasApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import GestionTabla from '@/components/GestionTabla.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()
const categorias = ref([])
const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const skip = ref(0)
const total = ref(0)
const limite = 20
const editandoId = ref(null)
const formularioElemento = ref(null)
const formulario = reactive({ nombre: '', descripcion: '' })
const columnas = [
  { clave: 'nombre', titulo: 'Categoría' },
  { clave: 'descripcion', titulo: 'Descripción' }
]

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const { data } = await categoriasApi.listar({ skip: skip.value, limit: limite })
    categorias.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudieron cargar las categorías.')
  } finally {
    cargando.value = false
  }
}

function limpiarFormulario() {
  editandoId.value = null
  Object.assign(formulario, { nombre: '', descripcion: '' })
}

function editar(categoria) {
  editandoId.value = categoria.id
  Object.assign(formulario, {
    nombre: categoria.nombre,
    descripcion: categoria.descripcion || ''
  })
  formularioElemento.value?.scrollIntoView({ behavior: 'smooth' })
}

async function guardar() {
  guardando.value = true
  const datos = {
    nombre: formulario.nombre.trim(),
    descripcion: formulario.descripcion.trim() || null
  }
  try {
    if (editandoId.value) {
      await categoriasApi.actualizar(editandoId.value, datos)
      notificaciones.exito('Categoría actualizada correctamente.')
    } else {
      await categoriasApi.crear(datos)
      notificaciones.exito('Categoría creada correctamente.')
    }
    limpiarFormulario()
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo guardar la categoría.'))
  } finally {
    guardando.value = false
  }
}

async function eliminar(categoria) {
  if (!window.confirm(`¿Eliminar la categoría ${categoria.nombre}?`)) return
  try {
    await categoriasApi.eliminar(categoria.id)
    notificaciones.exito('Categoría eliminada correctamente.')
    if (categorias.value.length === 1 && skip.value > 0) skip.value -= limite
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo eliminar la categoría.'))
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
        <h1 class="titulo-serif">Categorías</h1>
        <p>Organiza los géneros disponibles en la biblioteca.</p>
      </div>
    </header>

    <form
      ref="formularioElemento"
      class="gestion-formulario tarjeta-base"
      @submit.prevent="guardar"
    >
      <h2 class="titulo-serif">{{ editandoId ? 'Editar categoría' : 'Nueva categoría' }}</h2>
      <div class="gestion-form-grid">
        <label class="gestion-campo">
          <span>Nombre</span>
          <input v-model="formulario.nombre" required minlength="3" maxlength="50" />
        </label>
        <label class="gestion-campo">
          <span>Descripción</span>
          <input v-model="formulario.descripcion" maxlength="200" />
        </label>
      </div>
      <div class="gestion-form-acciones">
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Guardando...' : editandoId ? 'Guardar cambios' : 'Crear categoría' }}
        </button>
        <button v-if="editandoId" type="button" class="btn btn-suave" @click="limpiarFormulario">
          Cancelar
        </button>
      </div>
    </form>

    <GestionTabla
      :columnas="columnas"
      :filas="categorias"
      :cargando="cargando"
      :error="error"
      :total="total"
      :skip="skip"
      :limite="limite"
      mensaje-vacio="Todavía no hay categorías registradas."
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
