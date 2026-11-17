<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import BuscadorFiltros from '@/components/BuscadorFiltros.vue'
import EstadoCarga from '@/components/EstadoCarga.vue'
import EstadoVacio from '@/components/EstadoVacio.vue'
import LibroCard from '@/components/LibroCard.vue'
import { useCatalogoStore } from '@/stores/catalogo'

const route = useRoute()
const store = useCatalogoStore()

function aplicarParametrosRuta() {
  if (route.query.categoria) {
    store.categoriaId = Number(route.query.categoria)
  }
  if (route.query.autor) {
    store.tipoBusqueda = 'autor'
    store.textoBusqueda = String(route.query.autor)
  }
}

function filtrarPorCategoria(id) {
  store.categoriaId = store.categoriaId === id ? null : id
  store.skip = 0
  store.buscarLibros()
}

function aplicarOrden() {
  store.skip = 0
  store.buscarLibros()
}

onMounted(async () => {
  aplicarParametrosRuta()
  await store.cargarMetadatos()
  await store.buscarLibros()
})

watch(
  () => route.query,
  () => {
    aplicarParametrosRuta()
    store.skip = 0
    store.buscarLibros()
  }
)
</script>

<template>
  <main class="contenedor catalogo-pagina">
    <section class="hero-pastel">
      <div class="hero-texto">
        <p class="hero-saludo">Bienvenido a tu</p>
        <h1 class="titulo-serif hero-titulo">Biblioteca Digital</h1>
        <p class="hero-subtitulo">
          Encuentra tus libros favoritos y sumérgete en nuevas historias.
        </p>
        <a class="btn btn-rosa hero-accion" href="#catalogo-libros">
          Explorar catálogo
          <span aria-hidden="true">→</span>
        </a>
      </div>
      <div class="hero-ilustracion" aria-hidden="true">
        <svg viewBox="0 0 430 190" fill="none">
          <path d="M66 157c-15-28-3-54 21-70M73 122c-15 0-22-9-24-20 15 0 23 7 24 20Zm8-16c-2-15 5-24 17-28 2 15-4 24-17 28Z" />
          <path d="M357 159c14-30 3-56-20-74M351 124c15 0 23-8 26-19-15-1-24 6-26 19Zm-8-16c2-15-4-24-16-29-3 15 3 24 16 29Z" />
          <path d="m110 52 4 11 11 4-11 4-4 11-4-11-11-4 11-4 4-11Zm228-27 3 8 8 3-8 3-3 8-3-8-8-3 8-3 3-8Z" />
          <ellipse cx="225" cy="164" rx="157" ry="14" fill="#d9b6bd" opacity=".24" />
          <g class="ilustracion-libro libro-lila">
            <path d="m112 115 189-20 47 19-190 24-46-23Z" fill="#92729B" />
            <path d="m112 115 189-20 1 36-189 20-1-36Z" fill="#E9D8EB" />
            <path d="m301 95 47 19v36l-47-19V95Z" fill="#765C80" />
            <path d="m127 123 161-17m-160 24 160-17" stroke="#C9B6CC" stroke-width="2" />
          </g>
          <g class="ilustracion-libro libro-salvia">
            <path d="m89 82 178-20 70 21-179 23-69-24Z" fill="#71866D" />
            <path d="m89 82 178-20v35L89 119V82Z" fill="#F5F0E7" />
            <path d="m267 62 70 21v35l-70-21V62Z" fill="#92A18A" />
            <path d="m106 90 145-16m-145 24 145-16m16-25v34" stroke="#DED4CA" stroke-width="2" />
          </g>
          <g class="ilustracion-libro libro-rosa">
            <path d="m130 50 131-17 58 16-132 18-57-17Z" fill="#A87991" />
            <path d="m130 50 131-17v30l-131 18V50Z" fill="#FFF9F5" />
            <path d="m261 33 58 16v30l-58-16V33Z" fill="#C99AAF" />
            <path d="m145 57 103-13m-103 20 103-13m15-18v30" stroke="#E4D6D5" stroke-width="2" />
          </g>
          <path d="M376 121h34a4 4 0 0 1 4 4v21a18 18 0 0 1-18 18h-6a18 18 0 0 1-18-18v-21a4 4 0 0 1 4-4Z" fill="#F6E8E3" stroke="#C99AAF" stroke-width="2" />
          <path d="M414 129h5a9 9 0 0 1 0 18h-5m-20-15c-5-7-15 0 0 11 15-11 5-18 0-11Z" stroke="#B77D95" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
    </section>

    <div class="catalogo-layout">
      <section id="catalogo-libros" class="catalogo-principal">
        <BuscadorFiltros />

        <div class="catalogo-cabecera">
          <div class="catalogo-titulo-fila">
            <span class="catalogo-icono" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
                <path d="M3 5.5A2.5 2.5 0 0 1 5.5 3H11v17H5.5A2.5 2.5 0 0 0 3 22V5.5Zm18 0A2.5 2.5 0 0 0 18.5 3H13v17h5.5A2.5 2.5 0 0 1 21 22V5.5Z" />
              </svg>
            </span>
            <h2 class="titulo-serif">Catálogo de Libros</h2>
          </div>
          <div class="catalogo-meta">
            <select
              v-model="store.orden"
              class="orden-catalogo"
              aria-label="Ordenar libros"
              @change="aplicarOrden"
            >
              <option value="titulo">Título A-Z</option>
              <option value="-anio">Más recientes</option>
              <option value="anio">Más antiguos</option>
            </select>
            <span class="catalogo-cantidad">
              {{ store.totalLibros }} {{ store.totalLibros === 1 ? 'libro' : 'libros' }}
            </span>
          </div>
        </div>

        <div v-if="store.errorLibros" class="alerta-error tarjeta-base" role="alert">
          <div>
            <strong>No pudimos cargar el catálogo</strong>
            <p>{{ store.errorLibros }}</p>
          </div>
          <button type="button" class="btn btn-rosa" @click="store.buscarLibros()">
            Reintentar
          </button>
        </div>

        <EstadoCarga v-else-if="store.cargandoLibros" />

        <EstadoVacio
          v-else-if="store.libros.length === 0"
          :titulo="
            store.hayFiltrosActivos
              ? 'No se encontraron libros'
              : 'Aún no hay libros registrados'
          "
          :descripcion="
            store.hayFiltrosActivos
              ? 'Intenta con otra búsqueda o explora todas las categorías.'
              : 'Cuando se agreguen libros a la biblioteca, aparecerán aquí.'
          "
          :mostrar-accion="store.hayFiltrosActivos"
          texto-accion="Volver al catálogo"
          @accion="store.reiniciarFiltros()"
        />

        <section v-else aria-label="Listado de libros">
          <div class="libros-grid">
            <LibroCard v-for="libro in store.libros" :key="libro.id" :libro="libro" />
          </div>

          <nav
            v-if="store.totalPaginas > 1"
            class="paginacion"
            aria-label="Paginación del catálogo"
          >
            <button
              type="button"
              class="btn btn-suave"
              :disabled="store.paginaActual <= 1"
              @click="store.cambiarPagina(store.paginaActual - 1)"
            >
              Anterior
            </button>
            <span class="paginacion-info">
              Página {{ store.paginaActual }} de {{ store.totalPaginas }}
            </span>
            <button
              type="button"
              class="btn btn-suave"
              :disabled="store.paginaActual >= store.totalPaginas"
              @click="store.cambiarPagina(store.paginaActual + 1)"
            >
              Siguiente
            </button>
          </nav>
        </section>
      </section>

      <aside class="catalogo-lateral" aria-label="Explorar la biblioteca">
        <section v-if="store.categorias.length" class="panel-categorias tarjeta-base">
          <h2 class="titulo-serif panel-titulo">Categorías</h2>
          <ul class="lista-categorias">
            <li v-for="(categoria, indice) in store.categorias" :key="categoria.id">
              <button
                type="button"
                class="categoria-enlace"
                :class="{ seleccionada: store.categoriaId === categoria.id }"
                :aria-pressed="store.categoriaId === categoria.id"
                @click="filtrarPorCategoria(categoria.id)"
              >
                <span class="categoria-punto" :class="`punto-${indice % 5}`" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" />
                  </svg>
                </span>
                <span>{{ categoria.nombre }}</span>
              </button>
            </li>
          </ul>
          <RouterLink to="/categorias" class="ver-categorias">
            Ver todas las categorías <span aria-hidden="true">→</span>
          </RouterLink>
        </section>

        <section class="panel-lectura">
          <p class="panel-lectura-titulo">Leer es soñar despierto</p>
          <span class="panel-lectura-corazon" aria-hidden="true">♡</span>
          <svg class="panel-lectura-ilustracion" viewBox="0 0 180 100" fill="none" aria-hidden="true">
            <path d="M20 88c-9-18-3-35 12-47M28 66c-10 0-15-6-16-14 10 0 15 5 16 14Zm5-10c-1-10 4-16 12-19 2 10-2 16-12 19Z" />
            <path d="M148 87c10-20 5-35-9-47m8 26c10 0 15-5 17-13-10 0-15 5-17 13Z" />
            <path d="m47 70 57-7 32 12-58 9-31-14Z" fill="#9A7893" />
            <path d="m47 70 57-7v16l-57 8V70Z" fill="#F8F1E9" />
            <path d="m104 63 32 12v16l-32-12V63Z" fill="#C89DB3" />
            <path d="m57 48 43-6 28 9-44 7-27-10Z" fill="#74886F" />
            <path d="m57 48 43-6v15l-43 7V48Z" fill="#FFF9F4" />
            <path d="m100 42 28 9v15l-28-9V42Z" fill="#AAB79F" />
            <path d="m67 52 24-3m-24 8 24-3m14-11v15" />
          </svg>
        </section>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.catalogo-pagina {
  max-width: 1380px;
  padding-top: 1rem;
  padding-bottom: 2rem;
}

