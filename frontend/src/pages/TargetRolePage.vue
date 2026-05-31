<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const targetRole = ref('')
const currentStep = ref(2)
const totalSteps = ref(4)

function startInterview() {
  const roleValue = targetRole.value.trim()
  
  router.push({ 
    path: '/interview', 
    query: { 
      question: route.query.question,
      role: roleValue || undefined, 
    } 
  })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="border-b border-gray-200 bg-white px-6 py-4">
      <div class="mx-auto flex max-w-5xl items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">ReadTheRoom</h1>
        <div class="flex items-center gap-3">
          <div class="flex gap-2">
            <div
              v-for="step in totalSteps"
              :key="step"
              :class="[
                'h-3 w-3 rounded-full transition-colors',
                step <= currentStep ? 'bg-blue-500' : 'bg-gray-300',
              ]"
            />
          </div>
          <span class="text-sm text-gray-600 font-medium">
            Step {{ currentStep }} of {{ totalSteps }}
          </span>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-xl px-6 py-16">
      <div class="mb-8 text-center">
        <h2 class="text-4xl font-bold text-gray-900 mb-3">What are you interviewing for?</h2>
        <p class="text-lg text-gray-600">
          Enter your target role to tailor your practice session.
        </p>
      </div>

      <form @submit.prevent="startInterview" class="space-y-6">
        <div>
          <label for="role" class="sr-only">Target Role</label>
          <input
            id="role"
            type="text"
            v-model="targetRole"
            placeholder="e.g. Software Engineer, Product Manager..."
            class="w-full px-5 py-4 rounded-xl border-2 border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none transition-colors text-lg shadow-sm"
            autofocus
          />
        </div>

        <button
          type="submit"
          class="w-full px-6 py-4 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-700 active:bg-blue-800 shadow-md hover:shadow-lg transition-all duration-150 text-center text-lg"
        >
          Continue to Interview
        </button>
      </form>
    </main>
  </div>
</template>

<style scoped>
input, button {
  transition: all 0.2s ease-in-out;
}
</style>