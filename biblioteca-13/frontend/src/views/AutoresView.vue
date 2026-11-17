<script setup>
import { computed, onMounted, ref } from 'vue'
import { autoresApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import EstadoCarga from '@/components/EstadoCarga.vue'
import EstadoVacio from '@/components/EstadoVacio.vue'

const autores = ref([])
const cargando = ref(true)
const error = ref('')
const filtroTexto = ref('')

const autoresFiltrados = computed(() => {
  const q = filtroTexto.value.trim().toLowerCase()
  if (!q) return autores.value
  return autores.value.filter(
    (a) =>
      a.nombre.toLowerCase().includes(q) ||
      (a.nacionalidad && a.nacionalidad.toLowerCase().includes(q))
  )
})

onMounted(async () => {
  try {
    const { data } = await autoresApi.listar({ skip: 0, limit: 100 })
    autores.value = data.items || []
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudieron cargar los autores.')
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <main class="contenedor seccion-pagina">
    <header class="cabecera-seccion">
      <div>
        <span class="badge badge-salvia">Directorio</span>
        <h1 class="titulo-serif">Autores de la biblioteca</h1>
        <p>Consulta los escritores registrados y explora sus obras en el catálogo.</p>
      </div>
      <input
        v-model="filtroTexto"
        type="search"
        class="filtro-autor"
        placeholder="Filtrar por nombre o nacionalidad..."
        aria-label="Filtrar autores"
      />
    </header>

    <EstadoCarga v-if="cargando" mensaje="Cargando autores..." :tarjetas="4" />

    <div v-else-if="error" class="tarjeta-base mensaje-error">{{ error }}</div>

    <EstadoVacio
      v-else-if="autoresFiltrados.length === 0"
      titulo="No se encontraron autores"
      descripcion="Prueba con otro nombre o nacionalidad."
      :mostrar-accion="Boolean(filtroTexto)"
      texto-accion="Limpiar filtro"
      @accion="filtroTexto = ''"
    />

    <div v-else class="autores-grid">
      <RouterLink
        v-for="autor in autoresFiltrados"
        :key="autor.id"
        :to="{ path: '/', query: { autor: autor.nombre } }"
        class="autor-card tarjeta-base"
      >
        <div class="autor-avatar" aria-hidden="true">
          {{ autor.nombre.charAt(0).toUpperCase() }}
        </div>
        <div class="autor-info">
          <h2 class="titulo-serif autor-nombre">{{ autor.nombre }}</h2>
          <p class="autor-meta">
            {{ autor.nacionalidad || 'Nacionalidad no especificada' }}
            <span v-if="autor.anio_nacimiento">· {{ autor.anio_nacimiento }}</span>
          </p>
        </div>
      </RouterLink>
    </div>
  </main>
</template>

<style scoped>
.seccion-pagina {
  padding-top: 2rem;
  padding-bottom: 3.5rem;
}

.cabecera-seccion {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.cabecera-seccion h1 {
  font-size: 1.9rem;
  margin: 0.45rem 0 0.35rem;
}

.cabecera-seccion p {
  color: var(--color-texto-suave);
}

.filtro-autor {
  padding: 0.65rem 1rem;
  border-radius: var(--radio-pill);
  border: 1px solid var(--color-borde);
  background-color: var(--color-blanco-calido);
  min-width: 260px;
  outline: none;
}

.filtro-autor:focus {
  border-color: var(--color-salvia-oscuro);
}

.autores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.1rem;
}

.autor-card {
  display: flex;
  align-items: center;
  gap: 0.95rem;
  padding: 1.15rem;
  transition: transform var(--transicion), box-shadow var(--transicion);
}

.autor-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--sombra-hover);
}

.autor-avatar {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-salvia), var(--color-lila));
  color: var(--color-texto);
  font-family: var(--fuente-serif);
  font-size: 1.2rem;
  font-weight: 700;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.autor-nombre {
  font-size: 1.08rem;
  margin-bottom: 0.15rem;
}

.autor-meta {
  font-size: 0.85rem;
  color: var(--color-texto-suave);
}

.mensaje-error {
  padding: 1.25rem;
  background-color: var(--color-error-bg);
  color: var(--color-error-txt);
}
</style>
