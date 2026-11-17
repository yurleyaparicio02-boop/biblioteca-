<script setup>
import { onMounted, reactive, ref } from 'vue'
import { autoresApi, categoriasApi, librosApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import GestionTabla from '@/components/GestionTabla.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()
const libros = ref([])
const autores = ref([])
const categorias = ref([])
const cargando = ref(false)
const cargandoCatalogos = ref(false)
const guardando = ref(false)
const error = ref('')
const errorCatalogos = ref('')
const skip = ref(0)
const total = ref(0)
const limite = 20
const editandoId = ref(null)
const formularioElemento = ref(null)
const anioMaximo = new Date().getFullYear()
const formulario = reactive({
  titulo: '',
  isbn: '',
  anio_publicacion: anioMaximo,
  ejemplares: 1,
  autor_id: '',
  categoria_ids: [],
  imagen_url: ''
})
const columnas = [
  { clave: 'titulo', titulo: 'Título' },
  { clave: 'autor_nombre', titulo: 'Autor' },
  { clave: 'isbn', titulo: 'ISBN' },
  { clave: 'categorias_texto', titulo: 'Categorías' },
  { clave: 'disponibilidad', titulo: 'Disponibles' }
]

async function cargarCatalogos() {
  cargandoCatalogos.value = true
  errorCatalogos.value = ''
  try {
    const [resAutores, resCategorias] = await Promise.all([
      autoresApi.listar({ skip: 0, limit: 100 }),
      categoriasApi.listar({ skip: 0, limit: 100 })
    ])
    autores.value = resAutores.data.items || []
    categorias.value = resCategorias.data.items || []
  } catch (err) {
    errorCatalogos.value = extraerMensajeError(
      err,
      'No se pudieron cargar autores y categorías.'
    )
  } finally {
    cargandoCatalogos.value = false
  }
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const { data } = await librosApi.listar({ skip: skip.value, limit: limite })
    libros.value = (data.items || []).map((libro) => ({
      ...libro,
      autor_nombre: libro.autor?.nombre || 'Autor desconocido',
      categorias_texto: (libro.categorias || []).map((categoria) => categoria.nombre).join(', '),
      disponibilidad: `${libro.disponibles} / ${libro.ejemplares}`
    }))
    total.value = data.total || 0
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudieron cargar los libros.')
  } finally {
    cargando.value = false
  }
}

function limpiarFormulario() {
  editandoId.value = null
  Object.assign(formulario, {
    titulo: '',
    isbn: '',
    anio_publicacion: anioMaximo,
    ejemplares: 1,
    autor_id: '',
    categoria_ids: [],
    imagen_url: ''
  })
}

function editar(libro) {
  editandoId.value = libro.id
  Object.assign(formulario, {
    titulo: libro.titulo,
    isbn: libro.isbn,
    anio_publicacion: libro.anio_publicacion,
    ejemplares: libro.ejemplares,
    autor_id: libro.autor?.id ?? '',
    categoria_ids: (libro.categorias || []).map((categoria) => categoria.id),
    imagen_url: libro.imagen_url || ''
  })
  formularioElemento.value?.scrollIntoView({ behavior: 'smooth' })
}

async function guardar() {
  guardando.value = true
  const datos = {
    titulo: formulario.titulo.trim(),
    isbn: formulario.isbn.trim(),
    anio_publicacion: Number(formulario.anio_publicacion),
    ejemplares: Number(formulario.ejemplares),
    autor_id: Number(formulario.autor_id),
    categoria_ids: formulario.categoria_ids.map(Number),
    imagen_url: formulario.imagen_url.trim() || null
  }
  try {
    if (editandoId.value) {
      await librosApi.actualizar(editandoId.value, datos)
      notificaciones.exito('Libro actualizado correctamente.')
    } else {
      await librosApi.crear(datos)
      notificaciones.exito('Libro creado correctamente.')
    }
    limpiarFormulario()
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo guardar el libro.'))
  } finally {
    guardando.value = false
  }
}

