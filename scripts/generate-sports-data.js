#!/usr/bin/env node
/**
 * Fetches current NHL and NBA standings, recent results, and upcoming schedules,
 * then writes static JSON to /public/sports-data/.
 *
 * Usage:
 *   node scripts/generate-sports-data.js
 *
 * Environment variables:
 *   BALLDONTLIE_API_KEY  — free key from https://www.balldontlie.io (required for NBA)
 */

import { writeFileSync, mkdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const OUT_DIR = join(__dirname, '..', 'public', 'sports-data')

mkdirSync(OUT_DIR, { recursive: true })

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function get(url, headers = {}) {
  const res = await fetch(url, { headers })
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`)
  return res.json()
}

const sleep = ms => new Promise(r => setTimeout(r, ms))

function computeStreak(games) {
  // games is newest-first array of { result: 'W'|'L' }
  if (!games.length) return 0
  const first = games[0].result
  let streak = 0
  for (const g of games) {
    if (g.result !== first) break
    streak++
  }
  return first === 'W' ? streak : -streak
}

// ---------------------------------------------------------------------------
// NHL  (https://api-web.nhle.com/v1/)
// ---------------------------------------------------------------------------

async function fetchNHL() {
  console.log('Fetching NHL data…')

  const standingsData = await get('https://api-web.nhle.com/v1/standings/now')

  const standings = standingsData.standings.map(t => ({
    team: t.teamAbbrev.default,
    teamName: t.teamName.default,
    conference: t.conferenceName,
    division: t.divisionName,
    wins: t.wins,
    losses: t.losses,
    otLosses: t.otLosses,
    points: t.points,
    gamesPlayed: t.gamesPlayed,
    pct: t.gamesPlayed > 0 ? (t.points / (t.gamesPlayed * 2)) : 0,
    winStreak: t.winStreak ?? 0,
    streak: t.streakCode ?? '',
  }))

  // Fetch schedule for the next 7 days
  const today = new Date()
  const upcoming = {}
  const recentResults = {}

  // Pull each team's last 5 + next 5 games from the club schedule
  // NHL provides a per-team schedule endpoint; we use the current season week view
  // to keep requests low, we fetch the league-wide schedule for a date range
  for (const team of standings) {
    try {
      const schedData = await get(`https://api-web.nhle.com/v1/club-schedule/${team.team}/week/now`)
      const games = schedData.games ?? []

      const upcomingGames = []
      for (const g of games) {
        const gameDate = new Date(g.gameDate)
        if (gameDate >= today) {
          const isHome = g.homeTeam.abbrev === team.team
          const opponent = isHome ? g.awayTeam.abbrev : g.homeTeam.abbrev
          upcomingGames.push({
            date: g.gameDate,
            opponent,
            home_away: isHome ? 'home' : 'away',
          })
        }
      }
      if (upcomingGames.length) upcoming[team.team] = upcomingGames
    } catch {
      // non-critical — skip if team schedule unavailable
    }
    await sleep(200)
  }

  // Recent results: fetch last month of games for streak computation
  for (const team of standings) {
    try {
      const schedData = await get(`https://api-web.nhle.com/v1/club-schedule/${team.team}/month/now`)
      const games = (schedData.games ?? [])
        .filter(g => g.gameState === 'OFF' || g.gameState === 'FINAL')
        .sort((a, b) => new Date(b.gameDate) - new Date(a.gameDate))
        .slice(0, 10)

      recentResults[team.team] = games.map(g => {
        const isHome = g.homeTeam.abbrev === team.team
        const teamScore = isHome ? g.homeTeam.score : g.awayTeam.score
        const oppScore = isHome ? g.awayTeam.score : g.homeTeam.score
        const opponent = isHome ? g.awayTeam.abbrev : g.homeTeam.abbrev
        const result = teamScore > oppScore ? 'W' : 'L'
        return {
          date: g.gameDate,
          opponent,
          home_away: isHome ? 'home' : 'away',
          result,
          score: `${teamScore}-${oppScore}`,
        }
      })
    } catch {
      // non-critical
    }
    await sleep(200)
  }

  // Recompute streak from recent results where we have game data
  for (const team of standings) {
    const recent = recentResults[team.team] ?? []
    if (recent.length) {
      team.streak = computeStreak(recent)
    } else {
      // Fall back to the streak value from standings API (positive=win, negative=loss)
      const rawStreak = team.winStreak
      team.streak = rawStreak
    }
  }

  // Player stats leaders (points, goals, assists)
  const SEASON = '20252026'
  // Fetch stats sequentially to avoid NHL API rate limits
  const pointsData = await get(`https://api-web.nhle.com/v1/skater-stats-leaders/${SEASON}/2?categories=points&limit=1000`)
  await sleep(500)
  const goalsData = await get(`https://api-web.nhle.com/v1/skater-stats-leaders/${SEASON}/2?categories=goals&limit=1000`)
  await sleep(500)
  const assistsData = await get(`https://api-web.nhle.com/v1/skater-stats-leaders/${SEASON}/2?categories=assists&limit=1000`)

  // Merge into a per-player map keyed by player id
  const playerMap = {}
  const addStat = (list, statKey) => {
    for (const p of list) {
      if (!playerMap[p.id]) {
        playerMap[p.id] = {
          id: p.id,
          name: `${p.firstName.default} ${p.lastName.default}`,
          team: p.teamAbbrev,
          position: p.position,
          headshot: p.headshot,
          stats: {},
        }
      }
      playerMap[p.id].stats[statKey] = p.value
    }
  }
  addStat(pointsData.points ?? [], 'PTS')
  addStat(goalsData.goals ?? [], 'G')
  addStat(assistsData.assists ?? [], 'A')

  const players = Object.values(playerMap).sort(
    (a, b) => (b.stats.PTS ?? 0) - (a.stats.PTS ?? 0)
  )

  // Skater game logs (last 10 games per player)
  console.log(`Fetching game logs for ${players.length} skaters…`)
  for (let i = 0; i < players.length; i++) {
    const p = players[i]
    try {
      const logData = await get(`https://api-web.nhle.com/v1/player/${p.id}/game-log/${SEASON}/2`)
      p.game_log = (logData.gameLog ?? [])
        .sort((a, b) => b.gameDate.localeCompare(a.gameDate))
        .slice(0, 10)
        .map(g => ({
          date: g.gameDate,
          opponent: g.opponentAbbrev,
          home_away: g.homeRoadFlag === 'H' ? 'home' : 'away',
          goals: g.goals,
          assists: g.assists,
          points: g.points,
          plusMinus: g.plusMinus,
          shots: g.shots,
          toi: g.toi,
        }))
    } catch {
      p.game_log = []
    }
    if (i % 50 === 49) console.log(`  …${i + 1}/${players.length} skaters done`)
    await sleep(300)
  }

  // Goalie stats leaders (wins, save%, GAA, shutouts)
  await sleep(500)
  const goalieWinsData = await get(`https://api-web.nhle.com/v1/goalie-stats-leaders/${SEASON}/2?categories=wins&limit=100`)
  await sleep(500)
  const goalieSvData = await get(`https://api-web.nhle.com/v1/goalie-stats-leaders/${SEASON}/2?categories=savePctg&limit=100`)
  await sleep(500)
  const goalieGaaData = await get(`https://api-web.nhle.com/v1/goalie-stats-leaders/${SEASON}/2?categories=goalsAgainstAverage&limit=100`)
  await sleep(500)
  const goalieShutoutsData = await get(`https://api-web.nhle.com/v1/goalie-stats-leaders/${SEASON}/2?categories=shutouts&limit=100`)

  const goalieMap = {}
  const addGoalieStat = (list, statKey) => {
    for (const p of list) {
      if (!goalieMap[p.id]) {
        goalieMap[p.id] = {
          id: p.id,
          name: `${p.firstName.default} ${p.lastName.default}`,
          team: p.teamAbbrev,
          position: 'G',
          headshot: p.headshot,
          stats: {},
        }
      }
      goalieMap[p.id].stats[statKey] = p.value
    }
  }
  addGoalieStat(goalieWinsData.wins ?? [], 'W')
  addGoalieStat(goalieSvData.savePctg ?? [], 'SV%')
  addGoalieStat(goalieGaaData.goalsAgainstAverage ?? [], 'GAA')
  addGoalieStat(goalieShutoutsData.shutouts ?? [], 'SO')

  // Format SV% to 3 decimal places and GAA to 2
  for (const g of Object.values(goalieMap)) {
    if (g.stats['SV%'] != null) g.stats['SV%'] = g.stats['SV%'].toFixed(3)
    if (g.stats['GAA'] != null) g.stats['GAA'] = g.stats['GAA'].toFixed(2)
  }

  const goalies = Object.values(goalieMap).sort(
    (a, b) => (b.stats.W ?? 0) - (a.stats.W ?? 0)
  )

  // Goalie game logs (last 10 games per goalie)
  console.log(`Fetching game logs for ${goalies.length} goalies…`)
  for (let i = 0; i < goalies.length; i++) {
    const g = goalies[i]
    try {
      const logData = await get(`https://api-web.nhle.com/v1/player/${g.id}/game-log/${SEASON}/2`)
      g.game_log = (logData.gameLog ?? [])
        .sort((a, b) => b.gameDate.localeCompare(a.gameDate))
        .slice(0, 10)
        .map(gl => ({
          date: gl.gameDate,
          opponent: gl.opponentAbbrev,
          home_away: gl.homeRoadFlag === 'H' ? 'home' : 'away',
          decision: gl.decision ?? '–',
          saves: (gl.shotsAgainst ?? 0) - (gl.goalsAgainst ?? 0),
          goalsAgainst: gl.goalsAgainst ?? 0,
          savePct: gl.savePctg != null ? gl.savePctg.toFixed(3) : '–',
          toi: gl.toi,
        }))
    } catch {
      g.game_log = []
    }
    await sleep(300)
  }

  return {
    generated_at: new Date().toISOString(),
    standings,
    recent_results: recentResults,
    upcoming,
    players,
    goalies,
  }
}

