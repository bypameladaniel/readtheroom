<script setup>
import { onMounted, ref } from 'vue'

const questions = ref([])
const loading = ref(true)
const error = ref('')

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function loadQuestions() {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${apiBaseUrl}/questions`)

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`)
    }

    questions.value = await response.json()
  } catch (fetchError) {
    error.value = 'Could not load questions from the backend.'
    console.error(fetchError)
  } finally {
    loading.value = false
  }
}

onMounted(loadQuestions)
</script>

<template>
  <main class="min-h-screen bg-white px-6 py-10 text-slate-900">
    <div class="mx-auto max-w-3xl">
      <div v-if="loading">Loading...</div>
      <div v-else-if="error">{{ error }}</div>
      <ol v-else class="list-decimal space-y-4 pl-6 text-lg leading-8">
        <li v-for="question in questions" :key="question">
          {{ question }}
        </li>
      </ol>
    </div>
  </main>
</template>
