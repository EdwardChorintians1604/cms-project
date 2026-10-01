<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 1
  },
  ministries: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['add-child', 'edit', 'delete'])

const isCollapsed = ref(false)

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const getInitials = (name) => {
  if (!name) return 'PG'
  return name.split(' ').map(n => n[0]).filter(Boolean).slice(0, 2).join('').toUpperCase()
}

// Cari info lembaga yang dipimpin pejabat ini jika ada
const linkedMinistry = () => {
  if (!props.node.ministry_id || !props.ministries) return null
  return props.ministries.find(m => m.id === props.node.ministry_id)
}
</script>

<template>
  <div class="org-tree-node flex flex-col items-center">
    
    <!-- CARD PEJABAT STRUKTUR -->
    <div 
      class="w-72 bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 rounded-2xl p-4 transition-all duration-300 relative group z-10 text-left"
      :class="[
        node.hierarchy_level === 1 
          ? 'border-2 border-amber-400 shadow-2xl shadow-amber-500/20 hover:border-amber-300' 
          : node.hierarchy_level === 2 
            ? 'border-2 border-blue-500/70 shadow-xl shadow-blue-500/10 hover:border-blue-400' 
            : node.hierarchy_level === 3
              ? 'border border-emerald-500/60 shadow-lg shadow-emerald-500/5 hover:border-emerald-400'
              : 'border border-slate-700 hover:border-slate-500'
      ]">
      
      <!-- Top Accent Bar -->
      <div 
        class="absolute top-0 left-0 right-0 h-1.5 rounded-t-2xl"
        :class="[
          node.hierarchy_level === 1 
            ? 'bg-gradient-to-r from-amber-500 via-amber-300 to-amber-500' 
            : node.hierarchy_level === 2 
              ? 'bg-gradient-to-r from-blue-600 via-indigo-400 to-blue-600' 
              : node.hierarchy_level === 3
                ? 'bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-500'
                : 'bg-slate-600'
        ]"></div>

      <!-- Header: Department & Hierarchy Badge -->
      <div class="flex items-center justify-between gap-2 mb-2 pt-0.5">
        <span 
          class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border truncate max-w-[150px]"
          :class="[
            node.hierarchy_level === 1
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
              : node.hierarchy_level === 2
                ? 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
          ]">
          {{ node.department || 'Pelayanan' }}
        </span>

        <span 
          class="text-[9px] px-2 py-0.5 rounded-full font-semibold"
          :class="node.status === 'Aktif' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-300'">
          {{ node.status || 'Aktif' }}
        </span>
      </div>

      <!-- Main Profile: Photo & Info -->
      <div class="flex items-start gap-3">
        <!-- Avatar Photo / Initials -->
        <div 
          class="w-12 h-12 rounded-xl shrink-0 flex items-center justify-center font-black text-sm overflow-hidden shadow-inner border"
          :class="[
            node.hierarchy_level === 1
              ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
              : node.hierarchy_level === 2
                ? 'bg-blue-500/20 border-blue-500/40 text-blue-300'
                : 'bg-slate-800 border-slate-700 text-slate-300'
          ]">
          <img v-if="node.photo_url" :src="node.photo_url" alt="Foto" class="w-full h-full object-cover" />
          <span v-else>{{ getInitials(node.name) }}</span>
        </div>

        <div class="min-w-0 flex-1">
          <h4 class="text-sm font-bold text-white leading-tight truncate" :title="node.name">
            {{ node.title ? `${node.title} ` : '' }}{{ node.name }}
          </h4>
          <p 
            class="text-xs font-semibold mt-0.5 truncate"
            :class="node.hierarchy_level === 1 ? 'text-amber-400' : node.hierarchy_level === 2 ? 'text-blue-400' : 'text-emerald-400'"
            :title="node.role_position">
            {{ node.role_position }}
          </p>
          <p class="text-[10px] text-slate-400 mt-1">
            Periode: <span class="text-slate-300 font-medium">{{ node.period || '2024 - 2029' }}</span>
          </p>
        </div>
      </div>

      <!-- Integrated Ministry Badge (Jika Memimpin Lembaga Pelayanan) -->
      <div v-if="linkedMinistry()" class="mt-2.5 px-2.5 py-1 bg-cyan-950/40 border border-cyan-500/30 rounded-lg flex items-center justify-between text-[10px]">
        <div class="flex items-center gap-1.5 text-cyan-300 truncate">
          <span>🏛️</span>
          <span class="font-semibold truncate">{{ linkedMinistry().name }}</span>
        </div>
        <RouterLink to="/church-ministries" class="text-cyan-400 hover:text-cyan-200 shrink-0 ml-1 font-bold" title="Buka Detail Lembaga">
          ↗
        </RouterLink>
      </div>

      <!-- Quick Contact Links -->
      <div v-if="node.phone || node.email" class="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <div class="flex items-center gap-2">
          <a 
            v-if="node.phone" 
            :href="'https://wa.me/' + node.phone.replace(/[^0-9]/g, '')" 
            target="_blank" 
            class="p-1 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition" 
            title="Chat WhatsApp">
            <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.664-.698c.969.584 1.961.913 2.796.914h.005c3.18 0 5.767-2.587 5.768-5.766 0-3.181-2.587-5.767-5.768-5.767zm0 10.536h-.004c-.868 0-1.748-.242-2.545-.715l-.182-.108-1.58.414.422-1.541-.118-.188c-.521-.83-.796-1.794-.795-2.784.001-2.628 2.14-4.767 4.77-4.767 2.628 0 4.767 2.139 4.768 0 2.628-2.139 4.768-4.768 4.768z"/></svg>
          </a>
          <a 
            v-if="node.email" 
            :href="'mailto:' + node.email" 
            class="p-1 rounded-md bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 transition" 
            title="Kirim Email">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
          </a>
          <span class="text-[10px] text-slate-400 font-mono">{{ node.phone || node.email }}</span>
        </div>
      </div>

      <!-- Action Toolbar (Builder Features) -->
      <div class="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between gap-1 print:hidden">
        <!-- Add Subordinate / Child -->
        <button 
          @click="$emit('add-child', node)"
          class="px-2.5 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition shadow-sm"
          title="Tambah bawahan di bawah pejabat ini">
          <svg class="w-3 h-3 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
          </svg>
          + Bawahan
        </button>

        <div class="flex items-center gap-1">
          <!-- Edit Button -->
          <button 
            @click="$emit('edit', node)"
            class="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
            title="Edit Data Pejabat">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>

          <!-- Delete Button -->
          <button 
            @click="$emit('delete', node)"
            class="p-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 hover:text-rose-300 transition"
            title="Hapus dari Bagan">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Toggle Subordinates Button (if has children) -->
    <div v-if="node.children && node.children.length > 0" class="flex flex-col items-center z-20 -mt-1.5">
      <button 
        @click="toggleCollapse"
        class="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-tight shadow-md flex items-center gap-1.5 transition print:hidden"
        :class="isCollapsed 
          ? 'bg-amber-500 text-slate-950 hover:bg-amber-400 ring-2 ring-amber-400/50' 
          : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-600'">
        <svg v-if="isCollapsed" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
        </svg>
        <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 15l7-7 7 7" />
        </svg>
        <span>{{ isCollapsed ? `Buka (${node.children.length})` : `${node.children.length} Bawahan` }}</span>
      </button>
    </div>

    <!-- CONNECTOR LINE DOWN FROM PARENT -->
    <div v-if="!isCollapsed && node.children && node.children.length > 0" class="w-0.5 h-8 bg-slate-600"></div>

    <!-- CHILDREN BRANCH CONTAINER -->
    <div 
      v-if="!isCollapsed && node.children && node.children.length > 0" 
      class="flex items-start justify-center relative pt-4">
      
      <!-- HORIZONTAL CONNECTOR LINE -->
      <div 
        v-if="node.children.length > 1"
        class="absolute top-0 h-0.5 bg-slate-600"
        :style="{
          left: `calc(${100 / (node.children.length * 2)}%)`,
          right: `calc(${100 / (node.children.length * 2)}%)`
        }"></div>

      <!-- EACH CHILD NODE COLUMN -->
      <div 
        v-for="child in node.children" 
        :key="child.id"
        class="flex flex-col items-center px-4 relative">
        
        <!-- VERTICAL CONNECTOR LINE UP TO HORIZONTAL BAR -->
        <div class="w-0.5 h-4 bg-slate-600 -mt-4 mb-0"></div>

        <!-- RECURSIVE CHILD NODE -->
        <OrgTreeNode 
          :node="child"
          :level="level + 1"
          :ministries="ministries"
          @add-child="$emit('add-child', $event)"
          @edit="$emit('edit', $event)"
          @delete="$emit('delete', $event)" />
      </div>

    </div>

  </div>
</template>
