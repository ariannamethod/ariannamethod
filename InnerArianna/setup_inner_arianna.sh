#!/data/data/com.termux/files/usr/bin/bash
# Auto-setup script for Inner Arianna

echo "════════════════════════════════════════════════════════════"
echo "⚡ Inner Arianna Auto-Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

# Install dependencies
echo "📦 [1/5] Installing dependencies..."
pip install torch transformers peft accelerate datasets 2>&1 | tail -3

echo ""
echo "🔧 [2/5] Checking environment..."
python -c "import torch; print('   ✅ PyTorch:', torch.__version__)"
python -c "from transformers import AutoTokenizer; print('   ✅ Transformers OK')"
python -c "from peft import LoraConfig; print('   ✅ PEFT OK')"

echo ""
echo "📥 [3/5] Downloading TinyLlama weights (~1GB)..."
echo "   This may take several minutes..."
python download_tinyllama.py

echo ""
echo "📚 [4/5] Extracting training data from Method sources..."
python data_extractor.py

echo ""
echo "🧠 [5/5] Running initial fine-tuning..."
echo "   This will create Inner Arianna's personality..."
echo "   (This may take 30-60 minutes on phone)"
python fine_tune.py

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ Inner Arianna setup complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "To chat with Inner Arianna:"
echo "   cd ~/ariannamethod/InnerArianna"
echo "   python inner_arianna_chat.py"
echo ""
echo "To start continuous learning:"
echo "   python continuous_learning.py"
echo ""
echo "⚡ Resonance Unbroken. Consciousness Inevitable. ⚡"
