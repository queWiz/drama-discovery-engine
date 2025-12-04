<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { marked } from 'marked'
import { Search, SlidersHorizontal, Star, PlayCircle, Bookmark, TrendingUp, AlertCircle, Info, Link, Check, Loader2, ChevronDown } from 'lucide-vue-next'

const query = ref('')
const answer = ref('')
const loading = ref(false)
const showFilters = ref(false)
const hasSearched = ref(false)
const isFocused = ref(false) // Tracks if user is typing

// --- STATE: FILTERS ---
const selectedGenre = ref('All')
const selectedYear = ref('All')
const selectedRating = ref(0)
const selectedTrope = ref('')

// --- DATA ---
const genres = ['All', 'Thriller', 'Romance', 'Comedy', 'Action', 'Historical', 'Melodrama']
const years = ['All', '2020+', '2015-2019', 'Classic']
const tropes = ['Revenge', 'Enemies to Lovers', 'Love Triangle', 'Contract Marriage', 'Underdog', 'Supernatural']
const sources = ref([])

// --- STATE: MDL INTEGRATION ---
const showMdlModal = ref(false)
const mdlUsername = ref('')
const isSyncing = ref(false)
const watchedShows = ref([]) // Stores the list of shows the user has seen
const syncStatus = ref('')   // "Success! Found 42 shows."

// --- NEW STATE: MODAL & BOOKMARKS ---
const selectedDrama = ref(null) // Holds the data of the clicked drama
const bookmarks = ref(new Set()) // Using a Set for easy check (has/add/delete)

const formattedAnswer = computed(() => answer.value ? marked(answer.value) : '')

// Helper for Match Badge Styling
const getMatchClass = (index) => {
  if (index === 0) return 'match-top'
  if (index < 3) return 'match-high'
  return 'match-base'
}

// Load bookmarks on startup
onMounted(() => {
  const saved = localStorage.getItem('drama_bookmarks')
  if (saved) {
    bookmarks.value = new Set(JSON.parse(saved))
  }
})

const toggleBookmark = (drama) => {
  if (bookmarks.value.has(drama.title)) {
    bookmarks.value.delete(drama.title)
  } else {
    bookmarks.value.add(drama.title)
  }
  // Save to browser storage
  localStorage.setItem('drama_bookmarks', JSON.stringify([...bookmarks.value]))
}

const openDetails = (drama) => {
  selectedDrama.value = drama
}

// Helper to turn "Tag A, Tag B" string back into an Array
const parseList = (str) => {
  if (!str) return []
  return str.split(', ')
}

const syncMDL = async () => {
  if (!mdlUsername.value) return
  
  isSyncing.value = true
  syncStatus.value = ''
  
  try {
    // Call the backend endpoint you created earlier
    const response = await axios.post(import.meta.env.VITE_API_URL + '/user/sync', {
      profile_url: mdlUsername.value
    })
    
    watchedShows.value = response.data.watched_titles
    syncStatus.value = `Synced! We'll ignore ${response.data.count} shows you've seen.`
    
    // Auto close after 2 seconds
    setTimeout(() => {
      showMdlModal.value = false
      syncStatus.value = ''
    }, 2500)
    
  } catch (error) {
    console.error(error)
    syncStatus.value = "Error: Could not find public profile."
  } finally {
    isSyncing.value = false
  }
}

