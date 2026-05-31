<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function startCooking() {
  router.push('/questions')
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-gray-50 to-blue-50">
    <!-- Header -->
    <header class="border-b border-gray-200 bg-white px-6 py-4 shadow-sm">
      <div class="mx-auto max-w-6xl">
        <h1 class="text-2xl font-bold text-gray-900">ReadTheRoom</h1>
      </div>
    </header>

    <!-- Hero Section -->
    <main class="flex min-h-[calc(100vh-80px)] items-center justify-center px-6 py-20">
      <div class="max-w-2xl text-center">
        <!-- Main Headline -->
        <div class="mb-6">
          <h2 class="text-5xl font-bold text-gray-900 sm:text-6xl mb-4">
            Master Your Interview Skills
          </h2>
          <p class="text-xl text-gray-600">
            Get real-time AI feedback on your interview performance. Practice with confidence, interview with clarity.
          </p>
        </div>

        <!-- Feature Highlights -->
        <div class="my-12 grid grid-cols-3 gap-6">
          <div class="flex flex-col items-center">
            <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <span class="text-xl">🎤</span>
            </div>
            <h3 class="font-semibold text-gray-900">Record & Practice</h3>
            <p class="mt-1 text-sm text-gray-600">Answer interview questions on camera</p>
          </div>

          <div class="flex flex-col items-center">
            <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <span class="text-xl">🤖</span>
            </div>
            <h3 class="font-semibold text-gray-900">AI Analysis</h3>
            <p class="mt-1 text-sm text-gray-600">Get instant feedback powered by AI</p>
          </div>

          <div class="flex flex-col items-center">
            <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <span class="text-xl">📊</span>
            </div>
            <h3 class="font-semibold text-gray-900">Track Progress</h3>
            <p class="mt-1 text-sm text-gray-600">Improve across 8 key interview questions</p>
          </div>
        </div>

        <!-- CTA Button -->
        <button
          @click="startCooking"
          class="inline-block rounded-full bg-blue-600 px-8 py-4 text-lg font-semibold text-white transition-all hover:bg-blue-700 active:scale-95 shadow-lg hover:shadow-xl"
        >
          Get Started →
        </button>

        <!-- Social Proof / Tagline -->
        <p class="mt-8 text-sm text-gray-500">
          Ready to interview smarter? Let's go.
        </p>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Smooth animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h2 {
  animation: fadeInUp 0.6s ease-out;
}

p {
  animation: fadeInUp 0.6s ease-out 0.1s backwards;
}

.grid {
  animation: fadeInUp 0.6s ease-out 0.2s backwards;
}

button {
  animation: fadeInUp 0.6s ease-out 0.3s backwards;
}
</style>
