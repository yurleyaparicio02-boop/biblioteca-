<script setup>
defineProps({
  columnas: {
    type: Array,
    required: true
  },
  filas: {
    type: Array,
    default: () => []
  },
  cargando: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  total: {
    type: Number,
    default: 0
  },
  skip: {
    type: Number,
    default: 0
  },
  limite: {
    type: Number,
    default: 20
  },
  mensajeVacio: {
    type: String,
    default: 'No hay registros para mostrar.'
  }
})

const emit = defineEmits(['anterior', 'siguiente', 'reintentar'])
</script>

<template>
  <section class="gestion-tabla tarjeta-base">
    <div v-if="error" class="gestion-tabla-error" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn-suave" @click="emit('reintentar')">
        Reintentar
      </button>
    </div>

    <div v-else-if="cargando" class="gestion-tabla-estado" role="status" aria-busy="true">
      <span class="spinner" aria-hidden="true"></span>
      Cargando información...
    </div>

    <div v-else-if="filas.length === 0" class="gestion-tabla-estado">
      {{ mensajeVacio }}
    </div>

    <template v-else>
      <div class="tabla-scroll">
        <table class="tabla-gestion">
          <thead>
            <tr>
              <th v-for="columna in columnas" :key="columna.clave" scope="col">
                {{ columna.titulo }}
              </th>
              <th v-if="$slots.acciones" scope="col">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="fila in filas" :key="fila.id">
              <td v-for="columna in columnas" :key="columna.clave">
                {{ fila[columna.clave] ?? '—' }}
              </td>
              <td v-if="$slots.acciones" class="tabla-acciones">
                <slot name="acciones" :fila="fila" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav
        v-if="total > limite"
        class="gestion-paginacion"
        aria-label="Paginación"
      >
        <span>{{ skip + 1 }}–{{ Math.min(skip + filas.length, total) }} de {{ total }}</span>
        <div>
          <button
            type="button"
            class="btn btn-suave"
            :disabled="skip === 0 || cargando"
            @click="emit('anterior')"
          >
            Anterior
          </button>
          <button
            type="button"
            class="btn btn-suave"
            :disabled="skip + limite >= total || cargando"
            @click="emit('siguiente')"
          >
            Siguiente
          </button>
        </div>
      </nav>
    </template>
  </section>
</template>

<style scoped>
.gestion-tabla {
  overflow: hidden;
}

.tabla-scroll {
  overflow-x: auto;
}

.tabla-gestion {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.84rem;
}

.tabla-gestion th {
  padding: 0.8rem 0.9rem;
  background: #faf4f4;
  color: #806879;
  font-size: 0.73rem;
  font-weight: 600;
  letter-spacing: 0.035em;
  text-transform: uppercase;
  white-space: nowrap;
}

.tabla-gestion td {
  padding: 0.75rem 0.9rem;
  border-top: 1px solid #f1e9e5;
  color: var(--color-texto);
  vertical-align: middle;
}

.tabla-gestion tbody tr:hover {
  background: #fffaf8;
}

.tabla-acciones {
  min-width: 150px;
  white-space: nowrap;
}

.gestion-tabla-estado,
.gestion-tabla-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  min-height: 120px;
  padding: 1rem;
  color: var(--color-texto-suave);
  font-size: 0.9rem;
  text-align: center;
}

.gestion-tabla-error {
  flex-wrap: wrap;
  color: var(--color-error-txt);
  background: var(--color-error-bg);
}

.gestion-paginacion {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 0.9rem;
  border-top: 1px solid #f1e9e5;
  color: var(--color-texto-suave);
  font-size: 0.78rem;
}

.gestion-paginacion > div {
  display: flex;
  gap: 0.4rem;
}

.gestion-paginacion .btn {
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
}
</style>
