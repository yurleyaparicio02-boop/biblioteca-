<script setup>
import { onMounted } from 'vue'
import NavbarMenu from '@/components/NavbarMenu.vue'
import NotificacionToast from '@/components/NotificacionToast.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const anioActual = new Date().getFullYear()

onMounted(() => {
  if (authStore.estaAutenticado && !authStore.usuario) {
    authStore.cargarPerfil()
  }
})
</script>

<template>
  <div class="app-layout">
    <NavbarMenu />
    <div class="app-contenido">
      <RouterView />
    </div>
    <footer class="app-footer">
      <div class="footer-inner">
        <RouterLink to="/" class="footer-marca">
          <span class="footer-icono" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
              <path d="M3 5.5A2.5 2.5 0 0 1 5.5 3H11v18H5.5A2.5 2.5 0 0 0 3 23V5.5Zm18 0A2.5 2.5 0 0 0 18.5 3H13v18h5.5a2.5 2.5 0 0 1 2.5 2V5.5Z" />
            </svg>
          </span>
          <span class="titulo-serif">Mi Biblioteca</span>
        </RouterLink>
        <span class="footer-derechos">
          © {{ anioActual }} Mi Biblioteca. Todos los derechos reservados.
        </span>
        <span class="footer-lema">Un libro, una nueva aventura.</span>
      </div>
    </footer>
    <NotificacionToast />
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-contenido {
  flex: 1;
}

.app-footer {
  margin-top: 1.5rem;
  border-top: 1px solid #e8d5e5;
  background: linear-gradient(100deg, #f1e0ee, #f7e7ee 55%, #efe3ef);
  padding: 0.9rem 1.25rem;
  font-size: 0.78rem;
  color: #674b61;
}

.footer-inner {
  width: 100%;
  max-width: 1380px;
  min-height: 36px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.footer-marca {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #633d59;
  font-size: 0.95rem;
}

.footer-icono {
  display: inline-grid;
  width: 25px;
  height: 25px;
  place-items: center;
  border-radius: 8px;
  background: #e7d4e5;
}

.footer-icono svg {
  width: 17px;
  height: 17px;
}

.footer-lema {
  color: #8d6a80;
  font-style: italic;
}

@media (max-width: 650px) {
  .footer-inner {
    justify-content: center;
    text-align: center;
  }

  .footer-lema {
    display: none;
  }
}
</style>
