import { createRouter, createWebHistory } from 'vue-router'
import QuestionsPage from '../pages/QuestionsPage.vue'
import CameraRoomPage from '../pages/CameraRoomPage.vue'
import FeedbackPage from '../pages/FeedbackPage.vue'

const routes = [
  { 
    path: '/questions', 
    component: QuestionsPage 
  },
  { 
    path: '/interview', 
    component: CameraRoomPage 
  },
  {
    path: '/feedback',
    component: FeedbackPage,
  },
  // Fallback: Redirect anything else to /question
  { 
    path: '/:pathMatch(.*)*', 
    redirect: '/questions' 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router