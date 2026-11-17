<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { librosApi, prestamosApi, sociosApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import GestionTabla from '@/components/GestionTabla.vue'
import { useNotificacionesStore } from '@/stores/notificaciones'

const notificaciones = useNotificacionesStore()
const prestamos = ref([])
const libros = ref([])
const socios = ref([])
const cargando = ref(false)
const cargandoCatalogos = ref(false)
const guardando = ref(false)
const error = ref('')
const errorCatalogos = ref('')
const skip = ref(0)
const total = ref(0)
const limite = 20
const filtroEstado = ref('')
const prestamoEnProceso = ref(null)
const formulario = reactive({ libro_id: '', socio_id: '', dias: 14 })
const columnas = [
  { clave: 'id', titulo: 'N.º' },
  { clave: 'titulo', titulo: 'Libro' },
  { clave: 'socio', titulo: 'Socio' },
  { clave: 'fecha_prestamo_texto', titulo: 'Préstamo' },
  { clave: 'fecha_limite_texto', titulo: 'Fecha límite' },
  { clave: 'estado_texto', titulo: 'Estado' },
  { clave: 'multa_texto', titulo: 'Multa' }
]

const librosDisponibles = computed(() =>
  libros.value.filter((libro) => libro.disponibles > 0)
)
const sociosActivos = computed(() => socios.value.filter((socio) => socio.activo))

async function cargarCatalogos() {
  cargandoCatalogos.value = true
  errorCatalogos.value = ''
  try {
    const [resLibros, resSocios] = await Promise.all([
      librosApi.listar({ skip: 0, limit: 100 }),
      sociosApi.listar({ skip: 0, limit: 100, activo: true })
    ])
    libros.value = resLibros.data.items || []
    socios.value = resSocios.data.items || []
  } catch (err) {
    errorCatalogos.value = extraerMensajeError(
      err,
      'No se pudieron cargar libros y socios para crear préstamos.'
    )
  } finally {
    cargandoCatalogos.value = false
  }
}

function fechaTexto(valor) {
  return valor ? String(valor).slice(0, 10) : '—'
}

async function cargar() {
  cargando.value = true
  error.value = ''
  const params = { skip: skip.value, limit: limite }
  if (filtroEstado.value) params.estado = filtroEstado.value
  try {
    const { data } = await prestamosApi.listar(params)
    const libroPorId = new Map(libros.value.map((libro) => [libro.id, libro]))
    const socioPorId = new Map(socios.value.map((socio) => [socio.id, socio]))
    prestamos.value = (data.items || []).map((prestamo) => ({
      ...prestamo,
      titulo: libroPorId.get(prestamo.libro_id)?.titulo || `Libro #${prestamo.libro_id}`,
      socio: socioPorId.get(prestamo.socio_id)?.nombre || `Socio #${prestamo.socio_id}`,
      fecha_prestamo_texto: fechaTexto(prestamo.fecha_prestamo),
      fecha_limite_texto: fechaTexto(prestamo.fecha_limite),
      estado_texto: prestamo.estado.charAt(0).toUpperCase() + prestamo.estado.slice(1),
      multa_texto: `${Number(prestamo.multa).toLocaleString('es-CO')}${
        prestamo.estado_multa === 'pendiente' ? ' · pendiente' : ''
      }`
    }))
    total.value = data.total || 0
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudieron cargar los préstamos.')
  } finally {
    cargando.value = false
  }
}

async function crearPrestamo() {
  guardando.value = true
  try {
    await prestamosApi.crear({
      libro_id: Number(formulario.libro_id),
      socio_id: Number(formulario.socio_id),
      dias: Number(formulario.dias)
    })
    notificaciones.exito('Préstamo registrado correctamente.')
    Object.assign(formulario, { libro_id: '', socio_id: '', dias: 14 })
    await cargarCatalogos()
    skip.value = 0
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo registrar el préstamo.'))
  } finally {
    guardando.value = false
  }
}

function fechaLocal() {
  const fecha = new Date()
  const mes = String(fecha.getMonth() + 1).padStart(2, '0')
  const dia = String(fecha.getDate()).padStart(2, '0')
  return `${fecha.getFullYear()}-${mes}-${dia}`
}

async function registrarDevolucion(prestamo) {
  if (!window.confirm(`¿Registrar la devolución del préstamo #${prestamo.id}?`)) return
  prestamoEnProceso.value = prestamo.id
  try {
    await prestamosApi.registrarDevolucion(prestamo.id, fechaLocal())
    notificaciones.exito('Devolución registrada correctamente.')
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo registrar la devolución.'))
  } finally {
    prestamoEnProceso.value = null
  }
}

async function pagarMulta(prestamo) {
  if (!window.confirm(`¿Registrar el pago de la multa del préstamo #${prestamo.id}?`)) return
  prestamoEnProceso.value = prestamo.id
  try {
    await prestamosApi.pagarMulta(prestamo.id)
    notificaciones.exito('Pago de multa registrado correctamente.')
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo registrar el pago de la multa.'))
  } finally {
    prestamoEnProceso.value = null
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

onMounted(async () => {
  await cargarCatalogos()
  await cargar()
  if (libros.value.length && !formulario.libro_id) {
    formulario.libro_id = librosDisponibles.value[0]?.id || ''
  }
  if (sociosActivos.value.length && !formulario.socio_id) {
    formulario.socio_id = sociosActivos.value[0].id
  }
})
</script>

<template>
  <div class="gestion-vista">
    <header class="gestion-cabecera">
      <div>
        <span class="badge badge-lila">Circulación</span>
        <h1 class="titulo-serif">Préstamos</h1>
        <p>Registra préstamos, devoluciones y pagos de multas.</p>
      </div>
    </header>

    <div v-if="errorCatalogos" class="gestion-alerta" role="alert">
      <span>{{ errorCatalogos }}</span>
      <button type="button" class="btn btn-suave" @click="cargarCatalogos">Reintentar</button>
    </div>

    <form class="gestion-formulario tarjeta-base" @submit.prevent="crearPrestamo">
      <h2 class="titulo-serif">Nuevo préstamo</h2>
      <div class="gestion-form-grid gestion-form-grid-4">
        <label class="gestion-campo">
          <span>Libro disponible</span>
          <select v-model="formulario.libro_id" required>
            <option value="" disabled>Selecciona un libro</option>
            <option v-for="libro in librosDisponibles" :key="libro.id" :value="libro.id">
              {{ libro.titulo }} · {{ libro.disponibles }} disponibles
            </option>
          </select>
        </label>
        <label class="gestion-campo">
          <span>Socio</span>
          <select v-model="formulario.socio_id" required>
            <option value="" disabled>Selecciona un socio</option>
            <option v-for="socio in sociosActivos" :key="socio.id" :value="socio.id">
              {{ socio.nombre }}
            </option>
          </select>
        </label>
        <label class="gestion-campo">
          <span>Días de préstamo</span>
          <input v-model="formulario.dias" type="number" min="1" max="30" required />
        </label>
      </div>
      <div class="gestion-form-acciones">
        <button
          type="submit"
          class="btn btn-primario"
          :disabled="
            guardando ||
            cargandoCatalogos ||
            librosDisponibles.length === 0 ||
            sociosActivos.length === 0
          "
        >
          {{ guardando ? 'Registrando...' : 'Registrar préstamo' }}
        </button>
        <span v-if="!cargandoCatalogos && librosDisponibles.length === 0" class="gestion-ayuda">
          No hay libros disponibles para prestar.
        </span>
      </div>
    </form>

    <div class="gestion-filtros tarjeta-base">
      <label class="gestion-campo">
        <span>Estado del préstamo</span>
        <select v-model="filtroEstado" @change="aplicarFiltros">
          <option value="">Todos los estados</option>
          <option value="activo">Activo</option>
          <option value="vencido">Vencido</option>
          <option value="devuelto">Devuelto</option>
        </select>
      </label>
    </div>

    <GestionTabla
      :columnas="columnas"
      :filas="prestamos"
      :cargando="cargando"
      :error="error"
      :total="total"
      :skip="skip"
      :limite="limite"
      mensaje-vacio="No hay préstamos que coincidan con el filtro."
      @reintentar="cargar"
      @anterior="paginaAnterior"
      @siguiente="paginaSiguiente"
    >
      <template #acciones="{ fila }">
        <div class="gestion-acciones-fila">
          <button
            v-if="fila.estado !== 'devuelto'"
            type="button"
            class="btn-tabla"
            :disabled="prestamoEnProceso === fila.id"
            @click="registrarDevolucion(fila)"
          >
            Devolver
          </button>
          <button
            v-if="fila.estado_multa === 'pendiente' && Number(fila.multa) > 0"
            type="button"
            class="btn-tabla btn-tabla-peligro"
            :disabled="prestamoEnProceso === fila.id"
            @click="pagarMulta(fila)"
          >
            Pagar multa
          </button>
        </div>
      </template>
    </GestionTabla>
  </div>
</template>
