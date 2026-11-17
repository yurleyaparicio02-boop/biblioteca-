<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { librosApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import EstadoCarga from '@/components/EstadoCarga.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()

const libro = ref(null)
const cargando = ref(true)
const error = ref('')
const errorImagen = ref(false)
const subiendoPortada = ref(false)

const tienePortada = computed(
  () => Boolean(libro.value?.imagen_url) && !errorImagen.value
)

async function cargarLibro() {
  cargando.value = true
  error.value = ''
  errorImagen.value = false
  try {
    const { data } = await librosApi.obtenerPorId(route.params.id)
    libro.value = data
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudo cargar la información del libro.')
  } finally {
    cargando.value = false
  }
}

async function manejarSubidaPortada(evento) {
  const archivo = evento.target.files?.[0]
  if (!archivo || !libro.value) return

  subiendoPortada.value = true
  try {
    const { data } = await librosApi.subirPortada(libro.value.id, archivo)
    libro.value.imagen_url = data.imagen_url
    errorImagen.value = false
    notificaciones.exito('Portada actualizada en Cloudinary correctamente.')
  } catch (err) {
    notificaciones.error(
      extraerMensajeError(err, 'No se pudo subir la nueva portada.')
    )
  } finally {
    subiendoPortada.value = false
    evento.target.value = ''
  }
}

onMounted(cargarLibro)
</script>

<template>
  <main class="contenedor detalle-pagina">
    <button type="button" class="btn btn-suave btn-volver" @click="router.push('/')">
      ← Volver al catálogo
    </button>

    <EstadoCarga
      v-if="cargando"
      mensaje="Cargando detalles del libro..."
      :tarjetas="1"
    />

    <div v-else-if="error" class="tarjeta-base caja-error" role="alert">
      <h2 class="titulo-serif">No pudimos mostrar este libro</h2>
      <p>{{ error }}</p>
      <RouterLink to="/" class="btn btn-primario">Ir al catálogo</RouterLink>
    </div>

    <article v-else-if="libro" class="detalle-tarjeta tarjeta-base">
      <div class="detalle-portada-col">
        <div class="detalle-portada-marco">
          <img
            v-if="tienePortada"
            :src="libro.imagen_url"
            :alt="`Portada de ${libro.titulo}`"
            class="detalle-portada-img"
            @error="errorImagen = true"
          />
          <div v-else class="detalle-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
            <span>Portada no disponible</span>
          </div>
        </div>

        <div v-if="authStore.esStaff" class="subir-portada-box">
          <label class="btn btn-secundario btn-subir">
            {{ subiendoPortada ? 'Subiendo a Cloudinary...' : 'Actualizar portada' }}
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              hidden
              :disabled="subiendoPortada"
              @change="manejarSubidaPortada"
            />
          </label>
        </div>
      </div>

      <div class="detalle-info-col">
        <div class="detalle-badges">
          <span
            class="badge"
            :class="libro.disponibles > 0 ? 'badge-salvia' : 'badge-rosa'"
          >
            {{
              libro.disponibles > 0
                ? `${libro.disponibles} de ${libro.ejemplares} disponibles`
                : 'Sin ejemplares disponibles'
            }}
          </span>
          <span
            v-for="cat in libro.categorias"
            :key="cat.id"
            class="badge badge-lila"
            style="text-transform: capitalize"
          >
            {{ cat.nombre }}
          </span>
        </div>

        <h1 class="titulo-serif detalle-titulo">{{ libro.titulo }}</h1>

        <p class="detalle-autor">
          Por
          <RouterLink
            :to="{ path: '/', query: { autor: libro.autor?.nombre } }"
            class="enlace-autor"
          >
            {{ libro.autor?.nombre }}
          </RouterLink>
        </p>

        <dl class="ficha-tecnica">
          <div class="ficha-item">
            <dt>ISBN</dt>
            <dd>{{ libro.isbn }}</dd>
          </div>
          <div class="ficha-item">
            <dt>Año de publicación</dt>
            <dd>{{ libro.anio_publicacion }}</dd>
          </div>
          <div class="ficha-item">
            <dt>Ejemplares totales</dt>
            <dd>{{ libro.ejemplares }}</dd>
          </div>
          <div class="ficha-item">
            <dt>Disponibles ahora</dt>
            <dd>{{ libro.disponibles }}</dd>
          </div>
        </dl>

        <div class="detalle-acciones">
          <RouterLink to="/" class="btn btn-primario">
            Seguir explorando
          </RouterLink>
          <RouterLink
            v-if="libro.categorias?.length"
            :to="{ path: '/', query: { categoria: libro.categorias[0].id } }"
            class="btn btn-suave"
          >
            Ver más de {{ libro.categorias[0].nombre }}
          </RouterLink>
        </div>
      </div>
    </article>
  </main>
</template>

<style scoped>
.detalle-pagina {
  padding-top: 1.75rem;
  padding-bottom: 3.5rem;
}

.btn-volver {
  margin-bottom: 1.25rem;
}

.detalle-tarjeta {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2.25rem;
  padding: 2rem;
  align-items: start;
}

.detalle-portada-marco {
  width: 100%;
  height: 390px;
  border-radius: var(--radio-md);
  overflow: hidden;
  background-color: var(--color-beige);
  border: 1px solid var(--color-borde);
}

.detalle-portada-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.detalle-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  background: linear-gradient(145deg, var(--color-beige), var(--color-lila));
  color: var(--color-texto-suave);
}

.detalle-placeholder svg {
  width: 44px;
  height: 44px;
}

.subir-portada-box {
  margin-top: 0.85rem;
}

.btn-subir {
  width: 100%;
}

.detalle-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 0.9rem;
}

.detalle-titulo {
  font-size: clamp(1.6rem, 3vw, 2.2rem);
  line-height: 1.2;
  margin-bottom: 0.45rem;
}

.detalle-autor {
  font-size: 1.05rem;
  color: var(--color-texto-suave);
  margin-bottom: 1.5rem;
}

.enlace-autor {
  color: var(--color-lila-oscuro);
  font-weight: 500;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.ficha-tecnica {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.9rem;
  margin-bottom: 1.75rem;
}

.ficha-item {
  background-color: var(--color-crema);
  border: 1px solid var(--color-borde);
  border-radius: var(--radio-sm);
  padding: 0.85rem 1rem;
}

.ficha-item dt {
  font-size: 0.78rem;
  color: var(--color-texto-tenue);
  margin-bottom: 0.2rem;
}

.ficha-item dd {
  font-size: 1rem;
  font-weight: 600;
}

.detalle-acciones {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.caja-error {
  padding: 2.5rem;
  text-align: center;
}

.caja-error p {
  color: var(--color-texto-suave);
  margin: 0.6rem 0 1.25rem;
}

@media (max-width: 768px) {
  .detalle-tarjeta {
    grid-template-columns: 1fr;
    padding: 1.35rem;
  }

  .detalle-portada-marco {
    max-width: 260px;
    height: 350px;
    margin: 0 auto;
  }
}
</style>
