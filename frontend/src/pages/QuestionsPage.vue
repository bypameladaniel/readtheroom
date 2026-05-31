<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const questions = ref([
  "Tell me about yourself",
  "Describe a challenge you overcame",
  "Why do you want this role?",
  "Tell me about a time you led a team",
  "What's your biggest weakness?",
  "Where do you see yourself in 5 years?",
  "Why should we hire you?",
  "Tell me about a time you failed",
])

const selectedQuestion = ref("Describe a challenge you overcame")
const currentStep = ref(1)
const totalSteps = ref(3)

function selectQuestion(question) {
  selectedQuestion.value = question
}

function pickRandomQuestion() {
  const randomIndex = Math.floor(Math.random() * questions.value.length)
  selectedQuestion.value = questions.value[randomIndex]
}

function continueWithQuestion() {
  // Navigate to camera room with selected question
  console.log("Selected question:", selectedQuestion.value)
  router.push('/interview')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header with Step Indicator -->
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

    <!-- Main Content -->
    <main class="mx-auto max-w-3xl px-6 py-12">
      <!-- Title Section -->
      <div class="mb-10">
        <h2 class="text-4xl font-bold text-gray-900 mb-2">Pick a question</h2>
        <p class="text-lg text-gray-600">
          Choose one below — or let us pick randomly.
        </p>
      </div>

      <!-- Questions List -->
      <div class="space-y-3 mb-8">
        <button
          v-for="question in questions"
          :key="question"
          :class="[
            'w-full text-left px-6 py-4 rounded-lg border-2 transition-all duration-200',
            selectedQuestion === question
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-200 bg-white text-gray-900 hover:border-gray-300',
          ]"
          @click="selectQuestion(question)"
        >
          {{ question }}
        </button>
      </div>

      <!-- Pick Random Button -->
      <button
        class="w-full px-6 py-3 mb-8 rounded-lg border-2 border-gray-200 bg-white text-gray-700 font-medium hover:border-gray-300 transition-colors flex items-center justify-center gap-2"
        @click="pickRandomQuestion"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        Pick one for me
      </button>

      <!-- Action Buttons -->
      <div class="flex gap-4">
        <button
          class="w-full px-6 py-3 rounded-lg bg-white border-2 border-gray-200 text-gray-900 font-medium hover:border-gray-300 transition-colors"
          @click="continueWithQuestion"
        >
          Use this question
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Smooth transitions */
button {
  transition: all 0.2s ease-in-out;
}
</style>
