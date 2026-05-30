<script setup>
import { onMounted, ref } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

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

function getQuestionText(question) {
  if (typeof question === 'string') {
    return question
  }

  if (question && typeof question === 'object') {
    return question.question ?? question.text ?? JSON.stringify(question)
  }

  return String(question)
}
</script>

<template>
  <main
    class="min-h-screen bg-[radial-gradient(circle_at_top,_#fef9c3_0%,_#fff7ed_30%,_#f8fafc_70%)] px-4 py-8 text-slate-900 sm:px-6 sm:py-10"
  >
    <div class="mx-auto max-w-5xl space-y-5 sm:space-y-6">

      <div
        v-if="loading"
        class="rounded-xl border border-amber-200 bg-white/80 px-5 py-4 text-slate-700 shadow-sm sm:px-6 sm:py-5"
      >
        Loading questions...
      </div>

      <div
        v-else-if="error"
        class="rounded-xl border border-rose-200 bg-rose-50/70 px-5 py-4 text-rose-700 shadow-sm sm:px-6 sm:py-5"
      >
        {{ error }}
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 sm:gap-5 lg:grid-cols-3 lg:gap-6">
        <Card
          v-for="(question, index) in questions"
          :key="`${index}-${getQuestionText(question)}`"
          class="group relative overflow-hidden border-slate-200/90 bg-white/90 py-0 transition-all duration-300 ease-out hover:-translate-y-1 hover:border-amber-300 hover:shadow-[0_18px_38px_-20px_rgba(217,119,6,0.45)]"
        >
          <div
            class="pointer-events-none absolute -left-24 top-0 h-36 w-36 rounded-full bg-amber-200/30 blur-2xl transition-transform duration-300 group-hover:translate-x-4 group-hover:translate-y-2"
          />
          <CardHeader class="px-5 pb-1 pt-5 sm:px-6 sm:pt-6">
            <Badge variant="secondary" class="w-fit bg-slate-100 text-slate-700">
              Q{{ index + 1 }}
            </Badge>
          </CardHeader>
          <CardContent class="px-5 pb-5 pt-3 sm:px-6 sm:pb-6 sm:pt-4">
            <CardTitle
              class="text-[0.98rem] leading-relaxed text-slate-800 transition-colors duration-300 group-hover:text-amber-900"
            >
              {{ getQuestionText(question) }}
            </CardTitle>
          </CardContent>
        </Card>
      </div>
    </div>
  </main>
</template>