// ---------------------------------------------------------------------------
// NBA  (https://api.balldontlie.io/v1/)
// ---------------------------------------------------------------------------

async function fetchNBA() {
  const apiKey = process.env.BALLDONTLIE_API_KEY
  if (!apiKey) {
    console.warn('BALLDONTLIE_API_KEY not set — skipping NBA data')
    return {
      generated_at: new Date().toISOString(),
      error: 'BALLDONTLIE_API_KEY not set',
      standings: [],
      recent_results: {},
      upcoming: {},
    }
  }

  console.log('Fetching NBA data…')
  const headers = { Authorization: apiKey }

  // Standings
  const standingsRaw = await get('https://api.balldontlie.io/v1/standings?season=2024', headers)
  const standings = (standingsRaw.data ?? []).map(t => ({
    team: t.team.abbreviation,
    teamName: t.team.full_name,
    conference: t.conference,
    division: t.division,
    wins: t.wins,
    losses: t.losses,
    pct: t.wins + t.losses > 0 ? t.wins / (t.wins + t.losses) : 0,
    streak: 0, // computed below from recent games
  }))

  // Recent results + upcoming: fetch games for the last 30 and next 14 days
  const todayStr = new Date().toISOString().slice(0, 10)
  const past30 = new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10)
  const future14 = new Date(Date.now() + 14 * 86400000).toISOString().slice(0, 10)

  const recentRaw = await get(
    `https://api.balldontlie.io/v1/games?start_date=${past30}&end_date=${todayStr}&per_page=100`,
    headers
  )
  const upcomingRaw = await get(
    `https://api.balldontlie.io/v1/games?start_date=${todayStr}&end_date=${future14}&per_page=100`,
    headers
  )

  const recentResults = {}
  for (const g of (recentRaw.data ?? [])) {
    if (g.status !== 'Final') continue
    const processTeam = (teamObj, opponentObj, isHome) => {
      const abbr = teamObj.abbreviation
      const teamScore = isHome ? g.home_team_score : g.visitor_team_score
      const oppScore = isHome ? g.visitor_team_score : g.home_team_score
      if (!recentResults[abbr]) recentResults[abbr] = []
      recentResults[abbr].push({
        date: g.date.slice(0, 10),
        opponent: opponentObj.abbreviation,
        home_away: isHome ? 'home' : 'away',
        result: teamScore > oppScore ? 'W' : 'L',
        score: `${teamScore}-${oppScore}`,
      })
    }
    processTeam(g.home_team, g.visitor_team, true)
    processTeam(g.visitor_team, g.home_team, false)
  }

  // Sort recent results newest-first
  for (const abbr of Object.keys(recentResults)) {
    recentResults[abbr].sort((a, b) => b.date.localeCompare(a.date))
  }

  const upcoming = {}
  for (const g of (upcomingRaw.data ?? [])) {
    if (g.status === 'Final') continue
    const processTeam = (teamObj, opponentObj, isHome) => {
      const abbr = teamObj.abbreviation
      if (!upcoming[abbr]) upcoming[abbr] = []
      upcoming[abbr].push({
        date: g.date.slice(0, 10),
        opponent: opponentObj.abbreviation,
        home_away: isHome ? 'home' : 'away',
      })
    }
    processTeam(g.home_team, g.visitor_team, true)
    processTeam(g.visitor_team, g.home_team, false)
  }

  // Compute streaks
  for (const team of standings) {
    const recent = recentResults[team.team] ?? []
    team.streak = computeStreak(recent)
  }

  // Player stats leaders — season averages for top scorers
  let players = []
  try {
    const seasonAvgRaw = await get(
      'https://api.balldontlie.io/v1/season_averages?season=2024&per_page=100',
      headers
    )
    const playerListRaw = await get(
      'https://api.balldontlie.io/v1/players?per_page=100&cursor=0',
      headers
    )
    // balldontlie season_averages requires player_ids; fetch top scoring players differently
    // Use player_ids from standings teams or pull via stats endpoint
    // Simpler: fetch stats leaders directly
    const statsRaw = await get(
      'https://api.balldontlie.io/v1/stats?seasons[]=2024&per_page=100&postseason=false',
      headers
    )
    // Aggregate per player
    const agg = {}
    for (const s of statsRaw.data ?? []) {
      const pid = s.player.id
      if (!agg[pid]) {
        agg[pid] = {
          name: `${s.player.first_name} ${s.player.last_name}`,
          team: s.team.abbreviation,
          games: 0,
          pts: 0,
          reb: 0,
          ast: 0,
        }
      }
      agg[pid].games++
      agg[pid].pts += s.pts ?? 0
      agg[pid].reb += s.reb ?? 0
      agg[pid].ast += s.ast ?? 0
    }
    players = Object.values(agg)
      .filter(p => p.games >= 5)
      .map(p => ({
        name: p.name,
        team: p.team,
        stats: {
          PPG: (p.pts / p.games).toFixed(1),
          RPG: (p.reb / p.games).toFixed(1),
          APG: (p.ast / p.games).toFixed(1),
        },
      }))
      .sort((a, b) => parseFloat(b.stats.PPG) - parseFloat(a.stats.PPG))
      .slice(0, 50)
  } catch {
    // non-critical — player stats optional
  }

  return {
    generated_at: new Date().toISOString(),
    standings,
    recent_results: recentResults,
    upcoming,
    players,
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const [nhlData, nbaData] = await Promise.all([fetchNHL(), fetchNBA()])

writeFileSync(join(OUT_DIR, 'nhl.json'), JSON.stringify(nhlData, null, 2))
console.log(`Wrote nhl.json (${nhlData.standings.length} teams)`)

writeFileSync(join(OUT_DIR, 'nba.json'), JSON.stringify(nbaData, null, 2))
console.log(`Wrote nba.json (${nbaData.standings.length} teams)`)
