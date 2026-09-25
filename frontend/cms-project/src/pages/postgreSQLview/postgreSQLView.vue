<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import MainAdminLayout from '@/layouts/MainAdminLayout.vue'
import { APP_CONFIG } from '@/config'
import { STORAGE_KEYS } from '@/constants'
import { storage } from '@/utils'
import { useRouter } from 'vue-router'
import { authService } from '@/services/authService'

const router = useRouter()

// --- State Database & Overview ---
const overview = ref(null)
const selectedTable = ref('')
const activeTab = ref('data') // 'data' | 'schema' | 'erd' | 'roadmap' | 'query' | 'metrics'
const tableSearchQuery = ref('')
const selectedCategory = ref('all')
const isMobileTableListOpen = ref(false)

// --- State Data Preview & Pagination ---
const preview = ref(null)
const previewLimit = ref(25)
const previewOffset = ref(0)
const dataSearchQuery = ref('')
const sortColumn = ref('')
const sortDirection = ref('asc')

// --- Loading & Notification States ---
const isLoading = ref(true)
const isSyncing = ref(false)
const isPreviewLoading = ref(false)
const isChecking = ref(false)
const isOptimizing = ref(false)
const errorMessage = ref('')
const noticeMessage = ref('')
const latencyMs = ref(null)
const toastMessage = ref('')
const isToastVisible = ref(false)

// --- Row Inspector Modal ---
const selectedRow = ref(null)
const isRowModalOpen = ref(false)

// --- DDL Schema Modal ---
const isDdlModalOpen = ref(false)
const isDdlLoading = ref(false)
const ddlContent = ref('')

// --- ERD / UML Interactive Graph State ---
const erdData = ref({ nodes: [], edges: [] })
const isErdLoading = ref(false)
const selectedErdNode = ref(null)
const erdCategoryFilter = ref('all')

// --- Safe SQL Query Console State ---
const sqlQuery = ref('SELECT id, name, denomination, city, province FROM churches ORDER BY id DESC LIMIT 10;')
const isQueryRunning = ref(false)
const queryResult = ref(null)
const queryError = ref('')
const queryHistory = ref([])

const sampleQueries = [
	{
		label: '10 Gereja Terbaru',
		sql: 'SELECT id, name, denomination, city, province FROM churches ORDER BY id DESC LIMIT 10;'
	},
	{
		label: 'Pemasukan per Kategori',
		sql: 'SELECT kategori, COUNT(*) AS jumlah_transaksi, SUM(jumlah) AS total_nominal FROM pemasukan_gereja GROUP BY kategori ORDER BY total_nominal DESC;'
	},
	{
		label: 'Pengeluaran per Status',
		sql: 'SELECT status_persetujuan, COUNT(*) AS total_nota, SUM(jumlah) AS total_pengeluaran FROM pengeluaran_gereja GROUP BY status_persetujuan;'
	},
	{
		label: 'Distribusi Jemaat',
		sql: 'SELECT church_id, COUNT(*) AS total_jemaat FROM jemaat_users GROUP BY church_id ORDER BY total_jemaat DESC;'
	},
	{
		label: 'Aktivitas PostgreSQL',
		sql: 'SELECT datname, usename, client_addr, state, backend_start FROM pg_stat_activity WHERE datname = current_database();'
	}
]

const showToast = (msg) => {
	toastMessage.value = msg
	isToastVisible.value = true
	setTimeout(() => {
		isToastVisible.value = false
	}, 3200)
}

const authHeaders = () => {
	const token = storage.get(STORAGE_KEYS.AUTH_TOKEN)
	return token ? { Authorization: `Bearer ${token}` } : {}
}

const apiRequest = async (path, options = {}) => {
	const response = await fetch(`${APP_CONFIG.apiBaseUrl}${path}`, {
		...options,
		headers: { ...authHeaders(), ...(options.headers || {}) },
	})
	if (!response.ok) {
		const data = await response.json().catch(() => ({}))
		if (response.status === 401) {
			authService.logout()
			await router.replace({ name: 'main-login', query: { redirect: '/server-postgresql' } })
		}
		throw new Error(data.detail || 'Permintaan DBMS gagal diproses.')
	}
	return response.json()
}

// --- Load Overview Dinamis ---
const loadOverview = async (isSync = false) => {
	if (isSync) isSyncing.value = true
	else isLoading.value = true
	errorMessage.value = ''
	try {
		const res = await apiRequest('/database/overview')
		overview.value = res

		if (!selectedTable.value && res.tables && res.tables.length > 0) {
			selectedTable.value = res.tables[0].name
		} else if (selectedTable.value && !res.tables.some(t => t.name === selectedTable.value)) {
			selectedTable.value = res.tables[0]?.name || ''
		}

		if (isSync) {
			showToast(`Skema database diselaraskan: ${res.tables.length} tabel aktif terdeteksi.`)
		}

		if (selectedTable.value) {
			await loadPreview()
		}
		loadErdSchema()
	} catch (error) {
		errorMessage.value = error.message || 'Gagal memuat ringkasan database PostgreSQL.'
	} finally {
		isLoading.value = false
		isSyncing.value = false
	}
}

// --- Tes Koneksi & Latensi ---
const checkConnection = async () => {
	isChecking.value = true
	errorMessage.value = ''
	noticeMessage.value = ''
	try {
		const result = await apiRequest('/database/connection-check', { method: 'POST' })
		noticeMessage.value = result.message
		latencyMs.value = result.latency_ms
		showToast(result.message)
		await loadOverview()
	} catch (error) {
		errorMessage.value = error.message || 'Tes koneksi database gagal.'
	} finally {
		isChecking.value = false
	}
}

// --- Load Preview Data Tabel ---
const loadPreview = async () => {
	if (!selectedTable.value) return
	isPreviewLoading.value = true
	errorMessage.value = ''
	try {
		let queryUrl = `/database/tables/${encodeURIComponent(selectedTable.value)}?limit=${previewLimit.value}&offset=${previewOffset.value}`
		if (dataSearchQuery.value.trim()) {
			queryUrl += `&search=${encodeURIComponent(dataSearchQuery.value.trim())}`
		}
		if (sortColumn.value) {
			queryUrl += `&sort_by=${encodeURIComponent(sortColumn.value)}&sort_dir=${sortDirection.value}`
		}
		preview.value = await apiRequest(queryUrl)
	} catch (error) {
		errorMessage.value = error.message || 'Preview tabel gagal dimuat.'
		preview.value = null
	} finally {
		isPreviewLoading.value = false
	}
}

// --- Muat Ulang Data (Refresh Action) ---
const refreshTableData = async () => {
	await loadPreview()
	showToast(`Data tabel ${selectedTable.value} diperbarui.`)
}

// --- Reset Filter & Sorting ---
const resetDataFilters = () => {
	dataSearchQuery.value = ''
	sortColumn.value = ''
	sortDirection.value = 'asc'
	previewOffset.value = 0
	loadPreview()
	showToast('Filter pencarian & pengurutan telah direset.')
}

// --- Pilihan Tabel ---
const selectTable = (tableName) => {
	selectedTable.value = tableName
	previewOffset.value = 0
	dataSearchQuery.value = ''
	sortColumn.value = ''
	sortDirection.value = 'asc'
	if (activeTab.value !== 'data' && activeTab.value !== 'schema' && activeTab.value !== 'metrics') {
		activeTab.value = 'data'
	}
	isMobileTableListOpen.value = false
	loadPreview()
}

// --- Sorting Kolom ---
const handleSort = (colName) => {
	if (sortColumn.value === colName) {
		sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
	} else {
		sortColumn.value = colName
		sortDirection.value = 'asc'
	}
	previewOffset.value = 0
	loadPreview()
}

// --- Search Filter Data Baris ---
let searchDebounce = null
const onDataSearchInput = () => {
	clearTimeout(searchDebounce)
	searchDebounce = setTimeout(() => {
		previewOffset.value = 0
		loadPreview()
	}, 400)
}

// --- Navigasi Halaman Data ---
const totalRows = computed(() => preview.value?.total_rows || 0)
const totalPages = computed(() => Math.ceil(totalRows.value / previewLimit.value) || 1)
const currentPage = computed(() => Math.floor(previewOffset.value / previewLimit.value) + 1)

const goToPage = (page) => {
	if (page < 1 || page > totalPages.value) return
	previewOffset.value = (page - 1) * previewLimit.value
	loadPreview()
}

const onLimitChange = () => {
	previewOffset.value = 0
	loadPreview()
}

// --- Inspeksi Baris ---
const openRowInspector = (row) => {
	selectedRow.value = row
	isRowModalOpen.value = true
}

const closeRowInspector = () => {
	isRowModalOpen.value = false
	selectedRow.value = null
}

