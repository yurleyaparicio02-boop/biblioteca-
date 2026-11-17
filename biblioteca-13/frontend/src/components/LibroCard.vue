<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  libro: {
    type: Object,
    required: true
  }
})

const errorImagen = ref(false)

watch(
  () => props.libro?.imagen_url,
  () => {
    errorImagen.value = false
  }
)

const tienePortadaValida = computed(
  () => Boolean(props.libro?.imagen_url) && !errorImagen.value
)

const disponible = computed(() => (props.libro?.disponibles ?? 0) > 0)

const categoriasTexto = computed(() => {
  const lista = props.libro?.categorias || []
  return lista.length > 0 ? lista : [{ id: 0, nombre: 'general' }]
})
</script>

<template>
  <article class="libro-card tarjeta-base">
    <RouterLink :to="`/libros/${libro.id}`" class="portada-enlace">
      <div class="portada-marco">
        <img
          v-if="tienePortadaValida"
          :src="libro.imagen_url"
          :alt="`Portada de ${libro.titulo}`"
          class="portada-img"
          loading="lazy"
          @error="errorImagen = true"
        />
        <div v-else class="portada-placeholder" aria-label="Sin portada disponible">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
          <span>Sin portada</span>
        </div>

        <span
          class="estado-disponible badge"
          :class="disponible ? 'badge-salvia' : 'badge-rosa'"
        >
          {{ disponible ? `${libro.disponibles} disp.` : 'Agotado' }}
        </span>
      </div>
    </RouterLink>

    <div class="card-cuerpo">
      <div class="categorias-fila">
        <span
          v-for="cat in categoriasTexto.slice(0, 2)"
          :key="cat.id"
          class="badge badge-lila categoria-chip"
        >
          {{ cat.nombre }}
        </span>
      </div>

      <h3 class="libro-titulo" :title="libro.titulo">
        {{ libro.titulo }}
      </h3>

      <p class="libro-autor">
        {{ libro.autor?.nombre || 'Autor desconocido' }}
      </p>

      <div class="card-pie">
        <RouterLink :to="`/libros/${libro.id}`" class="btn btn-primario btn-detalle">
          Ver detalles
        </RouterLink>
      </div>
    </div>
  </article>
</template>

<style scoped>
.libro-card {
  display: grid;
  grid-template-columns: minmax(72px, 0.72fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 0.7rem;
  min-height: 172px;
  overflow: hidden;
  padding: 0.62rem;
  transition: transform var(--transicion), box-shadow var(--transicion),
    border-color var(--transicion);
}

.libro-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--sombra-hover);
  border-color: #d9c8df;
}

.portada-enlace {
  display: block;
  min-width: 0;
}

.portada-marco {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 145px;
  border-radius: var(--radio-sm);
  overflow: hidden;
  background-color: var(--color-beige);
}

.portada-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s ease;
}

.libro-card:hover .portada-img {
  transform: scale(1.03);
}

.portada-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  background: linear-gradient(145deg, var(--color-beige), var(--color-rosa));
  color: var(--color-texto-suave);
  font-size: 0.82rem;
}

.portada-placeholder svg {
  width: 34px;
  height: 34px;
  opacity: 0.75;
}

.estado-disponible {
  position: absolute;
  top: 0.35rem;
  right: 0.3rem;
  backdrop-filter: blur(4px);
  padding: 0.15rem 0.4rem;
  font-size: 0.63rem;
}

.card-cuerpo {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 0.15rem 0.05rem 0.05rem 0;
}

.categorias-fila {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  max-height: 25px;
  overflow: hidden;
  margin-bottom: 0.3rem;
}

.categoria-chip {
  text-transform: capitalize;
  padding: 0.13rem 0.48rem;
  font-size: 0.65rem;
}

.libro-titulo {
  font-family: var(--fuente-serif);
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.23;
  color: var(--color-texto);
  margin-bottom: 0.32rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.libro-autor {
  font-size: 0.73rem;
  color: var(--color-texto-suave);
  margin-bottom: 0.45rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-pie {
  margin-top: auto;
}

.btn-detalle {
  width: 100%;
  min-height: 29px;
  padding: 0.3rem 0.4rem;
  font-size: 0.72rem;
}

@media (max-width: 520px) {
  .libro-card {
    grid-template-columns: minmax(92px, 0.34fr) minmax(0, 1fr);
    min-height: 166px;
  }
}
</style>
