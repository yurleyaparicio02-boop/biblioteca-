<script setup>
import { onMounted, reactive, ref } from 'vue'
import { usuariosApi } from '@/api/biblioteca'
import { extraerMensajeError } from '@/api/cliente'
import GestionTabla from '@/components/GestionTabla.vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

const authStore = useAuthStore()
const notificaciones = useNotificacionesStore()
const usuarios = ref([])
const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const skip = ref(0)
const total = ref(0)
const limite = 20
const filtroRol = ref('')
const filtroActivo = ref('')
const formulario = reactive({
  nombre: '',
  email: '',
  password: '',
  rol: 'bibliotecario'
})
const columnas = [
  { clave: 'nombre', titulo: 'Nombre' },
  { clave: 'email', titulo: 'Correo' },
  { clave: 'rol', titulo: 'Rol' },
  { clave: 'estado', titulo: 'Estado' },
  { clave: 'creado', titulo: 'Creado' }
]

async function cargar() {
  cargando.value = true
  error.value = ''
  const params = { skip: skip.value, limit: limite }
  if (filtroRol.value) params.rol = filtroRol.value
  if (filtroActivo.value !== '') params.activo = filtroActivo.value
  try {
    const { data } = await usuariosApi.listar(params)
    usuarios.value = (data.items || []).map((usuario) => ({
      ...usuario,
      estado: usuario.activo ? 'Activo' : 'Inactivo',
      creado: new Date(usuario.creado_en).toLocaleDateString('es-CO')
    }))
    total.value = data.total || 0
  } catch (err) {
    error.value = extraerMensajeError(err, 'No se pudieron cargar los usuarios.')
  } finally {
    cargando.value = false
  }
}

async function crearUsuario() {
  guardando.value = true
  try {
    await usuariosApi.crear({
      nombre: formulario.nombre.trim(),
      email: formulario.email.trim(),
      password: formulario.password,
      rol: formulario.rol
    })
    notificaciones.exito('Usuario creado correctamente.')
    Object.assign(formulario, {
      nombre: '',
      email: '',
      password: '',
      rol: 'bibliotecario'
    })
    skip.value = 0
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo crear el usuario.'))
  } finally {
    guardando.value = false
  }
}

async function cambiarRol(usuario, evento) {
  const rolAnterior = usuario.rol
  const rolNuevo = evento.target.value
  if (rolNuevo === rolAnterior) return
  try {
    await usuariosApi.cambiarRol(usuario.id, rolNuevo)
    notificaciones.exito('Rol actualizado correctamente.')
    await cargar()
  } catch (err) {
    evento.target.value = rolAnterior
    notificaciones.error(extraerMensajeError(err, 'No se pudo cambiar el rol.'))
  }
}

async function cambiarActivo(usuario) {
  const activoNuevo = !usuario.activo
  try {
    await usuariosApi.cambiarActivo(usuario.id, activoNuevo)
    notificaciones.exito(
      activoNuevo ? 'Usuario activado correctamente.' : 'Usuario desactivado correctamente.'
    )
    await cargar()
  } catch (err) {
    notificaciones.error(extraerMensajeError(err, 'No se pudo actualizar el usuario.'))
  }
}

function aplicarFiltros() {
  skip.value = 0
  cargar()
}

function paginaAnterior() {
  skip.value = Math.max(0, skip.value - limite)
  cargar()
}

function paginaSiguiente() {
  skip.value += limite
  cargar()
}

onMounted(cargar)
</script>

<template>
  <div class="gestion-vista">
    <header class="gestion-cabecera">
      <div>
        <span class="badge badge-lila">Solo administradores</span>
        <h1 class="titulo-serif">Usuarios</h1>
        <p>Crea cuentas de personal y administra roles y accesos.</p>
      </div>
    </header>

    <form class="gestion-formulario tarjeta-base" @submit.prevent="crearUsuario">
      <h2 class="titulo-serif">Crear cuenta de personal</h2>
      <div class="gestion-form-grid gestion-form-grid-4">
        <label class="gestion-campo">
          <span>Nombre</span>
          <input v-model="formulario.nombre" required minlength="3" maxlength="100" />
        </label>
        <label class="gestion-campo">
          <span>Correo electrónico</span>
          <input v-model="formulario.email" type="email" required maxlength="150" />
        </label>
        <label class="gestion-campo">
          <span>Contraseña temporal</span>
          <input
            v-model="formulario.password"
            type="password"
            required
            minlength="8"
            maxlength="64"
            autocomplete="new-password"
          />
        </label>
        <label class="gestion-campo">
          <span>Rol</span>
          <select v-model="formulario.rol">
            <option value="bibliotecario">Bibliotecario</option>
            <option value="admin">Administrador</option>
          </select>
        </label>
      </div>
      <p class="gestion-ayuda">
        La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula y un número.
      </p>
      <div class="gestion-form-acciones">
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Creando...' : 'Crear usuario' }}
        </button>
      </div>
    </form>

    <div class="gestion-filtros tarjeta-base">
      <label class="gestion-campo">
        <span>Filtrar por rol</span>
        <select v-model="filtroRol" @change="aplicarFiltros">
          <option value="">Todos los roles</option>
          <option value="admin">Administrador</option>
          <option value="bibliotecario">Bibliotecario</option>
          <option value="socio">Socio</option>
        </select>
      </label>
      <label class="gestion-campo">
        <span>Estado de la cuenta</span>
        <select v-model="filtroActivo" @change="aplicarFiltros">
          <option value="">Todos</option>
          <option :value="true">Activos</option>
          <option :value="false">Inactivos</option>
        </select>
      </label>
    </div>

    <GestionTabla
      :columnas="columnas"
      :filas="usuarios"
      :cargando="cargando"
      :error="error"
      :total="total"
      :skip="skip"
      :limite="limite"
      mensaje-vacio="No hay usuarios que coincidan con los filtros."
      @reintentar="cargar"
      @anterior="paginaAnterior"
      @siguiente="paginaSiguiente"
    >
      <template #acciones="{ fila }">
        <div class="gestion-acciones-fila gestion-acciones-usuario">
          <select
            :value="fila.rol"
            aria-label="Cambiar rol"
            @change="cambiarRol(fila, $event)"
          >
            <option value="admin">Admin</option>
            <option value="bibliotecario">Bibliotecario</option>
            <option value="socio">Socio</option>
          </select>
          <button
            type="button"
            class="btn-tabla"
            :disabled="fila.id === authStore.usuario?.id"
            @click="cambiarActivo(fila)"
          >
            {{ fila.activo ? 'Desactivar' : 'Activar' }}
          </button>
        </div>
      </template>
    </GestionTabla>
  </div>
</template>
