<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const motionStates = [
  { x: '24%', y: '28%', rotate: '-8deg', scale: 0.92, label: 'Top left' },
  { x: '72%', y: '30%', rotate: '10deg', scale: 1, label: 'Top right' },
  { x: '68%', y: '74%', rotate: '-4deg', scale: 1.08, label: 'Bottom right' },
  { x: '30%', y: '72%', rotate: '6deg', scale: 0.98, label: 'Bottom left' },
]

const activeStateIndex = ref(0)
const cameraReady = ref(false)
const cameraError = ref('')
const videoElement = ref(null)

let mediaStream = null

const activeState = computed(() => motionStates[activeStateIndex.value])

const shapeStyle = computed(() => ({
  left: activeState.value.x,
  top: activeState.value.y,
  transform: `translate(-50%, -50%) rotate(${activeState.value.rotate}) scale(${activeState.value.scale})`,
}))

async function startCamera() {
  cameraError.value = ''

  if (!navigator.mediaDevices?.getUserMedia) {
    cameraError.value = 'This browser does not expose a camera API.'
    return
  }

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'user',
      },
      audio: false,
    })

    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
    }

    cameraReady.value = true
  } catch (error) {
    cameraError.value = 'Camera access is blocked or unavailable.'
    console.error(error)
  }
}

function triggerMotion() {
  activeStateIndex.value = (activeStateIndex.value + 1) % motionStates.length
}

onMounted(() => {
  startCamera()
})

onBeforeUnmount(() => {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    mediaStream = null
  }
})
</script>

<template>
  <main class="min-h-screen bg-[#06111e] text-slate-100">
    <div class="grid min-h-screen lg:grid-cols-2">
      <section class="relative overflow-hidden border-b border-white/10 lg:border-b-0 lg:border-r">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.18),_transparent_35%),radial-gradient(circle_at_bottom_right,_rgba(251,191,36,0.14),_transparent_32%),linear-gradient(160deg,_#07111f,_#04070f)]" />
        <div class="absolute inset-0 opacity-30 [background-image:linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.06)_1px,transparent_1px)] [background-size:2.5rem_2.5rem]" />

        <Card class="relative flex h-full min-h-[50vh] flex-col rounded-none border-0 bg-transparent shadow-none backdrop-blur-none">
          <CardContent class="flex flex-1 items-center justify-center px-6 py-6 sm:px-8">
            <div class="relative h-full w-full overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/70 shadow-[0_30px_80px_-40px_rgba(8,145,178,0.55)] backdrop-blur-sm">
              <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(34,211,238,0.12),_transparent_42%),linear-gradient(180deg,_rgba(15,23,42,0.98),_rgba(3,7,18,0.98))]" />
              <div class="absolute inset-0 opacity-25 [background-image:radial-gradient(circle,_rgba(255,255,255,0.28)_1px,transparent_1px)] [background-size:1.25rem_1.25rem]" />

              <div class="absolute left-1/2 top-1/2 h-40 w-40 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-300/20 bg-cyan-300/10 blur-2xl" />
              <div
                class="absolute h-28 w-28 rounded-[1.8rem] border border-cyan-200/30 bg-gradient-to-br from-cyan-300 via-sky-400 to-indigo-500 shadow-[0_0_50px_rgba(34,211,238,0.35)] transition-[left,top,transform] duration-700 ease-[cubic-bezier(0.16,1,0.3,1)]"
                :style="shapeStyle"
              />
            </div>
          </CardContent>
        </Card>
      </section>

      <section class="relative overflow-hidden bg-slate-950">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.14),_transparent_32%),linear-gradient(180deg,_#020617,_#0f172a)]" />

        <Card class="relative flex h-full min-h-[50vh] flex-col rounded-none border-0 bg-transparent shadow-none backdrop-blur-none">
          <CardContent class="flex flex-1 items-center justify-center px-6 py-6 sm:px-8">
            <div class="relative h-full w-full overflow-hidden rounded-[2rem] border border-white/10 bg-black shadow-[0_30px_90px_-35px_rgba(15,23,42,0.9)]">
              <video
                ref="videoElement"
                autoplay
                muted
                playsinline
                class="h-full w-full object-cover [transform:scaleX(-1)]"
              />

              <div
                v-if="cameraError"
                class="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-950/90 px-6 text-center"
              >
                <div class="rounded-full border border-rose-400/20 bg-rose-500/10 px-4 py-2 text-sm font-medium text-rose-200">
                  Camera unavailable
                </div>
                <p class="max-w-md text-sm leading-6 text-slate-300">
                  {{ cameraError }}
                </p>
              </div>

              <div
                v-else-if="!cameraReady"
                class="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-950/85 px-6 text-center"
              >
                <div class="rounded-full border border-cyan-400/20 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-100">
                  Starting camera
                </div>
                <p class="max-w-md text-sm leading-6 text-slate-300">
                  Waiting for the browser to grant video access.
                </p>
              </div>

              <div class="absolute bottom-6 left-1/2 -translate-x-1/2">
                <Button
                  as-child
                  size="lg"
                  class="group relative overflow-hidden rounded-full border border-cyan-300/30 bg-gradient-to-r from-cyan-400 via-sky-500 to-indigo-600 px-7 text-white shadow-[0_18px_44px_-18px_rgba(14,165,233,0.75)] transition-all duration-300 ease-out hover:-translate-y-0.5 hover:scale-[1.03] hover:shadow-[0_24px_56px_-18px_rgba(14,165,233,0.9)] active:translate-y-0 active:scale-95"
                >
                  <RouterLink to="/feedback">Done</RouterLink>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  </main>
</template>