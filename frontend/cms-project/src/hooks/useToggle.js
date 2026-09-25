import { ref } from 'vue'

export function useToggle(initialValue = false) {
  const state = ref(initialValue)

  const toggle = (val) => {
    state.value = typeof val === 'boolean' ? val : !state.value
  }

  return [state, toggle]
}
