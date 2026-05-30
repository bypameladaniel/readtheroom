import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 👈 1. Import the router you just created
import './assets/main.css' // global styles

const app = createApp(App)

app.use(router) // 👈 2. Tell Vue to use the router

app.mount('#app')