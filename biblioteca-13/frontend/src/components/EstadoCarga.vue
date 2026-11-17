<script setup>
defineProps({
  mensaje: {
    type: String,
    default: 'Cargando libros del catálogo...'
  },
  tarjetas: {
    type: Number,
    default: 8
  }
})
</script>

<template>
  <div class="estado-carga" role="status" aria-busy="true">
    <div class="carga-cabecera">
      <span class="spinner" aria-hidden="true"></span>
      <p>{{ mensaje }}</p>
    </div>

    <div class="esqueleto-grid">
      <div v-for="n in tarjetas" :key="n" class="esqueleto-tarjeta">
        <div class="esqueleto-portada"></div>
        <div class="esqueleto-linea largo"></div>
        <div class="esqueleto-linea medio"></div>
        <div class="esqueleto-linea corto"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.carga-cabecera {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin-bottom: 1.5rem;
  color: var(--color-texto-suave);
  font-size: 0.95rem;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2.5px solid var(--color-lila);
  border-top-color: var(--color-lila-oscuro);
  border-radius: 50%;
  animation: girar 0.8s linear infinite;
}

@keyframes girar {
  to {
    transform: rotate(360deg);
  }
}

.esqueleto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 1.25rem;
}

.esqueleto-tarjeta {
  background-color: var(--color-blanco-calido);
  border: 1px solid var(--color-borde);
  border-radius: var(--radio-md);
  padding: 0.85rem;
}

.esqueleto-portada {
  height: 210px;
  border-radius: var(--radio-sm);
  background: linear-gradient(90deg, var(--color-beige) 25%, #f7f0e8 50%, var(--color-beige) 75%);
  background-size: 200% 100%;
  animation: brillo 1.4s infinite;
  margin-bottom: 0.85rem;
}

.esqueleto-linea {
  height: 12px;
  border-radius: 6px;
  background-color: var(--color-beige);
  margin-bottom: 0.55rem;
}

.esqueleto-linea.largo {
  width: 85%;
}

.esqueleto-linea.medio {
  width: 60%;
}

.esqueleto-linea.corto {
  width: 45%;
  margin-bottom: 0;
}

@keyframes brillo {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