// --- Ekspor Data CSV ---
const exportCsv = () => {
	if (!preview.value || !preview.value.rows || preview.value.rows.length === 0) {
		showToast('Tidak ada data untuk diekspor.')
		return
	}
	const rows = preview.value.rows
	const headers = Object.keys(rows[0] || {})
	const csvRows = [headers.join(',')]

	for (const row of rows) {
		const values = headers.map(h => {
			const val = row[h]
			const escaped = ('' + (val ?? '')).replace(/"/g, '""')
			return `"${escaped}"`
		})
		csvRows.push(values.join(','))
	}

	const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' })
	const url = URL.createObjectURL(blob)
	const a = document.createElement('a')
	a.href = url
	a.download = `${selectedTable.value}_export_${new Date().toISOString().slice(0, 10)}.csv`
	a.click()
	URL.revokeObjectURL(url)
	showToast(`Berhasil mengekspor ${selectedTable.value}.csv`)
}

// --- Ekspor Data JSON ---
const exportJson = () => {
	if (!preview.value || !preview.value.rows || preview.value.rows.length === 0) {
		showToast('Tidak ada data untuk diekspor.')
		return
	}
	const dataStr = JSON.stringify(preview.value.rows, null, 2)
	const blob = new Blob([dataStr], { type: 'application/json;charset=utf-8;' })
	const url = URL.createObjectURL(blob)
	const a = document.createElement('a')
	a.href = url
	a.download = `${selectedTable.value}_export_${new Date().toISOString().slice(0, 10)}.json`
	a.click()
	URL.revokeObjectURL(url)
	showToast(`Berhasil mengekspor ${selectedTable.value}.json`)
}

// --- Salin SQL INSERT ---
const copySqlInserts = async () => {
	if (!preview.value || !preview.value.rows || preview.value.rows.length === 0) {
		showToast('Tidak ada data untuk disalin.')
		return
	}
	const rows = preview.value.rows
	const headers = Object.keys(rows[0] || {})
	const tableName = selectedTable.value

	const statements = rows.map(r => {
		const cols = headers.map(h => `"${h}"`).join(', ')
		const vals = headers.map(h => {
			const v = r[h]
			if (v === null) return 'NULL'
			if (typeof v === 'number' || typeof v === 'boolean') return `${v}`
			return `'${('' + v).replace(/'/g, "''")}'`
		}).join(', ')
		return `INSERT INTO "${tableName}" (${cols}) VALUES (${vals});`
	})

	const fullSql = statements.join('\n')
	try {
		await navigator.clipboard.writeText(fullSql)
		showToast(`Berhasil menyalin ${statements.length} baris SQL INSERT!`)
	} catch {
		showToast('Gagal menyalin ke clipboard.')
	}
}

// --- DDL Skema Modal ---
const openDdlModal = async () => {
	if (!selectedTable.value) return
	isDdlLoading.value = true
	isDdlModalOpen.value = true
	ddlContent.value = ''
	try {
		const res = await apiRequest(`/database/tables/${encodeURIComponent(selectedTable.value)}/ddl`)
		ddlContent.value = res.ddl || ''
	} catch (err) {
		ddlContent.value = `-- Gagal memuat DDL: ${err.message}`
	} finally {
		isDdlLoading.value = false
	}
}

const copyDdl = async () => {
	if (!ddlContent.value) return
	try {
		await navigator.clipboard.writeText(ddlContent.value)
		showToast('Skema DDL SQL berhasil disalin!')
	} catch {
		showToast('Gagal menyalin DDL.')
	}
}

// --- Optimasi Tabel (VACUUM ANALYZE) ---
const optimizeCurrentTable = async () => {
	if (!selectedTable.value) return
	if (!confirm(`Jalankan pembersihan dead tuples dan optimasi indeks (ANALYZE) untuk tabel "${selectedTable.value}"?`)) {
		return
	}
	isOptimizing.value = true
	try {
		const res = await apiRequest(`/database/tables/${encodeURIComponent(selectedTable.value)}/vacuum`, {
			method: 'POST'
		})
		showToast(res.message || `Tabel ${selectedTable.value} berhasil dioptimasi!`)
		await loadOverview()
	} catch (err) {
		showToast(`Gagal optimasi: ${err.message}`)
	} finally {
		isOptimizing.value = false
	}
}

// --- Load ERD Schema ---
const loadErdSchema = async () => {
	isErdLoading.value = true
	try {
		const res = await apiRequest('/database/erd-schema')
		erdData.value = res
	} catch {
		// Silent fallback
	} finally {
		isErdLoading.value = false
	}
}

// --- Safe SQL Query Runner ---
const runSqlQuery = async () => {
	if (!sqlQuery.value.trim()) {
		queryError.value = 'Silakan masukkan kueri SQL.'
		return
	}
	isQueryRunning.value = true
	queryError.value = ''
	queryResult.value = null
	try {
		const res = await apiRequest('/database/query', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ query: sqlQuery.value.trim() })
		})
		queryResult.value = res
		if (!queryHistory.value.includes(sqlQuery.value.trim())) {
			queryHistory.value.unshift(sqlQuery.value.trim())
			if (queryHistory.value.length > 5) queryHistory.value.pop()
		}
		showToast(`Kueri sukses dieksekusi (${res.execution_ms} ms, ${res.total_rows} baris).`)
	} catch (err) {
		queryError.value = err.message || 'Eksekusi kueri gagal.'
	} finally {
		isQueryRunning.value = false
	}
}

const setPresetQuery = (sql) => {
	sqlQuery.value = sql
	runSqlQuery()
}

// --- Computed Filters & Metrics ---
const tableCount = computed(() => overview.value?.tables?.length || 0)
const totalDatabaseRows = computed(() => overview.value?.total_rows ?? (overview.value?.tables?.reduce((tot, t) => tot + t.rows, 0) || 0))

const categories = computed(() => {
	if (!overview.value?.tables) return []
	const cats = new Set(overview.value.tables.map(t => t.category || 'Modul Lainnya'))
	return Array.from(cats)
})

const filteredTables = computed(() => {
	if (!overview.value?.tables) return []
	let list = overview.value.tables

	if (selectedCategory.value !== 'all') {
		list = list.filter(t => t.category === selectedCategory.value)
	}

	if (tableSearchQuery.value.trim()) {
		const q = tableSearchQuery.value.trim().toLowerCase()
		list = list.filter(t => t.name.toLowerCase().includes(q) || t.label.toLowerCase().includes(q))
	}

	return list
})

const currentTableMeta = computed(() => {
	return overview.value?.tables?.find(t => t.name === selectedTable.value) || null
})

// --- ERD Filtering & Highlighting ---
const filteredErdNodes = computed(() => {
	if (!erdData.value.nodes) return []
	if (erdCategoryFilter.value === 'all') return erdData.value.nodes
	return erdData.value.nodes.filter(n => n.category === erdCategoryFilter.value)
})

const isNodeHighlighted = (nodeId) => {
	if (!selectedErdNode.value) return true
	if (selectedErdNode.value === nodeId) return true
	return erdData.value.edges?.some(
		e => (e.from === selectedErdNode.value && e.to === nodeId) || (e.to === selectedErdNode.value && e.from === nodeId)
	)
}

const activeErdEdges = computed(() => {
	if (!erdData.value.edges) return []
	if (erdCategoryFilter.value === 'all' && !selectedErdNode.value) return erdData.value.edges
	return erdData.value.edges.filter(e => {
		if (selectedErdNode.value) {
			return e.from === selectedErdNode.value || e.to === selectedErdNode.value
		}
		return true
	})
})

const selectErdNode = (nodeId) => {
	if (selectedErdNode.value === nodeId) {
		selectedErdNode.value = null
	} else {
		selectedErdNode.value = nodeId
	}
}

watch(selectedTable, () => {
	previewOffset.value = 0
})

onMounted(() => {
	loadOverview()
})
</script>