.hero-pastel {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  position: relative;
  min-height: 184px;
  gap: 1rem;
  padding: 1.35rem clamp(1.35rem, 5vw, 4.5rem);
  margin-bottom: 1rem;
  overflow: hidden;
  border-radius: var(--radio-lg);
  background:
    radial-gradient(ellipse at 68% 115%, rgba(255, 255, 255, 0.55) 0 17%, transparent 17.5%),
    linear-gradient(105deg, #f9dfe4 0%, #f8dce2 54%, #f5e1e2 100%);
  border: 1px solid #f0d7d9;
}

.hero-texto {
  position: relative;
  z-index: 1;
  max-width: 58%;
}

.hero-saludo {
  font-family: var(--fuente-serif);
  font-size: clamp(1.2rem, 2.4vw, 1.8rem);
  font-style: italic;
  line-height: 1.15;
  color: #4b293f;
}

.hero-titulo {
  font-size: clamp(2rem, 4.4vw, 3.15rem);
  line-height: 1.08;
  margin: 0.08rem 0 0.35rem;
  color: #321b2d;
}

.hero-accion {
  margin-top: 0.85rem;
  padding-inline: 1.2rem;
  box-shadow: 0 5px 12px rgba(149, 85, 115, 0.16);
}

.hero-subtitulo {
  color: #59434f;
  font-size: 0.94rem;
}

.hero-ilustracion {
  position: absolute;
  right: 2.2%;
  bottom: -3px;
  width: min(43%, 430px);
  height: 100%;
  display: flex;
  align-items: end;
}

.hero-ilustracion svg {
  width: 100%;
  max-height: 100%;
  overflow: visible;
}

.hero-ilustracion svg > path {
  stroke: #8e7187;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.ilustracion-libro {
  filter: drop-shadow(0 5px 4px rgba(80, 48, 69, 0.1));
}

.catalogo-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 218px;
  align-items: start;
  gap: 1rem;
}

