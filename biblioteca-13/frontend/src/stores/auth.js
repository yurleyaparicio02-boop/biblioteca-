import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { authApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'

export const useAuthStore = defineStore('auth', () => {
  const usuario = ref(null)
  const cargando = ref(false)
  const accessToken = ref(localStorage.getItem('biblioteca_access_token') || '')
  const refreshToken = ref(localStorage.getItem('biblioteca_refresh_token') || '')

  const estaAutenticado = computed(() => Boolean(accessToken.value))
  const esStaff = computed(() =>
    ['admin', 'bibliotecario'].includes(usuario.value?.rol)
  )

  async function cargarPerfil() {
    if (!accessToken.value) return null
    try {
      const { data } = await authApi.perfil()
      usuario.value = data
      return data
    } catch {
      limpiarSesion()
      return null
    }
  }

  async function iniciarSesion(email, password) {
    cargando.value = true
    try {
      const { data } = await authApi.login(email, password)
      accessToken.value = data.access_token
      refreshToken.value = data.refresh_token
      localStorage.setItem('biblioteca_access_token', data.access_token)
      localStorage.setItem('biblioteca_refresh_token', data.refresh_token)
      await cargarPerfil()
      return { ok: true }
    } catch (err) {
      return {
        ok: false,
        mensaje: extraerMensajeError(err, 'No fue posible iniciar sesión.')
      }
    } finally {
      cargando.value = false
    }
  }

  async function registrar(datos) {
    cargando.value = true
    try {
      await authApi.registro(datos)
      return { ok: true }
    } catch (err) {
      return {
        ok: false,
        mensaje: extraerMensajeError(err, 'No se pudo completar el registro.')
      }
    } finally {
      cargando.value = false
    }
  }

  async function cerrarSesion() {
    try {
      if (refreshToken.value) {
        await authApi.logout(refreshToken.value)
      }
    } catch {
      // Ignoramos errores al revocar si el token ya venció
    } finally {
      limpiarSesion()
    }
  }

  function limpiarSesion() {
    usuario.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('biblioteca_access_token')
    localStorage.removeItem('biblioteca_refresh_token')
  }

  return {
    usuario,
    cargando,
    estaAutenticado,
    esStaff,
    cargarPerfil,
    iniciarSesion,
    registrar,
    cerrarSesion
  }
})
