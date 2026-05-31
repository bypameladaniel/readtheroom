<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const analysis = ref(null)
const expressionsAnalysis = ref(null)
const error = ref('')

const currentStep = ref(3)
const totalSteps = ref(3)

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
  
  <main class="flex min-h-screen flex-col items-center bg-gray-50 px-4 sm:px-6 py-12 text-gray-900">
    <div class="w-full max-w-5xl space-y-8">
      <!-- Header with Step Indicator -->
      
      <!-- Header -->
      <div class="text-center space-y-4">
        <h1 class="text-3xl font-bold tracking-tight sm:text-4xl text-gray-900">Your Feedback Dashboard</h1>
        <p class="text-gray-600 max-w-2xl mx-auto">We've analyzed your interview performance based on both your verbal responses and non-verbal expressions. Here is a breakdown of how you did.</p>
      </div>

      <!-- Loading State -->
      <div v-if="!analysis && !error" class="flex flex-col items-center space-y-4 py-12 text-gray-600">
         <!-- Spinner SVG -->
         <svg class="animate-spin h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
           <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
           <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
         </svg>
         <p>Loading audio analysis...</p>
      </div>
      <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center">
        {{ error }}
      </div>

      <!-- Dashboard Layout -->
      <Tabs v-if="analysis || expressionsAnalysis" defaultValue="overview" class="w-full">
        <TabsList class="grid w-full grid-cols-3 bg-white border border-gray-200 p-1 mb-8">
          <TabsTrigger value="overview" class="data-[state=active]:bg-gray-100 data-[state=active]:text-gray-900">Overview</TabsTrigger>
          <TabsTrigger value="speech" class="data-[state=active]:bg-gray-100 data-[state=active]:text-gray-900">Content & Speech</TabsTrigger>
          <TabsTrigger value="expressions" class="data-[state=active]:bg-gray-100 data-[state=active]:text-gray-900">Facial Expressions</TabsTrigger>
        </TabsList>

        <!-- OVERVIEW TAB -->
        <TabsContent value="overview" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <!-- Speech Score Card -->
            <Card class="bg-white border-gray-200 text-gray-900 shadow-lg overflow-hidden">
              <CardHeader class="border-b border-gray-200 bg-gray-50">
                <CardTitle>Content Reliability</CardTitle>
                <CardDescription class="text-gray-600">Response relevance and structure</CardDescription>
              </CardHeader>
              <CardContent class="flex flex-col items-center pt-8 pb-6">
                <div class="text-6xl font-extrabold text-blue-600 tracking-tighter drop-shadow-sm">
                  {{ analysis?.relevance_score !== undefined ? analysis.relevance_score * 10 : '--' }}<span class="text-3xl text-blue-300">/10</span>
                </div>
                <p class="text-sm font-medium text-gray-600 mt-3 uppercase tracking-wider">Relevance Score</p>
                <div class="w-full mt-8 space-y-2 max-w-[80%]">
                  <div class="flex justify-between text-xs font-semibold text-gray-700">
                    <span>Conciseness</span>
                    <span class="text-blue-600">{{ analysis?.conciseness_score || 0 }}/10</span>
                  </div>
                  <Progress :model-value="(analysis?.conciseness_score || 0) * 10" class="h-2.5 bg-gray-200 [&>div]:bg-blue-500 rounded-full" />
                </div>
              </CardContent>
            </Card>

            <!-- Expressions Score Card -->
            <Card class="bg-white border-gray-200 text-gray-900 shadow-lg overflow-hidden">
              <CardHeader class="border-b border-gray-200 bg-gray-50">
                <CardTitle>Non-Verbal Impact</CardTitle>
                <CardDescription class="text-gray-600">Facial expressions and engagement</CardDescription>
              </CardHeader>
              <CardContent class="flex flex-col items-center pt-8 pb-6" v-if="expressionsAnalysis?.overall_score !== undefined">
                <div class="text-6xl font-extrabold text-green-600 tracking-tighter drop-shadow-sm flex items-baseline">
                  {{ expressionsAnalysis.overall_score }}<span class="text-3xl text-green-300">%</span>
                </div>
                <p class="text-sm font-medium text-gray-600 mt-3 uppercase tracking-wider">Overall Engagement</p>
                <div class="w-full mt-8 space-y-2 max-w-[80%]">
                  <Progress :model-value="expressionsAnalysis.overall_score" class="h-2.5 bg-gray-200 [&>div]:bg-green-500 rounded-full" />
                </div>
              </CardContent>
              <CardContent v-else class="flex flex-col items-center justify-center pt-14 pb-12 opacity-80">
                <svg class="animate-spin h-10 w-10 text-green-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p class="text-sm text-gray-600 font-medium tracking-wide">Analyzing video data...</p>
              </CardContent>
            </Card>
          </div>

          <!-- Overall Summary -->
          <Card class="bg-white border-gray-200 shadow-lg" v-if="expressionsAnalysis?.overall_summary">
            <CardHeader class="pb-2">
              <CardTitle class="text-gray-900 text-xl font-semibold flex items-center gap-2">
                <span class="text-2xl">✨</span> Overall Impression
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p class="text-gray-700 leading-relaxed text-base sm:text-lg sm:leading-8">{{ expressionsAnalysis.overall_summary }}</p>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- SPEECH TAB -->
        <TabsContent value="speech" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6" v-if="analysis">
            <!-- Strengths -->
            <Card class="bg-white border-green-200 shadow-lg">
              <CardHeader class="bg-green-50 border-b border-green-200">
                <CardTitle class="text-green-700 flex items-center gap-2 text-lg">
                  <span class="text-xl">🏆</span> Key Strengths
                </CardTitle>
              </CardHeader>
              <CardContent class="pt-6">
                <ul v-if="analysis.strengths?.length > 0" class="space-y-4">
                  <li v-for="(item, i) in analysis.strengths" :key="i" class="text-gray-700 flex items-start gap-3">
                    <div class="bg-green-100 text-green-600 rounded-full p-1 mt-0.5 shadow-sm">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                    </div>
                    <span class="leading-snug">{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="text-gray-500 italic py-4 text-center bg-gray-100 rounded-lg">No specific strengths highlighted in this recording.</p>
              </CardContent>
            </Card>

            <!-- Improvements -->
            <Card class="bg-white border-orange-200 shadow-lg">
              <CardHeader class="bg-orange-50 border-b border-orange-200">
                <CardTitle class="text-orange-700 flex items-center gap-2 text-lg">
                  <span class="text-xl">💡</span> Areas to Improve
                </CardTitle>
              </CardHeader>
              <CardContent class="pt-6">
                <ul v-if="analysis.improvements?.length > 0" class="space-y-4">
                  <li v-for="(item, i) in analysis.improvements" :key="i" class="text-gray-700 flex items-start gap-3">
                     <div class="bg-orange-100 text-orange-600 rounded-full p-1 mt-0.5 shadow-sm">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>
                    </div>
                    <span class="leading-snug">{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="text-gray-500 italic py-4 text-center bg-gray-100 rounded-lg">No specific improvements suggested for this segment.</p>
              </CardContent>
            </Card>
          </div>

          <!-- STAR Method -->
          <Card class="bg-white border-gray-200 shadow-xl overflow-hidden" v-if="analysis?.star_method">
            <CardHeader class="bg-gray-50 pb-4">
              <CardTitle class="text-gray-900 flex items-center gap-2">
                <span class="text-blue-600">★</span> STAR Method Breakdown
              </CardTitle>
              <CardDescription class="text-gray-600 ml-6">Structure of your response</CardDescription>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div class="bg-blue-50 p-5 rounded-xl border border-blue-200 shadow-inner relative overflow-hidden group hover:border-blue-400 transition-colors">
                  <div class="absolute top-0 right-0 w-16 h-16 bg-blue-100 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
                  <h4 class="text-xs font-bold text-blue-600 mb-2 uppercase tracking-widest">Situation</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">{{ analysis.star_method.situation || 'Not identified' }}</p>
                </div>
                <div class="bg-blue-50 p-5 rounded-xl border border-blue-200 shadow-inner relative overflow-hidden group hover:border-blue-400 transition-colors">
                  <div class="absolute top-0 right-0 w-16 h-16 bg-blue-100 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
                  <h4 class="text-xs font-bold text-blue-600 mb-2 uppercase tracking-widest">Task</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">{{ analysis.star_method.task || 'Not identified' }}</p>
                </div>
                <div class="bg-blue-50 p-5 rounded-xl border border-blue-200 shadow-inner relative overflow-hidden group hover:border-blue-400 transition-colors">
                  <div class="absolute top-0 right-0 w-16 h-16 bg-blue-100 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
                  <h4 class="text-xs font-bold text-blue-600 mb-2 uppercase tracking-widest">Action</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">{{ analysis.star_method.action || 'Not identified' }}</p>
                </div>
                <div class="bg-blue-50 p-5 rounded-xl border border-blue-200 shadow-inner relative overflow-hidden group hover:border-blue-400 transition-colors">
                  <div class="absolute top-0 right-0 w-16 h-16 bg-blue-100 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
                  <h4 class="text-xs font-bold text-blue-600 mb-2 uppercase tracking-widest">Result</h4>
                  <p class="text-gray-700 text-sm leading-relaxed">{{ analysis.star_method.result || 'Not identified' }}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Filler Words -->
          <Card class="bg-white border-gray-200 shadow-xl" v-if="analysis?.filler_words !== undefined">
            <CardContent class="p-6">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <span class="text-red-500">"Um..."</span> Filler Words
                  </h3>
                  <p class="text-sm text-gray-600 mt-1">Words that distracted from your message</p>
                </div>
                <div class="flex flex-wrap gap-2 justify-start sm:justify-end max-w-md">
                  <Badge v-for="(word, i) in analysis.filler_words" :key="i" variant="destructive" class="bg-red-100 text-red-700 border border-red-200 px-3 py-1 shadow-sm">
                    {{ word }}
                  </Badge>
                  <div v-if="analysis.filler_words.length === 0" class="bg-green-100 border border-green-200 text-green-700 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 shadow-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>
                    Great! No filler words
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- EXPRESSIONS TAB -->
        <TabsContent value="expressions" class="space-y-6">
          <div v-if="!expressionsAnalysis" class="py-24 text-center text-gray-600 bg-gray-50 border border-gray-200 rounded-xl shadow-lg">
            <svg class="animate-spin h-10 w-10 text-green-500 mx-auto mb-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-lg font-medium text-gray-700">Processing Video Analysis</p>
            <p class="text-sm mt-2 text-gray-600 max-w-sm mx-auto">We're interpreting micro-expressions to give you detailed non-verbal feedback...</p>
          </div>
          
          <template v-else>
            <!-- Emotional Arc -->
            <Card class="bg-white border-gray-200 shadow-xl overflow-hidden">
              <CardHeader class="bg-gray-50 pb-4">
                <CardTitle class="text-gray-900 flex items-center gap-2">
                  <span class="text-purple-600">〰️</span> Emotional Arc
                </CardTitle>
                <CardDescription class="text-gray-600 ml-8">How your demeanour evolved over time</CardDescription>
              </CardHeader>
              <CardContent class="pt-6 px-4 sm:px-8">
                <div class="space-y-4">
                  <!-- Arc steps -->
                  <div class="flex flex-col gap-6 relative before:absolute before:inset-y-0 before:left-[11px] before:w-0.5 before:bg-gray-300 my-4">
                    <div class="relative flex gap-4">
                      <div class="min-w-0 max-w-full flex-1 relative pl-10">
                        <div class="absolute w-6 h-6 bg-white border-[3px] border-blue-600 rounded-full left-0 mt-[2px] shrink-0 z-10 shadow-[0_0_10px_rgba(37,99,235,0.4)]" />
                        <h4 class="text-sm font-bold text-gray-700 uppercase tracking-widest text-blue-600 mb-1">Opening</h4>
                        <p class="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-200 shadow-sm">{{ expressionsAnalysis.emotional_arc?.opening }}</p>
                      </div>
                    </div>
                    <div class="relative flex gap-4">
                      <div class="min-w-0 max-w-full flex-1 relative pl-10">
                        <div class="absolute w-6 h-6 bg-white border-[3px] border-green-600 rounded-full left-0 mt-[2px] shrink-0 z-10 shadow-[0_0_10px_rgba(22,163,74,0.4)]" />
                        <h4 class="text-sm font-bold text-gray-700 uppercase tracking-widest text-green-600 mb-1">Middle</h4>
                        <p class="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-200 shadow-sm">{{ expressionsAnalysis.emotional_arc?.middle }}</p>
                      </div>
                    </div>
                    <div class="relative flex gap-4">
                      <div class="min-w-0 max-w-full flex-1 relative pl-10">
                        <div class="absolute w-6 h-6 bg-white border-[3px] border-purple-600 rounded-full left-0 mt-[2px] shrink-0 z-10 shadow-[0_0_10px_rgba(147,51,234,0.4)]" />
                        <h4 class="text-sm font-bold text-gray-700 uppercase tracking-widest text-purple-600 mb-1">Closing</h4>
                        <p class="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-lg border border-gray-200 shadow-sm">{{ expressionsAnalysis.emotional_arc?.closing }}</p>
                      </div>
                    </div>
                  </div>
                  <div class="mt-8 p-5 bg-blue-50 rounded-xl border border-blue-200 flex gap-4 items-start shadow-inner">
                    <span class="text-2xl mt-0.5">📌</span>
                    <p class="text-sm text-gray-700 font-medium leading-relaxed">{{ expressionsAnalysis.emotional_arc?.arc_note }}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Strengths (Expressions) -->
              <Card class="bg-white border-green-200 shadow-lg">
                <CardHeader class="bg-green-50 border-b border-green-200">
                  <CardTitle class="text-green-700 text-lg flex items-center gap-2">
                    <span class="text-xl">🌟</span> Expression Strengths
                  </CardTitle>
                </CardHeader>
                <CardContent class="pt-6">
                  <ul class="space-y-4">
                    <li v-for="(item, i) in expressionsAnalysis.strengths" :key="i" class="text-gray-700 flex items-start gap-3 text-sm">
                      <div class="bg-green-100 text-green-600 rounded-full p-1 mt-0.5 shadow-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                      </div>
                      <span class="leading-snug">{{ item }}</span>
                    </li>
                  </ul>
                  <p v-if="!expressionsAnalysis.strengths?.length" class="text-gray-500 italic py-2 text-center bg-gray-100 rounded-lg">No specific strengths mapped.</p>
                </CardContent>
              </Card>

              <!-- Improvements (Expressions) -->
              <Card class="bg-white border-orange-200 shadow-lg">
                <CardHeader class="bg-orange-50 border-b border-orange-200">
                  <CardTitle class="text-orange-700 text-lg flex items-center gap-2">
                    <span class="text-xl">🎯</span> Areas to Polish
                  </CardTitle>
                </CardHeader>
                <CardContent class="pt-6">
                  <ul class="space-y-4">
                    <li v-for="(item, i) in expressionsAnalysis.improvements" :key="i" class="text-gray-700 flex items-start gap-3 text-sm">
                      <div class="bg-orange-100 text-orange-600 rounded-full p-1 mt-0.5 shadow-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>
                      </div>
                      <span class="leading-snug">{{ item }}</span>
                    </li>
                  </ul>
                  <p v-if="!expressionsAnalysis.improvements?.length" class="text-gray-500 italic py-2 text-center bg-gray-100 rounded-lg">No immediate improvements needed.</p>
                </CardContent>
              </Card>
            </div>

            <!-- Practice Exercises -->
            <Card class="bg-white border-blue-200 shadow-xl overflow-hidden" v-if="expressionsAnalysis.practice_exercises?.length > 0">
              <CardHeader class="bg-gradient-to-r from-blue-50 to-white border-b border-blue-200">
                <CardTitle class="text-blue-700 text-lg flex items-center gap-2">
                  <span class="text-xl">🏋️</span> Recommended Practice
                </CardTitle>
                <CardDescription class="text-blue-600 ml-8">Exercises to improve your stage presence</CardDescription>
              </CardHeader>
              <CardContent class="pt-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div v-for="(item, i) in expressionsAnalysis.practice_exercises" :key="i" class="bg-blue-50 p-5 rounded-xl border border-blue-200 hover:border-blue-400 transition-colors shadow-inner flex flex-col h-full">
                    <div class="text-blue-300 font-black text-4xl mb-2 opacity-50">0{{ i + 1 }}</div>
                    <p class="text-sm text-gray-700 leading-relaxed font-medium mt-auto">{{ item }}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
          </template>
        </TabsContent>

      </Tabs>
      
      <!-- Back button if they want to try again -->
      <div class="text-center pt-10 pb-6 w-full flex justify-center">
         <RouterLink to="/" class="inline-flex items-center justify-center pt-3 pb-3 px-8 gap-3 bg-blue-600 text-white hover:bg-blue-700 rounded-full font-bold transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0">
           <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
           Start New Session
         </RouterLink>
      </div>

    </div>
  </main>
</template>