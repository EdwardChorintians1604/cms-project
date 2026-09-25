/**
 * Utilitas Ekspor Laporan Keuangan GracePoint (PDF, Excel / CSV, JSON)
 */

const formatCurrencyIDR = (num) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  }).format(num || 0)
}

/**
 * 1. EKSPOR KE EXCEL / CSV (Dengan UTF-8 BOM agar kompatibel dengan MS Excel, Google Sheets, & LibreOffice)
 */
export function exportToCSV({ title, filename, items, isPemasukan = true, churchFilter = 'Semua' }) {
  if (!items || items.length === 0) {
    alert('Tidak ada data transaksi yang dapat diekspor.')
    return
  }

  const dateNow = new Date().toLocaleDateString('id-ID', { dateStyle: 'full' })
  let csvContent = '\uFEFF' // Byte Order Mark untuk UTF-8

  // Header Laporan
  csvContent += `"LAPORAN ${title.toUpperCase()}"\n`
  csvContent += `"Platform Manajemen & Pelayanan Gereja GracePoint"\n`
  csvContent += `"Kriteria Cabang: ${churchFilter}"\n`
  csvContent += `"Tanggal Ekspor: ${dateNow}"\n\n`

  // Header Kolom Tabel
  if (isPemasukan) {
    csvContent += `"No","No. Transaksi","Tanggal","Kategori","Cabang Gereja","Nominal (Rp)","Metode Pembayaran","Penyetor / Donatur","Keterangan"\n`
  } else {
    csvContent += `"No","No. Transaksi","Tanggal","Kategori","Cabang Gereja","Nominal (Rp)","Metode Pembayaran","Penerima / Vendor","Status","Keterangan"\n`
  }

  let totalNominal = 0

  // Isi Baris Data
  items.forEach((row, idx) => {
    const nominal = Number(row.nominal || row.jumlah || 0)
    totalNominal += nominal
    const no = idx + 1
    const noTrx = `"${row.nomor_transaksi || `TRX-${row.id || idx}`}"`
    const tanggal = `"${row.tanggal || '-'}"`
    const kategori = `"${(row.kategori || '-').replace(/"/g, '""')}"`
    const cabang = `"${(row.church_name || 'GracePoint Pusat').replace(/"/g, '""')}"`
    const metode = `"${row.metode_pembayaran || 'Tunai'}"`
    const pihak = `"${(row.nama_penyetor || row.donor_name || row.penerima || '-').replace(/"/g, '""')}"`
    const keterangan = `"${(row.keterangan || '-').replace(/"/g, '""')}"`

    if (isPemasukan) {
      csvContent += `${no},${noTrx},${tanggal},${kategori},${cabang},${nominal},${metode},${pihak},${keterangan}\n`
    } else {
      const status = `"${row.status_persetujuan || 'Disetujui'}"`
      csvContent += `${no},${noTrx},${tanggal},${kategori},${cabang},${nominal},${metode},${pihak},${status},${keterangan}\n`
    }
  })

  // Baris Total
  csvContent += `\n"","TOTAL AKUMULASI","","","",${totalNominal},"","",""\n`

  // Download Trigger
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * 2. EKSPOR KE PDF (Format Resmi Berkop Surat GracePoint Siap Cetak / Save to PDF)
 */
export function exportToPDF({ title, items, isPemasukan = true, churchFilter = 'Semua' }) {
  if (!items || items.length === 0) {
    alert('Tidak ada data transaksi yang dapat dicetak.')
    return
  }

  const printWindow = window.open('', '_blank', 'width=1000,height=800')
  if (!printWindow) {
    alert('Jendela cetak terblokir oleh browser pop-up. Harap izinkan pop-up untuk situs ini.')
    return
  }

  const dateNow = new Date().toLocaleDateString('id-ID', { dateStyle: 'full' })
  let totalNominal = 0

  let rowsHtml = ''
  items.forEach((row, idx) => {
    const nominal = Number(row.nominal || row.jumlah || 0)
    totalNominal += nominal
    const pihak = row.nama_penyetor || row.donor_name || row.penerima || '-'

    rowsHtml += `
      <tr>
        <td style="text-align: center;">${idx + 1}</td>
        <td>${row.nomor_transaksi || `TRX-${row.id || idx}`}</td>
        <td>${row.tanggal || '-'}</td>
        <td><strong>${row.kategori || '-'}</strong></td>
        <td>${row.church_name || 'GracePoint Pusat'}</td>
        <td style="text-align: right; font-weight: bold; font-family: monospace;">${formatCurrencyIDR(nominal)}</td>
        <td style="text-align: center;">${row.metode_pembayaran || 'Tunai'}</td>
        <td>${pihak}</td>
        ${!isPemasukan ? `<td style="text-align: center;"><span class="badge">${row.status_persetujuan || 'Disetujui'}</span></td>` : ''}
        <td><small>${row.keterangan || '-'}</small></td>
      </tr>
    `
  })

  const docHtml = `
    <!DOCTYPE html>
    <html lang="id">
    <head>
      <meta charset="UTF-8">
      <title>Laporan ${title} - GracePoint Church</title>
      <style>
        @page {
          size: A4 landscape;
          margin: 15mm;
        }
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          color: #1e293b;
          margin: 0;
          padding: 10px;
          font-size: 11px;
        }
        .header-kop {
          border-bottom: 3px double #b45309;
          padding-bottom: 12px;
          margin-bottom: 15px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .header-title h1 {
          margin: 0;
          font-size: 20px;
          color: #78350f;
          letter-spacing: 1px;
          text-transform: uppercase;
        }
        .header-title p {
          margin: 2px 0 0;
          font-size: 11px;
          color: #64748b;
        }
        .meta-info {
          display: flex;
          justify-content: space-between;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          padding: 8px 12px;
          border-radius: 6px;
          margin-bottom: 15px;
          font-size: 11px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 20px;
        }
        th {
          background-color: #f1f5f9;
          color: #334155;
          font-weight: bold;
          text-align: left;
          padding: 8px 6px;
          border: 1px solid #cbd5e1;
          font-size: 10px;
          text-transform: uppercase;
        }
        td {
          padding: 6px;
          border: 1px solid #cbd5e1;
          vertical-align: middle;
        }
        tr:nth-child(even) {
          background-color: #fafafa;
        }
        .total-row {
          background-color: #fef3c7 !important;
          font-weight: bold;
        }
        .total-row td {
          border-top: 2px solid #b45309;
          font-size: 12px;
        }
        .badge {
          background: #dcfce7;
          color: #166534;
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 9px;
          font-weight: bold;
        }
        .signatures {
          margin-top: 40px;
          display: flex;
          justify-content: space-between;
          padding: 0 40px;
        }
        .sig-box {
          text-align: center;
          width: 200px;
        }
        .sig-line {
          margin-top: 60px;
          border-bottom: 1px solid #334155;
          font-weight: bold;
        }
        @media print {
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <div class="no-print" style="margin-bottom: 15px; text-align: right;">
        <button onclick="window.print()" style="padding: 8px 16px; background: #d97706; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">
          🖨️ Cetak / Simpan sebagai PDF
        </button>
      </div>

      <div class="header-kop">
        <div class="header-title">
          <h1>GRACEPOINT CHURCH NETWORK</h1>
          <p>Soli Deo Gloria — Sekretariat Perbendaharaan &amp; Administrasi Keuangan Sinode</p>
        </div>
        <div style="text-align: right; font-size: 10px; color: #64748b;">
          <strong>LAPORAN KEUANGAN RESMI</strong><br>
          Dicetak: ${dateNow}
        </div>
      </div>

      <div class="meta-info">
        <div><strong>Jenis Laporan:</strong> Laporan ${title}</div>
        <div><strong>Kriteria Cabang:</strong> ${churchFilter}</div>
        <div><strong>Total Transaksi:</strong> ${items.length} Catatan</div>
      </div>

      <table>
        <thead>
          <tr>
            <th style="width: 30px; text-align: center;">No</th>
            <th>No. Transaksi</th>
            <th>Tanggal</th>
            <th>Kategori</th>
            <th>Cabang</th>
            <th style="text-align: right;">Nominal (Rp)</th>
            <th style="text-align: center;">Metode</th>
            <th>${isPemasukan ? 'Penyetor / Donatur' : 'Penerima / Vendor'}</th>
            ${!isPemasukan ? '<th style="text-align: center;">Status</th>' : ''}
            <th>Keterangan</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
          <tr class="total-row">
            <td colspan="5" style="text-align: right;">TOTAL KESELURUHAN:</td>
            <td style="text-align: right; font-family: monospace; color: #9a3412;">${formatCurrencyIDR(totalNominal)}</td>
            <td colspan="${isPemasukan ? '3' : '4'}"></td>
          </tr>
        </tbody>
      </table>

      <div class="signatures">
        <div class="sig-box">
          <p>Dibuat Oleh,</p>
          <div class="sig-line">Bendahara Pelayanan</div>
          <p style="font-size: 9px; color: #64748b; margin: 4px 0 0;">Majelis Perbendaharaan</p>
        </div>
        <div class="sig-box">
          <p>Mengetahui &amp; Menyetujui,</p>
          <div class="sig-line">Gembala Sidang / Ketua Sinode</div>
          <p style="font-size: 9px; color: #64748b; margin: 4px 0 0;">Badan Pengurus Harian</p>
        </div>
      </div>
    </body>
    </html>
  `

  printWindow.document.open()
  printWindow.document.write(docHtml)
  printWindow.document.close()

  // Tunggu konten selesai dimuat lalu tampilkan dialog cetak
  printWindow.onload = () => {
    printWindow.focus()
  }
}

/**
 * 3. EKSPOR KE JSON (Audit Trail & Backup Data Lengkap)
 */
export function exportToJSON({ title, filename, items, isPemasukan = true, churchFilter = 'Semua' }) {
  if (!items || items.length === 0) {
    alert('Tidak ada data transaksi yang dapat diekspor.')
    return
  }

  const totalNominal = items.reduce((acc, curr) => acc + Number(curr.nominal || curr.jumlah || 0), 0)

  const exportData = {
    platform: 'GracePoint Church Network Management System',
    report_title: `Laporan ${title}`,
    church_filter: churchFilter,
    export_timestamp: new Date().toISOString(),
    total_records: items.length,
    total_nominal: totalNominal,
    formatted_total: formatCurrencyIDR(totalNominal),
    transactions: items
  }

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}_${new Date().toISOString().slice(0, 10)}.json`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * 4. EKSPOR VIA SERVER PYTHON BACKEND (openpyxl & ReportLab)
 */
export async function downloadServerExport({ baseUrl, type = 'pemasukan', format = 'excel', churchId = null, token = null }) {
  const endpoint = `${baseUrl}/keuangan/${type}/export/${format}${churchId ? `?church_id=${churchId}` : ''}`
  const headers = token ? { Authorization: `Bearer ${token}` } : {}

  const response = await fetch(endpoint, { headers })
  if (!response.ok) {
    throw new Error(`Gagal mengunduh laporan dari server: HTTP ${response.status}`)
  }

  const blob = await response.blob()
  const extension = format === 'excel' ? 'xlsx' : 'pdf'
  const filename = `Laporan_${type.charAt(0).toUpperCase() + type.slice(1)}_Server_${new Date().toISOString().slice(0, 10)}.${extension}`

  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

