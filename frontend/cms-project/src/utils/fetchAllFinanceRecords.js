const PAGE_SIZE = 500

export async function fetchAllFinanceRecords(url, headers) {
  const records = []
  let skip = 0

  while (true) {
    const separator = url.includes('?') ? '&' : '?'
    const response = await fetch(`${url}${separator}skip=${skip}&limit=${PAGE_SIZE}`, { headers })
    if (!response.ok) {
      throw new Error(`Gagal memuat data transaksi (HTTP ${response.status}).`)
    }

    const page = await response.json()
    if (!Array.isArray(page)) {
      throw new Error('Format data transaksi dari server tidak valid.')
    }

    records.push(...page)
    if (page.length < PAGE_SIZE) return records
    skip += PAGE_SIZE
  }
}