async function eliminar(libro) {
  if (!window.confirm(`¿Eliminar el libro “${libro.titulo}”?`)) return
  try {
    await librosApi.eliminar(libro.id)
    notificaciones.exito('Libro eliminado correctamente.')
    if (libros.value.length === 1 && skip.value > 0) skip.value -= limite
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo eliminar el libro.'))
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

onMounted(async () => {
  await Promise.all([cargarCatalogos(), cargar()])
})
</script>

<template>
  <div class="gestion-vista">
    <header class="gestion-cabecera">
      <div>
        <span class="badge badge-lila">Catálogo</span>
        <h1 class="titulo-serif">Libros</h1>
        <p>Administra títulos, existencias y las portadas guardadas en Cloudinary.</p>
      </div>
      <RouterLink to="/" class="btn btn-suave">Ver catálogo</RouterLink>
    </header>

    <div v-if="errorCatalogos" class="gestion-alerta" role="alert">
      <span>{{ errorCatalogos }}</span>
      <button type="button" class="btn btn-suave" @click="cargarCatalogos">Reintentar</button>
    </div>

    <form
      ref="formularioElemento"
      class="gestion-formulario tarjeta-base"
      @submit.prevent="guardar"
    >
      <h2 class="titulo-serif">{{ editandoId ? 'Editar libro' : 'Registrar libro' }}</h2>
      <div v-if="cargandoCatalogos" class="gestion-form-estado" role="status">
        Cargando autores y categorías...
      </div>
      <div class="gestion-form-grid gestion-form-grid-3">
        <label class="gestion-campo">
          <span>Título</span>
          <input v-model="formulario.titulo" required minlength="1" maxlength="150" />
        </label>
        <label class="gestion-campo">
          <span>ISBN (13 dígitos)</span>
          <input
            v-model="formulario.isbn"
            required
            inputmode="numeric"
            pattern="[0-9]{13}"
            maxlength="13"
          />
        </label>
        <label class="gestion-campo">
          <span>Año de publicación</span>
          <input
            v-model="formulario.anio_publicacion"
            type="number"
            min="1450"
            :max="anioMaximo"
            required
          />
        </label>
        <label class="gestion-campo">
          <span>Ejemplares</span>
          <input v-model="formulario.ejemplares" type="number" min="1" max="50" required />
        </label>
        <label class="gestion-campo">
          <span>Autor</span>
          <select v-model="formulario.autor_id" required>
            <option value="" disabled>Selecciona un autor</option>
            <option v-for="autor in autores" :key="autor.id" :value="autor.id">
              {{ autor.nombre }}
            </option>
          </select>
        </label>
        <label class="gestion-campo">
          <span>Categorías (Ctrl/Cmd para varias)</span>
          <select v-model="formulario.categoria_ids" multiple required size="3">
            <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
              {{ categoria.nombre }}
            </option>
          </select>
        </label>
        <label class="gestion-campo gestion-campo-ancho">
          <span>URL de portada (opcional)</span>
          <input
            v-model="formulario.imagen_url"
            type="url"
            maxlength="500"
            placeholder="Usa una URL segura de Cloudinary"
          />
        </label>
      </div>
      <p class="gestion-ayuda">
        Si dejas la portada vacía, se conserva la imagen configurada por el backend. También puedes
        actualizarla desde el detalle del libro.
      </p>
      <div class="gestion-form-acciones">
        <button
          type="submit"
          class="btn btn-primario"
          :disabled="guardando || cargandoCatalogos || autores.length === 0 || categorias.length === 0"
        >
          {{ guardando ? 'Guardando...' : editandoId ? 'Guardar cambios' : 'Crear libro' }}
        </button>
        <button v-if="editandoId" type="button" class="btn btn-suave" @click="limpiarFormulario">
          Cancelar
        </button>
      </div>
    </form>

    <GestionTabla
      :columnas="columnas"
      :filas="libros"
      :cargando="cargando"
      :error="error"
      :total="total"
      :skip="skip"
      :limite="limite"
      mensaje-vacio="Todavía no hay libros registrados."
      @reintentar="cargar"
      @anterior="paginaAnterior"
      @siguiente="paginaSiguiente"
    >
      <template #acciones="{ fila }">
        <div class="gestion-acciones-fila">
          <button type="button" class="btn-tabla" @click="editar(fila)">Editar</button>
          <RouterLink :to="`/libros/${fila.id}`" class="btn-tabla">Detalle</RouterLink>
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
