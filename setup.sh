#!/bin/bash

# Hollanda Vize Randevu Otomasyonu - Kurulum Scripti

echo "=================================================="
echo "🇳🇱 Hollanda Vize Randevu Otomasyonu - Kurulum"
echo "=================================================="
echo ""

# Check Python version
echo "📋 Python versiyonu kontrol ediliyor..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version bulundu"
echo ""

# Create virtual environment
echo "🔧 Virtual environment oluşturuluyor..."
python3 -m venv venv
echo "✅ Virtual environment oluşturuldu"
echo ""

# Activate virtual environment
echo "🔌 Virtual environment aktifleştiriliyor..."
source venv/bin/activate
echo "✅ Virtual environment aktif"
echo ""

# Upgrade pip
echo "⬆️  pip güncelleniyor..."
pip install --upgrade pip
echo "✅ pip güncellendi"
echo ""

# Install requirements
echo "📦 Bağımlılıklar yükleniyor..."
pip install -r requirements.txt
echo "✅ Bağımlılıklar yüklendi"
echo ""

# Install Playwright browsers
echo "🌐 Playwright tarayıcıları yükleniyor..."
playwright install chromium
echo "✅ Playwright tarayıcıları yüklendi"
echo ""

# Create config file if not exists
if [ ! -f "config.json" ]; then
    echo "📝 config.json oluşturuluyor..."
    cp config.json.example config.json
    echo "✅ config.json oluşturuldu"
    echo ""
    echo "⚠️  ÖNEMLI: config.json dosyasını düzenlemeyi unutmayın!"
else
    echo "ℹ️  config.json zaten mevcut"
fi
echo ""

# Create logs directory
echo "📁 logs klasörü oluşturuluyor..."
mkdir -p logs
echo "✅ logs klasörü oluşturuldu"
echo ""

echo "=================================================="
echo "✅ Kurulum tamamlandı!"
echo "=================================================="
echo ""
echo "📝 Sonraki adımlar:"
echo "1. config.json dosyasını düzenleyin"
echo "2. Virtual environment'ı aktifleştirin: source venv/bin/activate"
echo "3. Botu çalıştırın: python main.py"
echo ""
echo "📚 Detaylı bilgi için README.md dosyasını okuyun"
echo ""
