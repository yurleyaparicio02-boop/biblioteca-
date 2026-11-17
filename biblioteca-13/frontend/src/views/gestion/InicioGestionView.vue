<script setup>
import { computed, onMounted, ref } from 'vue'
import { reportesApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const resumen = ref(null)
const cargando = ref(true)
const error = ref('')
const numero = new Intl.NumberFormat('es-CO')

const indicadores = computed(() => {
  if (!resumen.value) return []
  return [
    { etiqueta: 'Libros en catálogo', valor: numero.format(resumen.value.total_libros), tono: 'lila' },
    { etiqueta: 'Ejemplares totales', valor: numero.format(resumen.value.total_ejemplares), tono: 'salvia' },
    { etiqueta: 'Préstamos activos', valor: numero.format(resumen.value.total_prestados), tono: 'rosa' },
    { etiqueta: 'Socios activos', valor: numero.format(resumen.value.socios_activos), tono: 'beige' },
    { etiqueta: 'Préstamos vencidos', valor: numero.format(resumen.value.prestamos_vencidos), tono: 'rosa' },
    { etiqueta: 'Multas pendientes', valor: numero.format(resumen.value.multas_pendientes), tono: 'lila' }
  ]
})

const accesos = computed(() => {
  const items = [
    { ruta: '/gestion/libros', titulo: 'Libros', descripcion: 'Administra el catálogo y las portadas.' },
    { ruta: '/gestion/autores', titulo: 'Autores', descripcion: 'Mantén al día la información de autores.' },
    { ruta: '/gestion/categorias', titulo: 'Categorías', descripcion: 'Organiza los géneros disponibles.' },
    { ruta: '/gestion/socios', titulo: 'Socios', descripcion: 'Consulta y actualiza a los miembros.' },
    { ruta: '/gestion/prestamos', titulo: 'Préstamos', descripcion: 'Registra préstamos y devoluciones.' },
    { ruta: '/gestion/reportes', titulo: 'Reportes', descripcion: 'Revisa la actividad de la biblioteca.' }
  ]

  if (authStore.usuario?.rol === 'admin') {
    items.splice(3, 0, {
      ruta: '/gestion/usuarios',
      titulo: 'Usuarios',
      descripcion: 'Administra las cuentas y sus permisos.'
    })
  }

  return items
})

async function cargarResumen() {
  cargando.value = true
  error.value = ''
  try {
    const { data } = await reportesApi.resumen()
    resumen.value = data
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudo cargar el resumen de la biblioteca.')
  } finally {
    cargando.value = false
  }
}

onMounted(cargarResumen)
</script>

<template>
  <div class="gestion-vista">
    <header class="gestion-cabecera">
      <div>
        <span class="badge badge-lila">Panel de control</span>
        <h1 class="titulo-serif">Hola, {{ authStore.usuario?.nombre }}</h1>
        <p>Este es el resumen de actividad de tu biblioteca.</p>
      </div>
      <button type="button" class="btn btn-suave" :disabled="cargando" @click="cargarResumen">
        Actualizar
      </button>
    </header>

    <div v-if="error" class="gestion-alerta" role="alert">
      <span>{{ error }}</span>
      <button type="button" class="btn btn-suave" @click="cargarResumen">Reintentar</button>
    </div>

    <div v-else-if="cargando" class="gestion-cargando" role="status" aria-busy="true">
      <span class="spinner" aria-hidden="true"></span>
      Cargando el resumen...
    </div>

    <section v-else class="indicadores-grid" aria-label="Indicadores de la biblioteca">
      <article
        v-for="indicador in indicadores"
        :key="indicador.etiqueta"
        class="indicador-card tarjeta-base"
        :class="`indicador-${indicador.tono}`"
      >
        <span>{{ indicador.etiqueta }}</span>
        <strong>{{ indicador.valor }}</strong>
      </article>
    </section>

    <section class="accesos-gestion">
      <div class="gestion-subtitulo">
        <h2 class="titulo-serif">Accesos rápidos</h2>
        <p>Elige una sección para continuar.</p>
      </div>
      <div class="accesos-grid">
        <RouterLink
          v-for="acceso in accesos"
          :key="acceso.ruta"
          :to="acceso.ruta"
          class="acceso-card tarjeta-base"
        >
          <strong>{{ acceso.titulo }}</strong>
          <span>{{ acceso.descripcion }}</span>
          <span class="acceso-ir" aria-hidden="true">→</span>
        </RouterLink>
      </div>
    </section>
  </div>
</template>
