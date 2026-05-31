import { createRouter, createWebHistory } from "vue-router";
import LandingPage from "../pages/LandingPage.vue";
import QuestionsPage from "../pages/QuestionsPage.vue";
import CameraRoomPage from "../pages/CameraRoomPage.vue";
import FeedbackPage from "../pages/FeedbackPage.vue";
import TargetRolePage from "@/pages/TargetRolePage.vue";

const routes = [
  {
    path: "/",
    component: LandingPage,
  },
  {
    path: "/questions",
    component: QuestionsPage,
  },
  {
    path: "/role",
    component: TargetRolePage,
  },
  {
    path: "/interview",
    component: CameraRoomPage,
  },
  {
    path: "/feedback",
    component: FeedbackPage,
  },
  // Fallback: Redirect anything else to /
  {
    path: "/:pathMatch(.*)*",
    redirect: "/",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
