<script setup>
import { useNotificacionesStore } from '@/stores/notificaciones'

const store = useNotificacionesStore()
</script>

<template>
  <div class="toast-contenedor" aria-live="polite">
    <TransitionGroup name="toast">
      <div
        v-for="item in store.mensajes"
        :key="item.id"
        class="toast-item"
        :class="`toast-${item.tipo}`"
        role="status"
      >
        <span class="toast-texto">{{ item.texto }}</span>
        <button
          type="button"
          class="toast-cerrar"
          aria-label="Cerrar mensaje"
          @click="store.cerrar(item.id)"
        >
          ×
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-contenedor {
  position: fixed;
  bottom: 1.25rem;
  right: 1.25rem;
  z-index: 60;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-width: 360px;
  width: calc(100% - 2.5rem);
}

.toast-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.85rem 1.05rem;
  border-radius: var(--radio-sm);
  border: 1px solid var(--color-borde);
  box-shadow: var(--sombra-hover);
  font-size: 0.9rem;
}

.toast-exito {
  background-color: var(--color-exito-bg);
  color: var(--color-exito-txt);
  border-color: #c5dec5;
}

.toast-error {
  background-color: var(--color-error-bg);
  color: var(--color-error-txt);
  border-color: #f1c5cf;
}

.toast-info {
  background-color: var(--color-lila);
  color: #483963;
  border-color: #d6c7ea;
}

.toast-cerrar {
  background: none;
  border: none;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  opacity: 0.7;
}

.toast-cerrar:hover {
  opacity: 1;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
