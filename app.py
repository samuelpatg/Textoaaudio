import streamlit as st
import streamlit.components.v1 as components
import os
import time
import glob
import math
import struct
import wave
from PIL import Image
import base64
 
st.title("Conversión de Texto a Código Morse (Audio)")
 
# ---------------------------------------------------------------------------
# Tabla de código Morse
# ---------------------------------------------------------------------------
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    'Ñ': '--.--', 'Á': '.--.-', 'É': '..-..', 'Í': '..', 'Ó': '---.', 'Ú': '..--',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',
    '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
    ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
    '"': '.-..-.', '@': '.--.-.', '¡': '--...-', '¿': '..-.-',
}
 
 
def text_to_morse(text):
    """Convierte texto en su representación de código Morse (solo texto)."""
    text = text.upper()
    words = text.split(' ')
    morse_words = []
    for word in words:
        codes = [MORSE_CODE[ch] for ch in word if ch in MORSE_CODE]
        morse_words.append(' '.join(codes))
    return ' / '.join(w for w in morse_words if w)
 
 
def morse_to_wav(text, filename, freq=700, wpm=18, sample_rate=44100):
    """Genera un archivo .wav con los pitidos (beeps) del código Morse
    correspondientes al texto dado, y devuelve la representación en texto."""
    text = text.upper()
    unit = 1.2 / wpm  # duración de un "punto", estándar PARIS
 
    frames = bytearray()
 
    def add_tone(duration):
        n_samples = int(sample_rate * duration)
        for i in range(n_samples):
            value = int(32767 * 0.5 * math.sin(2 * math.pi * freq * i / sample_rate))
            frames.extend(struct.pack('<h', value))
 
    def add_silence(duration):
        n_samples = int(sample_rate * duration)
        frames.extend(b'\x00\x00' * n_samples)
 
    morse_words = []
    words = text.split(' ')
    for wi, word in enumerate(words):
        letter_codes = [MORSE_CODE[ch] for ch in word if ch in MORSE_CODE]
        for code in letter_codes:
            for si, symbol in enumerate(code):
                add_tone(unit if symbol == '.' else unit * 3)
                if si < len(code) - 1:
                    add_silence(unit)  # espacio entre símbolos de una letra
            add_silence(unit * 3)  # espacio entre letras
        morse_words.append(' '.join(letter_codes))
        if wi < len(words) - 1 and letter_codes:
            add_silence(unit * 7 - unit * 3)  # completar espacio entre palabras
 
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(frames))
 
    return ' / '.join(w for w in morse_words if w)
image = Image.open('gato_raton.png')
st.image(image, width=350)
with st.sidebar:
    st.subheader("Esrcibe y/o selecciona texto para ser escuchado.")
try:
    os.mkdir("temp")
except:
    pass
st.subheader("Una pequeña Fábula.")
st.write('¡Ay! -dijo el ratón-. El mundo se hace cada día más pequeño. Al principio era tan grande que le tenía miedo. '
         ' Corría y corría y por cierto que me alegraba ver esos muros, a diestra y siniestra, en la distancia. '
         ' Pero esas paredes se estrechan tan rápido que me encuentro en el último cuarto y ahí en el rincón está '
         ' la trampa sobre la cual debo pasar. Todo lo que debes hacer es cambiar de rumbo dijo el gato...y se lo comió. '
         '  '
         ' Franz Kafka.'
 
        )
 
st.markdown(f"Quieres escucharlo en código Morse?, copia el texto")
text = st.text_area("Ingrese El texto a convertir.")
 
# display_output_text = st.checkbox("Verifica el texto")
if st.button("convertir a Código Morse (Audio)"):
    if not text.strip():
        st.warning("Por favor ingresa algún texto.")
    else:
        safe_name = "".join(c if c.isalnum() else "_" for c in text[:20]).strip("_") or "audio"
        filename = f"temp/{safe_name}.wav"
        morse_text = morse_to_wav(text, filename)
 
        audio_file = open(filename, "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tu audio en Código Morse:")
        st.audio(audio_bytes, format="audio/wav", start_time=0)
 
        st.markdown("**Código Morse:**")
        st.code(morse_text if morse_text else "(no se encontraron caracteres convertibles)")
 
        with open(filename, "rb") as f:
            data = f.read()
 
        def get_binary_file_downloader_html(bin_file, file_label='File'):
            bin_str = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
            return href
 
        st.markdown(get_binary_file_downloader_html(filename, file_label="Audio File (.wav)"), unsafe_allow_html=True)
 
 
def remove_files(n):
    audio_files = glob.glob("temp/*mp3") + glob.glob("temp/*wav")
    if len(audio_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in audio_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)
 
 
remove_files(7)
 
 
# ---------------------------------------------------------------------------
# JUEGO: El ratón escapa del laberinto en busca del queso
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("🐭 Juego: El ratón escapa del laberinto")
st.write(
    "Ayuda al ratón de la fábula a escapar del laberinto antes de que las paredes "
    "se cierren sobre él. Usa las flechas del teclado (⬆️⬇️⬅️➡️) para moverte. "
    "¡Haz clic dentro del juego primero para activar el control con teclado!"
)
 
