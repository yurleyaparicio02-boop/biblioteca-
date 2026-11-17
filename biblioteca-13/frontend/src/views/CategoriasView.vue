<script setup>
import { onMounted, ref } from 'vue'
import { categoriasApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import EstadoCarga from '@/components/EstadoCarga.vue'
import EstadoVacio from '@/components/EstadoVacio.vue'

const categorias = ref([])
const cargando = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await categoriasApi.listar({ skip: 0, limit: 100 })
    categorias.value = data.items || []
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudieron cargar las categorías.')
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <main class="contenedor seccion-pagina">
    <header class="cabecera-seccion">
      <span class="badge badge-lila">Géneros literarios</span>
      <h1 class="titulo-serif">Categorías disponibles</h1>
      <p>Selecciona una categoría para explorar los libros relacionados en el catálogo.</p>
    </header>

    <EstadoCarga v-if="cargando" mensaje="Cargando categorías..." :tarjetas="4" />

    <div v-else-if="error" class="tarjeta-base mensaje-error">{{ error }}</div>

    <EstadoVacio
      v-else-if="categorias.length === 0"
      titulo="No hay categorías registradas"
      descripcion="Aún no se han creado categorías literarias en la biblioteca."
    />

    <div v-else class="categorias-grid">
      <RouterLink
        v-for="cat in categorias"
        :key="cat.id"
        :to="{ path: '/', query: { categoria: cat.id } }"
        class="categoria-card tarjeta-base"
      >
        <h2 class="titulo-serif categoria-nombre">{{ cat.nombre }}</h2>
        <p class="categoria-desc">
          {{ cat.descripcion || 'Explorar títulos disponibles en esta categoría.' }}
        </p>
        <span class="categoria-ir">Ver libros →</span>
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
  margin-bottom: 1.75rem;
}

.cabecera-seccion h1 {
  font-size: 1.9rem;
  margin: 0.45rem 0 0.35rem;
}

.cabecera-seccion p {
  color: var(--color-texto-suave);
}

.categorias-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.15rem;
}

.categoria-card {
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: transform var(--transicion), box-shadow var(--transicion);
}

.categoria-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--sombra-hover);
  border-color: #d5c5e8;
}

.categoria-nombre {
  font-size: 1.2rem;
  text-transform: capitalize;
}

.categoria-desc {
  font-size: 0.88rem;
  color: var(--color-texto-suave);
  flex: 1;
}

.categoria-ir {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-lila-oscuro);
  margin-top: 0.35rem;
}

.mensaje-error {
  padding: 1.25rem;
  background-color: var(--color-error-bg);
  color: var(--color-error-txt);
}
</style>
