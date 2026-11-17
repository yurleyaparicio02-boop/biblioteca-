import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_URL || '/api/v1'

const cliente = axios.create({
  baseURL: API_BASE_URL,
  timeout: 12000,
  headers: {
    'Content-Type': 'application/json'
  }
})

cliente.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('biblioteca_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

let renovando = null

cliente.interceptors.response.use(
  (response) => response,
  async (error) => {
    const peticionOriginal = error.config
    if (
      !error.response &&
      peticionOriginal &&
      !peticionOriginal._fallbackDirecto &&
      peticionOriginal.baseURL !== 'http://127.0.0.1:8001/api/v1'
    ) {
      peticionOriginal._fallbackDirecto = true
      peticionOriginal.baseURL = 'http://127.0.0.1:8001/api/v1'
      return cliente(peticionOriginal)
    }
    if (
      error.response?.status === 401 &&
      !peticionOriginal._reintentado &&
      !peticionOriginal.url?.includes('/auth/login') &&
      !peticionOriginal.url?.includes('/auth/refresh')
    ) {
      const refreshToken = localStorage.getItem('biblioteca_refresh_token')
      if (refreshToken) {
        peticionOriginal._reintentado = true
        try {
          if (!renovando) {
            renovando = axios
              .post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken
              })
              .finally(() => {
                renovando = null
              })
          }
          const { data } = await renovando
          localStorage.setItem('biblioteca_access_token', data.access_token)
          localStorage.setItem('biblioteca_refresh_token', data.refresh_token)
          peticionOriginal.headers.Authorization = `Bearer ${data.access_token}`
          return cliente(peticionOriginal)
        } catch {
          localStorage.removeItem('biblioteca_access_token')
          localStorage.removeItem('biblioteca_refresh_token')
        }
      }
    }
    return Promise.reject(error)
  }
)

export function extraerMensajeError(error, respaldo = 'Ocurrió un error al conectar con el servidor.') {
  if (!error) return respaldo
  if (axios.isAxiosError(error) && !error.response) {
    return 'No se pudo establecer conexión con el servidor. Verifica que la API esté en ejecución.'
  }
  if (!axios.isAxiosError(error)) {
    return error.message || respaldo
  }
  const detail = error.response.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((item) => item.msg || String(item)).join('. ')
  }
  if (error.response.status === 404) return 'El recurso solicitado no fue encontrado.'
  if (error.response.status === 403) return 'No tienes permisos para realizar esta acción.'
  if (error.response.status === 401) return 'Tu sesión expiró o las credenciales son inválidas.'
  return respaldo
}

export default cliente
