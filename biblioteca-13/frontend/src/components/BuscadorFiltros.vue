<script setup>
import { onUnmounted, watch } from 'vue'
import { useCatalogoStore } from '@/stores/catalogo'

const store = useCatalogoStore()
let temporizador = null

watch(
  () => store.textoBusqueda,
  () => {
    clearTimeout(temporizador)
    temporizador = setTimeout(() => {
      store.skip = 0
      store.buscarLibros()
    }, 320)
  }
)

function aplicarFiltroInmediato() {
  clearTimeout(temporizador)
  store.skip = 0
  store.buscarLibros()
}

onUnmounted(() => clearTimeout(temporizador))
</script>

<template>
  <section class="buscador-panel" aria-label="Buscador y filtros del catálogo">
    <form class="buscador-fila-principal" role="search" @submit.prevent="aplicarFiltroInmediato">
      <div class="campo-busqueda">
        <span class="icono-lupa" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="7" />
            <path d="M21 21l-4.35-4.35" />
          </svg>
        </span>
        <input
          v-model="store.textoBusqueda"
          type="search"
          class="input-busqueda"
          placeholder="Buscar por título, autor o categoría..."
          aria-label="Buscar libros"
        />
        <select
          v-model="store.tipoBusqueda"
          class="select-busqueda"
          aria-label="Buscar en"
          @change="aplicarFiltroInmediato"
        >
          <option value="todos">Todo</option>
          <option value="titulo">Título</option>
          <option value="autor">Autor</option>
          <option value="categoria">Categoría</option>
        </select>
        <button type="submit" class="btn btn-rosa btn-buscar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-4-4" />
          </svg>
          <span>Buscar</span>
        </button>
      </div>

      <div class="selectores-grupo">
        <select
          v-model="store.categoriaId"
          class="select-control select-categoria"
          aria-label="Filtrar por categoría"
          @change="aplicarFiltroInmediato"
        >
          <option :value="null">Todas las categorías</option>
          <option v-for="cat in store.categorias" :key="cat.id" :value="cat.id">
            {{ cat.nombre }}
          </option>
        </select>

        <button
          v-if="store.hayFiltrosActivos"
          type="button"
          class="btn-limpiar"
          @click="store.reiniciarFiltros()"
        >
          Limpiar
        </button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.buscador-panel {
  padding: 0.45rem 0.55rem;
  margin-bottom: 0.75rem;
  border: 1px solid #f0e2e0;
  border-radius: 15px;
  background: rgba(255, 253, 250, 0.88);
  box-shadow: var(--sombra-suave);
}

.buscador-fila-principal {
  display: flex;
  gap: 0.55rem;
  align-items: center;
}

.campo-busqueda {
  position: relative;
  display: flex;
  flex: 1 1 300px;
  min-width: 190px;
  align-items: center;
}

.icono-lupa {
  position: absolute;
  left: 0.95rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-texto-tenue);
  display: flex;
  pointer-events: none;
}

.icono-lupa svg {
  width: 18px;
  height: 18px;
}

.input-busqueda {
  flex: 1 1 auto;
  width: 0;
  min-width: 0;
  padding: 0.62rem 0.55rem 0.62rem 2.2rem;
  border: 0;
  border-radius: 10px;
  background-color: transparent;
  font-size: 0.86rem;
  outline: none;
  transition: background-color var(--transicion);
}

.input-busqueda:focus {
  background-color: #fff8f8;
}

.selectores-grupo {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding-left: 0.6rem;
  border-left: 1px solid #dfb9c3;
}

.select-control {
  max-width: 165px;
  padding: 0.55rem 1.8rem 0.55rem 0.7rem;
  border: 1px solid transparent;
  border-radius: 9px;
  background-color: #fbf7f4;
  font-size: 0.77rem;
  text-transform: capitalize;
  outline: none;
  cursor: pointer;
  transition: border-color var(--transicion), background-color var(--transicion);
}

.select-control:hover,
.select-control:focus {
  border-color: #e7cbd4;
  background-color: #fffdfb;
}

.select-categoria {
  width: 150px;
  max-width: 150px;
}

.select-busqueda {
  flex: 0 0 auto;
  max-width: 96px;
  padding: 0.5rem 1rem 0.5rem 0.25rem;
  border: 0;
  border-left: 1px solid #eadcdd;
  border-radius: 0;
  background: transparent;
  color: var(--color-texto-suave);
  font-size: 0.73rem;
  outline: none;
  cursor: pointer;
}

.btn-buscar {
  flex: 0 0 auto;
  padding: 0.5rem 0.85rem;
  font-size: 0.78rem;
  box-shadow: 0 3px 8px rgba(149, 85, 115, 0.14);
}

.btn-buscar svg {
  width: 15px;
  height: 15px;
}

.btn-limpiar {
  padding: 0.48rem 0.6rem;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--color-texto-suave);
  font-size: 0.75rem;
  cursor: pointer;
  white-space: nowrap;
}

.btn-limpiar:hover {
  background: #f7eaf0;
  color: #8d5770;
}

@media (max-width: 860px) {
  .buscador-fila-principal {
    flex-wrap: wrap;
  }

  .campo-busqueda {
    flex-basis: 100%;
  }

  .selectores-grupo {
    width: 100%;
    padding: 0.35rem 0.15rem 0.1rem;
    border-left: 0;
    border-top: 1px solid #f0e5e2;
  }
}

@media (max-width: 520px) {
  .selectores-grupo {
    flex-wrap: wrap;
    width: auto;
    flex: 1 1 auto;
  }

  .select-control {
    flex: 1 1 100%;
    max-width: none;
  }

  .select-categoria {
    width: 100%;
  }

  .btn-limpiar {
    margin-left: auto;
  }
}
</style>