.catalogo-principal {
  min-width: 0;
}

.catalogo-cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin: 0.1rem 0 0.6rem;
}

.catalogo-titulo-fila {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.catalogo-icono {
  color: #43213f;
  display: flex;
}

.catalogo-icono svg {
  width: 27px;
  height: 27px;
}

.catalogo-cabecera h2 {
  color: #3a2034;
  font-size: 1.35rem;
}

.catalogo-cantidad {
  color: var(--color-texto-tenue);
  font-size: 0.82rem;
  white-space: nowrap;
}

.catalogo-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.orden-catalogo {
  max-width: 128px;
  padding: 0.4rem 1.5rem 0.4rem 0.55rem;
  border: 1px solid #efe2df;
  border-radius: 9px;
  background: rgba(255, 253, 250, 0.8);
  color: var(--color-texto-suave);
  font-size: 0.72rem;
}

.orden-catalogo:focus-visible {
  outline: 2px solid var(--color-rosa-oscuro);
  outline-offset: 2px;
}

.catalogo-principal :deep(.estado-vacio) {
  display: grid;
  grid-template-columns: minmax(100px, 0.45fr) minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.75rem;
  max-width: none;
  min-height: 104px;
  margin: 0.35rem 0;
  padding: 0.8rem 1rem;
  text-align: left;
}

.catalogo-principal :deep(.vacio-icono) {
  width: 86px;
  height: 70px;
  margin: 0 auto;
  border-radius: 0;
  background: transparent;
}

.catalogo-principal :deep(.vacio-icono svg) {
  width: 64px;
  height: 64px;
  color: #b9859e;
}

.catalogo-principal :deep(.vacio-titulo) {
  margin: 0 0 0.2rem;
  font-size: 1.08rem;
}

.catalogo-principal :deep(.vacio-desc) {
  margin: 0;
  font-size: 0.82rem;
}

.catalogo-principal :deep(.estado-vacio .btn) {
  white-space: nowrap;
}

.libros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(195px, 1fr));
  gap: 0.65rem;
}

.catalogo-lateral {
  display: grid;
  gap: 0.8rem;
}

.panel-categorias {
  padding: 0.85rem 0.9rem;
}

.panel-titulo {
  padding-bottom: 0.55rem;
  margin-bottom: 0.35rem;
  border-bottom: 1px solid var(--color-borde);
  color: #3a2034;
  font-size: 1.2rem;
}

