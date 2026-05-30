<script setup>
import { ref, onMounted } from 'vue'

const analysis = ref(null)
const error = ref('')

onMounted(() => {
  try {
    const raw = localStorage.getItem('lastAnalysis')
    if (raw) analysis.value = JSON.parse(raw)
    else error.value = 'No server reply found.'
  } catch (e) {
    console.error(e)
    error.value = 'Failed to load server reply.'
  }
})
</script>

<template>
  <main class="flex min-h-screen items-start justify-center bg-slate-950 px-6 text-slate-100 py-12">
    <div class="w-full max-w-3xl text-center">
      <p class="text-2xl font-semibold tracking-wide sm:text-3xl">Thanks for your feedback.</p>

      <div class="mt-6 text-left">
        <template v-if="analysis">
          <p class="text-lg font-medium">Server reply:</p>
          <pre class="mt-2 bg-slate-800 p-4 rounded text-sm overflow-auto whitespace-pre-wrap">{{ typeof analysis === 'string' ? analysis : JSON.stringify(analysis, null, 2) }}</pre>
        </template>
        <p v-else class="mt-4 text-rose-400">{{ error }}</p>
      </div>
    </div>
  </main>
</template>