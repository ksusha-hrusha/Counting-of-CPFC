<template>
  <!-- Кнопка-триггер -->
  <button class="btn btn-scale-trigger" :class="{ connected: isConnected }" @click="open" type="button">
    <ScaleIcon style="width:16px;height:16px;" />
    <span>{{ isConnected ? `${currentWeight} г` : 'Весы' }}</span>
    <span v-if="isConnected" class="dot-live"></span>
  </button>

  <!-- Модальное окно -->
  <Teleport to="body">
    <div v-if="showModal" class="scale-overlay" @click.self="close">
      <div class="scale-modal">
        <div class="scale-modal-header">
          <span>Умные весы</span>
          <button class="close-btn" @click="close">✕</button>
        </div>

        <!-- Не подключено -->
        <template v-if="!isConnected && !connecting">
          <div class="scale-idle">
            <svg class="scale-icon-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3v18M8 21h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M5 8l-3 5h6L5 8z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
              <path d="M19 8l-3 5h6l-3-5z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
              <path d="M5 8h14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <p class="scale-desc">
              Подключите весы к Wi-Fi и положите продукт.<br>
              Нажмите кнопку ниже — вес появится автоматически.
            </p>
            <button class="btn btn-primary" @click="connect">Подключить</button>
          </div>
        </template>

        <!-- Подключение... -->
        <template v-else-if="connecting">
          <div class="scale-idle">
            <div class="scale-spinner"></div>
            <p class="scale-desc">Ищем весы...</p>
            <button class="btn btn-outline" @click="cancelConnect">Отмена</button>
          </div>
        </template>

        <!-- Ошибка -->
        <template v-else-if="connectError">
          <div class="scale-idle">
            <svg class="scale-icon-svg scale-icon-error" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3v18M8 21h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M5 8l-3 5h6L5 8z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
              <path d="M19 8l-3 5h6l-3-5z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
              <path d="M5 8h14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <p class="scale-desc">Не удалось найти весы.<br>Убедитесь что весы включены и подключены к Wi-Fi.</p>
            <button class="btn btn-primary" @click="connect">Попробовать снова</button>
          </div>
        </template>

        <!-- Подключено — живой вес -->
        <template v-else-if="isConnected">
          <div class="scale-live-block">
            <div class="scale-weight-display">{{ currentWeight }}</div>
            <div class="scale-weight-unit">граммов</div>
          </div>
          <div class="scale-actions">
            <button class="btn btn-primary" @click="applyAndClose">
              Применить {{ currentWeight }} г
            </button>
            <button class="btn btn-outline" @click="disconnect">Отключить</button>
          </div>
        </template>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { ScaleIcon } from '@heroicons/vue/24/outline'
import { io } from 'socket.io-client'

const emit = defineEmits(['apply'])

const showModal = ref(false)
const connecting = ref(false)
const connectError = ref(false)
const isConnected = ref(false)
const currentWeight = ref(0)

let socket = null

function open() {
  showModal.value = true
  connectError.value = false
}

function close() { showModal.value = false }

function connect() {
  connecting.value = true
  connectError.value = false

  // Всегда подключаемся к тому же серверу что и сайт
  const url = window.location.origin

  socket = io(url, {
    transports: ['websocket'],
    timeout: 6000,
    reconnection: false,
  })

  socket.on('connect', () => {
    connecting.value = false
    isConnected.value = true
  })

  socket.on('connect_error', () => {
    connecting.value = false
    connectError.value = true
    socket?.disconnect()
    socket = null
  })

  socket.on('disconnect', () => {
    isConnected.value = false
    currentWeight.value = 0
  })

  socket.on('weight_update', (data) => {
    currentWeight.value = data.weight
  })
}

function cancelConnect() {
  socket?.disconnect()
  socket = null
  connecting.value = false
}

function disconnect() {
  socket?.disconnect()
  socket = null
  isConnected.value = false
  currentWeight.value = 0
}

function applyAndClose() {
  emit('apply', currentWeight.value)
  close()
}

onUnmounted(() => { socket?.disconnect() })
</script>

<style scoped>
.btn-scale-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-soft, #f5f5f5);
  border: 1.5px solid var(--border, #ddd);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-mid, #888);
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
  flex-shrink: 0;
}
.btn-scale-trigger.connected {
  border-color: var(--primary, #7c3aed);
  color: var(--primary, #7c3aed);
  background: var(--bg-accent, #f3eeff);
}
.dot-live {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  animation: pulse 1.5s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.scale-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.scale-modal {
  background: var(--bg-card, #fff);
  border-radius: 16px;
  padding: 28px;
  width: 340px;
  max-width: 90vw;
  box-shadow: 0 8px 40px rgba(0,0,0,0.18);
}
.scale-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-dark);
  margin-bottom: 20px;
}
.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--text-mid, #888);
  padding: 2px 6px;
}

/* Idle / error состояние */
.scale-idle {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 10px 0 4px;
}
.scale-icon-big { font-size: 48px; }
.scale-icon-svg {
  width: 52px;
  height: 52px;
  color: var(--primary, #7c3aed);
  opacity: 0.85;
}
.scale-icon-error {
  color: #f87171;
}
.scale-desc {
  font-size: 14px;
  color: var(--text-mid, #888);
  text-align: center;
  line-height: 1.5;
  margin: 0;
}

/* Спиннер */
.scale-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--bg-soft, #f0f0f0);
  border-top-color: var(--primary, #7c3aed);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Живой вес */
.scale-live-block {
  text-align: center;
  padding: 20px 0 12px;
}
.scale-weight-display {
  font-size: 72px;
  font-weight: 800;
  color: var(--primary, #7c3aed);
  line-height: 1;
}
.scale-weight-unit {
  font-size: 14px;
  color: var(--text-mid, #888);
  margin-top: 4px;
}
.scale-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}
.scale-actions .btn { flex: 1; }
</style>
