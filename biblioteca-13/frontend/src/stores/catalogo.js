import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { autoresApi, categoriasApi, librosApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'

export const useCatalogoStore = defineStore('catalogo', () => {
  const libros = ref([])
  const totalLibros = ref(0)
  const categorias = ref([])
  const autores = ref([])
  const cargandoLibros = ref(false)
  const cargandoMeta = ref(false)
  const errorLibros = ref('')

  // Filtros reactivos
  const textoBusqueda = ref('')
  const tipoBusqueda = ref('todos') // 'todos' | 'titulo' | 'autor' | 'categoria'
  const categoriaId = ref(null)
  const orden = ref('titulo')
  const skip = ref(0)
  const limit = ref(12)
  let solicitudLibros = 0

  const hayFiltrosActivos = computed(
    () =>
      Boolean(textoBusqueda.value.trim()) ||
      categoriaId.value !== null ||
      orden.value !== 'titulo'
  )

  const paginaActual = computed(() => Math.floor(skip.value / limit.value) + 1)
  const totalPaginas = computed(() =>
    Math.max(1, Math.ceil(totalLibros.value / limit.value))
  )

  async function cargarMetadatos() {
    if (categorias.value.length > 0 && autores.value.length > 0) return
    cargandoMeta.value = true
    try {
      const [resCat, resAut] = await Promise.all([
        categoriasApi.listar({ skip: 0, limit: 100 }),
        autoresApi.listar({ skip: 0, limit: 100 })
      ])
      categorias.value = resCat.data.items || []
      autores.value = resAut.data.items || []
    } catch {
      // Si falla la carga secundaria, el catálogo principal sigue operando
    } finally {
      cargandoMeta.value = false
    }
  }

  async function buscarLibros() {
    const solicitudActual = ++solicitudLibros
    cargandoLibros.value = true
    errorLibros.value = ''

    const termino = textoBusqueda.value.trim()
    const params = {
      skip: skip.value,
      limit: limit.value,
      orden: orden.value,
      categoria_id: categoriaId.value
    }

    try {
      if (termino) {
        if (tipoBusqueda.value === 'titulo') {
          params.buscar = termino
        } else if (tipoBusqueda.value === 'autor') {
          params.autor = termino
        }

        const solicitudes = []
        if (tipoBusqueda.value !== 'categoria') {
          solicitudes.push(
            librosApi.listar({
              ...params,
              skip: 0,
              limit: 100,
              buscar: tipoBusqueda.value === 'autor' ? undefined : termino,
              autor: tipoBusqueda.value === 'autor' ? termino : undefined
            })
          )
          if (tipoBusqueda.value === 'todos') {
            solicitudes.push(
              librosApi.listar({
                ...params,
                skip: 0,
                limit: 100,
                autor: termino
              })
            )
          }
        }

        const coincidenciasCategoria = categorias.value.filter((categoria) =>
          categoria.nombre.toLocaleLowerCase().includes(termino.toLocaleLowerCase())
        )
        const categoriasParaBuscar = params.categoria_id
          ? coincidenciasCategoria.filter(
              (categoria) => categoria.id === params.categoria_id
            )
          : coincidenciasCategoria

        if (
          tipoBusqueda.value === 'categoria' ||
          tipoBusqueda.value === 'todos'
        ) {
          solicitudes.push(
            ...categoriasParaBuscar.map((categoria) =>
              librosApi.listar({
                ...params,
                skip: 0,
                limit: 100,
                categoria_id: categoria.id
              })
            )
          )
        }

        const respuestas = await Promise.all(solicitudes)
        const mapa = new Map()
        for (const respuesta of respuestas) {
          for (const item of respuesta.data.items || []) {
            mapa.set(item.id, item)
          }
        }

        const combinados = Array.from(mapa.values())
        if (orden.value === '-anio') {
          combinados.sort((a, b) => b.anio_publicacion - a.anio_publicacion)
        } else if (orden.value === 'anio') {
          combinados.sort((a, b) => a.anio_publicacion - b.anio_publicacion)
        } else {
          combinados.sort((a, b) => a.titulo.localeCompare(b.titulo))
        }

        if (solicitudActual !== solicitudLibros) return
        totalLibros.value = combinados.length
        libros.value = combinados.slice(skip.value, skip.value + limit.value)
        return
      }

      const { data } = await librosApi.listar(params)
      if (solicitudActual !== solicitudLibros) return
      libros.value = data.items || []
      totalLibros.value = data.total ?? libros.value.length
    } catch (err) {
      if (solicitudActual !== solicitudLibros) return
      errorLibros.value = extraerMensajeError(
        err,
        'No se pudieron cargar los libros del catálogo.'
      )
      libros.value = []
      totalLibros.value = 0
    } finally {
      if (solicitudActual === solicitudLibros) {
        cargandoLibros.value = false
      }
    }
  }

  function reiniciarFiltros() {
    textoBusqueda.value = ''
    tipoBusqueda.value = 'todos'
    categoriaId.value = null
    orden.value = 'titulo'
    skip.value = 0
    buscarLibros()
  }

  function cambiarPagina(nuevaPagina) {
    skip.value = (nuevaPagina - 1) * limit.value
    buscarLibros()
  }

  return {
    libros,
    totalLibros,
    categorias,
    autores,
    cargandoLibros,
    cargandoMeta,
    errorLibros,
    textoBusqueda,
    tipoBusqueda,
    categoriaId,
    orden,
    skip,
    limit,
    hayFiltrosActivos,
    paginaActual,
    totalPaginas,
    cargarMetadatos,
    buscarLibros,
    reiniciarFiltros,
    cambiarPagina
  }
})
