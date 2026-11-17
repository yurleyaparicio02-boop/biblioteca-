<script setup>
defineProps({
  titulo: {
    type: String,
    default: 'No encontramos libros con esos criterios'
  },
  descripcion: {
    type: String,
    default: 'Prueba con otro título, autor o categoría, o limpia los filtros activos.'
  },
  mostrarAccion: {
    type: Boolean,
    default: false
  },
  textoAccion: {
    type: String,
    default: 'Mostrar todos los libros'
  }
})

defineEmits(['accion'])
</script>

<template>
  <div class="estado-vacio tarjeta-base">
    <div class="vacio-icono" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        <path d="M9.5 9.5h5M9.5 13h3.5" />
      </svg>
    </div>
    <h3 class="titulo-serif vacio-titulo">{{ titulo }}</h3>
    <p class="vacio-desc">{{ descripcion }}</p>
    <button
      v-if="mostrarAccion"
      type="button"
      class="btn btn-secundario"
      @click="$emit('accion')"
    >
      {{ textoAccion }}
    </button>
  </div>
</template>

<style scoped>
.estado-vacio {
  text-align: center;
  padding: 3rem 1.5rem;
  max-width: 520px;
  margin: 1.5rem auto;
}

.vacio-icono {
  width: 58px;
  height: 58px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-rosa), var(--color-lila));
  color: #5d4a79;
  display: grid;
  place-items: center;
}

.vacio-icono svg {
  width: 28px;
  height: 28px;
}

.vacio-titulo {
  font-size: 1.3rem;
  margin-bottom: 0.45rem;
}

.vacio-desc {
  color: var(--color-texto-suave);
  font-size: 0.94rem;
  margin-bottom: 1.25rem;
}
</style>
