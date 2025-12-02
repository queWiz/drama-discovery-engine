<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { marked } from 'marked'
import { Search, SlidersHorizontal, Star, PlayCircle, Bookmark, TrendingUp, AlertCircle, X, ChevronDown } from 'lucide-vue-next'

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

const formattedAnswer = computed(() => answer.value ? marked(answer.value) : '')

const askAI = async () => {
  if (!query.value) return
  
  loading.value = true
  hasSearched.value = true
  answer.value = ''
  sources.value = []
  showFilters.value = false 
  isFocused.value = false // Remove focus mode on search
  
  try {
    const response = await axios.post('http://127.0.0.1:8000/chat', {
      message: query.value,
      genre: selectedGenre.value,
      rating: parseInt(selectedRating.value),
      year: selectedYear.value,
      trope: selectedTrope.value
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
        <div class="user-profile">
          <div class="avatar-circle">MDL</div>
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
            <div v-for="(source, index) in sources" :key="index" class="drama-card">
              
              <!-- Poster -->
              <div class="card-bg">
                <img :src="source.image_url || 'https://via.placeholder.com/300x450'" loading="lazy" />
                <div class="overlay-gradient"></div>
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
                  <button class="action-btn secondary">
                     <Bookmark size="16"/>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>

    </main>
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
</style>