<script setup>
import { ref } from 'vue'

const backendMessage = ref('Not connected yet')

async function testBackend() {
  try {
    const response = await fetch('http://localhost:8000/')
    const data = await response.json()
    backendMessage.value = data.message
  } catch (error) {
    backendMessage.value = 'Could not connect to backend'
    console.error(error)
  }
}
</script>

<template>
  <main class="min-h-screen flex items-center justify-center bg-neutral-950 text-white">
    <div class="rounded-2xl border border-neutral-800 bg-neutral-900 p-8 shadow-xl">
      <h1 class="text-3xl font-bold mb-4">ReadTheRoom</h1>

      <button
        @click="testBackend"
        class="rounded-xl bg-white px-4 py-2 font-medium text-black hover:bg-neutral-200"
      >
        Test backend connection
      </button>

      <p class="mt-4 text-neutral-300">
        {{ backendMessage }}
      </p>
    </div>
  </main>
</template>
