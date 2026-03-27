<template>
  <div class="komatsu-wordle">
    <div class="header">
      <h1>KOMATSU-LE</h1>
      <p>Guess the Komatsu term</p>
    </div>

    <!-- Category Tabs -->
    <div class="tabs">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="tab"
        :class="{ active: currentCategory === cat.id }"
        @click="switchCategory(cat.id)"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- Game Area -->
    <div class="game-wrapper">

      <!-- Reveal Overlay -->
      <transition name="fade">
        <div v-if="gameOver" class="reveal-overlay" @click.self="startNewGame">
          <div class="reveal-card">
            <div class="reveal-emoji">{{ won ? '🎉' : '💡' }}</div>
            <div class="reveal-outcome" :class="won ? 'win' : 'lose'">
              {{ won ? 'You got it!' : 'Better luck next time' }}
            </div>
            <div class="reveal-word">{{ target }}</div>
            <div class="reveal-category">{{ currentCategoryLabel }}</div>
            <hr class="reveal-divider" />
            <div class="reveal-def-label">What is it?</div>
            <div class="reveal-def">{{ currentDef }}</div>
            <div class="reveal-guesses">
              {{ won
                ? `Solved in ${guesses.length} of ${maxGuesses} guess${guesses.length === 1 ? '' : 'es'}`
                : `You used all ${maxGuesses} guesses`
              }}
            </div>
            <button class="reveal-btn" @click="startNewGame">Play again</button>
          </div>
        </div>
      </transition>

      <!-- Hint -->
      <div class="length-hint">
        <span class="hint-tag">{{ target.length }}-letter word</span>
        &nbsp;Hint: {{ currentHint }}
      </div>

      <!-- Message -->
      <div class="message" :class="messageClass">{{ message }}</div>

      <!-- Grid -->
      <div class="grid">
        <div v-for="rowIndex in maxGuesses" :key="rowIndex" class="row">
          <div
            v-for="colIndex in target.length"
            :key="colIndex"
            class="cell"
            :class="getCellClass(rowIndex - 1, colIndex - 1)"
          >
            {{ getCellLetter(rowIndex - 1, colIndex - 1) }}
          </div>
        </div>
      </div>

      <!-- Keyboard -->
      <div class="keyboard">
        <div v-for="(row, i) in keyboardRows" :key="i" class="kb-row">
          <button
            v-for="key in row"
            :key="key"
            class="key"
            :class="[key.length > 1 ? 'wide' : '', keyStates[key] || '']"
            @click="pressKey(key)"
          >
            {{ key === 'DEL' ? '←' : key }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
const WORDS = {
  models: [
    { word: 'DUMP', hint: 'Off-highway hauler type', def: 'A dump truck is an off-highway rigid or articulated hauler used to transport loose materials like rock, ore, or overburden on mine sites and large construction projects.' },
    { word: 'DOZER', hint: 'Blade-pushing machine', def: 'A bulldozer is a crawler-tracked machine fitted with a large front blade used to push soil, sand, rubble, or other material during grading and earthmoving work.' },
    { word: 'GRADER', hint: 'Road surface leveler', def: 'A motor grader is a long-bladed machine used to create a flat surface during grading. It is commonly used to finish grade roads and maintain unpaved haul roads on construction and mining sites.' },
    { word: 'LOADER', hint: 'Bucket lifting machine', def: 'A wheel loader is a front-end machine with a large bucket used to scoop and transport loose material such as dirt, gravel, and crushed stone around a job site.' },
    { word: 'MINING', hint: 'Excavation industry', def: 'Mining is the extraction of valuable minerals or materials from the earth. Komatsu produces a wide range of ultra-class equipment specifically engineered for the demands of surface and underground mining operations.' },
    { word: 'RIGID', hint: 'Non-articulated frame truck', def: 'A rigid dump truck has a single fixed chassis frame. Komatsu rigid trucks like the 930E are among the largest haul trucks in the world, used in ultra-class mining.' },
    { word: 'HYBRID', hint: 'Dual power system machine', def: 'A hybrid machine uses two power sources — typically a diesel engine combined with an electric motor and energy storage — to reduce fuel consumption and lower emissions.' },
    { word: 'CRAWLER', hint: 'Track-type base machine', def: 'A crawler is any machine that moves on continuous tracks rather than wheels, providing superior traction and ground pressure distribution on soft or uneven terrain.' },
    { word: 'BACKHOE', hint: 'Rear digging excavator', def: 'A backhoe loader has a digging bucket on the rear and a loader bucket on the front. It is a versatile machine used across construction, utility, and landscaping applications.' },
    { word: 'HAULER', hint: 'Material transport machine', def: 'A hauler transports excavated material from the digging face to a dump location. Komatsu produces both rigid and articulated haulers for a range of site conditions and payloads.' },
    { word: 'SCRAPER', hint: 'Earth-moving bowl machine', def: 'A scraper is an earthmoving machine with a front cutting blade and a bowl that collects, hauls, and deposits soil in a single pass. Used for large-scale grading and fill projects.' },
    { word: 'EXCAVATOR', hint: 'Boom and bucket digger', def: 'An excavator is a tracked or wheeled machine with a hydraulic boom, stick, and bucket used for digging trenches, foundations, and mines.' },
    { word: 'COMPACTOR', hint: 'Ground densification machine', def: 'A compactor applies force to the ground to increase its density and load-bearing capacity. Used in road construction and earthworks to achieve specified compaction standards.' },
  ],
  parts: [
    { word: 'BOOM', hint: 'Upper arm of an excavator', def: 'The boom is the primary structural arm of an excavator, attached to the upper frame. It lifts and positions the stick and bucket over the digging area.' },
    { word: 'BLADE', hint: 'Dozer pushing attachment', def: 'The blade is the large steel plate at the front of a bulldozer or grader used to push, cut, and level material. Types include straight, angle, universal, and semi-universal.' },
    { word: 'RIPPER', hint: 'Ground-breaking rear attachment', def: 'A ripper is a rear-mounted attachment on a bulldozer with hardened steel shanks used to break up hard rock, frozen ground, or compacted material before pushing or loading.' },
    { word: 'BUCKET', hint: 'Digging and carrying cup', def: 'The bucket is the primary digging and carrying attachment on excavators and loaders. Configurations include general purpose, rock, ditch cleaning, and high-capacity designs.' },
    { word: 'SPROCKET', hint: 'Track drive toothed wheel', def: 'The sprocket is a toothed drive wheel at the rear of a crawler undercarriage that meshes with the track links to propel the machine forward.' },
    { word: 'IDLER', hint: 'Front track guide wheel', def: 'The idler is the unpowered front wheel of a crawler undercarriage that guides and maintains tension in the track chain, working with the track adjuster to keep it taut.' },
    { word: 'AUGER', hint: 'Spiral soil drilling bit', def: 'An auger is a helical screw attachment used to drill holes into the ground for fence posts, foundations, or utility poles. Commonly mounted to excavators or skid steers.' },
    { word: 'ROLLER', hint: 'Track bottom contact wheel', def: 'Track rollers are the small wheels along the bottom of a crawler undercarriage that support the machine weight and guide the track along the ground.' },
    { word: 'DIPPER', hint: 'Stick and bucket arm', def: 'The dipper (or stick) is the second arm segment of an excavator, connecting the boom to the bucket. It controls the reach and depth during digging operations.' },
    { word: 'COUPLER', hint: 'Quick attachment mount system', def: 'A quick coupler allows an operator to change attachments such as buckets, hammers, and grapples without leaving the cab, improving versatility and reducing downtime.' },
    { word: 'GRAPPLE', hint: 'Clamping grab attachment', def: 'A grapple is a claw-like attachment used to grab, sort, and move irregular materials such as logs, scrap metal, or demolition debris.' },
    { word: 'LINKAGE', hint: 'Mechanical connection assembly', def: 'Linkage refers to the system of mechanical arms and pivot points that connect and control attachments. On a wheel loader, the Z-bar or parallel linkage determines how the bucket tilts during lifting.' },
    { word: 'HYDRAULIC', hint: 'Fluid power system type', def: 'Hydraulic systems use pressurized fluid to transmit power to actuators such as cylinders and motors. Nearly all functions on modern Komatsu machines are hydraulically controlled.' },
    { word: 'UNDERCARRIAGE', hint: 'Track frame and rollers', def: 'The undercarriage is the complete lower assembly of a crawler machine, including the track frames, track chains, rollers, idlers, and sprockets. It is the most maintenance-intensive wear system on any tracked machine.' },
  ]
}

export default {
  name: 'KomatsuWordle',

  data() {
    return {
      currentCategory: 'models',
      categories: [
        { id: 'models', label: 'Machine models' },
        { id: 'parts', label: 'Parts & components' },
      ],
      keyboardRows: [
        ['Q','W','E','R','T','Y','U','I','O','P'],
        ['A','S','D','F','G','H','J','K','L'],
        ['ENTER','Z','X','C','V','B','N','M','DEL'],
      ],
      maxGuesses: 6,
      target: '',
      currentHint: '',
      currentDef: '',
      guesses: [],
      currentGuess: '',
      gameOver: false,
      won: false,
      keyStates: {},
      message: '',
      messageClass: '',
    }
  },

  computed: {
    currentCategoryLabel() {
      return this.currentCategory === 'models' ? 'Machine model' : 'Part & component'
    },
  },

  mounted() {
    this.startNewGame()
    window.addEventListener('keydown', this.handleKeydown)
  },

  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeydown)
  },

  methods: {
    pickWord() {
      const list = WORDS[this.currentCategory]
      const entry = list[Math.floor(Math.random() * list.length)]
      this.target = entry.word
      this.currentHint = entry.hint
      this.currentDef = entry.def
    },

    startNewGame() {
      this.pickWord()
      this.guesses = []
      this.currentGuess = ''
      this.gameOver = false
      this.won = false
      this.keyStates = {}
      this.message = ''
      this.messageClass = ''
    },

    switchCategory(cat) {
      this.currentCategory = cat
      this.startNewGame()
    },

    handleKeydown(e) {
      if (e.key === 'Enter') this.pressKey('ENTER')
      else if (e.key === 'Backspace') this.pressKey('DEL')
      else if (/^[a-zA-Z]$/.test(e.key)) this.pressKey(e.key.toUpperCase())
    },

    pressKey(key) {
      if (this.gameOver) return
      if (key === 'ENTER') { this.submitGuess(); return }
      if (key === 'DEL') { this.currentGuess = this.currentGuess.slice(0, -1); return }
      if (this.currentGuess.length < this.target.length && /^[A-Z]$/.test(key)) {
        this.currentGuess += key
      }
    },

    submitGuess() {
      if (this.currentGuess.length !== this.target.length) {
        this.message = `Word must be ${this.target.length} letters!`
        this.messageClass = ''
        return
      }
      const result = this.evalGuess(this.currentGuess)
      this.guesses.push({ word: this.currentGuess, result })

      const priority = { correct: 3, present: 2, absent: 1 }
      result.forEach((r, i) => {
        const letter = this.currentGuess[i]
        if (!this.keyStates[letter] || priority[r] > priority[this.keyStates[letter]]) {
          this.keyStates[letter] = r
        }
      })

      this.message = ''
      this.currentGuess = ''

      if (result.every(r => r === 'correct')) {
        this.won = true
        setTimeout(() => { this.gameOver = true }, 400)
      } else if (this.guesses.length >= this.maxGuesses) {
        setTimeout(() => { this.gameOver = true }, 400)
      }
    },

    evalGuess(guess) {
      const result = Array(this.target.length).fill('absent')
      const tArr = this.target.split('')
      const used = Array(this.target.length).fill(false)
      for (let i = 0; i < this.target.length; i++) {
        if (guess[i] === tArr[i]) { result[i] = 'correct'; used[i] = true }
      }
      for (let i = 0; i < this.target.length; i++) {
        if (result[i] === 'correct') continue
        for (let j = 0; j < this.target.length; j++) {
          if (!used[j] && guess[i] === tArr[j]) { result[i] = 'present'; used[j] = true; break }
        }
      }
      return result
    },

    getCellLetter(rowIndex, colIndex) {
      if (rowIndex < this.guesses.length) {
        return this.guesses[rowIndex].word[colIndex] || ''
      } else if (rowIndex === this.guesses.length) {
        return this.currentGuess[colIndex] || ''
      }
      return ''
    },

    getCellClass(rowIndex, colIndex) {
      const classes = []
      if (rowIndex < this.guesses.length) {
        classes.push(this.guesses[rowIndex].result[colIndex])
        if (this.guesses[rowIndex].word[colIndex]) classes.push('filled')
      } else if (rowIndex === this.guesses.length && this.currentGuess[colIndex]) {
        classes.push('filled')
      }
      return classes
    },
  },
}
</script>

