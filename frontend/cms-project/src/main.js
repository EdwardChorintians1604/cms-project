import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import plugins from './plugins'
import VueApexCharts from 'vue3-apexcharts' 

// Font Awesome setup
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
library.add(fas)

// Bootstrap CSS & JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'

// Custom Tailwind CSS (must load AFTER bootstrap to override global styles)
import './styles/main.css'
import 'animate.css'

import AOS from 'aos'
import 'aos/dist/aos.css'


const app = createApp(App)

app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)
app.use(plugins)
app.use(VueApexCharts)

app.mount('#app')

setTimeout(() => {
  AOS.init({
    duration: 800,
    once: false,
    mirror: true,
    offset: 120,
    easing: 'ease-in-out'
  })
}, 100)

router.afterEach(() => {
  setTimeout(() => {
    try {
      AOS.refresh()
    } catch (e) {
      // Catch silently if route changes fast
    }
  }, 200)
})