maze_game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; font-family: 'Trebuchet MS', sans-serif; background: transparent; }
  #wrap {
    display: flex; flex-direction: column; align-items: center;
    outline: none;
  }
  #status {
    margin-bottom: 8px; font-size: 18px; font-weight: bold; color: #333;
    min-height: 26px;
  }
  canvas {
    background: #fdf6e3;
    border: 4px solid #6b4226;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
  }
  #controls { margin-top: 10px; }
  button {
    background: #6b4226; color: white; border: none; padding: 8px 16px;
    border-radius: 6px; cursor: pointer; font-size: 14px; margin: 0 4px;
  }
  button:hover { background: #8a5a34; }
  #win-msg {
    display: none; margin-top: 10px; font-size: 20px; font-weight: bold;
    color: #b8860b; text-align: center;
  }
</style>
</head>
<body>
<div id="wrap" tabindex="0">
  <div id="status">Movimientos: 0 &nbsp;|&nbsp; Usa las flechas del teclado ⬆️⬇️⬅️➡️</div>
  <canvas id="mazeCanvas"></canvas>
  <div id="controls">
    <button onclick="newGame()">🔄 Nuevo laberinto</button>
  </div>
  <div id="win-msg">🧀 ¡El ratón encontró el queso y escapó! ¡Ganaste! 🐭🎉</div>
</div>
 
<script>
  const wrap = document.getElementById('wrap');
  const canvas = document.getElementById('mazeCanvas');
  const ctx = canvas.getContext('2d');
  const statusEl = document.getElementById('status');
  const winMsg = document.getElementById('win-msg');
 
  const ROOM_COLS = 8;
  const ROOM_ROWS = 6;
  const CELL = 34; // pixel size of each grid cell (walls are thin cells too)
 
  const GRID_W = ROOM_COLS * 2 + 1;
  const GRID_H = ROOM_ROWS * 2 + 1;
 
  canvas.width = GRID_W * CELL;
  canvas.height = GRID_H * CELL;
 
  let grid, player, moves, won;
 
  function generateMaze() {
    // 1 = wall, 0 = path
    grid = [];
    for (let y = 0; y < GRID_H; y++) {
      grid.push(new Array(GRID_W).fill(1));
    }
 
    const visited = [];
    for (let ry = 0; ry < ROOM_ROWS; ry++) {
      visited.push(new Array(ROOM_COLS).fill(false));
    }
 
    function carve(rx, ry) {
      visited[ry][rx] = true;
      grid[ry * 2 + 1][rx * 2 + 1] = 0;
 
      const dirs = [[1,0],[-1,0],[0,1],[0,-1]];
      // shuffle
      for (let i = dirs.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [dirs[i], dirs[j]] = [dirs[j], dirs[i]];
      }
 
      for (const [dx, dy] of dirs) {
        const nx = rx + dx, ny = ry + dy;
        if (nx >= 0 && nx < ROOM_COLS && ny >= 0 && ny < ROOM_ROWS && !visited[ny][nx]) {
          grid[ry * 2 + 1 + dy][rx * 2 + 1 + dx] = 0;
          carve(nx, ny);
        }
      }
    }
 
    carve(0, 0);
  }
 
  function newGame() {
    generateMaze();
    player = { rx: 0, ry: 0 };
    moves = 0;
    won = false;
    winMsg.style.display = 'none';
    updateStatus();
    draw();
    wrap.focus();
  }
 
  function updateStatus() {
    statusEl.textContent = "Movimientos: " + moves + "  |  Usa las flechas del teclado ⬆️⬇️⬅️➡️";
  }
 
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
 
    // walls
    ctx.fillStyle = '#6b4226';
    for (let y = 0; y < GRID_H; y++) {
      for (let x = 0; x < GRID_W; x++) {
        if (grid[y][x] === 1) {
          ctx.fillRect(x * CELL, y * CELL, CELL, CELL);
        }
      }
    }
 
    // cheese at the end room
    const endPx = (ROOM_COLS - 1) * 2 + 1;
    const endPy = (ROOM_ROWS - 1) * 2 + 1;
    ctx.font = (CELL * 0.8) + "px serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("🧀", endPx * CELL + CELL / 2, endPy * CELL + CELL / 2);
 
    // mouse
    const px = player.rx * 2 + 1;
    const py = player.ry * 2 + 1;
    ctx.fillText("🐭", px * CELL + CELL / 2, py * CELL + CELL / 2);
  }
 
  function tryMove(dx, dy) {
    if (won) return;
    const nrx = player.rx + dx;
    const nry = player.ry + dy;
    if (nrx < 0 || nrx >= ROOM_COLS || nry < 0 || nry >= ROOM_ROWS) return;
 
    const wallX = player.rx * 2 + 1 + dx;
    const wallY = player.ry * 2 + 1 + dy;
    if (grid[wallY][wallX] === 1) return; // hay pared, no se puede mover
 
    player.rx = nrx;
    player.ry = nry;
    moves += 1;
    updateStatus();
    draw();
 
    if (player.rx === ROOM_COLS - 1 && player.ry === ROOM_ROWS - 1) {
      won = true;
      winMsg.style.display = 'block';
    }
  }
 
  wrap.addEventListener('keydown', function(e) {
    const key = e.key;
    if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(key)) {
      e.preventDefault();
    }
    if (key === "ArrowUp") tryMove(0, -1);
    else if (key === "ArrowDown") tryMove(0, 1);
    else if (key === "ArrowLeft") tryMove(-1, 0);
    else if (key === "ArrowRight") tryMove(1, 0);
  });
 
  wrap.addEventListener('click', function() { wrap.focus(); });
 
  newGame();
  wrap.focus();
</script>
</body>
</html>
"""
 
components.html(maze_game_html, height=560, scrolling=False)
 