<style scoped>
.komatsu-wordle {
  max-width: 520px;
  margin: 0 auto;
  padding: 2rem 1rem;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 1.25rem;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 3px;
  color: var(--color-heading, #111);
  margin: 0;
}

.header p {
  font-size: 13px;
  color: #888;
  margin-top: 4px;
}

.tabs {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.tab {
  padding: 6px 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: transparent;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.tab.active {
  background: #1D9E75;
  border-color: #1D9E75;
  color: #fff;
  font-weight: 500;
}

.tab:hover:not(.active) {
  background: #f5f5f5;
}

.game-wrapper {
  position: relative;
}

/* Reveal overlay */
.reveal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
}

.reveal-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e5e5;
  padding: 2rem 1.75rem;
  max-width: 320px;
  width: 90%;
  text-align: center;
}

.reveal-emoji {
  font-size: 36px;
  margin-bottom: 0.75rem;
}

.reveal-outcome {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.reveal-outcome.win { color: #0F6E56; }
.reveal-outcome.lose { color: #993C1D; }

.reveal-word {
  font-size: 26px;
  font-weight: 600;
  letter-spacing: 4px;
  color: #111;
  margin-bottom: 0.2rem;
}

.reveal-category {
  font-size: 11px;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 1.25rem;
}

.reveal-divider {
  border: none;
  border-top: 1px solid #eee;
  margin-bottom: 1.25rem;
}

.reveal-def-label {
  font-size: 11px;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 0.4rem;
}

.reveal-def {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 1.25rem;
  text-align: left;
}

.reveal-guesses {
  font-size: 12px;
  color: #888;
  margin-bottom: 1.25rem;
}

.reveal-btn {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: none;
  background: #1D9E75;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.reveal-btn:hover { background: #0F6E56; }

/* Hint */
.length-hint {
  text-align: center;
  font-size: 12px;
  color: #888;
  margin-bottom: 1rem;
}

.hint-tag {
  display: inline-block;
  font-size: 11px;
  background: #e8f4fd;
  color: #185FA5;
  border-radius: 6px;
  padding: 2px 8px;
}

/* Message */
.message {
  text-align: center;
  font-size: 14px;
  min-height: 20px;
  color: #888;
  margin-bottom: 0.75rem;
}

/* Grid */
.grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin-bottom: 1.25rem;
}

.row {
  display: flex;
  gap: 6px;
}

.cell {
  width: 48px;
  height: 48px;
  border: 1px solid #ddd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  text-transform: uppercase;
  color: #111;
  transition: background 0.2s, border-color 0.2s;
}

.cell.filled { border-color: #999; }
.cell.correct { background: #1D9E75; border-color: #1D9E75; color: #fff; }
.cell.present { background: #BA7517; border-color: #BA7517; color: #fff; }
.cell.absent  { background: #ccc;    border-color: transparent; color: #555; }

/* Keyboard */
.keyboard {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.kb-row {
  display: flex;
  gap: 5px;
}

.key {
  min-width: 34px;
  height: 42px;
  padding: 0 6px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: #f0f0f0;
  color: #111;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  text-transform: uppercase;
}

.key.wide { min-width: 54px; font-size: 11px; }
.key:hover { background: #e0e0e0; }
.key.correct { background: #1D9E75; border-color: #1D9E75; color: #fff; }
.key.present { background: #BA7517; border-color: #BA7517; color: #fff; }
.key.absent  { background: #aaa;    border-color: transparent; color: #fff; }

/* Transition */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .header h1 { color: #f0f0f0; }
  .reveal-card { background: #1e1e1e; border-color: #333; }
  .reveal-word { color: #f0f0f0; }
  .reveal-def  { color: #ccc; }
  .tab:hover:not(.active) { background: #2a2a2a; }
  .cell { border-color: #444; color: #f0f0f0; }
  .cell.filled { border-color: #777; }
  .cell.absent { background: #555; color: #ccc; }
  .key  { background: #2a2a2a; border-color: #444; color: #f0f0f0; }
  .key:hover { background: #333; }
  .key.absent { background: #555; }
}
</style>