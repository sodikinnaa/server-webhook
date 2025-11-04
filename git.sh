#!/bin/bash
# gitpush.sh
# Skrip otomatis untuk add, commit, dan push ke branch aktif

# Pastikan ada pesan commit
if [ -z "$1" ]; then
  echo "⚠️  Harap masukkan pesan commit!"
  echo "Contoh: ./gitpush.sh \"update fitur login\""
  exit 1
fi

# Pindah ke folder tempat skrip berada (root project)
cd "$(dirname "$0")"

# Tampilkan status
echo "📦 Status repository:"
git status

# Tambahkan semua perubahan
echo "➕ Menambahkan semua perubahan..."
git add .

# Commit dengan pesan dari argumen
echo "📝 Melakukan commit dengan pesan: \"$1\""
git commit -m "$1"

# Push ke branch aktif
echo "🚀 Mengirim ke branch aktif..."
git push

echo "✅ Selesai! Semua perubahan sudah dikirim ke remote repository."
