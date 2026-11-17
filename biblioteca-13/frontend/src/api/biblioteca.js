import cliente from './cliente'

function limpiarParams(params = {}) {
  return Object.fromEntries(
    Object.entries(params).filter(
      ([, valor]) => valor !== undefined && valor !== null && valor !== ''
    )
  )
}

export const librosApi = {
  listar(params = {}) {
    return cliente.get('/libros', { params: limpiarParams(params) })
  },
  obtenerPorId(id) {
    return cliente.get(`/libros/${id}`)
  },
  crear(datos) {
    return cliente.post('/libros', datos)
  },
  actualizar(id, datos) {
    return cliente.patch(`/libros/${id}`, datos)
  },
  eliminar(id) {
    return cliente.delete(`/libros/${id}`)
  },
  subirPortada(id, archivo) {
    const formData = new FormData()
    formData.append('archivo', archivo)
    return cliente.post(`/libros/${id}/imagen`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export const categoriasApi = {
  listar(params = { skip: 0, limit: 100 }) {
    return cliente.get('/categorias', { params: limpiarParams(params) })
  },
  obtenerPorId(id) {
    return cliente.get(`/categorias/${id}`)
  },
  crear(datos) {
    return cliente.post('/categorias', datos)
  },
  actualizar(id, datos) {
    return cliente.patch(`/categorias/${id}`, datos)
  },
  eliminar(id) {
    return cliente.delete(`/categorias/${id}`)
  }
}

export const autoresApi = {
  listar(params = { skip: 0, limit: 100 }) {
    return cliente.get('/autores', { params: limpiarParams(params) })
  },
  obtenerPorId(id) {
    return cliente.get(`/autores/${id}`)
  },
  listarLibros(id, params = { skip: 0, limit: 12 }) {
    return cliente.get(`/autores/${id}/libros`, { params: limpiarParams(params) })
  },
  crear(datos) {
    return cliente.post('/autores', datos)
  },
  actualizar(id, datos) {
    return cliente.patch(`/autores/${id}`, datos)
  },
  eliminar(id) {
    return cliente.delete(`/autores/${id}`)
  }
}

export const authApi = {
  login(email, password) {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return cliente.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  registro(datos) {
    return cliente.post('/auth/registro', datos)
  },
  logout(refreshToken) {
    return cliente.post('/auth/logout', { refresh_token: refreshToken })
  },
  perfil() {
    return cliente.get('/auth/me')
  },
  cambiarPassword(passwordActual, passwordNueva) {
    return cliente.patch('/auth/me/password', {
      password_actual: passwordActual,
      password_nueva: passwordNueva
    })
  }
}

export const usuariosApi = {
  listar(params = { skip: 0, limit: 20 }) {
    return cliente.get('/usuarios', { params: limpiarParams(params) })
  },
  crear(datos) {
    return cliente.post('/usuarios', datos)
  },
  cambiarRol(id, rol) {
    return cliente.patch(`/usuarios/${id}/rol`, { rol })
  },
  cambiarActivo(id, activo) {
    return cliente.patch(`/usuarios/${id}/activo`, { activo })
  }
}

export const sociosApi = {
  listar(params = { skip: 0, limit: 20 }) {
    return cliente.get('/socios', { params: limpiarParams(params) })
  },
  obtenerPorId(id) {
    return cliente.get(`/socios/${id}`)
  },
  crear(datos) {
    return cliente.post('/socios', datos)
  },
  actualizar(id, datos) {
    return cliente.patch(`/socios/${id}`, datos)
  },
  eliminar(id) {
    return cliente.delete(`/socios/${id}`)
  },
  prestamosPorSocio(id, params = { skip: 0, limit: 20 }) {
    return cliente.get(`/socios/${id}/prestamos`, { params: limpiarParams(params) })
  },
  miPerfil() {
    return cliente.get('/socios/me')
  },
  actualizarMiPerfil(datos) {
    return cliente.patch('/socios/me', datos)
  },
  misPrestamos(params = { skip: 0, limit: 20 }) {
    return cliente.get('/socios/me/prestamos', { params: limpiarParams(params) })
  },
  misMultas() {
    return cliente.get('/socios/me/multas')
  }
}

export const prestamosApi = {
  listar(params = { skip: 0, limit: 20 }) {
    return cliente.get('/prestamos', { params: limpiarParams(params) })
  },
  obtenerPorId(id) {
    return cliente.get(`/prestamos/${id}`)
  },
  crear(datos) {
    return cliente.post('/prestamos', datos)
  },
  registrarDevolucion(id, fecha_devolucion) {
    return cliente.post(`/prestamos/${id}/devolucion`, { fecha_devolucion })
  },
  pagarMulta(id) {
    return cliente.post(`/prestamos/${id}/pago-multa`)
  }
}

export const reportesApi = {
  resumen() {
    return cliente.get('/reportes/resumen')
  },
  librosMasPrestados(params = { limite: 5, skip: 0 }) {
    return cliente.get('/reportes/libros-mas-prestados', {
      params: limpiarParams(params)
    })
  },
  categorias(params = { skip: 0, limit: 20 }) {
    return cliente.get('/reportes/categorias', { params: limpiarParams(params) })
  },
  prestamosVencidos(params = { skip: 0, limit: 20 }) {
    return cliente.get('/reportes/prestamos-vencidos', {
      params: limpiarParams(params)
    })
  },
  sociosConMultas(params = { skip: 0, limit: 20, solo_pendientes: true }) {
    return cliente.get('/reportes/socios-con-multas', {
      params: limpiarParams(params)
    })
  },
  autores(params = { skip: 0, limit: 20 }) {
    return cliente.get('/reportes/autores', { params: limpiarParams(params) })
  }
}
