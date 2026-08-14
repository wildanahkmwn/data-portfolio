# LinkedIn Case Study (siap copy-paste)

Pakai post ini setelah repo sudah di GitHub dan ada screenshot dashboard.

---

## Post versi pendek

Saya bangun portfolio end-to-end data stack dari nol:

Raw ecommerce orders -> ClickHouse -> SQL marts -> data quality checks -> Streamlit dashboard.

Yang saya tekankan bukan hanya "bisa query", tapi alur yang dipakai bisnis:
1. Ingest data transaksi
2. Model metric yang jelas (GMV, AOV, LTV)
3. Validasi quality sebelum data dipakai
4. Serve dashboard yang langsung kebaca non-teknis

Stack: Python, ClickHouse, Airflow (optional), Streamlit, SQL.

Repo: [isi link GitHub]
Dashboard demo: [isi screenshot / loom 60 detik]

Open for side project / freelance:
- Data health check
- MVP data stack (ingest + warehouse + dashboard)
- Perbaikan metric yang sering beda angka

DM siap.

#dataengineering #clickhouse #analytics #freelance #opentowork

---

## Post versi panjang (lebih bagus untuk Featured)

Problem yang sering saya lihat di UMKM/startup:
- Sales data ada di banyak tempat
- Dashboard beda angka dengan finance
- Tidak ada pengecekan freshness / duplicate
- Tim bisnis tidak percaya datanya

Jadi saya buat mini project yang meniru solusi production:

Architecture
- Source: sample ecommerce orders
- Ingest: Python (bisa dijadwalkan lewat Airflow)
- Warehouse: ClickHouse
- Marts: daily sales, customer LTV, top products
- Quality gate: null, duplicate, GMV consistency, freshness
- Serve: Streamlit dashboard

Business metrics
- GMV
- Orders
- AOV
- Top products
- Customer LTV

Pelajaran penting:
Metric bagus tidak cukup. Harus ada definisi + quality check + cara serve yang jelas.

Kalau perusahaanmu masih manual Excel / dashboard sering mismatch, saya bisa bantu mulai dari audit 3 hari.

Repo: [link]
#EndToEndData #DataEngineer #AnalyticsEngineer #ClickHouse #Airflow

---

## Caption screenshot (kalau upload gambar dashboard)

"Sebelum optimasi narrative: data mentah.
Sesudah: GMV, AOV, top products, freshness — satu layar."
