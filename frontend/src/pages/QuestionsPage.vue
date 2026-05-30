<script setup>
import { computed, onMounted, ref } from 'vue'

const questions = ref([])
const loading = ref(true)
const error = ref('')

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const questionCount = computed(() => questions.value.length)

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
  <main class="min-h-screen overflow-hidden bg-[#0b1020] text-slate-100">
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(34,197,94,0.2),_transparent_35%),radial-gradient(circle_at_top_right,_rgba(6,182,212,0.18),_transparent_28%),linear-gradient(180deg,_#0b1020_0%,_#111827_100%)]"></div>
    <div class="absolute -left-24 top-24 h-72 w-72 rounded-full bg-emerald-400/10 blur-3xl"></div>
    <div class="absolute -right-24 bottom-12 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl"></div>

    <section class="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 md:px-10">
      <header class="mb-10 flex flex-col gap-5 border-b border-white/10 pb-8 md:flex-row md:items-end md:justify-between">
        <div class="space-y-4 max-w-2xl">
          <p class="inline-flex rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.28em] text-emerald-200">
            Interview prompts
          </p>
          <div class="space-y-3">
            <h1 class="text-4xl font-semibold tracking-tight text-white md:text-6xl">
              ReadTheRoom question bank
            </h1>
            <p class="max-w-2xl text-sm leading-6 text-slate-300 md:text-base">
              Browse the interview questions served by the FastAPI backend. Each prompt includes the criteria the coach uses to evaluate answers.
            </p>
          </div>
        </div>

        <div class="rounded-2xl border border-white/10 bg-white/5 px-5 py-4 backdrop-blur-sm">
          <p class="text-xs uppercase tracking-[0.24em] text-slate-400">Loaded questions</p>
          <p class="mt-2 text-3xl font-semibold text-white">{{ questionCount }}</p>
        </div>
      </header>

      <div v-if="loading" class="grid flex-1 place-items-center py-20 text-slate-300">
        <div class="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 backdrop-blur-sm">
          Loading questions...
        </div>
      </div>

      <div v-else-if="error" class="grid flex-1 place-items-center py-20">
        <div class="max-w-xl rounded-3xl border border-rose-400/20 bg-rose-400/10 p-6 text-center text-rose-100 backdrop-blur-sm">
          <p class="text-lg font-semibold">{{ error }}</p>
          <button
            class="mt-5 rounded-xl border border-rose-200/20 bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/15"
            @click="loadQuestions"
          >
            Try again
          </button>
        </div>
      </div>

      <div v-else class="grid gap-5 pb-8 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="question in questions"
          :key="question.id"
          class="group rounded-3xl border border-white/10 bg-white/6 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.25)] backdrop-blur-md transition duration-300 hover:-translate-y-1 hover:border-emerald-300/30 hover:bg-white/8"
        >
          <div class="flex items-center justify-between gap-4">
            <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-400/15 text-sm font-semibold text-emerald-200 ring-1 ring-inset ring-emerald-300/20">
              {{ question.id }}
            </span>
            <span class="text-xs uppercase tracking-[0.24em] text-slate-400">Question</span>
          </div>

          <h2 class="mt-5 text-xl font-semibold leading-8 text-white">
            {{ question.question }}
          </h2>

          <div class="mt-6 space-y-3">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
              Expected answer points
            </p>
            <ul class="space-y-3 text-sm leading-6 text-slate-300">
              <li
                v-for="point in question.expected_answer_points"
                :key="point"
                class="flex gap-3 rounded-2xl border border-white/8 bg-black/10 px-4 py-3"
              >
                <span class="mt-2 h-2 w-2 shrink-0 rounded-full bg-cyan-300"></span>
                <span>{{ point }}</span>
              </li>
            </ul>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>
