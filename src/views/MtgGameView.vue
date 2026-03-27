<template>
  <div class="mtg-game">
    <h1 class="game-title">MTG Art Game</h1>

    <!-- TAB BAR -->
    <div class="tab-bar">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'game' }"
        @click="activeTab = 'game'"
      >Game</button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'stats' }"
        @click="activeTab = 'stats'"
      >Stats</button>
    </div>

    <!-- STATS TAB -->
    <div v-if="activeTab === 'stats'">
      <div v-if="!stats" class="status-msg">Loading stats…</div>
      <div v-else class="stats-panel">
        <p class="stats-meta">
          {{ stats.total_cards.toLocaleString() }} eligible cards &mdash;
          data from {{ new Date(stats.generated_at).toLocaleDateString() }}
        </p>

        <h3 class="stats-heading">Color Identity</h3>
        <div class="bar-chart">
          <div v-for="[label, key, cls] in colorRows" :key="key" class="bar-row">
            <span class="bar-label">{{ label }}</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :class="cls"
                :style="{ width: pct(stats.color_distribution[key], colorMax) }"
              ></div>
            </div>
            <span class="bar-value">{{ stats.color_distribution[key].toLocaleString() }}</span>
          </div>
        </div>

        <h3 class="stats-heading">Card Type</h3>
        <div class="bar-chart">
          <div v-for="[label, key] in typeRows" :key="key" class="bar-row">
            <span class="bar-label">{{ label }}</span>
            <div class="bar-track">
              <div
                class="bar-fill bar-type"
                :style="{ width: pct(stats.type_distribution[key], typeMax) }"
              ></div>
            </div>
            <span class="bar-value">{{ stats.type_distribution[key].toLocaleString() }}</span>
          </div>
        </div>

        <h3 class="stats-heading">Rarity</h3>
        <div class="bar-chart">
          <div v-for="[label, key, cls] in rarityRows" :key="key" class="bar-row">
            <span class="bar-label">{{ label }}</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :class="cls"
                :style="{ width: pct(stats.rarity_distribution[key], rarityMax) }"
              ></div>
            </div>
            <span class="bar-value">{{ stats.rarity_distribution[key].toLocaleString() }}</span>
          </div>
        </div>

        <h3 class="stats-heading">Top Sets by Card Count</h3>
        <div class="bar-chart">
          <div v-for="s in stats.top_sets" :key="s.set_code" class="bar-row">
            <span class="bar-label bar-label--set" :title="s.set_name">{{ s.set_code.toUpperCase() }}</span>
            <div class="bar-track">
              <div
                class="bar-fill bar-type"
                :style="{ width: pct(s.count, stats.top_sets[0].count) }"
              ></div>
            </div>
            <span class="bar-value">{{ s.count.toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- GAME TAB -->
    <div v-else>
    <p class="game-subtitle">Drag each card name onto its art.</p>

    <!-- LOADING DATA -->
    <div v-if="phase === 'loading_data'" class="status-msg">Loading game data…</div>

    <!-- LANDING -->
    <div v-else-if="phase === 'landing'">
      <div class="landing-card">
        <label for="cardType">Card type</label>
        <select id="cardType" v-model="cardType">
          <option value="">Any</option>
          <option value="Creature">Creature</option>
          <option value="Instant">Instant</option>
          <option value="Sorcery">Sorcery</option>
          <option value="Enchantment">Enchantment</option>
          <option value="Artifact">Artifact</option>
          <option value="Planeswalker">Planeswalker</option>
        </select>

        <label for="cardColor">Color</label>
        <select id="cardColor" v-model="cardColor">
          <option value="">Any</option>
          <option value="W">White</option>
          <option value="U">Blue</option>
          <option value="B">Black</option>
          <option value="R">Red</option>
          <option value="G">Green</option>
        </select>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <button class="btn btn-primary" @click="startGame">Play</button>
      </div>
    </div>

    <!-- LOADING BOARD -->
    <div v-else-if="phase === 'loading'" class="status-msg">Loading…</div>

    <!-- PLAYING -->
    <div v-else-if="phase === 'playing'">
      <div class="game-header">
        <div>
          <div class="tray-label">Guesses left</div>
          <div class="guess-tracker">
            <div
              v-for="n in [1,2,3,4]"
              :key="n"
              class="guess-pip"
              :class="{ used: n > guessesLeft }"
            ></div>
          </div>
        </div>

        <div class="guess-history">
          <div v-for="(round, ri) in guessHistory" :key="ri" class="history-row">
            <div
              v-for="(color, ci) in round"
              :key="ci"
              class="history-sq"
              :class="color"
            ></div>
          </div>
        </div>

        <button
          class="btn btn-primary btn-submit"
          @click="submitGuess"
          :disabled="!canSubmit"
        >Submit</button>
      </div>

      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

      <!-- Photo grid -->
      <div class="photo-grid">
        <div
          v-for="photo in photos"
          :key="photo.card_id"
          class="photo-slot"
          :class="{
            'drag-over': dragOverPhoto === photo.card_id && !isLocked(photo.card_id),
            'locked': isLocked(photo.card_id)
          }"
          @dragover.prevent
          @dragenter.prevent="dragOverPhoto = photo.card_id"
          @dragleave="dragOverPhoto = null"
          @drop="onDropOnPhoto($event, photo.card_id)"
        >
          <img :src="photo.photo_url" alt="MTG card art">

          <div
            v-if="placements[photo.card_id]"
            class="chip-on-photo"
            :class="[results[photo.card_id] || '', isLocked(photo.card_id) ? 'locked' : '']"
            :draggable="!isLocked(photo.card_id)"
            @dragstart="onDragStart($event, placements[photo.card_id])"
          >{{ getChipName(placements[photo.card_id]) }}</div>
        </div>
      </div>

      <!-- Chip tray -->
      <div class="tray-label">Name chips — drag onto a card</div>
      <div
        class="chip-tray"
        :class="{ 'drag-over': dragOverTray }"
        @dragover.prevent
        @dragenter.prevent="dragOverTray = true"
        @dragleave="dragOverTray = false"
        @drop="onDropOnTray($event)"
      >
        <div
          v-for="chip in availableChips"
          :key="chip.chip_id"
          class="chip"
          draggable="true"
          @dragstart="onDragStart($event, chip.chip_id)"
        >{{ chip.name }}</div>
      </div>
    </div>

    <!-- WON -->
    <div v-else-if="phase === 'won'">
      <div class="result-panel">
        <h2>You got it!</h2>
        <p>Solved in {{ guessHistory.length }} of 4 guess{{ guessHistory.length === 1 ? '' : 'es' }}.</p>
        <button class="btn btn-primary btn-centered" @click="playAgain">Play again</button>
      </div>
    </div>

    <!-- LOST -->
    <div v-else-if="phase === 'lost'">
      <div class="result-panel">
        <h2>Better luck next time!</h2>
        <p>The correct answers were:</p>
        <div class="answers-grid">
          <div v-for="cp in correctPlacements" :key="cp.card_id" class="answer-card">
            <img :src="cp.full_card_url" :alt="cp.name">
            <div class="answer-card-name">{{ cp.name }}</div>
          </div>
        </div>
        <button class="btn btn-primary btn-centered" @click="playAgain">Play again</button>
      </div>
    </div>
    </div><!-- end game tab -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const activeTab = ref('game')
const stats = ref(null)

const colorRows = [
  ['White', 'W', 'bar-white'],
  ['Blue',  'U', 'bar-blue'],
  ['Black', 'B', 'bar-black'],
  ['Red',   'R', 'bar-red'],
  ['Green', 'G', 'bar-green'],
  ['Colorless', 'C', 'bar-colorless'],
]
const typeRows = [
  ['Creature', 'Creature'],
  ['Instant', 'Instant'],
  ['Sorcery', 'Sorcery'],
  ['Enchantment', 'Enchantment'],
  ['Artifact', 'Artifact'],
  ['Land', 'Land'],
  ['Planeswalker', 'Planeswalker'],
]
const rarityRows = [
  ['Common',   'common',   'bar-common'],
  ['Uncommon', 'uncommon', 'bar-uncommon'],
  ['Rare',     'rare',     'bar-rare'],
  ['Mythic',   'mythic',   'bar-mythic'],
]

const colorMax  = computed(() => stats.value ? Math.max(...Object.values(stats.value.color_distribution)) : 1)
const typeMax   = computed(() => stats.value ? Math.max(...Object.values(stats.value.type_distribution)) : 1)
const rarityMax = computed(() => stats.value ? Math.max(...Object.values(stats.value.rarity_distribution)) : 1)

function pct(value, max) {
  if (!max) return '0%'
  return Math.round((value / max) * 100) + '%'
}

const phase = ref('loading_data')
const allBoards = ref([])
const board = ref(null)
const photos = ref([])
const chips = ref([])
const placements = ref({})
const results = ref({})
const guessesLeft = ref(4)
const guessHistory = ref([])
const correctPlacements = ref([])
const cardType = ref('')
const cardColor = ref('')
const errorMsg = ref('')
const dragOverPhoto = ref(null)
const dragOverTray = ref(false)

onMounted(async () => {
  try {
    const [boardsResp, statsResp] = await Promise.all([
      fetch('/game-data/boards.json'),
      fetch('/game-data/stats.json'),
    ])
    allBoards.value = await boardsResp.json()
    stats.value = await statsResp.json()
  } catch (e) {
    errorMsg.value = 'Could not load game data.'
  } finally {
    phase.value = 'landing'
  }
})

const filteredBoards = computed(() => {
  return allBoards.value.filter(b => {
    if (cardType.value && !b.photos.every(p => p.type_line?.includes(cardType.value))) return false
    if (cardColor.value && !b.photos.every(p => p.color_identity?.includes(cardColor.value))) return false
    return true
  })
})

const availableChips = computed(() => {
  const placed = new Set(Object.values(placements.value))
  return chips.value.filter(c => !placed.has(c.chip_id))
})

const canSubmit = computed(() => {
  const unlocked = photos.value.filter(p => !isLocked(p.card_id))
  return unlocked.length > 0 && unlocked.every(p => p.card_id in placements.value)
})

function isLocked(cardId) {
  return results.value[cardId] === 'green'
}

function getChipName(chipId) {
  return chips.value.find(c => c.chip_id === chipId)?.name ?? ''
}

function startGame() {
  errorMsg.value = ''
  if (filteredBoards.value.length === 0) {
    errorMsg.value = 'No boards match those filters. Try different options.'
    return
  }
  const b = filteredBoards.value[Math.floor(Math.random() * filteredBoards.value.length)]
  board.value = b
  photos.value = [...b.photos].sort(() => Math.random() - 0.5)
  chips.value = [...b.name_chips].sort(() => Math.random() - 0.5)
  placements.value = {}
  results.value = {}
  guessesLeft.value = 4
  guessHistory.value = []
  correctPlacements.value = []
  phase.value = 'playing'
}

function onDragStart(event, chipId) {
  event.dataTransfer.setData('chip_id', String(chipId))
  event.dataTransfer.effectAllowed = 'move'
}

function onDropOnPhoto(event, photoCardId) {
  dragOverPhoto.value = null
  if (isLocked(photoCardId)) return
  const chipId = event.dataTransfer.getData('chip_id')
  if (!chipId) return

  const newPlacements = { ...placements.value }
  const newResults = { ...results.value }
  for (const [pid, cid] of Object.entries(newPlacements)) {
    if (cid === chipId) {
      delete newPlacements[pid]
      if (newResults[pid] !== 'green') delete newResults[pid]
      break
    }
  }
  if (newPlacements[photoCardId] && !isLocked(photoCardId)) {
    delete newResults[photoCardId]
    delete newPlacements[photoCardId]
  }
  newPlacements[photoCardId] = chipId
  placements.value = newPlacements
  results.value = newResults
}

function onDropOnTray(event) {
  dragOverTray.value = false
  const chipId = event.dataTransfer.getData('chip_id')
  if (!chipId) return
  const newPlacements = { ...placements.value }
  const newResults = { ...results.value }
  for (const [pid, cid] of Object.entries(newPlacements)) {
    if (cid === chipId && !isLocked(pid)) {
      delete newPlacements[pid]
      delete newResults[pid]
      break
    }
  }
  placements.value = newPlacements
  results.value = newResults
}

function submitGuess() {
  if (!canSubmit.value) return
  errorMsg.value = ''
  const answerSet = new Set(board.value.answer_ids)
  const newResults = { ...results.value }
  const roundColors = []

  for (const [pid, cid] of Object.entries(placements.value)) {
    if (isLocked(pid)) continue
    let result
    if (answerSet.has(cid)) {
      result = cid === pid ? 'green' : 'yellow'
    } else {
      result = 'red'
    }
    newResults[pid] = result
    roundColors.push(result)
  }

  results.value = newResults
  guessHistory.value.push(roundColors)
  guessesLeft.value--

  const greenCount = Object.values(newResults).filter(r => r === 'green').length
  if (greenCount === board.value.answer_ids.length) {
    phase.value = 'won'
  } else if (guessesLeft.value <= 0) {
    correctPlacements.value = board.value.answer_ids.map(id => ({
      card_id: id,
      name: chips.value.find(c => c.chip_id === id)?.name ?? '',
      full_card_url: board.value.photos.find(p => p.card_id === id)?.full_card_url ?? '',
    }))
    phase.value = 'lost'
  }
}

function playAgain() {
  board.value = null
  photos.value = []
  chips.value = []
  placements.value = {}
  results.value = {}
  guessesLeft.value = 4
  guessHistory.value = []
  correctPlacements.value = []
  errorMsg.value = ''
  phase.value = 'landing'
}
</script>

<style scoped>
.mtg-game {
  max-width: 860px;
  margin: 0 auto;
  padding: 20px 16px 40px;
}

.game-title {
  font-size: 2rem;
  margin-bottom: 12px;
  color: var(--accent-color);
}

/* ── TABS ── */
.tab-bar {
  display: flex;
  justify-content: center;
  gap: 4px;
  margin-bottom: 24px;
  border-bottom: 2px solid #2a2a4a;
}

.tab-btn {
  padding: 8px 22px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #888;
  cursor: pointer;
  transition: color .15s, border-color .15s;
}

.tab-btn.active {
  color: var(--accent-color);
  border-bottom-color: var(--accent-color);
}

.tab-btn:hover:not(.active) { color: var(--primary-light); }

/* ── STATS ── */
.stats-panel {
  max-width: 620px;
  margin: 0 auto;
}

.stats-meta {
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 24px;
}

.stats-heading {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: #aaa;
  margin: 24px 0 10px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bar-row {
  display: grid;
  grid-template-columns: 110px 1fr 56px;
  align-items: center;
  gap: 10px;
}

.bar-label {
  font-size: 0.85rem;
  color: var(--primary-light);
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-label--set {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: .04em;
}

.bar-track {
  background: #1a1a30;
  border-radius: 4px;
  height: 18px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width .4s ease;
}

.bar-value {
  font-size: 0.8rem;
  color: #888;
  text-align: right;
}

/* MTG color identity palette */
.bar-white      { background: #f9f3d5; }
.bar-blue       { background: #4a90d9; }
.bar-black      { background: #9b59b6; }
.bar-red        { background: #e74c3c; }
.bar-green      { background: #6aaa64; }
.bar-colorless  { background: #888; }

/* generic type/set bar */
.bar-type { background: var(--accent-color); opacity: 0.75; }

/* rarity colours */
.bar-common   { background: #aaa; }
.bar-uncommon { background: #a0c4d8; }
.bar-rare     { background: #c9a84c; }
.bar-mythic   { background: #e87a2e; }

.game-subtitle {
  color: #888;
  font-size: 0.95rem;
  margin-bottom: 28px;
}

.status-msg {
  text-align: center;
  padding: 60px 0;
  color: #666;
  font-size: 1.1rem;
}

/* ── LANDING ── */
.landing-card {
  background: var(--secondary-blue-dark);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,.3);
  padding: 32px;
  max-width: 400px;
  margin: 0 auto;
  text-align: left;
}

.landing-card label {
  display: block;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  margin-bottom: 6px;
  color: #aaa;
}

.landing-card select {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #2a2a4a;
  border-radius: 8px;
  font-size: 1rem;
  background: var(--primary-dark);
  color: var(--primary-light);
  margin-bottom: 18px;
  cursor: pointer;
}

.landing-card select:focus {
  outline: none;
  border-color: var(--accent-color);
}

.error-msg {
  color: var(--accent-color);
  font-size: 0.9rem;
  margin-bottom: 14px;
  text-align: center;
}

/* ── BUTTONS ── */
.btn {
  display: block;
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .15s, transform .1s;
}

.btn:active { transform: scale(.98); }
.btn:disabled { opacity: .4; cursor: not-allowed; transform: none; }

.btn-primary {
  background: var(--accent-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.85;
}

.btn-submit {
  width: auto;
  padding: 10px 24px;
}

.btn-centered {
  max-width: 220px;
  margin: 0 auto;
}

/* ── GAME HEADER ── */
.game-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 10px;
}

.tray-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: #888;
  margin-bottom: 6px;
}

.guess-tracker {
  display: flex;
  gap: 6px;
  align-items: center;
}

.guess-pip {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #2a2a4a;
  transition: background .2s;
}

.guess-pip.used { background: #888; }

.guess-history {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
}

.history-row { display: flex; gap: 4px; }

.history-sq {
  width: 14px;
  height: 14px;
  border-radius: 3px;
}

.history-sq.green  { background: #6aaa64; }
.history-sq.yellow { background: #c9b458; }
.history-sq.red    { background: #e74c3c; }

/* ── PHOTO GRID ── */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}

.photo-slot {
  position: relative;
  aspect-ratio: 4/3;
  border: 2px solid #2a2a4a;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: var(--primary-dark);
  transition: border-color .15s, box-shadow .15s;
}

.photo-slot.drag-over {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(255,90,95,.2);
}

.photo-slot.locked { cursor: default; }

.photo-slot img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.chip-on-photo {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 4px 6px;
  font-size: 11px;
  font-weight: 700;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: grab;
  user-select: none;
  background: rgba(2,25,39,.88);
  color: var(--primary-light);
  transition: background .2s;
}

.chip-on-photo.green  { background: #6aaa64; }
.chip-on-photo.yellow { background: #c9b458; color: #333; }
.chip-on-photo.red    { background: #e74c3c; }
.chip-on-photo.locked { cursor: default; }

/* ── CHIP TRAY ── */
.chip-tray {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 14px;
  background: var(--secondary-blue-dark);
  border-radius: 10px;
  min-height: 58px;
  margin-bottom: 14px;
  transition: background .15s;
}

.chip-tray.drag-over { background: var(--primary-dark); }

.chip {
  padding: 7px 15px;
  background: var(--primary-dark);
  border: 2px solid var(--accent-color);
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--accent-color);
  cursor: grab;
  user-select: none;
  transition: box-shadow .1s, transform .1s;
}

.chip:hover  { box-shadow: 0 2px 8px rgba(255,90,95,.3); }
.chip:active { cursor: grabbing; transform: scale(.97); }

/* ── RESULT PANELS ── */
.result-panel {
  background: var(--secondary-blue-dark);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,.3);
  padding: 28px 24px;
  text-align: center;
  margin-bottom: 20px;
}

.result-panel h2 {
  font-size: 1.6rem;
  margin-bottom: 8px;
  color: var(--accent-color);
}

.result-panel p {
  color: #888;
  margin-bottom: 20px;
}

.answers-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

@media (max-width: 520px) {
  .answers-grid { grid-template-columns: repeat(2, 1fr); }
}

.answer-card {
  border-radius: 8px;
  overflow: hidden;
  border: 3px solid #6aaa64;
}

.answer-card img {
  width: 100%;
  aspect-ratio: 5/7;
  object-fit: cover;
  display: block;
}

.answer-card-name {
  background: #6aaa64;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 6px;
  text-align: center;
}
</style>