<template>
	<MainAdminLayout>
		<div class="relative space-y-4 sm:space-y-6 text-[#EDE6D6] max-w-7xl mx-auto px-1 sm:px-2">
			<!-- Background Glow & Accent -->
			<div class="pointer-events-none fixed inset-0 -z-10 bg-[#0B2027]"></div>
			<div class="pointer-events-none fixed -top-40 right-0 h-[34rem] w-[34rem] rounded-full bg-emerald-500/5 blur-3xl -z-10"></div>
			<div class="pointer-events-none fixed bottom-10 left-10 h-72 w-72 rounded-full bg-blue-500/5 blur-3xl -z-10"></div>

			<!-- TOP BANNER: Control Center Header -->
			<section class="rounded-2xl sm:rounded-3xl border border-emerald-500/25 bg-[#123138]/85 p-4 sm:p-6 lg:p-8 shadow-2xl backdrop-blur-xl relative overflow-hidden">
				<div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between relative z-10">
					<div class="space-y-1.5 sm:space-y-2">
						<div class="flex items-center gap-2 flex-wrap">
							<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-bold uppercase tracking-wider border border-emerald-500/40">
								<span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
								Live Database Engine
							</span>
							<span class="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">
								PostgreSQL Multi-Schema
							</span>
						</div>
						<h1 class="font-serif text-2xl sm:text-3xl lg:text-4xl font-extrabold text-[#F5EFE0] tracking-tight">
							PostgreSQL Control Center
						</h1>
						<p class="max-w-2xl text-xs sm:text-sm leading-relaxed text-[#B8C4C2]">
							Sistem adaptif yang otomatis mendeteksi pertumbuhan tabel, relasi kunci asing, skema DDL, diagram UML/ERD interaktif, serta roadmap arsitektur data CMS secara menyeluruh.
						</p>
					</div>

					<!-- Header Action Buttons -->
					<div class="flex flex-wrap items-center gap-2 pt-2 lg:pt-0">
						<button 
							type="button" 
							:disabled="isChecking" 
							class="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 rounded-xl border border-emerald-400/30 bg-emerald-500/10 px-3.5 sm:px-4 py-2 sm:py-2.5 text-xs font-semibold text-emerald-300 transition hover:bg-emerald-500/20 disabled:opacity-50 cursor-pointer shadow-sm active:scale-95"
							@click="checkConnection"
							title="Periksa konektivitas dan latensi respon PostgreSQL"
						>
							<span class="h-2 w-2 rounded-full bg-emerald-400" :class="{ 'animate-ping': isChecking }"></span>
							<span>{{ isChecking ? 'Menguji...' : (latencyMs ? `Aktif (${latencyMs} ms)` : 'Tes Koneksi') }}</span>
						</button>

						<button 
							type="button" 
							:disabled="isSyncing || isLoading" 
							class="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 px-3.5 sm:px-4 py-2 sm:py-2.5 text-xs font-semibold text-slate-200 transition disabled:opacity-50 cursor-pointer active:scale-95"
							@click="loadOverview(true)"
							title="Deteksi ulang seluruh tabel dan skema database terkini"
						>
							<i class="bi bi-arrow-repeat text-emerald-400" :class="{ 'animate-spin': isSyncing }"></i>
							<span>{{ isSyncing ? 'Menyelaraskan...' : 'Sinkronkan Skema' }}</span>
						</button>
					</div>
				</div>
			</section>

			<!-- ALERT MESSAGES -->
			<div v-if="errorMessage" class="rounded-xl sm:rounded-2xl border border-rose-500/40 bg-rose-950/50 p-3 sm:p-4 text-xs sm:text-sm text-rose-200 flex items-start gap-2.5 shadow-lg">
				<i class="bi bi-exclamation-triangle-fill text-rose-400 text-base shrink-0 mt-0.5"></i>
				<div>
					<strong>Terjadi Kendala DBMS:</strong>
					<p class="mt-0.5">{{ errorMessage }}</p>
				</div>
			</div>

			<div v-if="noticeMessage" class="rounded-xl sm:rounded-2xl border border-emerald-500/40 bg-emerald-950/50 p-3 sm:p-4 text-xs sm:text-sm text-emerald-200 flex items-start gap-2.5 shadow-lg">
				<i class="bi bi-check-circle-fill text-emerald-400 text-base shrink-0 mt-0.5"></i>
				<div>
					<strong>Status Sistem:</strong>
					<p class="mt-0.5">{{ noticeMessage }}</p>
				</div>
			</div>

			<!-- DATABASE HEALTH & STATS METRICS (5 Cards) -->
			<section v-if="overview" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-4">
				<div class="rounded-xl sm:rounded-2xl border border-white/10 bg-[#123138]/70 p-3.5 sm:p-4 shadow-lg flex flex-col justify-between">
					<div class="flex items-center justify-between text-slate-400">
						<span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider">Status Server</span>
						<i class="bi bi-hdd-network text-emerald-400 text-xs sm:text-sm"></i>
					</div>
					<div class="mt-2 sm:mt-3">
						<div class="flex items-center gap-1.5 text-base sm:text-lg font-bold text-emerald-300">
							<span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
							<span>Terhubung</span>
						</div>
						<p class="text-[10px] sm:text-[11px] text-slate-400 mt-0.5 truncate">User: {{ overview.user }}</p>
					</div>
				</div>

				<div class="rounded-xl sm:rounded-2xl border border-white/10 bg-[#123138]/70 p-3.5 sm:p-4 shadow-lg flex flex-col justify-between">
					<div class="flex items-center justify-between text-slate-400">
						<span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider">Database Aktif</span>
						<i class="bi bi-database text-cyan-400 text-xs sm:text-sm"></i>
					</div>
					<div class="mt-2 sm:mt-3">
						<p class="font-mono text-sm sm:text-base font-bold text-[#F5EFE0] truncate" :title="overview.database">
							{{ overview.database }}
						</p>
						<p class="text-[10px] sm:text-[11px] text-cyan-300/80 mt-0.5 font-mono truncate">
							{{ overview.engine }} {{ overview.version?.split(' ')[1] || '' }}
						</p>
					</div>
				</div>

				<div class="rounded-xl sm:rounded-2xl border border-white/10 bg-[#123138]/70 p-3.5 sm:p-4 shadow-lg flex flex-col justify-between">
					<div class="flex items-center justify-between text-slate-400">
						<span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider">Tabel Terdeteksi</span>
						<i class="bi bi-table text-amber-400 text-xs sm:text-sm"></i>
					</div>
					<div class="mt-2 sm:mt-3">
						<p class="text-xl sm:text-2xl lg:text-3xl font-extrabold text-amber-300">
							{{ tableCount }}
						</p>
						<p class="text-[10px] sm:text-[11px] text-slate-400 mt-0.5">
							Ditemukan otomatis
						</p>
					</div>
				</div>

				<div class="rounded-xl sm:rounded-2xl border border-white/10 bg-[#123138]/70 p-3.5 sm:p-4 shadow-lg flex flex-col justify-between">
					<div class="flex items-center justify-between text-slate-400">
						<span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider">Total Baris Data</span>
						<i class="bi bi-layers text-indigo-400 text-xs sm:text-sm"></i>
					</div>
					<div class="mt-2 sm:mt-3">
						<p class="text-xl sm:text-2xl lg:text-3xl font-extrabold text-indigo-300">
							{{ totalDatabaseRows.toLocaleString('id-ID') }}
						</p>
						<p class="text-[10px] sm:text-[11px] text-slate-400 mt-0.5">
							Akumulasi database
						</p>
					</div>
				</div>

				<div class="col-span-2 md:col-span-1 lg:col-span-1 rounded-xl sm:rounded-2xl border border-white/10 bg-[#123138]/70 p-3.5 sm:p-4 shadow-lg flex flex-col justify-between">
					<div class="flex items-center justify-between text-slate-400">
						<span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider">Ukuran Disk</span>
						<i class="bi bi-pie-chart text-emerald-400 text-xs sm:text-sm"></i>
					</div>
					<div class="mt-2 sm:mt-3">
						<p class="text-xl sm:text-2xl lg:text-3xl font-extrabold text-emerald-300">
							{{ overview.db_size || 'N/A' }}
						</p>
						<p class="text-[10px] sm:text-[11px] text-slate-400 mt-0.5">
							Koneksi aktif: {{ overview.active_connections || 1 }}
						</p>
					</div>
				</div>
			</section>

			<!-- MOBILE TABLE SELECTOR BAR (< lg) -->
			<div class="block lg:hidden">
				<button 
					type="button" 
					@click="isMobileTableListOpen = !isMobileTableListOpen"
					class="w-full flex items-center justify-between p-3.5 rounded-2xl bg-[#123138] border border-emerald-500/30 text-xs font-semibold text-white shadow-md active:scale-98 transition cursor-pointer"
				>
					<div class="flex items-center gap-2 truncate">
						<i class="bi bi-folder2-open text-amber-400 text-sm"></i>
						<span class="text-slate-300">Tabel Terpilih:</span>
						<span class="font-mono text-emerald-300 font-bold truncate">{{ selectedTable }}</span>
						<span class="text-[10px] text-slate-400">({{ tableCount }})</span>
					</div>
					<div class="flex items-center gap-1.5 text-xs text-slate-400 shrink-0 ml-2">
						<span>{{ isMobileTableListOpen ? 'Tutup Daftar' : 'Ganti Tabel' }}</span>
						<i class="bi" :class="isMobileTableListOpen ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
					</div>
				</button>
			</div>

			<!-- MAIN WORKSPACE: Adaptive Dual Panel (Left: Tables, Right: 6-Tab Workspace) -->
			<section class="grid min-w-0 gap-4 sm:gap-6 lg:grid-cols-[minmax(280px,330px)_1fr] items-start">
				
				<!-- LEFT PANEL: Dynamic Table Directory -->
				<div 
					:class="[
						'rounded-2xl sm:rounded-3xl border border-white/10 bg-[#123138]/85 p-4 sm:p-5 shadow-xl backdrop-blur-md flex flex-col',
						isMobileTableListOpen ? 'block' : 'hidden lg:flex',
						'h-[420px] sm:h-[520px] lg:h-[820px]'
					]"
				>
					<div class="mb-3 sm:mb-4 shrink-0">
						<div class="flex items-center justify-between mb-1">
							<h2 class="font-serif text-base sm:text-lg font-bold text-[#F5EFE0] flex items-center gap-2">
								<i class="bi bi-folder2-open text-amber-400"></i>
								<span>Daftar Tabel ({{ tableCount }})</span>
							</h2>
							<button 
								type="button" 
								@click="loadOverview(true)" 
								class="text-xs text-emerald-400 hover:text-emerald-300 p-1 cursor-pointer"
								title="Segarkan daftar tabel"
							>
								<i class="bi bi-arrow-clockwise" :class="{ 'animate-spin': isSyncing }"></i>
							</button>
						</div>
						<p class="text-[10px] sm:text-[11px] text-[#8AA0A4]">
							Otomatis update saat ada tabel baru hasil migrasi.
						</p>

						<!-- Search Table Input -->
						<div class="mt-2.5 relative">
							<i class="bi bi-search absolute left-3 top-2.5 text-xs text-slate-400"></i>
							<input 
								v-model="tableSearchQuery"
								type="text" 
								placeholder="Cari tabel database..."
								class="w-full rounded-xl bg-[#0B2027] border border-slate-700 pl-8 pr-3 py-1.5 sm:py-2 text-xs text-slate-200 outline-none focus:border-emerald-400 transition"
							/>
						</div>

						<!-- Category Chips -->
						<div class="flex items-center gap-1.5 overflow-x-auto custom-scrollbar no-scrollbar-on-touch py-1 mt-2">
							<button 
								type="button"
								@click="selectedCategory = 'all'"
								:class="[
									'text-[10px] font-semibold px-2.5 py-1 rounded-lg transition-all cursor-pointer shrink-0',
									selectedCategory === 'all' ? 'bg-emerald-500 text-slate-950 font-bold' : 'bg-slate-900 text-slate-400 hover:text-white'
								]"
							>
								Semua
							</button>
							<button 
								v-for="cat in categories" 
								:key="cat"
								type="button"
								@click="selectedCategory = cat"
								:class="[
									'text-[10px] font-semibold px-2.5 py-1 rounded-lg transition-all cursor-pointer shrink-0 truncate max-w-[130px]',
									selectedCategory === cat ? 'bg-emerald-500 text-slate-950 font-bold' : 'bg-slate-900 text-slate-400 hover:text-white'
								]"
							>
								{{ cat }}
							</button>
						</div>
					</div>

					<!-- Scrollable Table Cards List -->
					<div class="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar min-h-0">
						<button 
							v-for="tbl in filteredTables" 
							:key="tbl.name"
							type="button"
							@click="selectTable(tbl.name)"
							:class="[
								'w-full text-left p-2.5 sm:p-3 rounded-xl sm:rounded-2xl border transition-all duration-200 cursor-pointer flex flex-col gap-1 active:scale-98',
								selectedTable === tbl.name 
									? 'bg-gradient-to-r from-emerald-500/20 to-teal-500/10 border-emerald-400/50 shadow-md' 
									: 'bg-[#0B2027]/70 border-white/5 hover:border-slate-700 hover:bg-[#0B2027]'
							]"
						>
							<div class="flex items-center justify-between gap-2">
								<span class="font-mono text-xs font-bold text-white truncate" :class="{ 'text-emerald-300': selectedTable === tbl.name }">
									{{ tbl.name }}
								</span>
								<span 
									class="text-[9px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider shrink-0"
									:class="[
										tbl.category === 'Keuangan Gereja' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
										tbl.category === 'Gereja & Jemaat' ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30' :
										tbl.category === 'Autentikasi & Akun' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
										'bg-slate-800 text-slate-300 border border-slate-700'
									]"
								>
									{{ tbl.category }}
								</span>
							</div>

							<div class="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-[11px] text-slate-400">
								<span><strong class="text-slate-200">{{ tbl.rows.toLocaleString('id-ID') }}</strong> baris</span>
								<span>•</span>
								<span><strong class="text-slate-200">{{ tbl.columns_count || tbl.columns?.length || 0 }}</strong> kol</span>
								<span v-if="tbl.size && tbl.size !== 'N/A'">•</span>
								<span v-if="tbl.size && tbl.size !== 'N/A'" class="text-cyan-300 font-mono">{{ tbl.size }}</span>
							</div>
						</button>

						<div v-if="filteredTables.length === 0" class="py-10 text-center text-xs text-slate-500">
							Tidak ada tabel yang sesuai dengan kata kunci pencarian.
						</div>
					</div>

					<!-- Left Panel Footer -->
					<div class="pt-2.5 border-t border-white/10 mt-2 flex items-center justify-between text-[11px] text-slate-400 shrink-0">
						<span class="flex items-center gap-1">
							<i class="bi bi-shield-check text-emerald-400"></i>
							<span>Masking Aktif</span>
						</span>
						<span class="text-[10px] text-slate-500 font-mono">SQL Guard</span>
					</div>
				</div>

				<!-- RIGHT PANEL: Multi-View Workspace (6 TABS PERFECTION) -->
				<div class="rounded-2xl sm:rounded-3xl border border-white/10 bg-[#123138]/85 p-3.5 sm:p-5 lg:p-6 shadow-xl backdrop-blur-md flex flex-col h-[680px] sm:h-[750px] lg:h-[820px] min-w-0">
					
					<!-- Header Selected Table & Quick Action Controls -->
					<div class="mb-3 pb-3 border-b border-white/10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2.5 shrink-0">
						<div>
							<div class="flex items-center gap-2 flex-wrap">
								<h2 class="font-serif text-lg sm:text-xl lg:text-2xl font-black text-[#F5EFE0] tracking-tight truncate max-w-[260px] sm:max-w-md">
									{{ currentTableMeta?.name || selectedTable }}
								</h2>
								<span class="text-[10px] sm:text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold font-mono">
									{{ currentTableMeta?.rows?.toLocaleString('id-ID') || 0 }} Baris
								</span>
								<span v-if="currentTableMeta?.size && currentTableMeta.size !== 'N/A'" class="text-[10px] sm:text-xs px-2 py-0.5 rounded-full bg-slate-800 text-cyan-300 font-mono border border-slate-700">
									{{ currentTableMeta.size }}
								</span>
							</div>
							<p class="text-[11px] sm:text-xs text-[#8AA0A4] mt-0.5 font-sans">
								Kategori: <strong class="text-slate-200">{{ currentTableMeta?.category || 'Database Table' }}</strong>
								• PK: <code class="text-amber-300">{{ currentTableMeta?.primary_keys?.join(', ') || 'None' }}</code>
							</p>
						</div>

						<!-- Quick Actions on Selected Table (DDL & Optimasi) -->
						<div class="flex items-center gap-1.5 self-start sm:self-auto shrink-0">
							<button 
								type="button" 
								@click="openDdlModal"
								class="px-2.5 py-1.5 rounded-xl bg-cyan-950/60 hover:bg-cyan-900/60 text-cyan-300 border border-cyan-500/40 text-[11px] font-semibold transition cursor-pointer flex items-center gap-1 active:scale-95"
								title="Lihat skema DDL SQL CREATE TABLE"
							>
								<i class="bi bi-file-earmark-code"></i>
								<span>DDL</span>
							</button>
							<button 
								type="button" 
								@click="optimizeCurrentTable"
								:disabled="isOptimizing"
								class="px-2.5 py-1.5 rounded-xl bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-300 border border-emerald-500/40 text-[11px] font-semibold transition cursor-pointer flex items-center gap-1 disabled:opacity-50 active:scale-95"
								title="Jalankan ANALYZE untuk optimasi query planner"
							>
								<i class="bi bi-speedometer2" :class="{ 'animate-spin': isOptimizing }"></i>
								<span>{{ isOptimizing ? 'Optimasi...' : 'Optimasi' }}</span>
							</button>
						</div>
					</div>

					<!-- ⭐ DEDICATED FULL-WIDTH RESPONSIVE 6-TAB CONTROL (Grid 2/3/6 cols: Tidak akan pernah terdesak!) ⭐ -->
					<div class="mb-3.5 shrink-0">
						<div class="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-1.5 bg-slate-950/90 p-1.5 rounded-2xl border border-slate-800/80 shadow-inner">
							
							<!-- Tab 1: Data Baris -->
							<button 
								type="button" 
								@click="activeTab = 'data'"
								:class="[
									'px-2 py-1.5 sm:py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all duration-200 cursor-pointer text-center select-none active:scale-95',
									activeTab === 'data' 
										? 'bg-emerald-500 text-slate-950 shadow-md font-bold ring-1 ring-emerald-400/50' 
										: 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
								]"
							>
								<i class="bi bi-grid-3x3 text-xs" :class="activeTab === 'data' ? 'text-slate-950' : 'text-emerald-400'"></i>
								<span class="truncate">Data Baris</span>
							</button>

							<!-- Tab 2: Struktur Kolom -->
							<button 
								type="button" 
								@click="activeTab = 'schema'"
								:class="[
									'px-2 py-1.5 sm:py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all duration-200 cursor-pointer text-center select-none active:scale-95',
									activeTab === 'schema' 
										? 'bg-emerald-500 text-slate-950 shadow-md font-bold ring-1 ring-emerald-400/50' 
										: 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
								]"
							>
								<i class="bi bi-diagram-2 text-xs" :class="activeTab === 'schema' ? 'text-slate-950' : 'text-emerald-400'"></i>
								<span class="truncate">Kolom ({{ currentTableMeta?.columns_count || currentTableMeta?.columns?.length || 0 }})</span>
							</button>

							<!-- Tab 3: Bagan UML / ERD -->
							<button 
								type="button" 
								@click="activeTab = 'erd'"
								:class="[
									'px-2 py-1.5 sm:py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all duration-200 cursor-pointer text-center select-none active:scale-95',
									activeTab === 'erd' 
										? 'bg-cyan-500 text-slate-950 shadow-md font-bold ring-1 ring-cyan-400/50' 
										: 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
								]"
								title="Bagan UML & Diagram Relasi ERD Interaktif"
							>
								<i class="bi bi-diagram-3-fill text-xs" :class="activeTab === 'erd' ? 'text-slate-950' : 'text-cyan-400'"></i>
								<span class="truncate">Bagan UML/ERD</span>
							</button>

							<!-- Tab 4: Roadmap & Alur -->
							<button 
								type="button" 
								@click="activeTab = 'roadmap'"
								:class="[
									'px-2 py-1.5 sm:py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all duration-200 cursor-pointer text-center select-none active:scale-95',
									activeTab === 'roadmap' 
										? 'bg-amber-400 text-slate-950 shadow-md font-bold ring-1 ring-amber-300/50' 
										: 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
								]"
								title="Alur Kerja Sistem & Roadmap Arsitektur Database"
							>
								<i class="bi bi-signpost-2-fill text-xs" :class="activeTab === 'roadmap' ? 'text-slate-950' : 'text-amber-400'"></i>
								<span class="truncate">Roadmap &amp; Alur</span>
							</button>

							<!-- Tab 5: Konsol SQL -->
							<button 
								type="button" 
								@click="activeTab = 'query'"
								:class="[
									'px-2 py-1.5 sm:py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all duration-200 cursor-pointer text-center select-none active:scale-95',
									activeTab === 'query' 
										? 'bg-indigo-500 text-slate-950 shadow-md font-bold ring-1 ring-indigo-400/50' 
										: 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
								]"
								title="Konsol Kueri SQL Aman"
							>
								<i class="bi bi-terminal-fill text-xs" :class="activeTab === 'query' ? 'text-slate-950' : 'text-indigo-400'"></i>
								<span class="truncate">Konsol SQL</span>
							</button>

							<!-- Tab 6: Statistik -->
							<button 
								type="button" 
								@click="activeTab = 'metrics'"
								:class="[
									'px-2 py-1.5 sm:py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all duration-200 cursor-pointer text-center select-none active:scale-95',
									activeTab === 'metrics' 
										? 'bg-emerald-500 text-slate-950 shadow-md font-bold ring-1 ring-emerald-400/50' 
										: 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
								]"
							>
								<i class="bi bi-bar-chart text-xs" :class="activeTab === 'metrics' ? 'text-slate-950' : 'text-emerald-400'"></i>
								<span class="truncate">Statistik</span>
							</button>

						</div>
					</div>

					<!-- ========================================================= -->
					<!-- TAB 1 CONTENT: DATA BARIS                                 -->
					<!-- ========================================================= -->
					<div v-if="activeTab === 'data'" class="flex-1 flex flex-col min-h-0">
						<!-- Sub-toolbar -->
						<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5 mb-3 shrink-0">
							<div class="flex items-center gap-2 flex-1">
								<div class="relative w-full max-w-xs">
									<i class="bi bi-search absolute left-3 top-2.5 text-xs text-slate-400"></i>
									<input 
										v-model="dataSearchQuery"
										type="text" 
										placeholder="Cari dalam tabel ini..."
										@input="onDataSearchInput"
										class="w-full rounded-xl bg-[#0B2027] border border-slate-700 pl-8 pr-7 py-1.5 sm:py-2 text-xs text-slate-200 outline-none focus:border-emerald-400 transition"
									/>
									<button 
										v-if="dataSearchQuery" 
										type="button" 
										@click="resetDataFilters"
										class="absolute right-2.5 top-2 text-xs text-slate-400 hover:text-white cursor-pointer"
										title="Hapus filter"
									>
										<i class="bi bi-x-circle-fill"></i>
									</button>
								</div>

								<button 
									type="button" 
									@click="refreshTableData" 
									:disabled="isPreviewLoading"
									class="px-2.5 py-1.5 sm:py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-emerald-300 border border-slate-700 text-xs font-medium transition cursor-pointer flex items-center gap-1.5 shrink-0 active:scale-95"
									title="Muat ulang data tabel ini"
								>
									<i class="bi bi-arrow-clockwise" :class="{ 'animate-spin': isPreviewLoading }"></i>
									<span class="hidden sm:inline">Refresh</span>
								</button>
							</div>

							<!-- Action Buttons: Limit & Export -->
							<div class="flex items-center gap-1.5 flex-wrap justify-end">
								<div class="flex items-center gap-1 text-[11px] text-slate-400 bg-slate-950 px-2 py-1 rounded-lg border border-slate-800">
									<span>Hal:</span>
									<select 
										v-model="previewLimit" 
										@change="onLimitChange"
										class="bg-transparent text-[11px] text-white outline-none cursor-pointer"
									>
										<option :value="10">10</option>
										<option :value="25">25</option>
										<option :value="50">50</option>
										<option :value="100">100</option>
									</select>
								</div>

								<button 
									type="button" 
									@click="exportCsv"
									class="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 text-[11px] font-medium transition cursor-pointer flex items-center gap-1"
									title="Ekspor CSV"
								>
									<i class="bi bi-filetype-csv text-emerald-400"></i>
									<span>CSV</span>
								</button>
								<button 
									type="button" 
									@click="exportJson"
									class="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 text-[11px] font-medium transition cursor-pointer flex items-center gap-1"
									title="Ekspor JSON"
								>
									<i class="bi bi-filetype-json text-amber-400"></i>
									<span>JSON</span>
								</button>
								<button 
									type="button" 
									@click="copySqlInserts"
									class="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 text-[11px] font-medium transition cursor-pointer flex items-center gap-1"
									title="Salin SQL INSERT"
								>
									<i class="bi bi-clipboard text-sky-400"></i>
									<span>Salin SQL</span>
								</button>
							</div>
						</div>

						<!-- Table Data Matrix -->
						<div class="flex-1 min-h-0 overflow-auto rounded-xl sm:rounded-2xl border border-white/10 bg-[#0B2027]/80 custom-scrollbar relative">
							<div v-if="isPreviewLoading" class="absolute inset-0 bg-[#0B2027]/70 backdrop-blur-sm flex items-center justify-center z-20">
								<div class="flex items-center gap-2 text-emerald-400 text-xs sm:text-sm font-semibold">
									<i class="bi bi-arrow-repeat animate-spin text-base sm:text-lg"></i>
									<span>Memuat data {{ selectedTable }}...</span>
								</div>
							</div>

							<table v-if="preview && preview.rows && preview.rows.length > 0" class="min-w-[650px] sm:min-w-full text-left text-xs border-collapse">
								<thead class="sticky top-0 bg-[#0B2027] border-b border-emerald-500/30 text-emerald-300 z-10 shadow-md">
									<tr>
										<th class="px-2.5 sm:px-3 py-2.5 w-10 text-center font-bold text-slate-500">#</th>
										<th 
											v-for="col in preview.columns" 
											:key="col.name"
											@click="handleSort(col.name)"
											class="px-3 sm:px-4 py-2.5 font-bold uppercase tracking-wider whitespace-nowrap cursor-pointer hover:bg-white/5 transition-colors select-none"
											:title="`Klik untuk mengurutkan ${col.name}`"
										>
											<div class="flex items-center gap-1.5">
												<i v-if="col.is_pk" class="bi bi-key-fill text-amber-400 text-xs" title="Primary Key"></i>
												<i v-if="col.is_sensitive" class="bi bi-shield-lock-fill text-rose-400 text-xs" title="Kolom Terproteksi"></i>
												<span>{{ col.name }}</span>
												<span class="text-[9px] text-slate-400 font-normal font-mono lowercase">({{ col.type }})</span>
												<i 
													v-if="sortColumn === col.name" 
													:class="sortDirection === 'asc' ? 'bi-sort-up' : 'bi-sort-down'"
													class="bi text-amber-400 font-bold ml-0.5"
												></i>
											</div>
										</th>
										<th class="px-2.5 py-2.5 text-center font-bold text-slate-400 w-14">Aksi</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-white/5 font-mono text-[11px]">
									<tr 
										v-for="(row, rIdx) in preview.rows" 
										:key="rIdx"
										class="hover:bg-white/[0.04] transition-colors group cursor-pointer"
										@click="openRowInspector(row)"
									>
										<td class="px-2.5 sm:px-3 py-2 text-center text-slate-500">
											{{ previewOffset + rIdx + 1 }}
										</td>
										<td 
											v-for="col in preview.columns" 
											:key="col.name"
											class="px-3 sm:px-4 py-2 max-w-[220px] truncate text-slate-300"
										>
											<span v-if="row[col.name] && String(row[col.name]).includes('TERLINDUNGI')" class="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-sans font-semibold">
												<i class="bi bi-lock-fill"></i> Terlindungi
											</span>
											<span v-else-if="row[col.name] === null" class="text-slate-600 italic">
												&lt;null&gt;
											</span>
											<span v-else-if="typeof row[col.name] === 'boolean'" :class="row[col.name] ? 'text-emerald-400' : 'text-rose-400'">
												{{ row[col.name] ? 'TRUE' : 'FALSE' }}
											</span>
											<span v-else>
												{{ row[col.name] }}
											</span>
										</td>
										<td class="px-2.5 py-2 text-center" @click.stop="openRowInspector(row)">
											<button 
												type="button" 
												class="p-1 rounded hover:bg-emerald-500/20 text-emerald-400 hover:text-emerald-300 transition cursor-pointer"
												title="Inspeksi Baris"
											>
												<i class="bi bi-arrows-angle-expand text-xs"></i>
											</button>
										</td>
									</tr>
								</tbody>
							</table>

							<div v-else-if="!isPreviewLoading" class="py-16 text-center text-slate-500 text-xs p-4">
								<i class="bi bi-inbox text-3xl block mb-2 text-slate-600"></i>
								<span>Tabel <strong>{{ selectedTable }}</strong> belum memiliki data atau tidak sesuai dengan filter.</span>
								<div class="mt-3">
									<button 
										v-if="dataSearchQuery" 
										type="button" 
										@click="resetDataFilters"
										class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-emerald-300 text-xs font-semibold cursor-pointer"
									>
										Reset Filter
									</button>
								</div>
							</div>
						</div>

						<!-- Pagination Footer -->
						<div class="pt-2.5 sm:pt-3 border-t border-white/10 mt-2.5 flex flex-col sm:flex-row items-center justify-between gap-2.5 text-xs shrink-0">
							<div class="text-slate-400 text-center sm:text-left text-[11px] sm:text-xs">
								Menampilkan <strong class="text-white">{{ totalRows > 0 ? previewOffset + 1 : 0 }}</strong> - <strong class="text-white">{{ Math.min(previewOffset + previewLimit, totalRows) }}</strong> dari <strong class="text-white">{{ totalRows.toLocaleString('id-ID') }}</strong> baris
							</div>

							<div class="flex items-center gap-1">
								<button 
									type="button" 
									:disabled="currentPage <= 1 || isPreviewLoading"
									@click="goToPage(1)"
									class="px-2 py-1 rounded-lg border border-slate-700 bg-slate-900 text-slate-300 hover:text-white disabled:opacity-40 cursor-pointer text-[11px]"
									title="Ke halaman pertama"
								>
									<i class="bi bi-chevron-double-left"></i>
								</button>
								<button 
									type="button" 
									:disabled="currentPage <= 1 || isPreviewLoading"
									@click="goToPage(currentPage - 1)"
									class="px-2.5 py-1 rounded-lg border border-slate-700 bg-slate-900 text-slate-300 hover:text-white disabled:opacity-40 cursor-pointer"
								>
									<i class="bi bi-chevron-left"></i>
								</button>
								<span class="px-2.5 py-1 text-slate-300 font-semibold font-mono text-[11px]">
									{{ currentPage }} / {{ totalPages }}
								</span>
								<button 
									type="button" 
									:disabled="currentPage >= totalPages || isPreviewLoading"
									@click="goToPage(currentPage + 1)"
									class="px-2.5 py-1 rounded-lg border border-slate-700 bg-slate-900 text-slate-300 hover:text-white disabled:opacity-40 cursor-pointer"
								>
									<i class="bi bi-chevron-right"></i>
								</button>
								<button 
									type="button" 
									:disabled="currentPage >= totalPages || isPreviewLoading"
									@click="goToPage(totalPages)"
									class="px-2 py-1 rounded-lg border border-slate-700 bg-slate-900 text-slate-300 hover:text-white disabled:opacity-40 cursor-pointer text-[11px]"
									title="Ke halaman terakhir"
								>
									<i class="bi bi-chevron-double-right"></i>
								</button>
							</div>
						</div>
					</div>

					<!-- ========================================================= -->
					<!-- TAB 2 CONTENT: STRUKTUR KOLOM                             -->
					<!-- ========================================================= -->
					<div v-else-if="activeTab === 'schema'" class="flex-1 overflow-y-auto space-y-4 pr-1 custom-scrollbar">
						<div>
							<h3 class="font-serif font-bold text-sm text-white mb-2 flex items-center gap-2">
								<i class="bi bi-columns-gap text-emerald-400"></i>
								<span>Katalog Kolom ({{ currentTableMeta?.columns?.length || 0 }})</span>
							</h3>
							<div class="overflow-x-auto rounded-xl border border-white/10 bg-[#0B2027]">
								<table class="min-w-[580px] w-full text-left text-xs">
									<thead class="border-b border-slate-800 bg-[#061418] text-slate-400">
										<tr>
											<th class="px-3.5 py-2.5 font-bold uppercase">Nama Kolom</th>
											<th class="px-3.5 py-2.5 font-bold uppercase">Tipe Data</th>
											<th class="px-3.5 py-2.5 font-bold uppercase text-center">Primary Key</th>
											<th class="px-3.5 py-2.5 font-bold uppercase text-center">Null</th>
											<th class="px-3.5 py-2.5 font-bold uppercase text-center">Keamanan</th>
										</tr>
									</thead>
									<tbody class="divide-y divide-white/5 font-mono text-[11px]">
										<tr v-for="col in currentTableMeta?.columns || []" :key="col.name" class="hover:bg-white/[0.02]">
											<td class="px-3.5 py-2 font-bold text-white flex items-center gap-1.5">
												<i v-if="col.is_pk" class="bi bi-key-fill text-amber-400 text-xs"></i>
												<span>{{ col.name }}</span>
											</td>
											<td class="px-3.5 py-2 text-cyan-300 font-sans">
												{{ col.type }}
											</td>
											<td class="px-3.5 py-2 text-center font-sans">
												<span v-if="col.is_pk" class="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold text-[10px]">
													PRIMARY
												</span>
												<span v-else class="text-slate-600">-</span>
											</td>
											<td class="px-3.5 py-2 text-center font-sans">
												<span :class="col.nullable ? 'text-slate-400' : 'text-rose-400 font-semibold'">
													{{ col.nullable ? 'Ya' : 'NOT NULL' }}
												</span>
											</td>
											<td class="px-3.5 py-2 text-center font-sans">
												<span v-if="col.is_sensitive" class="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold text-[10px]">
													Terproteksi
												</span>
												<span v-else class="text-emerald-400 text-[10px]">
													Standar
												</span>
											</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>

						<!-- Foreign Keys -->
						<div v-if="preview?.foreign_keys && preview.foreign_keys.length > 0">
							<h3 class="font-serif font-bold text-sm text-white mb-2 flex items-center gap-2">
								<i class="bi bi-link-45deg text-cyan-400"></i>
								<span>Relasi Foreign Key</span>
							</h3>
							<div class="space-y-2">
								<div 
									v-for="(fk, fIdx) in preview.foreign_keys" 
									:key="fIdx"
									class="p-2.5 sm:p-3 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 text-xs"
								>
									<div class="flex items-center gap-2 flex-wrap font-mono">
										<span class="text-amber-300 font-bold">{{ fk.constrained_columns.join(', ') }}</span>
										<i class="bi bi-arrow-right text-slate-500"></i>
										<span class="text-cyan-300 font-bold">{{ fk.referred_table }} ({{ fk.referred_columns.join(', ') }})</span>
									</div>
									<button 
										type="button" 
										@click="selectTable(fk.referred_table)"
										class="text-xs text-emerald-400 hover:text-white underline cursor-pointer self-end sm:self-auto"
									>
										Lihat Tabel ➔
									</button>
								</div>
							</div>
						</div>

						<!-- Indeks Database -->
						<div v-if="preview?.indexes && preview.indexes.length > 0">
							<h3 class="font-serif font-bold text-sm text-white mb-2 flex items-center gap-2">
								<i class="bi bi-lightning text-amber-400"></i>
								<span>Indeks Pencarian (Indexes)</span>
							</h3>
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
								<div v-for="idx in preview.indexes" :key="idx.name" class="p-2.5 sm:p-3 rounded-xl bg-slate-900 border border-slate-800 font-mono">
									<div class="flex items-center justify-between mb-1">
										<span class="text-white font-bold truncate">{{ idx.name }}</span>
										<span v-if="idx.unique" class="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[9px] font-sans font-bold">UNIQUE</span>
									</div>
									<span class="text-[11px] text-slate-400 truncate block">Kolom: {{ idx.column_names.join(', ') }}</span>
								</div>
							</div>
						</div>
					</div>

					<!-- ========================================================= -->
					<!-- TAB 3 CONTENT: BAGAN UML / ERD INTERAKTIF                -->
					<!-- ========================================================= -->
					<div v-else-if="activeTab === 'erd'" class="flex-1 flex flex-col min-h-0">
						<!-- Domain Filter Bar -->
						<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-3 p-3 rounded-xl sm:rounded-2xl bg-[#0B2027] border border-white/5 shrink-0">
							<div class="flex items-center gap-1.5 flex-wrap">
								<span class="text-xs font-bold text-slate-300 flex items-center gap-1 mr-1">
									<i class="bi bi-filter text-cyan-400"></i>
									<span>Domain:</span>
								</span>
								<button 
									type="button" 
									@click="erdCategoryFilter = 'all'"
									:class="[
										'text-[10px] font-semibold px-2.5 py-1 rounded-lg transition-all cursor-pointer',
										erdCategoryFilter === 'all' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-900 text-slate-400 hover:text-white'
									]"
								>
									Semua ({{ erdData.nodes.length }})
								</button>
								<button 
									v-for="cat in categories" 
									:key="cat"
									type="button" 
									@click="erdCategoryFilter = cat"
									:class="[
										'text-[10px] font-semibold px-2.5 py-1 rounded-lg transition-all cursor-pointer',
										erdCategoryFilter === cat ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-900 text-slate-400 hover:text-white'
									]"
								>
									{{ cat }}
								</button>
							</div>

							<div class="flex items-center justify-between sm:justify-end gap-2">
								<button 
									v-if="selectedErdNode"
									type="button" 
									@click="selectedErdNode = null"
									class="px-2 py-1 rounded-lg bg-slate-800 text-slate-400 hover:text-white text-[11px] cursor-pointer"
								>
									Batal Fokus ({{ selectedErdNode }})
								</button>
								<span class="text-[11px] text-slate-400">
									Relasi: <strong class="text-emerald-400">{{ activeErdEdges.length }}</strong> FK
								</span>
							</div>
						</div>

						<!-- ERD Cards Grid -->
						<div class="flex-1 overflow-auto rounded-xl sm:rounded-2xl border border-white/10 bg-[#07171C] p-3 sm:p-4 custom-scrollbar relative">
							<div v-if="isErdLoading" class="absolute inset-0 bg-[#07171C]/70 backdrop-blur-sm flex items-center justify-center z-20">
								<div class="flex items-center gap-2 text-cyan-400 text-xs sm:text-sm font-semibold">
									<i class="bi bi-arrow-repeat animate-spin text-base sm:text-lg"></i>
									<span>Membuat bagan relasi UML / ERD...</span>
								</div>
							</div>

							<!-- Notice Hub -->
							<div class="mb-3 sm:mb-4 p-3 rounded-xl sm:rounded-2xl bg-gradient-to-r from-emerald-950/40 via-cyan-950/30 to-blue-950/20 border border-emerald-500/20 text-xs">
								<div class="flex items-center gap-2 font-bold text-emerald-300">
									<i class="bi bi-info-circle-fill"></i>
									<span>Struktur Sentral Multi-Tenant CMS:</span>
								</div>
								<p class="mt-1 text-slate-300 leading-relaxed font-sans text-[11px] sm:text-xs">
									Tabel <strong class="text-white bg-slate-800 px-1 py-0.5 rounded font-mono">churches</strong> adalah <em>Central Entity Hub</em>. Seluruh modul pelayanan dan kas terisolasi per gereja menggunakan Foreign Key terindeks.
								</p>
							</div>

							<!-- Entity Cards -->
							<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 sm:gap-4">
								<div 
									v-for="node in filteredErdNodes" 
									:key="node.id"
									@click="selectErdNode(node.id)"
									:class="[
										'rounded-xl sm:rounded-2xl border p-3.5 sm:p-4 transition-all duration-300 cursor-pointer flex flex-col justify-between select-none relative overflow-hidden',
										selectedErdNode === node.id 
											? 'border-amber-400 bg-slate-900 shadow-2xl ring-2 ring-amber-400/40' 
											: isNodeHighlighted(node.id)
												? 'border-white/10 bg-[#0B2027]/90 hover:border-cyan-400/50 hover:bg-[#0B2027]'
												: 'border-white/5 bg-[#0B2027]/30 opacity-40 hover:opacity-100'
									]"
								>
									<div>
										<div class="flex items-center justify-between gap-2 mb-2">
											<span 
												class="text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider font-mono border"
												:class="[
													node.category === 'Keuangan Gereja' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
													node.category === 'Gereja & Jemaat' ? 'bg-sky-500/20 text-sky-300 border-sky-500/40' :
													node.category === 'Autentikasi & Akun' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
													'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
												]"
											>
												{{ node.category }}
											</span>
											<span class="text-[10px] text-slate-400 font-mono">
												{{ node.rows.toLocaleString('id-ID') }} rows
											</span>
										</div>

										<div class="flex items-center gap-2">
											<i 
												class="bi text-base"
												:class="[
													node.name === 'churches' ? 'bi-buildings text-amber-400' :
													node.category === 'Keuangan Gereja' ? 'bi-cash-coin text-emerald-400' :
													node.category === 'Gereja & Jemaat' ? 'bi-people text-sky-400' :
													node.category === 'Autentikasi & Akun' ? 'bi-shield-lock text-amber-400' :
													'bi-cpu text-indigo-400'
												]"
											></i>
											<h4 class="font-mono text-sm font-black text-white truncate">
												{{ node.name }}
											</h4>
										</div>

										<div class="mt-2.5 space-y-1 font-mono text-[11px] max-h-32 overflow-y-auto custom-scrollbar pr-1 border-t border-white/5 pt-2">
											<div 
												v-for="col in node.columns.slice(0, 5)" 
												:key="col.name"
												class="flex items-center justify-between text-slate-300 py-0.5"
											>
												<span class="flex items-center gap-1.5 truncate">
													<i v-if="col.is_pk" class="bi bi-key-fill text-amber-400 text-[10px]" title="Primary Key"></i>
													<span :class="{ 'text-amber-300 font-bold': col.is_pk }">{{ col.name }}</span>
												</span>
												<span class="text-[9px] text-slate-500 font-sans truncate">{{ col.type }}</span>
											</div>
											<div v-if="node.columns.length > 5" class="text-[10px] text-slate-500 italic pt-0.5">
												+ {{ node.columns.length - 5 }} kolom lainnya...
											</div>
										</div>
									</div>

									<div class="pt-2.5 border-t border-white/5 mt-2.5 flex items-center justify-between">
										<div class="flex items-center gap-1 text-[10px] text-slate-400">
											<i class="bi bi-link-45deg text-cyan-400"></i>
											<span>{{ erdData.edges.filter(e => e.from === node.id || e.to === node.id).length }} relasi</span>
										</div>
										<button 
											type="button" 
											@click.stop="selectTable(node.name)"
											class="text-[10px] px-2 py-1 rounded bg-slate-800 hover:bg-emerald-500/20 text-emerald-300 border border-slate-700 transition cursor-pointer flex items-center gap-1"
										>
											<span>Buka Data</span>
											<i class="bi bi-box-arrow-up-right text-[9px]"></i>
										</button>
									</div>
								</div>
							</div>

							<!-- Relations List -->
							<div class="mt-4 sm:mt-6 p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-[#0B2027] border border-white/10">
								<h4 class="font-serif font-bold text-xs text-slate-200 mb-2 flex items-center gap-2">
									<i class="bi bi-share text-cyan-400"></i>
									<span>Koneksi Relasi Foreign Key Aktif</span>
								</h4>
								<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1.5 sm:gap-2 font-mono text-[11px]">
									<div 
										v-for="edge in activeErdEdges" 
										:key="edge.id"
										class="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-2"
									>
										<span class="text-amber-300 font-bold truncate">{{ edge.from }}.{{ edge.from_col }}</span>
										<i class="bi bi-arrow-right text-slate-500 shrink-0"></i>
										<span class="text-emerald-300 font-bold truncate">{{ edge.to }}.{{ edge.to_col }}</span>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- ========================================================= -->
					<!-- TAB 4 CONTENT: ROADMAP & ALUR SISTEM                      -->
					<!-- ========================================================= -->
					<div v-else-if="activeTab === 'roadmap'" class="flex-1 overflow-y-auto space-y-4 sm:space-y-6 pr-1 custom-scrollbar">
						<!-- 5-Layer Workflow -->
						<div class="rounded-xl sm:rounded-2xl border border-white/10 bg-[#0B2027] p-4 sm:p-5">
							<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
								<div>
									<h3 class="font-serif font-extrabold text-sm sm:text-base text-white flex items-center gap-2">
										<i class="bi bi-diagram-3-fill text-amber-400"></i>
										<span>Bagan Alur Kerja Sistem (5-Layer Pipeline)</span>
									</h3>
									<p class="text-xs text-slate-400 mt-0.5">
										Visualisasi bagaimana data masuk, diproses, direlasikan, dan diaudit.
									</p>
								</div>
								<span class="px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/30 uppercase tracking-wider self-start sm:self-auto">
									5-Layer Flow
								</span>
							</div>

							<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-3 sm:gap-4 mt-4">
								<div class="min-h-[190px] p-4 rounded-xl bg-gradient-to-b from-amber-950/40 to-slate-900 border border-amber-500/30 flex flex-col justify-between">
									<div>
										<span class="text-[10px] font-bold text-amber-300 uppercase tracking-widest block mb-1">Layer 1</span>
										<h4 class="font-serif font-bold text-sm sm:text-base text-white">Identitas &amp; Akses</h4>
										<p class="text-xs sm:text-sm text-slate-400 mt-1 leading-relaxed">
											Pintu gerbang autentikasi JWT.
										</p>
										<div class="mt-3 space-y-1.5 font-mono text-[11px]">
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-amber-200">main_admin</div>
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-amber-200">users</div>
										</div>
									</div>
									<div class="mt-3 text-center text-amber-400 text-xs">
										<i class="bi bi-arrow-down xl:bi-arrow-right"></i>
									</div>
								</div>

								<div class="min-h-[190px] p-4 rounded-xl bg-gradient-to-b from-sky-950/40 to-slate-900 border border-sky-500/40 flex flex-col justify-between ring-1 ring-sky-400/20">
									<div>
										<span class="text-[10px] font-bold text-sky-300 uppercase tracking-widest block mb-1">Layer 2</span>
										<h4 class="font-serif font-bold text-sm sm:text-base text-white">Central Hub</h4>
										<p class="text-xs sm:text-sm text-slate-400 mt-1 leading-relaxed">
											Isolasi data gereja multi-tenant.
										</p>
										<div class="mt-3 font-mono text-[11px]">
											<div class="p-1.5 rounded bg-sky-950/60 border border-sky-500/50 text-white font-bold text-center">
												churches (Hub)
											</div>
										</div>
									</div>
									<div class="mt-3 text-center text-sky-400 text-xs">
										<i class="bi bi-arrow-down xl:bi-arrow-right"></i>
									</div>
								</div>

								<div class="min-h-[190px] p-4 rounded-xl bg-gradient-to-b from-teal-950/40 to-slate-900 border border-teal-500/30 flex flex-col justify-between">
									<div>
										<span class="text-[10px] font-bold text-teal-300 uppercase tracking-widest block mb-1">Layer 3</span>
										<h4 class="font-serif font-bold text-sm sm:text-base text-white">Operasional Gereja</h4>
										<p class="text-xs sm:text-sm text-slate-400 mt-1 leading-relaxed">
											Kegiatan ibadah &amp; jemaat.
										</p>
										<div class="mt-3 space-y-1.5 font-mono text-[11px]">
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-teal-200">church_admins</div>
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-teal-200">jemaat_users</div>
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-teal-200">church_agendas</div>
										</div>
									</div>
									<div class="mt-3 text-center text-teal-400 text-xs">
										<i class="bi bi-arrow-down xl:bi-arrow-right"></i>
									</div>
								</div>

								<div class="min-h-[190px] p-4 rounded-xl bg-gradient-to-b from-emerald-950/40 to-slate-900 border border-emerald-500/30 flex flex-col justify-between">
									<div>
										<span class="text-[10px] font-bold text-emerald-300 uppercase tracking-widest block mb-1">Layer 4</span>
										<h4 class="font-serif font-bold text-sm sm:text-base text-white">Finansial &amp; Kas</h4>
										<p class="text-xs sm:text-sm text-slate-400 mt-1 leading-relaxed">
											Arus kas &amp; kontrol pagu RAPB.
										</p>
										<div class="mt-3 space-y-1.5 font-mono text-[11px]">
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-emerald-200">anggaran_gereja</div>
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-emerald-200">pemasukan_gereja</div>
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-emerald-200">pengeluaran_gereja</div>
										</div>
									</div>
									<div class="mt-3 text-center text-emerald-400 text-xs">
										<i class="bi bi-arrow-down xl:bi-arrow-right"></i>
									</div>
								</div>

								<div class="min-h-[190px] p-4 rounded-xl bg-gradient-to-b from-indigo-950/40 to-slate-900 border border-indigo-500/30 flex flex-col justify-between">
									<div>
										<span class="text-[10px] font-bold text-indigo-300 uppercase tracking-widest block mb-1">Layer 5</span>
										<h4 class="font-serif font-bold text-sm sm:text-base text-white">Audit &amp; Integritas</h4>
										<p class="text-xs sm:text-sm text-slate-400 mt-1 leading-relaxed">
											Audit trail immutable &amp; log.
										</p>
										<div class="mt-3 space-y-1.5 font-mono text-[11px]">
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-indigo-200">audit_transaksi_keuangan</div>
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-indigo-200">audit_logs</div>
											<div class="p-1 rounded bg-slate-950 border border-slate-800 text-indigo-200">system_settings</div>
										</div>
									</div>
									<div class="mt-3 text-center text-indigo-400 text-xs">
										<i class="bi bi-shield-check"></i>
									</div>
								</div>
							</div>
						</div>

						<!-- Timeline Milestones -->
						<div class="rounded-xl sm:rounded-2xl border border-white/10 bg-[#0B2027] p-4 sm:p-5">
							<h3 class="font-serif font-extrabold text-sm sm:text-base text-white flex items-center gap-2 mb-3">
								<i class="bi bi-signpost-split text-emerald-400"></i>
								<span>Roadmap Evolusi Database CMS</span>
							</h3>

							<div class="space-y-3 sm:space-y-4 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
								<div class="relative pl-7 sm:pl-8">
									<div class="absolute left-1 top-1 h-4 w-4 rounded-full bg-emerald-500 flex items-center justify-center text-slate-950 text-[10px] font-bold shadow">
										<i class="bi bi-check"></i>
									</div>
									<div class="p-3 sm:p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30">
										<div class="flex items-center justify-between gap-2">
											<h4 class="font-serif font-bold text-xs sm:text-sm text-emerald-300">
												Fase 1: Fondasi Autentikasi &amp; Entitas Gereja (Core Baseline)
											</h4>
											<span class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 uppercase">Selesai</span>
										</div>
										<p class="text-xs text-slate-300 mt-1 leading-relaxed">
											Tabel dasar <code>main_admin</code>, <code>users</code>, <code>churches</code>, <code>church_admins</code>, dan <code>jemaat_users</code>.
										</p>
									</div>
								</div>

								<div class="relative pl-7 sm:pl-8">
									<div class="absolute left-1 top-1 h-4 w-4 rounded-full bg-emerald-500 flex items-center justify-center text-slate-950 text-[10px] font-bold shadow">
										<i class="bi bi-check"></i>
									</div>
									<div class="p-3 sm:p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30">
										<div class="flex items-center justify-between gap-2">
											<h4 class="font-serif font-bold text-xs sm:text-sm text-emerald-300">
												Fase 2: Mesin Keuangan Terpadu &amp; Audit Trail (Financial Ledger)
											</h4>
											<span class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 uppercase">Selesai</span>
										</div>
										<p class="text-xs text-slate-300 mt-1 leading-relaxed">
											Tabel finansial: <code>anggaran_gereja</code>, <code>pemasukan_gereja</code>, <code>pengeluaran_gereja</code>, dan <code>audit_transaksi_keuangan</code>.
										</p>
									</div>
								</div>

								<div class="relative pl-7 sm:pl-8">
									<div class="absolute left-1 top-1 h-4 w-4 rounded-full bg-amber-400 flex items-center justify-center text-slate-950 text-[10px] font-bold shadow animate-pulse">
										<i class="bi bi-lightning-fill"></i>
									</div>
									<div class="p-3 sm:p-4 rounded-xl bg-slate-900/80 border border-amber-500/40">
										<div class="flex items-center justify-between gap-2">
											<h4 class="font-serif font-bold text-xs sm:text-sm text-amber-300">
												Fase 3: Dynamic DBMS Inspector &amp; Bagan UML Interaktif
											</h4>
											<span class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 uppercase">Aktif</span>
										</div>
										<p class="text-xs text-slate-300 mt-1 leading-relaxed">
											PostgreSQL Control Center adaptif tanpa hardcoding. Auto-discovery skema, masking kolom, DDL generator, optimasi indeks (ANALYZE), visual ERD, dan konsol SQL baca aman.
										</p>
									</div>
								</div>

								<div class="relative pl-7 sm:pl-8">
									<div class="absolute left-1 top-1 h-4 w-4 rounded-full bg-slate-700 flex items-center justify-center text-slate-400 text-[10px] font-bold shadow">
										<i class="bi bi-hourglass-split"></i>
									</div>
									<div class="p-3 sm:p-4 rounded-xl bg-slate-900/40 border border-slate-800">
										<div class="flex items-center justify-between gap-2">
											<h4 class="font-serif font-bold text-xs sm:text-sm text-slate-300">
												Fase 4: Skalabilitas Tinggi &amp; Partisi Data Skala Besar
											</h4>
											<span class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 uppercase">Mendatang</span>
										</div>
										<ul class="mt-1.5 space-y-1 text-xs text-slate-400 list-disc list-inside">
											<li>Table Partitioning bulanan untuk <code>audit_logs</code>.</li>
											<li>Materialized Views untuk ringkasan laporan kas instan.</li>
											<li>Read-Replica Connection Pooling (PgBouncer).</li>
										</ul>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- ========================================================= -->
					<!-- TAB 5 CONTENT: KONSOL SQL AMAN                            -->
					<!-- ========================================================= -->
					<div v-else-if="activeTab === 'query'" class="flex-1 flex flex-col min-h-0">
						<div class="space-y-2.5 sm:space-y-3 mb-3 shrink-0">
							<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
								<div class="flex items-center gap-2">
									<i class="bi bi-terminal-fill text-indigo-400"></i>
									<h3 class="font-serif font-bold text-xs sm:text-sm text-white">Konsol Kueri SQL Aman (Read-Only)</h3>
								</div>
								<span class="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800 self-start sm:self-auto">
									SELECT / EXPLAIN / WITH (Maks 100 baris)
								</span>
							</div>

							<!-- Presets -->
							<div class="flex items-center gap-1.5 flex-wrap">
								<span class="text-[10px] text-slate-400 font-semibold">Preset:</span>
								<button 
									v-for="(preset, pIdx) in sampleQueries" 
									:key="pIdx"
									type="button" 
									@click="setPresetQuery(preset.sql)"
									class="text-[10px] px-2 py-0.5 sm:py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-indigo-300 border border-indigo-500/30 transition cursor-pointer active:scale-95"
								>
									{{ preset.label }}
								</button>
							</div>

							<!-- Editor -->
							<div class="space-y-2">
								<textarea 
									v-model="sqlQuery"
									rows="3" 
									placeholder="Tulis kueri SELECT di sini..."
									class="w-full rounded-xl sm:rounded-2xl bg-[#0B2027] border border-slate-700 p-3 font-mono text-xs text-indigo-200 outline-none focus:border-indigo-400 resize-none shadow-inner"
								></textarea>
								
								<div class="flex justify-end">
									<button 
										type="button" 
										@click="runSqlQuery" 
										:disabled="isQueryRunning || !sqlQuery.trim()"
										class="w-full sm:w-auto px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition cursor-pointer shadow-lg disabled:opacity-50 flex items-center justify-center gap-1.5 active:scale-95"
									>
										<i class="bi bi-play-fill text-sm" :class="{ 'animate-spin': isQueryRunning }"></i>
										<span>{{ isQueryRunning ? 'Mengeksekusi...' : 'Jalankan Kueri SQL' }}</span>
									</button>
								</div>
							</div>

							<div v-if="queryError" class="p-2.5 sm:p-3 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-200 text-xs flex items-center gap-2">
								<i class="bi bi-exclamation-octagon-fill text-rose-400 shrink-0"></i>
								<span class="break-all">{{ queryError }}</span>
							</div>
						</div>

						<!-- Results -->
						<div class="flex-1 min-h-0 overflow-auto rounded-xl sm:rounded-2xl border border-white/10 bg-[#0B2027]/80 custom-scrollbar relative">
							<div v-if="isQueryRunning" class="absolute inset-0 bg-[#0B2027]/70 backdrop-blur-sm flex items-center justify-center z-20">
								<div class="flex items-center gap-2 text-indigo-300 text-xs sm:text-sm font-semibold">
									<i class="bi bi-arrow-repeat animate-spin text-base sm:text-lg"></i>
									<span>Mengeksekusi query database...</span>
								</div>
							</div>

							<div v-if="queryResult" class="min-w-full">
								<div class="sticky top-0 bg-[#061418] border-b border-indigo-500/30 px-3 sm:px-4 py-2 flex items-center justify-between text-xs z-10">
									<span class="text-slate-300 text-[11px] sm:text-xs">
										Hasil: <strong class="text-white">{{ queryResult.total_rows }}</strong> baris
									</span>
									<span class="text-emerald-400 font-mono text-[10px] sm:text-[11px]">
										Waktu: {{ queryResult.execution_ms }} ms
									</span>
								</div>

								<table class="min-w-[500px] sm:min-w-full text-left text-xs border-collapse">
									<thead class="bg-[#0B2027] border-b border-white/10 text-indigo-300">
										<tr>
											<th class="px-2.5 sm:px-3 py-2 w-10 text-center font-bold text-slate-500">#</th>
											<th 
												v-for="col in queryResult.columns" 
												:key="col"
												class="px-3 sm:px-4 py-2 font-bold uppercase tracking-wider whitespace-nowrap"
											>
												{{ col }}
											</th>
										</tr>
									</thead>
									<tbody class="divide-y divide-white/5 font-mono text-[11px]">
										<tr 
											v-for="(r, qIdx) in queryResult.rows" 
											:key="qIdx"
											class="hover:bg-white/[0.03]"
										>
											<td class="px-2.5 sm:px-3 py-1.5 text-center text-slate-500">{{ qIdx + 1 }}</td>
											<td 
												v-for="col in queryResult.columns" 
												:key="col"
												class="px-3 sm:px-4 py-1.5 max-w-[220px] truncate text-slate-300"
											>
												<span v-if="r[col] === null" class="text-slate-600 italic">&lt;null&gt;</span>
												<span v-else>{{ r[col] }}</span>
											</td>
										</tr>
									</tbody>
								</table>
							</div>

							<div v-else-if="!isQueryRunning" class="py-16 text-center text-slate-500 text-xs p-4">
								<i class="bi bi-terminal text-3xl block mb-2 text-slate-600"></i>
								<span>Pilih preset di atas atau tulis kueri SQL kustom untuk melihat hasil data.</span>
							</div>
						</div>
					</div>

					<!-- ========================================================= -->
					<!-- TAB 6 CONTENT: STATISTIK TABEL                            -->
					<!-- ========================================================= -->
					<div v-else-if="activeTab === 'metrics'" class="flex-1 overflow-y-auto space-y-3 sm:space-y-4 pr-1 custom-scrollbar">
						<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
							<div class="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-[#0B2027] border border-white/5 space-y-1">
								<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400">Jumlah Baris</span>
								<p class="text-xl sm:text-2xl font-bold text-white">{{ currentTableMeta?.rows?.toLocaleString('id-ID') || 0 }}</p>
							</div>
							<div class="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-[#0B2027] border border-white/5 space-y-1">
								<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400">Ukuran Disk</span>
								<p class="text-xl sm:text-2xl font-bold text-emerald-300">{{ currentTableMeta?.size || 'N/A' }}</p>
							</div>
							<div class="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-[#0B2027] border border-white/5 space-y-1">
								<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400">Jumlah Kolom</span>
								<p class="text-xl sm:text-2xl font-bold text-cyan-300">{{ currentTableMeta?.columns?.length || 0 }}</p>
							</div>
						</div>

						<div class="p-4 sm:p-5 rounded-xl sm:rounded-2xl bg-[#0B2027] border border-white/5 space-y-3 text-xs">
							<h4 class="font-serif font-bold text-xs sm:text-sm text-white">Ringkasan Integritas Data &amp; Pemeliharaan</h4>
							<p class="text-slate-300 leading-relaxed font-sans text-[11px] sm:text-xs">
								Tabel <strong>{{ currentTableMeta?.name }}</strong> berada di bawah skema publik PostgreSQL. Seluruh query diarahkan melalui koneksi terenkripsi dengan proteksi parameterisasi SQLAlchemy untuk menjamin tidak ada celah SQL berbahaya.
							</p>
							<div class="flex flex-col sm:flex-row sm:items-center justify-between pt-2 border-t border-slate-800 gap-2">
								<div class="flex items-center gap-2">
									<span class="h-2 w-2 rounded-full bg-emerald-400"></span>
									<span class="text-emerald-300 font-semibold text-[11px] sm:text-xs">Tabel terindeks &amp; siap melayani query operasional CMS.</span>
								</div>
								<button 
									type="button" 
									@click="optimizeCurrentTable" 
									:disabled="isOptimizing"
									class="px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 text-xs font-semibold cursor-pointer active:scale-95 self-start sm:self-auto"
								>
									Optimasi Indeks Sekarang
								</button>
							</div>
						</div>
					</div>

				</div>
			</section>

			<!-- MODAL ROW INSPECTOR -->
			<Transition name="fade">
				<div 
					v-if="isRowModalOpen && selectedRow" 
					@click.self="closeRowInspector"
					class="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-3 sm:p-4 overflow-y-auto"
				>
					<div class="bg-slate-900 border border-emerald-500/30 rounded-2xl sm:rounded-3xl max-w-2xl w-full p-4 sm:p-6 shadow-2xl my-auto max-h-[90vh] sm:max-h-[85vh] flex flex-col">
						<div class="flex items-center justify-between pb-3 border-b border-white/10 shrink-0">
							<div>
								<span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wider text-emerald-400">Inspeksi Baris</span>
								<h3 class="font-serif font-bold text-lg sm:text-xl text-white">Tabel: {{ selectedTable }}</h3>
							</div>
							<button 
								type="button" 
								@click="closeRowInspector"
								class="p-1.5 sm:p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white cursor-pointer transition"
							>
								<i class="bi bi-x-lg text-xs sm:text-sm"></i>
							</button>
						</div>

						<div class="flex-1 overflow-y-auto my-3 sm:my-4 space-y-2 font-mono text-xs custom-scrollbar pr-1">
							<div 
								v-for="(val, key) in selectedRow" 
								:key="key"
								class="p-2.5 sm:p-3 rounded-xl bg-[#0B2027] border border-white/5 flex flex-col sm:flex-row sm:items-start justify-between gap-1 text-[11px] sm:text-xs"
							>
								<span class="text-slate-400 font-semibold shrink-0 sm:w-44">{{ key }}:</span>
								<span class="text-slate-200 break-all select-all sm:text-left">
									{{ val === null ? '<null>' : val }}
								</span>
							</div>
						</div>

						<div class="pt-2.5 border-t border-white/10 flex items-center justify-end shrink-0">
							<button 
								type="button" 
								@click="closeRowInspector"
								class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold cursor-pointer"
							>
								Tutup
							</button>
						</div>
					</div>
				</div>
			</Transition>

			<!-- MODAL DDL SCHEMA VIEWER -->
			<Transition name="fade">
				<div 
					v-if="isDdlModalOpen" 
					@click.self="isDdlModalOpen = false"
					class="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 flex items-center justify-center p-3 sm:p-4 overflow-y-auto"
				>
					<div class="bg-slate-900 border border-cyan-500/40 rounded-2xl sm:rounded-3xl max-w-3xl w-full p-4 sm:p-6 shadow-2xl my-auto max-h-[90vh] sm:max-h-[85vh] flex flex-col">
						<div class="flex items-center justify-between pb-3 border-b border-white/10 shrink-0">
							<div class="flex items-center gap-2">
								<i class="bi bi-file-earmark-code text-cyan-400 text-lg sm:text-xl"></i>
								<div>
									<h3 class="font-serif font-bold text-lg sm:text-xl text-white">DDL SQL: {{ selectedTable }}</h3>
									<span class="text-[10px] sm:text-[11px] text-slate-400">CREATE TABLE dengan Constraint PostgreSQL</span>
								</div>
							</div>
							<button 
								type="button" 
								@click="isDdlModalOpen = false"
								class="p-1.5 sm:p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white cursor-pointer transition"
							>
								<i class="bi bi-x-lg text-xs sm:text-sm"></i>
							</button>
						</div>

						<div class="flex-1 overflow-y-auto my-3 sm:my-4 custom-scrollbar">
							<div v-if="isDdlLoading" class="py-12 text-center text-cyan-400 text-xs font-semibold">
								<i class="bi bi-arrow-repeat animate-spin text-xl block mb-2"></i>
								<span>Menghasilkan skema DDL PostgreSQL...</span>
							</div>
							<pre v-else class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-[#061418] border border-cyan-500/20 font-mono text-[11px] sm:text-xs text-cyan-200 overflow-x-auto selection:bg-cyan-500/30 selection:text-white leading-relaxed">{{ ddlContent }}</pre>
						</div>

						<div class="pt-2.5 sm:pt-3 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 shrink-0">
							<span class="text-[10px] sm:text-[11px] text-slate-400">PostgreSQL Standard Dialect</span>
							<div class="flex items-center gap-2 w-full sm:w-auto">
								<button 
									type="button" 
									@click="copyDdl"
									class="flex-1 sm:flex-initial px-3.5 sm:px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs cursor-pointer flex items-center justify-center gap-1.5 transition active:scale-95"
								>
									<i class="bi bi-clipboard-check"></i>
									<span>Salin DDL</span>
								</button>
								<button 
									type="button" 
									@click="isDdlModalOpen = false"
									class="flex-1 sm:flex-initial px-3.5 sm:px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold cursor-pointer text-center"
								>
									Tutup
								</button>
							</div>
						</div>
					</div>
				</div>
			</Transition>

			<!-- FLOATING TOAST NOTIFICATION -->
			<Transition name="fade">
				<div 
					v-if="isToastVisible"
					class="fixed bottom-4 sm:bottom-6 right-4 sm:right-6 z-50 px-3.5 sm:px-4 py-2.5 sm:py-3 rounded-xl sm:rounded-2xl bg-emerald-950/95 border border-emerald-500/40 text-emerald-200 text-xs font-semibold shadow-2xl flex items-center gap-2 backdrop-blur-md max-w-sm"
				>
					<i class="bi bi-check-circle-fill text-emerald-400 text-sm shrink-0"></i>
					<span class="truncate">{{ toastMessage }}</span>
				</div>
			</Transition>
		</div>
	</MainAdminLayout>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
	width: 5px;
	height: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
	background: rgba(11, 32, 39, 0.5);
	border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
	background: rgba(52, 211, 153, 0.25);
	border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
	background: rgba(52, 211, 153, 0.45);
}

.no-scrollbar-on-touch {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
.no-scrollbar-on-touch::-webkit-scrollbar {
	display: none;
}

.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
	transform: scale(0.97);
}
</style>
