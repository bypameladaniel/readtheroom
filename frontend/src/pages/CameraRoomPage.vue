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
const isAudioPlaying = ref(false)

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
  isAudioPlaying.value = false
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
      isAudioPlaying.value = true
      questionAudio.onended = () => {
        isAudioPlaying.value = false
        resolve()
      }
      questionAudio.onerror = () => {
        isAudioPlaying.value = false
        reject(new Error('Could not play the question audio.'))
      }
      questionAudio.play().catch(err => {
        isAudioPlaying.value = false
        reject(err)
      })
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

  mediaRecorder.stop()

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

  // Helper to POST and save result to localStorage under a given key
  const postAndStore = async (url, key) => {
    const response = await fetch(url, { method: 'POST', body: formData })
    if (!response.ok) throw new Error(`Server returned ${response.status}`)
    const data = await response.json().catch(() => null)
    if (data) {
      try { localStorage.setItem(key, JSON.stringify(data)) } catch (e) { console.warn(`Could not save ${key} to localStorage`, e) }
    }
    return data
  }

  try {
    localStorage.removeItem('lastAnalysis')
    localStorage.removeItem('expressionsAnalysis')

    const audioPromise = postAndStore(`${apiBaseUrl}/questions/analyze-interview`, 'lastAnalysis')
    const expressionsPromise = postAndStore(`${apiBaseUrl}/analyze/expressions`, 'expressionsAnalysis')

    await audioPromise
    router.push('/feedback')

    expressionsPromise.catch((error) => {
      console.error('Background request failed:', error)
    })

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
    <div class="flex flex-col md:flex-row gap-6 items-start justify-center max-w-5xl mx-auto">
      <div class="w-full md:w-2/3">
        <video ref="videoElement" autoplay muted playsinline class="w-full rounded-lg shadow-xl" />
      </div>

      <aside class="w-full md:w-1/3">
        <Card>
          <CardContent class="p-6 flex flex-col items-center gap-4">
            <div class="w-48 h-48 flex items-center justify-center">
              <div :class="['shape', isAudioPlaying ? 'playing' : 'idle']" aria-hidden="true"></div>
            </div>
            <div class="mt-4 w-full text-center">
              <Button @click="handleActionClick" :disabled="isUploading || interviewStage === 'reading-question'" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-full">
                {{ actionLabel }}
              </Button>
            </div>
            <p class="mt-3 text-rose-400">{{ recordingError }}</p>
            <p class="mt-2 text-slate-400 text-center">{{ actionMessage }}</p>
          </CardContent>
        </Card>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.shape {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #7dd3fc 0%, #60a5fa 50%, #a78bfa 100%);
  transition: all 400ms cubic-bezier(.2,.9,.2,1);
  will-change: border-radius, transform, clip-path;
  box-shadow: 0 8px 24px rgba(2,6,23,0.6);
}
.shape.idle {
  border-radius: 16px;
  transform: rotate(0deg) scale(1);
  clip-path: polygon(10% 10%, 90% 10%, 90% 90%, 10% 90%);
}
.shape.playing {
  border-radius: 9999px;
  transform: rotate(12deg) scale(1.08);
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
}

/* subtle pulsing while playing */
.shape.playing {
  animation: pulse 900ms ease-in-out infinite;
}

@keyframes pulse {
  0% { transform: rotate(12deg) scale(1.03); }
  50% { transform: rotate(12deg) scale(1.12); }
  100% { transform: rotate(12deg) scale(1.03); }
}
</style>