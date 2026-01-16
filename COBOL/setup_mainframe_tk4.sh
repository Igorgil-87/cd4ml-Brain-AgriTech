cat > setup_mainframe_tk4.sh << 'EOF'
#!/bin/bash
set -e

echo "==============================="
echo "  TK4- MAINFRAME INSTALLER"
echo "  macOS  (ARM/Intel)"
echo "  Hercules + MVS 3.8j + TSO"
echo "==============================="
echo

# -------------------------
# 1) Limpa porta 3270
# -------------------------
echo "🔍 Verificando porta 3270..."
PID=$(lsof -t -i :3270 || true)

if [ ! -z "$PID" ]; then
  echo "⚠️ Processo ocupando a porta 3270: PID=$PID"
  echo "🔨 Matando processo..."
  kill -9 $PID || true
else
  echo "✅ Porta 3270 está livre."
fi

echo

# -------------------------
# 2) Baixar imagem TK4-Hercules
# -------------------------
echo "🐳 Baixando imagem TK4-Hercules..."
docker pull ghcr.io/skunklabz/tk4-hercules:latest
echo

# -------------------------
# 3) Criar container temporário e copiar /tk4-
# -------------------------
echo "🗂️  Extraindo TK4- completo do container..."

docker rm -f tk4src 2>/dev/null || true
rm -rf "$HOME/tk4-mainframe"

docker create --name tk4src ghcr.io/skunklabz/tk4-hercules:latest
docker cp tk4src:/tk4- "$HOME/tk4-mainframe"
docker rm tk4src

echo "✅ TK4- extraído com sucesso."
echo

# -------------------------
# 4) Criar script de boot start_mvs.sh
# -------------------------
echo "⚙️ Criando script start_mvs.sh..."

cat > "$HOME/tk4-mainframe/start_mvs.sh" << 'EOFS'
#!/bin/bash
cd "$(dirname "$0")"

HERC=$(command -v hercules)

if [ -z "$HERC" ]; then
  echo "❌ Hercules não encontrado. Instale com:"
  echo "   brew install hercules"
  exit 1
fi

CONF="conf/tk4-.cnf"

echo "===================================="
echo " Iniciando Hercules + TK4-"
echo " Configuração: $CONF"
echo "===================================="

"$HERC" -f "$CONF"
EOFS

chmod +x "$HOME/tk4-mainframe/start_mvs.sh"

echo "✅ Script start_mvs.sh criado."
echo

# -------------------------
# 5) Mostrar próximos passos
# -------------------------
echo "======================================="
echo "✔️ INSTALAÇÃO DO MAINFRAME COMPLETA!"
echo "======================================="
echo
echo "📌 Para iniciar o mainframe, execute:"
echo
echo "    cd ~/tk4-mainframe"
echo "    ./start_mvs.sh"
echo
echo "📌 Quando aparecer o prompt:"
echo "    herc =====>"
echo "Digite:"
echo
echo "    ipl 148"
echo
echo "📌 Para conectar via terminal 3270:"
echo
echo "    c3270 127.0.0.1:3270"
echo
echo "📌 Login TSO:"
echo "    USERID: HERC01"
echo "    PASSWORD: CUL8TR"
echo
echo "Bom uso do seu mainframe! 🚀"
echo
EOF

chmod +x setup_mainframe_tk4.sh

echo "🎉 Script criado com sucesso!"
echo
echo "Execute agora:"
echo "   ./setup_mainframe_tk4.sh"
echo