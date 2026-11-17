import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const CatalogoView = () => import('@/views/CatalogoView.vue')
const LibroDetalleView = () => import('@/views/LibroDetalleView.vue')
const CategoriasView = () => import('@/views/CategoriasView.vue')
const AutoresView = () => import('@/views/AutoresView.vue')
const LoginView = () => import('@/views/LoginView.vue')
const RegistroView = () => import('@/views/RegistroView.vue')
const PerfilView = () => import('@/views/PerfilView.vue')
const GestionView = () => import('@/views/GestionView.vue')
const InicioGestionView = () => import('@/views/gestion/InicioGestionView.vue')
const LibrosGestionView = () => import('@/views/gestion/LibrosGestionView.vue')
const AutoresGestionView = () => import('@/views/gestion/AutoresGestionView.vue')
const CategoriasGestionView = () => import('@/views/gestion/CategoriasGestionView.vue')
const UsuariosGestionView = () => import('@/views/gestion/UsuariosGestionView.vue')
const SociosGestionView = () => import('@/views/gestion/SociosGestionView.vue')
const PrestamosGestionView = () => import('@/views/gestion/PrestamosGestionView.vue')
const ReportesGestionView = () => import('@/views/gestion/ReportesGestionView.vue')

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    { path: '/', name: 'catalogo', component: CatalogoView, meta: { requiereAuth: true } },
    {
      path: '/libros/:id',
      name: 'libro-detalle',
      component: LibroDetalleView,
      meta: { requiereAuth: true }
    },
    { path: '/categorias', name: 'categorias', component: CategoriasView, meta: { requiereAuth: true } },
    { path: '/autores', name: 'autores', component: AutoresView, meta: { requiereAuth: true } },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/registro', name: 'registro', component: RegistroView },
    {
      path: '/perfil',
      name: 'perfil',
      component: PerfilView,
      meta: { requiereAuth: true }
    },
    {
      path: '/gestion',
      component: GestionView,
      meta: { requiereStaff: true },
      children: [
        { path: '', name: 'gestion-inicio', component: InicioGestionView },
        { path: 'libros', name: 'gestion-libros', component: LibrosGestionView },
        { path: 'autores', name: 'gestion-autores', component: AutoresGestionView },
        { path: 'categorias', name: 'gestion-categorias', component: CategoriasGestionView },
        {
          path: 'usuarios',
          name: 'gestion-usuarios',
          component: UsuariosGestionView,
          meta: { requiereAdmin: true }
        },
        { path: 'socios', name: 'gestion-socios', component: SociosGestionView },
        { path: 'prestamos', name: 'gestion-prestamos', component: PrestamosGestionView },
        { path: 'reportes', name: 'gestion-reportes', component: ReportesGestionView }
      ]
    },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  const requiereAuth = to.matched.some((ruta) =>
    ruta.meta.requiereAuth || ruta.meta.requiereStaff || ruta.meta.requiereAdmin
  )

  if (requiereAuth && !authStore.estaAutenticado) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (authStore.estaAutenticado && !authStore.usuario && requiereAuth) {
    await authStore.cargarPerfil()
  }

  if (to.name === 'login' && authStore.estaAutenticado) {
    if (!authStore.usuario) await authStore.cargarPerfil()
    return authStore.esStaff ? { name: 'gestion-inicio' } : { name: 'perfil' }
  }

  if (to.matched.some((ruta) => ruta.meta.requiereAdmin) && authStore.usuario?.rol !== 'admin') {
    return authStore.esStaff ? { name: 'gestion-inicio' } : { name: 'perfil' }
  }

  if (to.matched.some((ruta) => ruta.meta.requiereStaff) && !authStore.esStaff) {
    return authStore.usuario ? { name: 'perfil' } : { name: 'login' }
  }

  return true
})

export default router
