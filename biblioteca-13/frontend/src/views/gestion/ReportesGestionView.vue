<script setup>
import { computed, onMounted, ref } from 'vue'
import { reportesApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import GestionTabla from '@/components/GestionTabla.vue'

const cargando = ref(false)
const resumen = ref(null)
const librosMasPrestados = ref([])
const categorias = ref([])
const prestamosVencidos = ref([])
const sociosConMultas = ref([])
const autores = ref([])
const errores = ref({})
const numero = new Intl.NumberFormat('es-CO')
const limiteReporte = 100

const indicadores = computed(() => {
  if (!resumen.value) return []
  return [
    { etiqueta: 'Libros', valor: numero.format(resumen.value.total_libros) },
    { etiqueta: 'Ejemplares', valor: numero.format(resumen.value.total_ejemplares) },
    { etiqueta: 'En préstamo', valor: numero.format(resumen.value.total_prestados) },
    { etiqueta: 'Socios activos', valor: numero.format(resumen.value.socios_activos) },
    { etiqueta: 'Préstamos vencidos', valor: numero.format(resumen.value.prestamos_vencidos) },
    { etiqueta: 'Multas pendientes', valor: numero.format(resumen.value.multas_pendientes) }
  ]
})

const columnasLibros = [
  { clave: 'titulo', titulo: 'Libro' },
  { clave: 'autor', titulo: 'Autor' },
  { clave: 'total_prestamos', titulo: 'Préstamos' }
]
const columnasCategorias = [
  { clave: 'categoria', titulo: 'Categoría' },
  { clave: 'total_libros', titulo: 'Libros' }
]
const columnasVencidos = [
  { clave: 'titulo', titulo: 'Libro' },
  { clave: 'socio', titulo: 'Socio' },
  { clave: 'email', titulo: 'Correo' },
  { clave: 'fecha_limite', titulo: 'Fecha límite' },
  { clave: 'dias_retraso', titulo: 'Días de retraso' }
]
const columnasMultas = [
  { clave: 'socio', titulo: 'Socio' },
  { clave: 'total_multas', titulo: 'Total multas' },
  { clave: 'prestamos_con_multa', titulo: 'Préstamos con multa' }
]
const columnasAutores = [
  { clave: 'autor', titulo: 'Autor' },
  { clave: 'total_libros', titulo: 'Libros' },
  { clave: 'total_ejemplares', titulo: 'Ejemplares' },
  { clave: 'total_prestamos', titulo: 'Préstamos' }
]

async function cargar() {
  cargando.value = true
  errores.value = {}
  const consultas = [
    ['resumen', () => reportesApi.resumen()],
    ['libros', () => reportesApi.librosMasPrestados({ limite: 10, skip: 0 })],
    ['categorias', () => reportesApi.categorias({ skip: 0, limit: limiteReporte })],
    ['vencidos', () => reportesApi.prestamosVencidos({ skip: 0, limit: limiteReporte })],
    [
      'multas',
      () => reportesApi.sociosConMultas({ skip: 0, limit: limiteReporte, solo_pendientes: true })
    ],
    ['autores', () => reportesApi.autores({ skip: 0, limit: limiteReporte })]
  ]
  const resultados = await Promise.allSettled(consultas.map(([, consulta]) => consulta()))

  resultados.forEach((resultado, indice) => {
    const clave = consultas[indice][0]
    if (resultado.status === 'rejected') {
      errores.value[clave] = extraerMensajeError(
        resultado.reason,
        'No se pudo cargar este reporte.'
      )
      return
    }

    const { data } = resultado.value
    if (clave === 'resumen') {
      resumen.value = data
    } else if (clave === 'libros') {
      librosMasPrestados.value = (data.items || []).map((item) => ({
        ...item,
        id: item.libro_id
      }))
    } else if (clave === 'categorias') {
      categorias.value = (data.items || []).map((item) => ({
        ...item,
        id: item.categoria_id
      }))
    } else if (clave === 'vencidos') {
      prestamosVencidos.value = (data.items || []).map((item) => ({
        ...item,
        id: item.prestamo_id
      }))
    } else if (clave === 'multas') {
      sociosConMultas.value = (data.items || []).map((item) => ({
        ...item,
        id: item.socio_id,
        total_multas: numero.format(Number(item.total_multas))
      }))
    } else if (clave === 'autores') {
      autores.value = (data.items || []).map((item) => ({
        ...item,
        id: item.autor_id
      }))
    }
  })

  cargando.value = false
}

onMounted(cargar)
</script>

<template>
  <div class="gestion-vista">
    <header class="gestion-cabecera">
      <div>
        <span class="badge badge-lila">Indicadores</span>
        <h1 class="titulo-serif">Reportes</h1>
        <p>Consulta la actividad y el estado de la biblioteca.</p>
      </div>
      <button type="button" class="btn btn-suave" :disabled="cargando" @click="cargar">
        Actualizar reportes
      </button>
    </header>

    <div v-if="cargando && !resumen" class="gestion-cargando" role="status" aria-busy="true">
      <span class="spinner" aria-hidden="true"></span>
      Cargando reportes...
    </div>

    <section v-else-if="indicadores.length" class="indicadores-grid indicadores-grid-compacta">
      <article
        v-for="indicador in indicadores"
        :key="indicador.etiqueta"
        class="indicador-card tarjeta-base"
      >
        <span>{{ indicador.etiqueta }}</span>
        <strong>{{ indicador.valor }}</strong>
      </article>
    </section>

    <div v-if="errores.resumen" class="gestion-alerta" role="alert">
      <span>{{ errores.resumen }}</span>
    </div>

    <section class="reporte-seccion">
      <h2 class="titulo-serif">Libros más prestados</h2>
      <GestionTabla
        :columnas="columnasLibros"
        :filas="librosMasPrestados"
        :cargando="cargando"
        :error="errores.libros"
        :total="librosMasPrestados.length"
        :limite="limiteReporte"
        mensaje-vacio="Todavía no hay datos de préstamos."
        @reintentar="cargar"
      />
    </section>

    <section class="reporte-seccion">
      <h2 class="titulo-serif">Libros por categoría</h2>
      <GestionTabla
        :columnas="columnasCategorias"
        :filas="categorias"
        :cargando="cargando"
        :error="errores.categorias"
        :total="categorias.length"
        :limite="limiteReporte"
        mensaje-vacio="No hay categorías registradas."
        @reintentar="cargar"
      />
    </section>

    <section class="reporte-seccion">
      <h2 class="titulo-serif">Préstamos vencidos</h2>
      <GestionTabla
        :columnas="columnasVencidos"
        :filas="prestamosVencidos"
        :cargando="cargando"
        :error="errores.vencidos"
        :total="prestamosVencidos.length"
        :limite="limiteReporte"
        mensaje-vacio="No hay préstamos vencidos."
        @reintentar="cargar"
      />
    </section>

    <section class="reporte-seccion">
      <h2 class="titulo-serif">Socios con multas pendientes</h2>
      <GestionTabla
        :columnas="columnasMultas"
        :filas="sociosConMultas"
        :cargando="cargando"
        :error="errores.multas"
        :total="sociosConMultas.length"
        :limite="limiteReporte"
        mensaje-vacio="No hay multas pendientes."
        @reintentar="cargar"
      />
    </section>

    <section class="reporte-seccion">
      <h2 class="titulo-serif">Actividad por autor</h2>
      <GestionTabla
        :columnas="columnasAutores"
        :filas="autores"
        :cargando="cargando"
        :error="errores.autores"
        :total="autores.length"
        :limite="limiteReporte"
        mensaje-vacio="No hay estadísticas de autores."
        @reintentar="cargar"
      />
    </section>
  </div>
</template>
