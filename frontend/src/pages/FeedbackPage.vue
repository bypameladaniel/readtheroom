<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const analysis = ref(null)
const expressionsAnalysis = ref(null)
const error = ref('')

// Keep track of the interval ID so we can stop it
let pollInterval = null

// The worker function that checks localStorage
const pollExpressionsData = () => {
  const rawExpressions = localStorage.getItem('expressionsAnalysis')
  
  if (rawExpressions) {
    try {
      expressionsAnalysis.value = JSON.parse(rawExpressions)
      
      // SUCCESS! Clear the interval immediately so we stop hitting localStorage
      stopPolling()
    } catch (e) {
      console.error('Failed to parse expressions analysis:', e)
      // If it's malformed JSON, you might want to stop polling to avoid infinite loops
      stopPolling()
    }
  }
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

onMounted(() => {
  try {
    const raw = localStorage.getItem('lastAnalysis')
    if (raw) analysis.value = JSON.parse(raw)
    else error.value = 'No server reply found.'
  } catch (e) {
    console.error(e)
    error.value = 'Failed to load server reply.'
  }

  // Check for expression analysis immediately (in case the network beat the router)
  pollExpressionsData()
  
  // If it's not there yet, start the 500ms poll loop
  if (!expressionsAnalysis.value) {
    pollInterval = setInterval(pollExpressionsData, 500)
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <main class="flex min-h-screen items-start justify-center bg-slate-950 px-6 text-slate-100 py-12">
    <div class="w-full max-w-3xl text-center">
      <p class="text-2xl font-semibold tracking-wide sm:text-3xl">Thanks for your feedback.</p>

      <div class="mt-6 text-left space-y-6">
        <div>
          <template v-if="analysis">
            <p class="text-lg font-medium text-slate-300">Server reply:</p>
            <pre class="mt-2 bg-slate-800 p-4 rounded text-sm overflow-auto whitespace-pre-wrap">{{ typeof analysis === 'string' ? analysis : JSON.stringify(analysis, null, 2) }}</pre>
          </template>
          <p v-else class="mt-4 text-rose-400">{{ error }}</p>
        </div>

        <hr class="border-slate-800" />

        <div>
          <p class="text-lg font-medium text-slate-300">Expressions Analysis:</p>
          
          <div v-if="expressionsAnalysis" class="mt-2">
            <pre class="bg-slate-800 p-4 rounded text-sm overflow-auto whitespace-pre-wrap">{{ JSON.stringify(expressionsAnalysis, null, 2) }}</pre>
          </div>
          
          <div v-else class="mt-3 flex items-center gap-3 rounded-lg bg-slate-900/50 border border-slate-800 p-4 text-slate-400 italic">
            <svg class="animate-spin h-5 w-5 text-indigo-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Analyzing video expressions... Loading</span>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>