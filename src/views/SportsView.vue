<template>
  <div class="sports-page">
    <h1 class="page-title">Sports Dashboard</h1>

    <!-- League tab (NHL only for now) -->
    <div class="tab-bar">
      <button class="tab-btn active">NHL</button>
    </div>

    <!-- Loading / error states -->
    <div v-if="loading" class="status-msg">Loading NHL data…</div>
    <div v-else-if="error" class="status-msg error">{{ error }}</div>

    <div v-else class="content">
      <p class="meta-line">
        Data from {{ new Date(data.generated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) }}
      </p>

      <!-- Search -->
      <div class="search-wrap" ref="searchWrap">
        <input
          v-model="searchQuery"
          class="search-input"
          type="text"
          placeholder="Search team or player…"
          @focus="showDropdown = true"
          @keydown.escape="closeSearch"
        />
        <div v-if="showDropdown && searchResults.length" class="search-dropdown">
          <div
            v-for="result in searchResults"
            :key="result.type + result.name"
            class="search-result"
            @mousedown.prevent="selectEntity(result)"
          >
            <span class="result-type">{{ result.type === 'team' ? '🏒' : result.position === 'G' ? '🥅' : '⛸' }}</span>
            <span class="result-name">{{ result.type === 'team' ? result.teamName : result.name }}</span>
            <span class="result-meta">{{ result.team }}{{ result.type !== 'team' ? ` · ${result.position}` : '' }}</span>
          </div>
        </div>
      </div>

      <!-- Section tabs (hidden in detail view) -->
      <div v-if="section !== 'detail'" class="section-bar">
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
              <div
                v-for="team in teamsInDivision(conf, div)"
                :key="team.team"
                class="bar-row clickable"
                @click="selectEntity({ type: 'team', ...team })"
                :title="`View ${team.teamName} dashboard`"
              >
                <span class="bar-label">{{ team.team }}</span>
                <div class="bar-track">
                  <div class="bar-fill bar-wins" :style="{ width: pct(team.wins, maxWins) }"></div>
                </div>
                <span class="bar-value">{{ team.wins }}W {{ team.losses }}L {{ team.otLosses }}OTL &mdash; {{ (team.pct * 100).toFixed(1) }}%</span>
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
              <div v-for="team in hotTeams" :key="team.team" class="bar-row clickable" @click="selectEntity({ type: 'team', ...team })">
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
              <div v-for="team in coldTeams" :key="team.team" class="bar-row clickable" @click="selectEntity({ type: 'team', ...team })">
                <span class="bar-label" :title="team.teamName">{{ team.team }}</span>
                <div class="bar-track">
                  <div class="bar-fill bar-cold" :style="{ width: pct(Math.abs(team.streak), maxStreak) }"></div>
                </div>
                <span class="bar-value">{{ team.streak }}</span>
              </div>
            </div>
          </div>
        </div>

        <h3 class="section-subheading">Last 5 Games — All Teams</h3>
        <div class="form-table">
          <div v-for="team in sortedByStreak" :key="team.team" class="form-row clickable" @click="selectEntity({ type: 'team', ...team })">
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
              <td class="td-matchup">
                <span class="team-link" @click="selectEntity(teamByAbbr(game.away))">{{ game.away }}</span>
                <span class="td-at"> @ </span>
                <span class="team-link" @click="selectEntity(teamByAbbr(game.home))">{{ game.home }}</span>
              </td>
              <td class="td-form">
                <span v-for="(g, j) in form5(game.away)" :key="j" class="form-dot" :class="g.result === 'W' ? 'win' : 'loss'" :title="`${g.result} vs ${g.opponent}`">{{ g.result }}</span>
              </td>
              <td class="td-form">
                <span v-for="(g, j) in form5(game.home)" :key="j" class="form-dot" :class="g.result === 'W' ? 'win' : 'loss'" :title="`${g.result} vs ${g.opponent}`">{{ g.result }}</span>
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
            <div
              v-for="player in playersByConference(conf)"
              :key="player.name"
              class="player-card clickable"
              @click="selectEntity({ type: 'skater', ...player })"
            >
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
            <div
              v-for="goalie in goaliesByConference(conf)"
              :key="goalie.name"
              class="player-card clickable"
              @click="selectEntity({ type: 'goalie', ...goalie })"
            >
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

      <!-- DETAIL VIEW -->
      <div v-if="section === 'detail' && selectedEntity" class="panel">
        <button class="back-btn" @click="goBack">← Back</button>

        <!-- TEAM DETAIL -->
        <div v-if="selectedEntity.type === 'team'">
          <div class="detail-header">
            <h2 class="detail-title">{{ selectedEntity.teamName }}</h2>
            <div class="detail-record">
              {{ selectedEntity.wins }}W {{ selectedEntity.losses }}L {{ selectedEntity.otLosses }}OTL
              &mdash; {{ selectedEntity.points }} pts
              <span class="detail-streak" :class="selectedEntity.streak > 0 ? 'hot' : selectedEntity.streak < 0 ? 'cold' : ''">
                {{ selectedEntity.streak > 0 ? `W${selectedEntity.streak}` : selectedEntity.streak < 0 ? `L${Math.abs(selectedEntity.streak)}` : '' }}
              </span>
            </div>
          </div>

          <!-- Recent form chart -->
          <h3 class="detail-section-title">Recent Form (last 10 games)</h3>
          <div v-if="!(recentResults[selectedEntity.team] || []).length" class="status-msg">No recent game data.</div>
          <div v-else class="form-chart">
            <div
              v-for="(game, i) in (recentResults[selectedEntity.team] || [])"
              :key="i"
              class="form-bar-wrap"
              :title="`${game.result} vs ${game.opponent} — ${game.score} (${game.date})`"
            >
              <div class="form-bar-goals-for" :style="{ height: goalBarHeight(game, 'for') }" :class="game.result === 'W' ? 'win' : 'loss'"></div>
              <div class="form-bar-goals-against" :style="{ height: goalBarHeight(game, 'against') }"></div>
              <div class="form-bar-label">
                <span class="form-bar-result" :class="game.result === 'W' ? 'win' : 'loss'">{{ game.result }}</span>
                <span class="form-bar-opp">{{ game.opponent }}</span>
              </div>
            </div>
          </div>
          <div class="form-chart-legend">
            <span class="legend-win">■ Goals scored (W)</span>
            <span class="legend-loss">■ Goals scored (L)</span>
            <span class="legend-against">■ Goals against</span>
          </div>

          <!-- Upcoming matchups -->
          <h3 class="detail-section-title">Upcoming Games</h3>
          <div v-if="!(upcoming[selectedEntity.team] || []).length" class="status-msg">No upcoming games in current data window.</div>
          <table v-else class="matchup-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Opponent</th>
                <th>H/A</th>
                <th>Their Last 5</th>
                <th>Our Last 5</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(game, i) in (upcoming[selectedEntity.team] || [])" :key="i">
                <td class="td-date">{{ game.date }}</td>
                <td>
                  <span class="team-link" @click="selectEntity(teamByAbbr(game.opponent))">{{ game.opponent }}</span>
                </td>
                <td class="td-ha">{{ game.home_away === 'home' ? 'H' : 'A' }}</td>
                <td class="td-form">
                  <span v-for="(g, j) in form5(game.opponent)" :key="j" class="form-dot" :class="g.result === 'W' ? 'win' : 'loss'" :title="`${g.result} vs ${g.opponent}`">{{ g.result }}</span>
                </td>
                <td class="td-form">
                  <span v-for="(g, j) in form5(selectedEntity.team)" :key="j" class="form-dot" :class="g.result === 'W' ? 'win' : 'loss'" :title="`${g.result} vs ${g.opponent}`">{{ g.result }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- SKATER DETAIL -->
        <div v-else-if="selectedEntity.type === 'skater'">
          <div class="detail-header">
            <h2 class="detail-title">{{ selectedEntity.name }}</h2>
            <div class="detail-record">{{ selectedEntity.team }} &middot; {{ selectedEntity.position }}</div>
            <div class="player-stats mt-2">
              <span v-for="(val, key) in selectedEntity.stats" :key="key" class="stat-chip">
                <span class="stat-label">{{ key }}</span>
                <span class="stat-val">{{ val }}</span>
              </span>
            </div>
          </div>

          <h3 class="detail-section-title">Recent Game Log</h3>
          <div v-if="!(selectedEntity.game_log || []).length" class="status-msg">No game log available.</div>
          <table v-else class="log-table">
            <thead>
              <tr><th>Date</th><th>Opp</th><th>H/A</th><th>G</th><th>A</th><th>PTS</th><th>+/-</th><th>SOG</th><th>TOI</th></tr>
            </thead>
            <tbody>
              <tr v-for="(g, i) in selectedEntity.game_log" :key="i">
                <td class="td-date">{{ g.date }}</td>
                <td><span class="team-link" @click="selectEntity(teamByAbbr(g.opponent))">{{ g.opponent }}</span></td>
                <td class="td-ha">{{ g.home_away === 'home' ? 'H' : 'A' }}</td>
                <td>{{ g.goals }}</td>
                <td>{{ g.assists }}</td>
                <td class="td-pts">{{ g.points }}</td>
                <td :class="g.plusMinus > 0 ? 'td-pos' : g.plusMinus < 0 ? 'td-neg' : ''">{{ g.plusMinus > 0 ? '+' : '' }}{{ g.plusMinus }}</td>
                <td>{{ g.shots }}</td>
                <td class="td-mono">{{ g.toi }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- GOALIE DETAIL -->
        <div v-else-if="selectedEntity.type === 'goalie'">
          <div class="detail-header">
            <h2 class="detail-title">{{ selectedEntity.name }}</h2>
            <div class="detail-record">{{ selectedEntity.team }} &middot; G</div>
            <div class="player-stats mt-2">
              <span v-for="(val, key) in selectedEntity.stats" :key="key" class="stat-chip">
                <span class="stat-label">{{ key }}</span>
                <span class="stat-val">{{ val }}</span>
              </span>
            </div>
          </div>

          <h3 class="detail-section-title">Recent Game Log</h3>
          <div v-if="!(selectedEntity.game_log || []).length" class="status-msg">No game log available.</div>
          <table v-else class="log-table">
            <thead>
              <tr><th>Date</th><th>Opp</th><th>H/A</th><th>Dec</th><th>Saves</th><th>GA</th><th>SV%</th><th>TOI</th></tr>
            </thead>
            <tbody>
              <tr v-for="(g, i) in selectedEntity.game_log" :key="i">
                <td class="td-date">{{ g.date }}</td>
                <td><span class="team-link" @click="selectEntity(teamByAbbr(g.opponent))">{{ g.opponent }}</span></td>
                <td class="td-ha">{{ g.home_away === 'home' ? 'H' : 'A' }}</td>
                <td :class="g.decision === 'W' ? 'td-pos' : g.decision === 'L' ? 'td-neg' : ''">{{ g.decision }}</td>
                <td>{{ g.saves }}</td>
                <td>{{ g.goalsAgainst }}</td>
                <td class="td-pts">{{ g.savePct }}</td>
                <td class="td-mono">{{ g.toi }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const loading = ref(true)
const error = ref(null)
const data = ref(null)

const section = ref('standings')
const previousSection = ref('standings')
const selectedEntity = ref(null)

const searchQuery = ref('')
const showDropdown = ref(false)
const searchWrap = ref(null)

async function loadData() {
  loading.value = true
  error.value = null
  data.value = null
  try {
    const res = await fetch('/sports-data/nhl.json')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    data.value = await res.json()
  } catch (e) {
    error.value = `Failed to load NHL data: ${e.message}`
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  document.addEventListener('mousedown', handleOutsideClick)
})
onUnmounted(() => document.removeEventListener('mousedown', handleOutsideClick))

function handleOutsideClick(e) {
  if (searchWrap.value && !searchWrap.value.contains(e.target)) {
    showDropdown.value = false
  }
}

function closeSearch() {
  showDropdown.value = false
  searchQuery.value = ''
}

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

function teamByAbbr(abbr) {
  const t = standings.value.find(s => s.team === abbr)
  return t ? { type: 'team', ...t } : null
}

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

function playersByConference(conf) {
  const confTeams = new Set(standings.value.filter(t => t.conference === conf).map(t => t.team))
  return players.value.filter(p => confTeams.has(p.team))
}

function goaliesByConference(conf) {
  const confTeams = new Set(standings.value.filter(t => t.conference === conf).map(t => t.team))
  return goalies.value.filter(g => confTeams.has(g.team))
}

// ---------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------

const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (q.length < 2) return []
  const results = []

  for (const t of standings.value) {
    if (t.team.toLowerCase().includes(q) || t.teamName.toLowerCase().includes(q)) {
      results.push({ type: 'team', ...t })
    }
    if (results.length >= 8) break
  }

  if (results.length < 8) {
    for (const p of players.value) {
      if (p.name.toLowerCase().includes(q) || p.team.toLowerCase().includes(q)) {
        results.push({ type: 'skater', ...p })
      }
      if (results.length >= 8) break
    }
  }

  if (results.length < 8) {
    for (const g of goalies.value) {
      if (g.name.toLowerCase().includes(q) || g.team.toLowerCase().includes(q)) {
        results.push({ type: 'goalie', ...g })
      }
      if (results.length >= 8) break
    }
  }

  return results
})

watch(searchQuery, q => {
  showDropdown.value = q.trim().length >= 2
})

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

function selectEntity(entity) {
  if (!entity) return
  previousSection.value = section.value !== 'detail' ? section.value : previousSection.value
  selectedEntity.value = entity
  section.value = 'detail'
  showDropdown.value = false
  searchQuery.value = ''
}

function goBack() {
  section.value = previousSection.value
  selectedEntity.value = null
}

// ---------------------------------------------------------------------------
// Team form chart helpers
// ---------------------------------------------------------------------------

const maxGoals = computed(() => {
  let max = 1
  for (const games of Object.values(recentResults.value)) {
    for (const g of games) {
      const [gf, ga] = g.score.split('-').map(Number)
      if (gf > max) max = gf
      if (ga > max) max = ga
    }
  }
  return max
})

function goalBarHeight(game, side) {
  const [gf, ga] = game.score.split('-').map(Number)
  const goals = side === 'for' ? gf : ga
  const h = Math.max(4, (goals / maxGoals.value) * 80)
  return `${h}px`
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

/* Search */
.search-wrap {
  @apply relative mb-6
}
.search-input {
  @apply w-full bg-secondaryBlueDark text-primaryLight border border-primaryLight rounded
         px-4 py-2 text-sm placeholder-secondaryBlueLight focus:outline-none focus:border-accentColor
}
.search-dropdown {
  @apply absolute top-full left-0 right-0 z-10 bg-primaryDark border border-secondaryBlueDark rounded
         shadow-lg mt-1 max-h-64 overflow-y-auto
}
.search-result {
  @apply flex items-center gap-2 px-4 py-2 cursor-pointer hover:bg-secondaryBlueDark text-sm
}
.result-type {
  @apply w-5 text-center shrink-0
}
.result-name {
  @apply text-primaryLight flex-1
}
.result-meta {
  @apply text-secondaryBlueLight text-xs
}

/* Clickable rows/cards */
.clickable {
  @apply cursor-pointer hover:opacity-80 transition-opacity
}
.team-link {
  @apply text-accentColor cursor-pointer hover:underline font-bold
}
.td-at {
  @apply text-secondaryBlueLight
}

/* Conference / division */
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
.bar-wins { @apply bg-accentColor }
.bar-hot  { @apply bg-orange-500 }
.bar-cold { @apply bg-blue-400 }
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
.streak-heading {
  @apply text-lg font-bold mb-3
}
.streak-heading.hot { @apply text-orange-400 }
.streak-heading.cold { @apply text-blue-400 }
.section-subheading {
  @apply text-base font-bold text-primaryLight mt-6 mb-3
}

/* Form table */
.form-table { @apply flex flex-col gap-1 }
.form-row   { @apply flex items-center gap-3 }
.form-team  { @apply text-xs font-mono text-primaryLight w-10 text-right shrink-0 }
.form-dots  { @apply flex gap-1 }
.form-dot   { @apply text-xs font-bold w-6 h-6 flex items-center justify-center rounded }
.form-dot.win   { @apply bg-green-700 text-white }
.form-dot.loss  { @apply bg-red-800 text-white }
.form-dot.empty { @apply bg-secondaryBlueDark text-secondaryBlueLight }
.form-streak    { @apply text-xs font-bold ml-2 }
.form-streak.hot  { @apply text-orange-400 }
.form-streak.cold { @apply text-blue-400 }

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
.td-date { @apply font-mono text-secondaryBlueLight w-28 }
.td-matchup { @apply font-bold }
.td-ha { @apply text-secondaryBlueLight text-xs w-8 }
.td-form { @apply flex gap-1 items-center }

/* Players */
.players-grid {
  @apply grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-6
}
.player-card {
  @apply bg-secondaryBlueDark rounded p-3
}
.player-name { @apply font-bold text-primaryLight text-sm }
.player-team { @apply text-xs text-accentColor mb-2 }
.player-stats { @apply flex flex-wrap gap-1 }
.stat-chip {
  @apply flex flex-col items-center bg-primaryDark rounded px-2 py-1
}
.stat-label { @apply text-xs text-secondaryBlueLight }
.stat-val   { @apply text-sm font-bold text-primaryLight }

/* Detail view */
.back-btn {
  @apply mb-4 text-sm text-accentColor hover:underline cursor-pointer font-bold
}
.detail-header {
  @apply mb-6
}
.detail-title {
  @apply text-2xl font-bold text-primaryLight
}
.detail-record {
  @apply text-sm text-secondaryBlueLight mt-1 flex items-center gap-2
}
.detail-streak {
  @apply font-bold
}
.detail-streak.hot  { @apply text-orange-400 }
.detail-streak.cold { @apply text-blue-400 }
.detail-section-title {
  @apply text-base font-bold text-accentColor mt-6 mb-3 border-b border-secondaryBlueDark pb-1
}

/* Form bar chart (team detail) */
.form-chart {
  @apply flex gap-2 items-end h-28 overflow-x-auto pb-1
}
.form-bar-wrap {
  @apply flex flex-col items-center gap-0.5 shrink-0 w-12
}
.form-bar-goals-for {
  @apply w-8 rounded-t transition-all
}
.form-bar-goals-for.win  { @apply bg-green-600 }
.form-bar-goals-for.loss { @apply bg-red-700 }
.form-bar-goals-against {
  @apply w-8 rounded-t bg-gray-600
}
.form-bar-label {
  @apply flex flex-col items-center mt-1
}
.form-bar-result {
  @apply text-xs font-bold
}
.form-bar-result.win  { @apply text-green-400 }
.form-bar-result.loss { @apply text-red-400 }
.form-bar-opp {
  @apply text-xs text-secondaryBlueLight
}
.form-chart-legend {
  @apply flex gap-4 text-xs mt-2 mb-4
}
.legend-win     { @apply text-green-400 }
.legend-loss    { @apply text-red-400 }
.legend-against { @apply text-gray-400 }

/* Game log table */
.log-table {
  @apply w-full text-sm text-primaryLight border-collapse
}
.log-table th {
  @apply text-left text-secondaryBlueLight font-bold pb-2 border-b border-secondaryBlueDark text-xs
}
.log-table td {
  @apply py-1.5 border-b border-secondaryBlueDark text-sm
}
.td-pts  { @apply font-bold text-accentColor }
.td-pos  { @apply text-green-400 font-bold }
.td-neg  { @apply text-red-400 font-bold }
.td-mono { @apply font-mono text-xs }
.mt-2 { margin-top: 0.5rem }
</style>
