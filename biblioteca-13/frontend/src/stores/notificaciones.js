import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificacionesStore = defineStore('notificaciones', () => {
  const mensajes = ref([])
  let contador = 0

  function mostrar(texto, tipo = 'exito', duracion = 4000) {
    const id = ++contador
    mensajes.value.push({ id, texto, tipo })
    if (duracion > 0) {
      setTimeout(() => {
        cerrar(id)
      }, duracion)
    }
  }

  function exito(texto) {
    mostrar(texto, 'exito')
  }

  function error(texto) {
    mostrar(texto, 'error', 5500)
  }

  function info(texto) {
    mostrar(texto, 'info')
  }

  function cerrar(id) {
    mensajes.value = mensajes.value.filter((m) => m.id !== id)
  }

  return { mensajes, mostrar, exito, error, info, cerrar }
})
