<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const secciones = computed(() => {
  const items = [
    { ruta: '/gestion', nombre: 'Resumen', icono: 'resumen', exacto: true },
    { ruta: '/gestion/libros', nombre: 'Libros', icono: 'libros' },
    { ruta: '/gestion/autores', nombre: 'Autores', icono: 'autores' },
    { ruta: '/gestion/categorias', nombre: 'Categorías', icono: 'categorias' },
    { ruta: '/gestion/socios', nombre: 'Socios', icono: 'socios' },
    { ruta: '/gestion/prestamos', nombre: 'Préstamos', icono: 'prestamos' },
    { ruta: '/gestion/reportes', nombre: 'Reportes', icono: 'reportes' }
  ]

  if (authStore.usuario?.rol === 'admin') {
    items.splice(4, 0, {
      ruta: '/gestion/usuarios',
      nombre: 'Usuarios',
      icono: 'usuarios'
    })
  }

  return items
})
</script>

<template>
  <main class="contenedor gestion-pagina">
    <aside class="gestion-navegacion">
      <div class="gestion-marca">
        <span class="gestion-marca-icono" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
            <path d="M3 5.5A2.5 2.5 0 0 1 5.5 3H11v18H5.5A2.5 2.5 0 0 0 3 23V5.5Zm18 0A2.5 2.5 0 0 0 18.5 3H13v18h5.5a2.5 2.5 0 0 1 2.5 2V5.5Z" />
          </svg>
        </span>
        <div>
          <strong>Administración</strong>
          <span>Biblioteca Digital</span>
        </div>
      </div>

      <nav class="gestion-enlaces" aria-label="Secciones de gestión">
        <RouterLink
          v-for="seccion in secciones"
          :key="seccion.ruta"
          :to="seccion.ruta"
          class="gestion-enlace"
          :active-class="seccion.exacto ? '' : 'gestion-enlace-activo'"
          exact-active-class="gestion-enlace-activo"
        >
          <svg
            v-if="seccion.icono === 'resumen'"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            aria-hidden="true"
          >
            <rect x="3" y="3" width="8" height="8" rx="2" />
            <rect x="14" y="3" width="7" height="5" rx="2" />
            <rect x="14" y="11" width="7" height="10" rx="2" />
            <rect x="3" y="14" width="8" height="7" rx="2" />
          </svg>
          <svg
            v-else-if="seccion.icono === 'autores' || seccion.icono === 'socios' || seccion.icono === 'usuarios'"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            aria-hidden="true"
          >
            <circle cx="9" cy="8" r="3.5" />
            <path d="M2.5 20a6.5 6.5 0 0 1 13 0m3-11v8m-4-4h8" />
          </svg>
          <svg
            v-else-if="seccion.icono === 'prestamos'"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            aria-hidden="true"
          >
            <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v18H6.5A2.5 2.5 0 0 0 4 23V5.5Zm16 0A2.5 2.5 0 0 0 17.5 3H13v18h4.5a2.5 2.5 0 0 1 2.5 2V5.5Z" />
          </svg>
          <svg
            v-else-if="seccion.icono === 'reportes'"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            aria-hidden="true"
          >
            <path d="M4 19V9m8 10V4m8 15v-7" />
            <path d="M2 21h20" />
          </svg>
          <svg
            v-else
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            aria-hidden="true"
          >
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" />
          </svg>
          <span>{{ seccion.nombre }}</span>
        </RouterLink>
      </nav>

      <div class="gestion-usuario">
        <span class="gestion-avatar">
          {{ authStore.usuario?.nombre?.charAt(0)?.toUpperCase() || 'U' }}
        </span>
        <div>
          <strong>{{ authStore.usuario?.nombre }}</strong>
          <span>{{ authStore.usuario?.rol }}</span>
        </div>
      </div>
    </aside>

    <section class="gestion-contenido">
      <RouterView />
    </section>
  </main>
</template>
