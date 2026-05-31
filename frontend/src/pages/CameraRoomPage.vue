<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const motionStates = [
  { x: '24%', y: '28%', rotate: '-8deg', scale: 0.92, label: 'Top left' },
  { x: '72%', y: '30%', rotate: '10deg', scale: 1, label: 'Top right' },
  { x: '68%', y: '74%', rotate: '-4deg', scale: 1.08, label: 'Bottom right' },
  { x: '30%', y: '72%', rotate: '6deg', scale: 0.98, label: 'Bottom left' },
]

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const route = useRoute()
const router = useRouter()

const activeStateIndex = ref(0)
const cameraReady = ref(false)
const cameraError = ref('')
const recordingError = ref('')
const recordingErrorStage = ref('')
const interviewStage = ref('ready-to-listen')
const isRecording = ref(false)
const isUploading = ref(false)
const videoElement = ref(null)

let mediaStream = null
let mediaRecorder = null
let recordedChunks = []
let questionAudio = null
let questionAudioObjectUrl = null

const activeState = computed(() => motionStates[activeStateIndex.value])

const interviewQuestion = computed(() => (Array.isArray(route.query.question) ? route.query.question[0] : route.query.question) || 'Tell me about yourself.')
const interviewRole = computed(() => (Array.isArray(route.query.role) ? route.query.role[0] : route.query.role) || 'General job interview')

const actionLabel = computed(() => {
  if (isUploading.value) return 'Uploading...'
  if (interviewStage.value === 'ready-to-listen') return 'Read Question'
  if (interviewStage.value === 'reading-question') return 'Reading...'
  if (interviewStage.value === 'ready-to-record') return 'Start Recording'
  return isRecording.value ? 'Done' : 'Start'
})

const actionMessage = computed(() => {
  if (isUploading.value) return 'Uploading your recording. Please wait...'
  if (interviewStage.value === 'ready-to-listen') return 'Click Read Question to hear the prompt before you answer.'
  if (interviewStage.value === 'reading-question') return 'Listening to the question. Recording will unlock when playback finishes.'
  if (interviewStage.value === 'ready-to-record') return 'Question finished. Click Start Recording when you are ready.'
  if (isRecording.value) return 'Recording now. Click Done to send the video.'
  return 'Click Start to begin recording your answer.'
})

const shapeStyle = computed(() => ({
  left: activeState.value.x,
  top: activeState.value.y,
  transform: `translate(-50%, -50%) rotate(${activeState.value.rotate}) scale(${activeState.value.scale})`,
}))

async function startCamera() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
    }
    cameraReady.value = true
  } catch (error) {
    cameraError.value = 'Camera access denied.'
    console.error(error)
  }
}

function cleanupQuestionAudio() {
  if (questionAudio) {
    questionAudio.pause()
    questionAudio.src = ''
    questionAudio.onended = null
    questionAudio.onerror = null
    questionAudio = null
  }

  if (questionAudioObjectUrl) {
    URL.revokeObjectURL(questionAudioObjectUrl)
    questionAudioObjectUrl = null
  }
}

async function readQuestion() {
  recordingError.value = ''
  interviewStage.value = 'reading-question'
  cleanupQuestionAudio()

  try {
    const response = await fetch(
      `${apiBaseUrl}/questions/speak?question=${encodeURIComponent(interviewQuestion.value)}`,
    )

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`)
    }

    const audioBlob = await response.blob()
    questionAudioObjectUrl = URL.createObjectURL(audioBlob)
    questionAudio = new Audio(questionAudioObjectUrl)

    await new Promise((resolve, reject) => {
      questionAudio.onended = resolve
      questionAudio.onerror = () => reject(new Error('Could not play the question audio.'))
      questionAudio.play().catch(reject)
    })

    interviewStage.value = 'ready-to-record'
  } catch (error) {
    interviewStage.value = 'ready-to-listen'
    recordingError.value = 'Could not read the question: ' + error.message
    console.error('Question audio error:', error)
  } finally {
    cleanupQuestionAudio()
  }
}

function startRecording() {
  recordingError.value = ''
  recordedChunks = []
  
  const options = { mimeType: MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm' }
  mediaRecorder = new MediaRecorder(mediaStream, options)
  
  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) recordedChunks.push(event.data)
  }
  
  mediaRecorder.start()
  isRecording.value = true
  interviewStage.value = 'recording'
  console.log('Recording started')
}

async function uploadRecording() {
  if (!mediaRecorder) return
  isUploading.value = true
  interviewStage.value = 'uploading'
  
  console.log('Stopping recorder...')
  mediaRecorder.stop()

  // Wait for the recorder to stop with a timeout fallback
  await new Promise((resolve) => {
    const timeout = setTimeout(resolve, 2000)
    mediaRecorder.onstop = () => {
      clearTimeout(timeout)
      resolve()
    }
  })

  const blob = new Blob(recordedChunks, { type: 'video/webm' })
  const formData = new FormData()
  formData.append('video', blob, 'interview.webm')
  formData.append('question', interviewQuestion.value)
  formData.append('role', interviewRole.value)

  console.log('Sending request to:', `${apiBaseUrl}/questions/analyze-interview`)

  try {
    const response = await fetch(`${apiBaseUrl}/questions/analyze-interview`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) throw new Error(`Server returned ${response.status}`)
    // try to read JSON reply and persist it for the feedback page
    const data = await response.json().catch(() => null)
    if (data) {
      try { localStorage.setItem('lastAnalysis', JSON.stringify(data)) } catch (e) { console.warn('Could not save analysis to localStorage', e) }
    }
    router.push('/feedback')
  } catch (error) {
    recordingError.value = 'Upload failed: ' + error.message
    console.error('Upload Error:', error)
  } finally {
    isUploading.value = false
    isRecording.value = false
    interviewStage.value = 'ready-to-listen'
  }
}

async function handleActionClick() {
  if (isUploading.value) return

  if (interviewStage.value === 'ready-to-listen') {
    await readQuestion()
    return
  }

  if (interviewStage.value === 'ready-to-record') {
    startRecording()
    return
  }

  if (interviewStage.value === 'recording') {
    await uploadRecording()
  }
}

onMounted(startCamera)
onBeforeUnmount(() => {
  cleanupQuestionAudio()
  mediaStream?.getTracks().forEach(track => track.stop())
})
</script>

<template>
  <main class="min-h-screen bg-[#06111e] text-slate-100 p-8">
    <video ref="videoElement" autoplay muted playsinline class="w-full max-w-2xl mx-auto rounded-lg shadow-xl" />
    <div class="mt-8 text-center">
      <Button @click="handleActionClick" :disabled="isUploading || interviewStage === 'reading-question'" class="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-full">
        {{ actionLabel }}
      </Button>
      <p class="mt-4 text-rose-400">{{ recordingError }}</p>
      <p class="mt-2 text-slate-400">{{ actionMessage }}</p>
    </div>
  </main>
</template>