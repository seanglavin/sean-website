<template>
  <div class="sports-page">
    <h1 class="page-title">Sports Dashboard</h1>

    <!-- League tabs -->
    <div class="tab-bar">
      <button class="tab-btn" :class="{ active: league === 'nhl' }" @click="league = 'nhl'">NHL</button>
      <button class="tab-btn" :class="{ active: league === 'nba' }" @click="league = 'nba'">NBA</button>
    </div>

    <!-- Loading / error states -->
    <div v-if="loading" class="status-msg">Loading {{ league.toUpperCase() }} data…</div>
    <div v-else-if="error" class="status-msg error">{{ error }}</div>

    <div v-else class="content">
      <p class="meta-line">
        Data from {{ new Date(data.generated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) }}
      </p>

      <!-- Section tabs -->
      <div class="section-bar">
        <button class="section-btn" :class="{ active: section === 'standings' }" @click="section = 'standings'">Standings</button>
        <button class="section-btn" :class="{ active: section === 'streaks' }" @click="section = 'streaks'">Hot Streaks</button>
        <button class="section-btn" :class="{ active: section === 'upcoming' }" @click="section = 'upcoming'">Upcoming</button>
        <button class="section-btn" :class="{ active: section === 'players' }" @click="section = 'players'" v-if="hasPlayers">Top Skaters</button>
        <button class="section-btn" :class="{ active: section === 'goalies' }" @click="section = 'goalies'" v-if="hasGoalies">Goalies</button>
      </div>

      <!-- STANDINGS -->
      <div v-if="section === 'standings'" class="panel">
        <div v-for="conf in conferencesInStandings" :key="conf" class="conference-block">
          <h2 class="conf-title">{{ conf }}</h2>
          <div v-for="div in divisionsInConference(conf)" :key="div" class="division-block">
            <h3 class="div-title">{{ div }}</h3>
            <div class="bar-chart">
              <div v-for="team in teamsInDivision(conf, div)" :key="team.team" class="bar-row">
                <span class="bar-label" :title="team.teamName">{{ team.team }}</span>
                <div class="bar-track">
                  <div class="bar-fill bar-wins" :style="{ width: pct(team.wins, maxWins) }"></div>
                </div>
                <span class="bar-value">{{ team.wins }}W {{ team.losses }}L{{ league === 'nhl' ? ` ${team.otLosses}OTL` : '' }} &mdash; {{ (team.pct * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- HOT STREAKS -->
      <div v-if="section === 'streaks'" class="panel">
        <p class="section-note">Positive = win streak, negative = losing streak. Based on most recent games.</p>
        <div class="streak-grid">
          <div class="streak-col">
            <h3 class="streak-heading hot">🔥 Hottest</h3>
            <div class="bar-chart">
              <div v-for="team in hotTeams" :key="team.team" class="bar-row">
                <span class="bar-label" :title="team.teamName">{{ team.team }}</span>
                <div class="bar-track">
                  <div class="bar-fill bar-hot" :style="{ width: pct(team.streak, maxStreak) }"></div>
                </div>
                <span class="bar-value">+{{ team.streak }}</span>
              </div>
            </div>
          </div>
          <div class="streak-col">
            <h3 class="streak-heading cold">❄️ Coldest</h3>
            <div class="bar-chart">
              <div v-for="team in coldTeams" :key="team.team" class="bar-row">
                <span class="bar-label" :title="team.teamName">{{ team.team }}</span>
                <div class="bar-track">
                  <div class="bar-fill bar-cold" :style="{ width: pct(Math.abs(team.streak), maxStreak) }"></div>
                </div>
                <span class="bar-value">{{ team.streak }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent form for all teams -->
        <h3 class="section-subheading">Last 5 Games — All Teams</h3>
        <div class="form-table">
          <div v-for="team in sortedByStreak" :key="team.team" class="form-row">
            <span class="form-team" :title="team.teamName">{{ team.team }}</span>
            <div class="form-dots">
              <span
                v-for="(g, i) in (recentResults[team.team] || []).slice(0, 5)"
                :key="i"
                class="form-dot"
                :class="g.result === 'W' ? 'win' : 'loss'"
                :title="`${g.result} vs ${g.opponent} (${g.score}) on ${g.date}`"
              >{{ g.result }}</span>
              <span v-for="i in Math.max(0, 5 - (recentResults[team.team] || []).length)" :key="'e'+i" class="form-dot empty">–</span>
            </div>
            <span class="form-streak" :class="team.streak > 0 ? 'hot' : team.streak < 0 ? 'cold' : ''">
              {{ team.streak > 0 ? `W${team.streak}` : team.streak < 0 ? `L${Math.abs(team.streak)}` : '–' }}
            </span>
          </div>
        </div>
      </div>

      <!-- UPCOMING MATCHUPS -->
      <div v-if="section === 'upcoming'" class="panel">
        <div v-if="!upcomingGamesList.length" class="status-msg">No upcoming games found in data.</div>
        <table v-else class="matchup-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Matchup</th>
              <th>Away Form</th>
              <th>Home Form</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(game, i) in upcomingGamesList" :key="i">
              <td class="td-date">{{ game.date }}</td>
              <td class="td-matchup">{{ game.away }} @ {{ game.home }}</td>
              <td class="td-form">
                <span
                  v-for="(g, j) in form5(game.away)"
                  :key="j"
                  class="form-dot"
                  :class="g.result === 'W' ? 'win' : 'loss'"
                  :title="`${g.result} vs ${g.opponent}`"
                >{{ g.result }}</span>
              </td>
              <td class="td-form">
                <span
                  v-for="(g, j) in form5(game.home)"
                  :key="j"
                  class="form-dot"
                  :class="g.result === 'W' ? 'win' : 'loss'"
                  :title="`${g.result} vs ${g.opponent}`"
                >{{ g.result }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- TOP SKATERS -->
      <div v-if="section === 'players' && hasPlayers" class="panel">
        <div v-for="conf in conferencesInStandings" :key="conf" class="conference-block">
          <h2 class="conf-title">{{ conf }}</h2>
          <div class="players-grid">
            <div v-for="player in playersByConference(conf)" :key="player.name" class="player-card">
              <div class="player-name">{{ player.name }}</div>
              <div class="player-team">{{ player.team }} &middot; {{ player.position }}</div>
              <div class="player-stats">
                <span v-for="(val, key) in player.stats" :key="key" class="stat-chip">
                  <span class="stat-label">{{ key }}</span>
                  <span class="stat-val">{{ val }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- GOALIES -->
      <div v-if="section === 'goalies' && hasGoalies" class="panel">
        <div v-for="conf in conferencesInStandings" :key="conf" class="conference-block">
          <h2 class="conf-title">{{ conf }}</h2>
          <div class="players-grid">
            <div v-for="goalie in goaliesByConference(conf)" :key="goalie.name" class="player-card">
              <div class="player-name">{{ goalie.name }}</div>
              <div class="player-team">{{ goalie.team }}</div>
              <div class="player-stats">
                <span v-for="(val, key) in goalie.stats" :key="key" class="stat-chip">
                  <span class="stat-label">{{ key }}</span>
                  <span class="stat-val">{{ val }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const league = ref('nhl')
const section = ref('standings')
const loading = ref(true)
const error = ref(null)
const data = ref(null)

async function loadData(lg) {
  loading.value = true
  error.value = null
  data.value = null
  try {
    const res = await fetch(`/sports-data/${lg}.json`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json = await res.json()
    if (json.error) throw new Error(json.error)
    data.value = json
  } catch (e) {
    error.value = `Failed to load ${lg.toUpperCase()} data: ${e.message}`
  } finally {
    loading.value = false
  }
}

onMounted(() => loadData(league.value))
watch(league, lg => {
  section.value = 'standings'
  loadData(lg)
})

// ---------------------------------------------------------------------------
// Derived data
// ---------------------------------------------------------------------------

const standings = computed(() => data.value?.standings ?? [])
const recentResults = computed(() => data.value?.recent_results ?? {})
const upcoming = computed(() => data.value?.upcoming ?? {})
const players = computed(() => data.value?.players ?? [])
const hasPlayers = computed(() => players.value.length > 0)
const goalies = computed(() => data.value?.goalies ?? [])
const hasGoalies = computed(() => goalies.value.length > 0)

function pct(value, max) {
  if (!max) return '0%'
  return `${Math.max(2, (value / max) * 100).toFixed(1)}%`
}

const maxWins = computed(() => Math.max(...standings.value.map(t => t.wins), 1))

const conferencesInStandings = computed(() => {
  const set = new Set(standings.value.map(t => t.conference))
  return [...set].sort()
})

function divisionsInConference(conf) {
  const set = new Set(standings.value.filter(t => t.conference === conf).map(t => t.division))
  return [...set].sort()
}

function teamsInDivision(conf, div) {
  return standings.value
    .filter(t => t.conference === conf && t.division === div)
    .sort((a, b) => b.wins - a.wins)
}

// Streaks
const hotTeams = computed(() =>
  [...standings.value].filter(t => t.streak > 0).sort((a, b) => b.streak - a.streak).slice(0, 5)
)
const coldTeams = computed(() =>
  [...standings.value].filter(t => t.streak < 0).sort((a, b) => a.streak - b.streak).slice(0, 5)
)
const maxStreak = computed(() =>
  Math.max(...standings.value.map(t => Math.abs(t.streak)), 1)
)
const sortedByStreak = computed(() =>
  [...standings.value].sort((a, b) => b.streak - a.streak)
)

// Upcoming: deduplicate into home @ away pairs
const upcomingGamesList = computed(() => {
  const seen = new Set()
  const games = []
  for (const [team, teamGames] of Object.entries(upcoming.value)) {
    for (const g of teamGames) {
      const home = g.home_away === 'home' ? team : g.opponent
      const away = g.home_away === 'away' ? team : g.opponent
      const key = `${g.date}-${home}-${away}`
      if (!seen.has(key)) {
        seen.add(key)
        games.push({ date: g.date, home, away })
      }
    }
  }
  return games.sort((a, b) => a.date.localeCompare(b.date))
})

function form5(team) {
  return (recentResults.value[team] ?? []).slice(0, 5)
}

// Players / Goalies
function playersByConference(conf) {
  const confTeams = new Set(standings.value.filter(t => t.conference === conf).map(t => t.team))
  return players.value.filter(p => confTeams.has(p.team))
}

function goaliesByConference(conf) {
  const confTeams = new Set(standings.value.filter(t => t.conference === conf).map(t => t.team))
  return goalies.value.filter(g => confTeams.has(g.team))
}
</script>

<style scoped>
.sports-page {
  @apply max-w-5xl mx-auto px-4 py-6
}
.page-title {
  @apply text-3xl font-bold text-primaryLight mb-4 text-center
}
.tab-bar {
  @apply flex justify-center gap-2 mb-6
}
.tab-btn {
  @apply px-6 py-2 font-bold text-primaryLight border-2 border-primaryLight rounded
         hover:bg-primaryLight hover:text-primaryDark transition-colors
}
.tab-btn.active {
  @apply bg-accentColor border-accentColor text-primaryDark
}
.section-bar {
  @apply flex flex-wrap justify-center gap-2 mb-6
}
.section-btn {
  @apply px-4 py-1 text-sm font-bold text-primaryLight border border-primaryLight rounded
         hover:bg-primaryLight hover:text-primaryDark transition-colors
}
.section-btn.active {
  @apply bg-secondaryBlueDark border-accentColor text-accentColor
}
.status-msg {
  @apply text-center text-primaryLight mt-8 text-lg
}
.status-msg.error {
  @apply text-red-400
}
.meta-line {
  @apply text-center text-sm text-secondaryBlueLight mb-4
}
.panel {
  @apply mt-4
}
.conference-block {
  @apply mb-8
}
.conf-title {
  @apply text-xl font-bold text-accentColor mb-3 border-b border-secondaryBlueDark pb-1
}
.division-block {
  @apply mb-5
}
.div-title {
  @apply text-base font-bold text-secondaryBlueLight mb-2
}

/* Bar charts */
.bar-chart {
  @apply flex flex-col gap-1
}
.bar-row {
  @apply flex items-center gap-2
}
.bar-label {
  @apply text-xs font-mono text-primaryLight w-10 text-right shrink-0
}
.bar-track {
  @apply flex-1 bg-secondaryBlueDark rounded h-5 overflow-hidden
}
.bar-fill {
  @apply h-full rounded transition-all duration-300
}
.bar-wins {
  @apply bg-accentColor
}
.bar-hot {
  @apply bg-orange-500
}
.bar-cold {
  @apply bg-blue-400
}
.bar-value {
  @apply text-xs text-primaryLight w-52 shrink-0
}

/* Streaks */
.section-note {
  @apply text-sm text-secondaryBlueLight mb-4 text-center
}
.streak-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6 mb-8
}
.streak-col {}
.streak-heading {
  @apply text-lg font-bold mb-3
}
.streak-heading.hot {
  @apply text-orange-400
}
.streak-heading.cold {
  @apply text-blue-400
}
.section-subheading {
  @apply text-base font-bold text-primaryLight mt-6 mb-3
}

/* Form table */
.form-table {
  @apply flex flex-col gap-1
}
.form-row {
  @apply flex items-center gap-3
}
.form-team {
  @apply text-xs font-mono text-primaryLight w-10 text-right shrink-0
}
.form-dots {
  @apply flex gap-1
}
.form-dot {
  @apply text-xs font-bold w-6 h-6 flex items-center justify-center rounded
}
.form-dot.win {
  @apply bg-green-700 text-white
}
.form-dot.loss {
  @apply bg-red-800 text-white
}
.form-dot.empty {
  @apply bg-secondaryBlueDark text-secondaryBlueLight
}
.form-streak {
  @apply text-xs font-bold ml-2
}
.form-streak.hot {
  @apply text-orange-400
}
.form-streak.cold {
  @apply text-blue-400
}

/* Upcoming table */
.matchup-table {
  @apply w-full text-sm text-primaryLight border-collapse
}
.matchup-table th {
  @apply text-left text-secondaryBlueLight font-bold pb-2 border-b border-secondaryBlueDark
}
.matchup-table td {
  @apply py-2 border-b border-secondaryBlueDark
}
.td-date {
  @apply font-mono text-secondaryBlueLight w-28
}
.td-matchup {
  @apply font-bold
}
.td-form {
  @apply flex gap-1 items-center
}

/* Players */
.players-grid {
  @apply grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-6
}
.player-card {
  @apply bg-secondaryBlueDark rounded p-3
}
.player-name {
  @apply font-bold text-primaryLight text-sm
}
.player-team {
  @apply text-xs text-accentColor mb-2
}
.player-stats {
  @apply flex flex-wrap gap-1
}
.stat-chip {
  @apply flex flex-col items-center bg-primaryDark rounded px-2 py-1
}
.stat-label {
  @apply text-xs text-secondaryBlueLight
}
.stat-val {
  @apply text-sm font-bold text-primaryLight
}
</style>