.lista-categorias {
  list-style: none;
  display: grid;
  gap: 0.15rem;
}

.categoria-enlace {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.45rem 0.35rem;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: var(--color-texto);
  font-size: 0.82rem;
  text-align: left;
  text-transform: capitalize;
  cursor: pointer;
  transition: background-color var(--transicion), color var(--transicion);
}

.categoria-enlace:hover,
.categoria-enlace.seleccionada {
  background: #f7eaf0;
  color: #7c4965;
}

.categoria-punto {
  width: 25px;
  height: 25px;
  flex: 0 0 25px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #8c6384;
  background: #f5e5f0;
}

.categoria-punto svg {
  width: 15px;
  height: 15px;
}

.punto-1 {
  color: #58785b;
  background: #e8f0e5;
}

.punto-2 {
  color: #b27555;
  background: #f9e9dc;
}

.punto-3 {
  color: #71608c;
  background: #eee8f5;
}

.punto-4 {
  color: #b16a82;
  background: #f8e6ec;
}

.ver-categorias {
  display: flex;
  justify-content: space-between;
  gap: 0.4rem;
  padding: 0.6rem 0.25rem 0.1rem;
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-borde);
  color: var(--color-rosa-oscuro);
  font-size: 0.76rem;
  font-weight: 600;
}

.panel-lectura {
  position: relative;
  min-height: 120px;
  overflow: hidden;
  padding: 0.8rem 0.9rem;
  border: 1px solid #dfe4d2;
  border-radius: var(--radio-md);
  background: linear-gradient(140deg, #e8eddf, #f0efdf);
}

.panel-lectura-titulo {
  max-width: 145px;
  color: #394234;
  font-family: var(--fuente-serif);
  font-size: 1.05rem;
  font-style: italic;
  font-weight: 600;
  line-height: 1.2;
}

.panel-lectura-corazon {
  display: inline-block;
  margin-top: 0.15rem;
  color: #bd8291;
}

.panel-lectura-ilustracion {
  position: absolute;
  right: 0;
  bottom: -2px;
  width: 100%;
  height: 66px;
}

.panel-lectura-ilustracion path {
  stroke: #899578;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.panel-lectura-ilustracion path:nth-last-child(-n + 4) {
  stroke: #d3c4b8;
}

.alerta-error {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background-color: var(--color-error-bg);
  color: var(--color-error-txt);
  border-color: #f1c5cf;
}

.alerta-error p {
  font-size: 0.9rem;
  margin-top: 0.2rem;
}

@media (max-width: 1000px) {
  .catalogo-layout {
    grid-template-columns: minmax(0, 1fr) 200px;
    gap: 0.75rem;
  }

  .libros-grid {
    grid-template-columns: repeat(auto-fill, minmax(185px, 1fr));
  }
}

@media (max-width: 760px) {
  .hero-pastel {
    min-height: 170px;
    padding: 1.25rem;
  }

  .hero-texto {
    max-width: 70%;
  }

  .hero-ilustracion {
    right: -5%;
    width: 42%;
    opacity: 0.8;
  }

  .catalogo-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .catalogo-lateral {
    grid-template-columns: minmax(0, 1fr) minmax(180px, 0.7fr);
    align-items: start;
  }

  .catalogo-principal :deep(.estado-vacio) {
    grid-template-columns: 72px minmax(0, 1fr);
  }

  .catalogo-principal :deep(.estado-vacio .btn) {
    grid-column: 2;
    justify-self: start;
  }
}

@media (max-width: 520px) {
  .catalogo-pagina {
    padding-inline: 0.85rem;
  }

  .hero-pastel {
    min-height: 180px;
    padding: 1.1rem;
  }

  .hero-texto {
    max-width: 100%;
  }

  .hero-saludo {
    font-size: 1.15rem;
  }

  .hero-titulo {
    max-width: 74%;
    font-size: 2rem;
  }

  .hero-subtitulo {
    max-width: 75%;
    font-size: 0.82rem;
  }

  .hero-ilustracion {
    right: -18%;
    width: 60%;
    opacity: 0.42;
  }

  .catalogo-lateral {
    grid-template-columns: minmax(0, 1fr);
  }

  .catalogo-principal :deep(.estado-vacio) {
    grid-template-columns: minmax(0, 1fr);
    text-align: center;
  }

  .catalogo-principal :deep(.estado-vacio .btn) {
    grid-column: auto;
    justify-self: center;
  }

  .libros-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .catalogo-cabecera h2 {
    font-size: 1.18rem;
  }

  .catalogo-meta {
    gap: 0.25rem;
  }

  .orden-catalogo {
    max-width: 105px;
    font-size: 0.66rem;
  }
}
</style>