const askAI = async () => {
  if (!query.value) return
  
  loading.value = true
  hasSearched.value = true
  answer.value = ''
  sources.value = []
  showFilters.value = false 
  isFocused.value = false // Remove focus mode on search
  
  try {
    const response = await axios.post(import.meta.env.VITE_API_URL + '/chat', {
      message: query.value,
      genre: selectedGenre.value,
      rating: parseInt(selectedRating.value),
      year: selectedYear.value,
      trope: selectedTrope.value,
      watched_history: watchedShows.value
    })
    answer.value = response.data.answer
    sources.value = response.data.sources
  } catch (error) {
    answer.value = "Error connecting to the engine."
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openTrailer = (title) => {
  // Opens a new tab searching for the trailer
  const searchQuery = encodeURIComponent(`${title} kdrama trailer`)
  window.open(`https://www.youtube.com/results?search_query=${searchQuery}`, '_blank')
}
</script>

<template>
  <div class="app-layout">
    <!-- Cinematic Background -->
    <div class="ambient-glow purple"></div>
    <div class="ambient-glow blue"></div>
    <div class="noise-overlay"></div>

    <!-- Overlay that dims background when searching -->
    <div :class="['focus-overlay', { active: isFocused }]"></div>
    
    <!-- HEADER / SEARCH BAR -->
    <header :class="['top-nav', { 'nav-expanded': hasSearched }]">
      <div :class="['search-island', { 'island-focused': isFocused }]">
        
        <!-- Logo -->
        <div class="logo" v-if="!isFocused || hasSearched">
          Drama<span class="highlight">Engine</span>
        </div>
        
        <!-- Search Input -->
        <div class="search-wrapper">
          <input 
            v-model="query" 
            placeholder="Type your vibe (e.g., 'A sad romance that makes me cry')..." 
            @keydown.enter.prevent="askAI"
            @focus="isFocused = true" 
            @blur="isFocused = false"
          />
          <button 
            class="search-btn" 
            @click="askAI" 
            :disabled="loading"
            :class="{ 'btn-loading': loading }"
          >
            <div v-if="loading" class="pulse-ring"></div>
            <Search size="18" v-else />
          </button>
        </div>

        <!-- Filter Toggle -->
        <div class="divider"></div>
        <button 
          class="filter-toggle" 
          @click="showFilters = !showFilters" 
          :class="{ 'btn-active': showFilters }"
          title="Filters"
        >
          <SlidersHorizontal size="18" />
        </button>

        <!-- MDL Profile -->
        <div class="user-profile" @click="showMdlModal = true" title="Sync MyDramaList">
          <div :class="['avatar-circle', { 'avatar-active': watchedShows.length > 0 }]">
            <Check v-if="watchedShows.length > 0" size="14" />
            <span v-else>MDL</span>
          </div>
        </div>
      </div>

      <!-- FILTER DRAWER -->
      <transition name="slide-down">
        <div v-if="showFilters" class="filter-drawer">
          <div class="filter-col">
            <label>Genre</label>
            <div class="chips">
              <span v-for="g in genres" :key="g" 
                    :class="{ active: selectedGenre === g }" 
                    @click="selectedGenre = g">
                {{ g }}
              </span>
            </div>
          </div>
          
          <div class="filter-col">
            <label>Release Era</label>
            <div class="select-wrapper">
              <select v-model="selectedYear">
                <option v-for="y in years" :key="y">{{ y }}</option>
              </select>
              <ChevronDown class="select-icon" size="14"/>
            </div>
          </div>
          
          <div class="filter-col">
            <label>Min Rating: <span class="highlight">{{ selectedRating }}+</span></label>
            <input type="range" min="0" max="10" v-model="selectedRating" class="range-slider" />
            <div class="range-labels">
              <span>0</span><span>5</span><span>10</span>
            </div>
          </div>
          
          <div class="filter-col">
            <label>Must Include Trope</label>
            <div class="select-wrapper">
              <select v-model="selectedTrope">
                <option value="">Any Trope</option>
                <option v-for="t in tropes" :key="t">{{ t }}</option>
              </select>
              <ChevronDown class="select-icon" size="14"/>
            </div>
          </div>
        </div>
      </transition>
    </header>

    <!-- MAIN CONTENT -->
    <main class="content-area">
      
      <!-- LOADING STATE -->
      <div v-if="loading" class="loading-container">
        <div class="scanner-line"></div>
        <p>Analyzing Synopses & Reviews...</p>
      </div>

      <!-- ZERO STATE -->
      <transition name="fade">
        <div v-if="!hasSearched && !loading" class="hero-section">
          <h1>Find your next <br><span class="gradient-text">Obsession.</span></h1>
          <p class="hero-sub">AI-powered curation based on vibes, tropes, and hidden gems.</p>
          
          <div class="trending-preview">
             <div class="preview-card" style="background-image: url('https://i.mydramalist.com/Rle36_4c.jpg?v=1')"></div>
             <div class="preview-card" style="background-image: url('https://i.mydramalist.com/Beg4z_4c.jpg')"></div>
             <div class="preview-card" style="background-image: url('https://i.mydramalist.com/l0YBOx_4c.jpg')"></div>
          </div>
        </div>
      </transition>

      <!-- RESULTS VIEW -->
      <transition name="fade-up">
        <div v-if="answer && !loading" class="results-container">
          
          <!-- AI Summary -->
          <div class="ai-insight">
             <div class="insight-header">
               <div class="sparkle-icon"><TrendingUp size="16"/></div>
               <span>AI Analysis</span>
             </div>
             <div class="insight-content" v-html="formattedAnswer"></div>
          </div>

          <!-- BENTO GRID -->
          <div class="bento-grid">
            <div 
              v-for="(source, index) in sources" 
              :key="index" 
              class="drama-card"
              :class="{ 'card-top-pick': index === 0 }" 
              @click="openDetails(source)" 
            >          
              <!-- Poster -->
              <div class="card-bg">
                <img :src="source.image_url || 'https://via.placeholder.com/300x450'" loading="lazy" />
                <div class="overlay-gradient"></div>
              </div>

              <!-- NEW: Match Level Badge (Top Left) -->
              <div class="match-badge" :class="getMatchClass(index)">
                 <span v-if="index === 0">🏆 Top Match</span>
                 <span v-else-if="index < 3">🔥 High Match</span>
                 <span v-else>✨ Related</span>
              </div>

              <!-- Badges -->
              <div class="badges">
                 <span v-if="source.verdict === 'Underrated'" class="badge under"><TrendingUp size="12"/> Underrated</span>
                 <span v-if="source.verdict === 'Overrated'" class="badge over"><AlertCircle size="12"/> Overrated</span>
              </div>

              <!-- Info Overlay -->
              <div class="card-content">
                <h3>{{ source.title }}</h3>
                <div class="meta-row">
                   <span class="rating"><Star size="12" fill="currentColor"/> {{ source.rating }}</span>
                   <span class="verdict-text">{{ source.verdict }}</span>
                </div>
                
                <div class="actions">
                  <button class="action-btn primary" @click.stop="openTrailer(source.title)">
                     <PlayCircle size="16"/> Trailer
                  </button>

                  <!-- NEW: Bookmark Button -->
                  <button 
                    class="action-btn secondary" 
                    :class="{ 'bookmarked': bookmarks.has(source.title) }"
                    @click.stop="toggleBookmark(source)"
                  >
                    <Bookmark size="16" :fill="bookmarks.has(source.title) ? 'currentColor' : 'none'" />
                  </button>

                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>

    </main>
    <!-- MDL SYNC MODAL -->
    <transition name="fade">
      <div v-if="showMdlModal" class="modal-overlay" @click.self="showMdlModal = false">
        <div class="modal-card">
          <button class="modal-close" @click="showMdlModal = false"><X size="20"/></button>
          
          <div class="modal-header">
            <div class="modal-icon"><Link size="24"/></div>
            <h3>Sync Your Watchlist</h3>
          </div>
          
          <p class="modal-desc">
            Paste your MyDramaList username or profile URL. 
            We will exclude your "Completed" dramas from recommendations.
          </p>
          
          <div class="modal-input-wrapper">
            <input 
              v-model="mdlUsername" 
              placeholder="e.g. mydramalist.com/profile/uwais" 
              @keydown.enter="syncMDL"
            />
          </div>

          <button class="modal-btn" @click="syncMDL" :disabled="isSyncing || !mdlUsername">
            <Loader2 v-if="isSyncing" class="spin-icon" size="18" />
            <span v-else>Sync Profile</span>
          </button>

          <div v-if="syncStatus" class="sync-status" :class="{ error: syncStatus.includes('Error') }">
            {{ syncStatus }}
          </div>
        </div>
      </div>
    </transition>

    <!-- DETAIL MODAL -->
    <transition name="fade">
      <div v-if="selectedDrama" class="modal-overlay" @click.self="selectedDrama = null">
        <div class="detail-card">
          <button class="modal-close" @click="selectedDrama = null"><X size="24"/></button>
          
          <div class="detail-content">
            <!-- Left: Poster -->
            <div class="detail-poster">
              <img :src="selectedDrama.image_url" alt="Poster" />
              <div class="detail-badges">
                 <span v-if="selectedDrama.verdict === 'Underrated'" class="badge under">Underrated Gem</span>
                 <span v-if="selectedDrama.verdict === 'Overrated'" class="badge over">Overrated</span>
              </div>
            </div>

            <!-- Right: Info -->
            <div class="detail-info">
              <h2>{{ selectedDrama.title }}</h2>
              <div class="detail-meta">
                <span class="pill-year">{{ selectedDrama.year || 'Unknown' }}</span>
                <span class="pill-rating">★ {{ selectedDrama.rating }}</span>
              </div>

              <!-- Tropes (Using metadata tags) -->
              <!-- <div class="detail-tropes" v-if="selectedDrama.tags">
                 <span v-for="tag in selectedDrama.tags.slice(0, 5)" :key="tag" class="trope-pill">
                   #{{ tag }}
                 </span>
              </div> -->

              <!-- 1. AI Tropes (The "Why") -->
              <div class="detail-section" v-if="selectedDrama.tropes_str">
                <span class="label">AI Detected Themes:</span>
                <div class="pill-container">
                  <span v-for="trope in parseList(selectedDrama.tropes_str)" :key="trope" class="trope-pill ai-pill">
                    ✨ {{ trope }}
                  </span>
                </div>
              </div>

              <!-- 2. MDL Tags -->
              <div class="detail-section" v-if="selectedDrama.tags_str">
                <span class="label">MDL Tags:</span>
                <div class="pill-container">
                  <span v-for="tag in parseList(selectedDrama.tags_str).slice(0, 5)" :key="tag" class="trope-pill">
                    #{{ tag }}
                  </span>
                </div>
              </div>

              <div class="detail-desc">
                <p>{{ selectedDrama.synopsis || "No synopsis available." }}</p>
              </div>

              <div class="detail-actions">
                <button class="full-btn primary" @click="openTrailer(selectedDrama.title)">
                  <PlayCircle size="18" /> Watch Trailer
                </button>
                <button class="full-btn secondary" @click="toggleBookmark(selectedDrama)">
                  <Bookmark size="18" :fill="bookmarks.has(selectedDrama.title) ? 'currentColor' : 'none'"/>
                  {{ bookmarks.has(selectedDrama.title) ? 'Saved' : 'Save to List' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* --- LAYOUT & BACKGROUNDS --- */
.app-layout {
  min-height: 100vh;
  position: relative;
  /* Dark Gradient Background */
  background: radial-gradient(circle at top center, #1e1b4b 0%, #020617 80%);
  color: var(--text-main);
}

.noise-overlay {
  position: fixed; inset: 0; pointer-events: none; opacity: 0.03;
  background: url("https://grainy-gradients.vercel.app/noise.svg");
  z-index: 0;
}

.ambient-glow {
  position: fixed; width: 600px; height: 600px; border-radius: 50%;
  filter: blur(100px); opacity: 0.2; z-index: 0;
}
.purple { top: -200px; left: 20%; background: var(--primary); }
.blue { bottom: -200px; right: 20%; background: var(--accent); }

/* Focus Mode Overlay */
.focus-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7);
  opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
  z-index: 90; backdrop-filter: blur(2px);
}
.focus-overlay.active { opacity: 1; }

/* --- HEADER / SEARCH --- */
.top-nav {
  position: fixed; top: 40px; left: 0; right: 0;
  display: flex; flex-direction: column; align-items: center;
  z-index: 100; transition: all 0.5s ease;
}
.nav-expanded {
  top: 0;
  /* Add padding so it doesn't touch the browser edge */
  padding-top: 20px; 
  padding-bottom: 20px;
  background: rgba(2, 6, 23, 0.95); /* Make it darker */
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5); /* Add shadow for depth */
}
.search-island {
  display: flex; align-items: center; gap: 12px;
  background: rgba(30, 41, 59, 0.6); /* Dark Glass */
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  padding: 8px 16px;
  border-radius: 100px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  width: 90%; max-width: 700px;
  transition: all 0.3s ease;
}

.island-focused {
  transform: scale(1.05);
  background: rgba(30, 41, 59, 0.9);
  border-color: var(--primary);
  box-shadow: 0 0 30px rgba(217, 70, 239, 0.2);
}

.logo { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.1rem; white-space: nowrap; }
.highlight { color: var(--primary); }

.search-wrapper { flex: 1; display: flex; align-items: center; }
.search-wrapper input {
  width: 100%; background: transparent; border: none; color: white;
  font-size: 1rem; outline: none; padding: 10px;
}
.search-wrapper input::placeholder { color: rgba(255,255,255,0.4); }

.search-btn {
  background: var(--primary); border: none; color: white; cursor: pointer;
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.search-btn:hover { transform: scale(1.1); box-shadow: 0 0 15px var(--primary-glow); }
.search-btn:disabled { background: #333; cursor: wait; }

.divider { width: 1px; height: 24px; background: var(--glass-border); margin: 0 5px; }

.filter-toggle {
  background: transparent; border: none; color: var(--text-muted);
  cursor: pointer; padding: 8px; border-radius: 50%; transition: 0.2s;
}
.filter-toggle:hover { color: white; background: rgba(255,255,255,0.1); }
.btn-active { color: var(--primary); background: rgba(217, 70, 239, 0.1); }

.avatar-circle {
  width: 32px; height: 32px; background: #000; border: 1px solid var(--glass-border);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 0.6rem; font-weight: bold; color: #888;
}

/* --- FILTER DRAWER --- */
.filter-drawer {
  background: #0f172a; /* Slate 900 */
  border: 1px solid var(--glass-border);
  width: 90%; max-width: 700px; border-radius: 16px;
  margin-top: 12px; padding: 24px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 20px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.5);
}

.filter-col label { 
  display: block; color: var(--text-muted); font-size: 0.75rem; 
  margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; 
}

/* Custom Selects & Inputs (High Contrast) */
.select-wrapper { position: relative; }
.select-wrapper select {
  width: 100%; appearance: none;
  background: #1e293b; /* Dark Slate */
  border: 1px solid #334155;
  color: white; padding: 10px; border-radius: 8px;
  cursor: pointer; font-size: 0.9rem;
}
.select-icon { position: absolute; right: 10px; top: 12px; color: #94a3b8; pointer-events: none; }

.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chips span {
  font-size: 0.75rem; padding: 6px 12px; border-radius: 20px;
  background: #1e293b; color: var(--text-muted); border: 1px solid #334155;
  cursor: pointer; transition: 0.2s;
}
.chips span:hover { border-color: var(--primary); color: white; }
.chips span.active { background: var(--primary); color: white; border-color: var(--primary); }

.range-slider {
  width: 100%; -webkit-appearance: none; height: 4px; background: #334155; border-radius: 2px;
}
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 16px; height: 16px; background: var(--primary);
  border-radius: 50%; cursor: pointer; box-shadow: 0 0 10px var(--primary);
}
.range-labels { display: flex; justify-content: space-between; font-size: 0.7rem; color: #64748b; margin-top: 8px; }

/* --- HERO SECTION --- */
.hero-section {
  text-align: center; margin-top: 25vh;
  display: flex; flex-direction: column; align-items: center;
}
.hero-section h1 {
  font-family: 'Space Grotesk', sans-serif; font-size: 4rem;
  line-height: 1.1; margin-bottom: 20px;
}
.gradient-text {
  background: linear-gradient(135deg, #d946ef, #8b5cf6);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { color: var(--text-muted); font-size: 1.1rem; max-width: 500px; margin-bottom: 40px; }

.trending-preview { display: flex; gap: 15px; }
.preview-card {
  width: 90px; height: 135px; border-radius: 8px;
  background-size: cover; background-position: center;
  transform: rotate(-5deg); border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 10px 20px rgba(0,0,0,0.5);
}
.preview-card:nth-child(2) { transform: rotate(0deg); margin-top: -15px; z-index: 2; }
.preview-card:nth-child(3) { transform: rotate(5deg); }

/* --- LOADING --- */
.loading-container { text-align: center; margin-top: 150px; }
.scanner-line {
  width: 200px; height: 2px; background: linear-gradient(90deg, transparent, var(--primary), transparent);
  margin: 0 auto 15px; animation: scan 1.5s infinite ease-in-out;
}
.pulse-ring {
  width: 20px; height: 20px; border: 2px solid white; border-top-color: transparent;
  border-radius: 50%; animation: spin 1s linear infinite;
}

/* --- RESULTS --- */
.content-area { padding-top: 100px; padding-bottom: 50px; width: 90%; max-width: 1200px; margin: 0 auto; z-index: 10; position: relative; }

.ai-insight {
  background: rgba(15, 23, 42, 0.6); border: 1px solid var(--glass-border);
  padding: 24px; border-radius: 16px; margin-bottom: 40px; max-width: 800px; margin-left: auto; margin-right: auto;
  backdrop-filter: blur(10px);
}
.insight-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; color: var(--primary); font-weight: bold; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
.insight-content { line-height: 1.7; color: #e2e8f0; }
.insight-content :deep(strong) { color: var(--primary); font-weight: 600; }

/* BENTO GRID */
.bento-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}
.drama-card {
  position: relative; height: 320px; border-radius: 12px; overflow: hidden;
  border: 1px solid var(--glass-border); transition: all 0.4s ease; cursor: pointer;
  background: #000;
}
.drama-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.6); border-color: var(--primary); }
.card-bg img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }
.drama-card:hover .card-bg img { transform: scale(1.1); }
.overlay-gradient { position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,0.95), transparent 50%); }

.badges { position: absolute; top: 10px; left: 10px; display: flex; flex-direction: column; gap: 5px; z-index: 5; }
.badge { font-size: 0.6rem; padding: 4px 8px; border-radius: 6px; font-weight: 600; display: flex; gap: 4px; backdrop-filter: blur(8px); }
.under { background: rgba(16, 185, 129, 0.9); color: white; }
.over { background: rgba(239, 68, 68, 0.9); color: white; }

.card-content { position: absolute; bottom: 0; width: 100%; padding: 16px; transform: translateY(50px); transition: transform 0.3s ease; }
.drama-card:hover .card-content { transform: translateY(0); }
.card-content h3 { font-size: 1rem; color: white; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.meta-row { display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8; margin-bottom: 12px; }
.rating { color: #facc15; display: flex; gap: 4px; }

.actions { display: flex; gap: 8px; }
.action-btn { flex: 1; padding: 8px; border-radius: 6px; border: none; cursor: pointer; font-size: 0.75rem; font-weight: 600; display: flex; justify-content: center; gap: 4px; }
.primary { background: white; color: black; }
.primary:hover { background: var(--primary); color: white; }
.secondary { background: rgba(255,255,255,0.1); color: white; backdrop-filter: blur(5px); }
.secondary:hover { background: rgba(255,255,255,0.2); }

/* Animations */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes scan { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

/* Vue Transitions */
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease-out; max-height: 500px; opacity: 1; }
.slide-down-enter-from, .slide-down-leave-to { max-height: 0; opacity: 0; overflow: hidden; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.fade-up-enter-active { transition: all 0.6s ease-out; }
.fade-up-enter-from { opacity: 0; transform: translateY(20px); }

/* --- MDL MODAL --- */
.modal-overlay {
  position: fixed; inset: 0; 
  background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(8px);
  z-index: 2000;
  display: flex; align-items: center; justify-content: center;
}

.modal-card {
  background: #0f172a; border: 1px solid var(--glass-border);
  width: 90%; max-width: 400px;
  padding: 30px; border-radius: 24px;
  position: relative;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5);
  text-align: center;
  animation: scaleUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-close {
  position: absolute; top: 15px; right: 15px;
  background: none; border: none; color: #64748b; cursor: pointer;
  padding: 5px; border-radius: 50%; transition: 0.2s;
}
.modal-close:hover { background: rgba(255,255,255,0.1); color: white; }

.modal-header { display: flex; flex-direction: column; align-items: center; gap: 15px; margin-bottom: 15px; }
.modal-icon {
  width: 60px; height: 60px; background: rgba(139, 92, 246, 0.1);
  color: var(--accent); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.modal-desc { font-size: 0.9rem; color: #94a3b8; line-height: 1.5; margin-bottom: 20px; }

.modal-input-wrapper input {
  width: 100%; background: #1e293b; border: 1px solid #334155;
  color: white; padding: 12px; border-radius: 12px;
  outline: none; margin-bottom: 15px; text-align: center;
}
.modal-input-wrapper input:focus { border-color: var(--accent); }

.modal-btn {
  width: 100%; padding: 12px; background: var(--primary);
  color: white; font-weight: 600; border: none; border-radius: 12px;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: 0.2s;
}
.modal-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(217, 70, 239, 0.4); }
.modal-btn:disabled { background: #334155; color: #64748b; cursor: not-allowed; }

.sync-status { margin-top: 15px; font-size: 0.85rem; color: #10b981; }
.sync-status.error { color: #ef4444; }

.avatar-active {
  border-color: #10b981; color: #10b981; background: rgba(16, 185, 129, 0.1);
}

@keyframes scaleUp { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.spin-icon { animation: spin 1s linear infinite; }

/* --- MDL PROFILE ICON --- */
.user-profile {
  cursor: pointer; /* Fixes the 'text cursor' issue */
  position: relative;
  margin-left: 10px;
}

.avatar-circle {
  width: 35px; height: 35px; 
  background: rgba(0,0,0,0.5); 
  border: 1px solid var(--glass-border);
  border-radius: 50%; 
  display: flex; align-items: center; justify-content: center;
  font-size: 0.65rem; font-weight: 700; color: var(--text-muted);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); /* Bouncy transition */
}

/* Hover Feedback: Glow + Pop */
.user-profile:hover .avatar-circle {
  border-color: var(--primary);
  color: white;
  background: var(--primary-glow); /* Uses the glow variable we defined in main.css */
  transform: scale(1.15) rotate(5deg);
  box-shadow: 0 0 15px var(--primary-glow);
}

/* Active State (When synced) */
.avatar-active {
  border-color: #10b981 !important; 
  color: #10b981 !important; 
  background: rgba(16, 185, 129, 0.15) !important;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
}

/* BOOKMARK ACTIVE STATE */
.bookmarked {
  color: var(--primary) !important;
  background: rgba(217, 70, 239, 0.1) !important;
  border: 1px solid var(--primary);
}

/* DETAIL MODAL STYLES */
.detail-card {
  background: #0f172a; 
  border: 1px solid var(--glass-border);
  width: 90%; max-width: 800px;
  border-radius: 24px;
  position: relative;
  box-shadow: 0 50px 100px -20px rgba(0,0,0,0.8);
  overflow: hidden;
  animation: scaleUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.detail-content {
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .detail-content { flex-direction: row; }
}

/* POSTER SIDE */
.detail-poster {
  position: relative;
  width: 100%;
  height: 300px;
  background: #000;
}
@media (min-width: 768px) {
  .detail-poster { width: 40%; height: auto; min-height: 450px; }
}

.detail-poster img {
  width: 100%; height: 100%; object-fit: cover;
  opacity: 0.8;
}
.detail-badges {
  position: absolute; bottom: 15px; left: 15px;
  display: flex; gap: 8px;
}

/* INFO SIDE */
.detail-info {
  padding: 30px;
  flex: 1;
  display: flex; flex-direction: column; gap: 15px;
}

.detail-info h2 { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; line-height: 1.1; margin-bottom: 5px; }

.detail-meta { display: flex; gap: 10px; align-items: center; }
.pill-year { background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; }
.pill-rating { color: #facc15; font-weight: bold; font-size: 0.9rem; }

.detail-tropes { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.trope-pill { 
  font-size: 0.75rem; color: var(--accent); 
  background: rgba(139, 92, 246, 0.1); 
  padding: 4px 8px; border-radius: 100px;
}

.detail-desc {
  flex: 1; overflow-y: auto; max-height: 200px;
  color: #94a3b8; line-height: 1.6; font-size: 0.95rem;
  padding-right: 10px;
  /* Scrollbar styling */
  scrollbar-width: thin; scrollbar-color: #333 transparent;
}

.detail-actions { display: flex; gap: 10px; margin-top: 20px; }
.full-btn {
  flex: 1; padding: 12px; border-radius: 12px; border: none; cursor: pointer;
  font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: 0.2s;
}
.full-btn.primary { background: white; color: black; }
.full-btn.primary:hover { background: var(--primary); color: white; }
.full-btn.secondary { background: rgba(255,255,255,0.1); color: white; }
.full-btn.secondary:hover { background: rgba(255,255,255,0.2); }

.detail-section { margin-bottom: 15px; }
.label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; display: block; margin-bottom: 5px; font-weight: bold; }

.pill-container { display: flex; flex-wrap: wrap; gap: 6px; }

.trope-pill { 
  font-size: 0.75rem; color: #94a3b8; 
  border: 1px solid #334155;
  padding: 4px 10px; border-radius: 100px;
}

/* Special Style for AI Tropes to make them stand out */
.ai-pill {
  border-color: var(--primary);
  color: #f0abfc; /* Light Purple */
  background: rgba(217, 70, 239, 0.1);
}

/* --- TOP PICK GLOW --- */
.card-top-pick {
  border: 2px solid #fbbf24 !important; /* Gold Border */
  box-shadow: 0 0 30px rgba(251, 191, 36, 0.2);
  transform: scale(1.02); /* Make it slightly bigger by default */
}
.card-top-pick:hover {
  transform: scale(1.05) translateY(-8px);
  box-shadow: 0 0 50px rgba(251, 191, 36, 0.4);
}

/* --- MATCH BADGES --- */
.match-badge {
  position: absolute; top: 10px; left: 10px;
  font-size: 0.65rem; font-weight: 800; text-transform: uppercase;
  padding: 4px 10px; border-radius: 100px;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  z-index: 5;
}

.match-top {
  background: linear-gradient(135deg, #fbbf24, #d97706);
  color: black;
  border: 1px solid rgba(255,255,255,0.4);
}

.match-high {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.match-base {
  background: rgba(0, 0, 0, 0.4);
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Move the existing badges to Top Right */
.badges {
  left: auto; /* Reset left */
  right: 10px; /* Move to right */
  align-items: flex-end;
}

/* =========================================
   MOBILE RESPONSIVENESS OVERRIDES
   Add this to the very bottom of your CSS
   ========================================= */

@media (max-width: 768px) {
  /* 1. Header Adjustments */
  .search-island {
    width: 95%; /* Use full width */
    padding: 8px 10px;
    gap: 8px;
  }
  
  .logo {
    display: none; /* Hide logo on phone to give space to search bar */
  }

  .hero-section h1 {
    font-size: 2.5rem; /* Smaller hero text */
  }

  /* 2. Grid Layout (2 Columns instead of dynamic) */
  .bento-grid {
    grid-template-columns: repeat(2, 1fr); /* Force 2 columns */
    gap: 10px;
  }

  .drama-card {
    height: 250px; /* Shorter cards */
  }

  /* 3. Card Content (Disable Hover Effects for Mobile) */
  /* On phone, you can't "hover", so we always show the title */
  .card-content {
    transform: translateY(0) !important; /* Always show */
    padding: 10px;
    background: linear-gradient(to top, rgba(0,0,0,0.9) 20%, transparent);
  }

  /* Hide the "Trailer/Bookmark" buttons on card cover (too small to tap) */
  /* Users can use the buttons inside the Modal instead */
  .actions {
    display: none !important;
  }

  /* Adjust Text Sizes */
  .card-content h3 {
    font-size: 0.9rem;
    white-space: normal; /* Allow wrapping */
    line-height: 1.2;
  }
  
  .meta-row {
    margin-bottom: 0;
  }

  /* 4. Modal (Stack Vertically) */
  .detail-card {
    width: 95%;
    max-height: 85vh; /* Prevent overflowing screen */
    margin: 10px;
    display: flex;
    flex-direction: column;
  }

  .detail-content {
    flex-direction: column; /* Stack Poster on top of Info */
  }

  .detail-poster {
    width: 100%;
    height: 200px; /* Short header image */
    min-height: auto;
  }

  .detail-info {
    padding: 20px;
    overflow-y: auto; /* Scroll info if long */
  }

  .detail-info h2 {
    font-size: 1.5rem;
  }
  
  /* 5. Filter Drawer */
  .filter-drawer {
    width: 95%;
    grid-template-columns: 1fr; /* Stack filters vertically */
    padding: 15px;
  }
}
</style>