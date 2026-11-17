import os
import socket
import qrcode
import io
import base64
from flask import Flask, render_template_string, request

app = Flask(__name__)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

LOCAL_IP = get_local_ip()
PORT = 5000
SERVER_URL = f"http://{LOCAL_IP}:{PORT}"

def gerar_qr_base64():
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(SERVER_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

CONTROLE_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Controle Smart HUD</title>
    <style>
        body {
            background-color: #d1d5db;
            color: #1f2937;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            height: 100vh;
            padding: 25px 0;
            box-sizing: border-box;
            user-select: none;
        }
        
        /* Linha Superior (Teclado Numérico, Home Centralizado e Power) */
        .top-container {
            width: 85%;
            max-width: 340px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: center;
        }
        .top-row {
            display: flex;
            justify-content: space-between;
            width: 100%;
            align-items: center;
        }
        .top-btn {
            width: 55px;
            height: 55px;
            background: #e5e7eb;
            border: none;
            border-radius: 50%;
            box-shadow: 4px 4px 10px rgba(163, 177, 198, 0.6), -4px -4px 10px rgba(255, 255, 255, 0.8);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: bold;
            color: #374151;
            transition: 0.1s;
        }
        .top-btn:active {
            box-shadow: inset 3px 3px 6px rgba(163, 177, 198, 0.6), inset -3px -3px 6px rgba(255, 255, 255, 0.8);
        }
        .btn-power-icon {
            color: #ef4444;
            font-size: 22px;
        }
        
        /* Botão Home Centralizado */
        .home-btn {
            width: 60px;
            height: 40px;
            background: #e5e7eb;
            border: none;
            border-radius: 20px;
            box-shadow: 4px 4px 10px rgba(163, 177, 198, 0.6), -4px -4px 10px rgba(255, 255, 255, 0.8);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #374151;
            transition: 0.1s;
        }
        .home-btn:active {
            box-shadow: inset 3px 3px 6px rgba(163, 177, 198, 0.6), inset -3px -3px 6px rgba(255, 255, 255, 0.8);
        }

        /* Botão de Voltar Extra no Controle (Abaixo do D-pad) */
        .extra-nav-row {
            display: flex;
            justify-content: center;
            width: 100%;
        }
        .back-btn {
            width: 50px;
            height: 50px;
            background: #e5e7eb;
            border: none;
            border-radius: 50%;
            box-shadow: 4px 4px 10px rgba(163, 177, 198, 0.6), -4px -4px 10px rgba(255, 255, 255, 0.8);
            cursor: pointer;
            font-size: 20px;
            color: #4b5563;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .back-btn:active {
            box-shadow: inset 3px 3px 6px rgba(163, 177, 198, 0.6), inset -3px -3px 6px rgba(255, 255, 255, 0.8);
        }

        .dpad-container {
            position: relative;
            width: 220px;
            height: 220px;
            background: #e5e7eb;
            border-radius: 50%;
            box-shadow: 8px 8px 20px rgba(163, 177, 198, 0.6), -8px -8px 20px rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .dpad-btn {
            position: absolute;
            background: transparent;
            border: none;
            color: #4b5563;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.1s;
        }
        .dpad-btn:active { color: #111827; transform: scale(0.92); }
        .btn-up { top: 10px; left: 50%; transform: translateX(-50%); width: 60px; height: 45px; }
        .btn-down { bottom: 10px; left: 50%; transform: translateX(-50%); width: 60px; height: 45px; }
        .btn-left { left: 10px; top: 50%; transform: translateY(-50%); width: 45px; height: 60px; }
        .btn-right { right: 10px; top: 50%; transform: translateY(-50%); width: 45px; height: 60px; }
        
        .btn-center {
            width: 90px;
            height: 90px;
            background: #d8dade;
            border: none;
            border-radius: 50%;
            color: #1f2937;
            font-weight: 800;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 4px 4px 8px rgba(163, 177, 198, 0.5), inset -4px -4px 8px rgba(255, 255, 255, 0.8);
            transition: 0.1s;
        }
        .btn-center:active { transform: scale(0.95); }

        .bottom-controls {
            display: flex;
            flex-direction: column;
            gap: 15px;
            width: 85%;
            max-width: 340px;
        }
        .volume-pill {
            display: flex;
            background: #e5e7eb;
            height: 50px;
            border-radius: 25px;
            box-shadow: 6px 6px 15px rgba(163, 177, 198, 0.6), -6px -6px 15px rgba(255, 255, 255, 0.8);
            overflow: hidden;
            position: relative;
        }
        .vol-half {
            flex: 1;
            background: transparent;
            border: none;
            font-size: 22px;
            font-weight: bold;
            color: #4b5563;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.1s;
        }
        .vol-half:active { background: rgba(0,0,0,0.05); }
        .vol-divider {
            position: absolute;
            left: 50%;
            top: 15%;
            height: 70%;
            width: 2px;
            background: #cbd5e1;
            transform: translateX(-50%);
        }

        #modal-num {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(209, 213, 219, 0.95);
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 99;
        }
        .num-grid {
            display: grid;
            grid-template-columns: repeat(3, 75px);
            gap: 15px;
        }
        .num-btn {
            height: 60px;
            background: #e5e7eb;
            border: none;
            border-radius: 15px;
            font-size: 22px;
            font-weight: bold;
            color: #374151;
            box-shadow: 4px 4px 10px rgba(163, 177, 198, 0.6), -4px -4px 10px rgba(255, 255, 255, 0.8);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .num-btn:active { box-shadow: inset 3px 3px 6px rgba(163, 177, 198, 0.6), inset -3px -3px 6px rgba(255, 255, 255, 0.8); }
    </style>
</head>
<body>

    <div class="top-container">
        <div class="top-row">
            <button class="top-btn" onclick="vibrate(); abrirTeclado()">1.2.3</button>
            <button class="home-btn" onclick="vibrate(); enviar('home')">⌂</button>
            <button class="top-btn" onclick="vibrate(); enviar('fechar_tudo')">
                <span class="btn-power-icon">⏻</span>
            </button>
        </div>
    </div>

    <div class="dpad-container">
        <button class="dpad-btn btn-up" onclick="vibrate(); enviar('up')">▲</button>
        <button class="dpad-btn btn-left" onclick="vibrate(); enviar('left')">◀</button>
        <button class="btn-center" onclick="vibrate(); enviar('play_pause')">OK</button>
        <button class="dpad-btn btn-right" onclick="vibrate(); enviar('right')">▶</button>
        <button class="dpad-btn btn-down" onclick="vibrate(); enviar('down')">▼</button>
    </div>

    <div class="extra-nav-row">
        <button class="back-btn" onclick="vibrate(); enviar('voltar_serie')">↩</button>
    </div>

    <div class="bottom-controls">
        <div class="volume-pill">
            <button class="vol-half" onclick="vibrate(); enviar('vol_down')">-</button>
            <div class="vol-divider"></div>
            <button class="vol-half" onclick="vype(); vibrate(); enviar('vol_up')">+</button>
        </div>
    </div>

    <div id="modal-num">
        <div class="num-grid">
            <button class="num-btn" onclick="vibrate(); digitar('1')">1</button>
            <button class="num-btn" onclick="vibrate(); digitar('2')">2</button>
            <button class="num-btn" onclick="vibrate(); digitar('3')">3</button>
            <button class="num-btn" onclick="vibrate(); digitar('4')">4</button>
            <button class="num-btn" onclick="vibrate(); digitar('5')">5</button>
            <button class="num-btn" onclick="vibrate(); digitar('6')">6</button>
            <button class="num-btn" onclick="vibrate(); digitar('7')">7</button>
            <button class="num-btn" onclick="vibrate(); digitar('8')">8</button>
            <button class="num-btn" onclick="vibrate(); digitar('9')">9</button>
            <button class="num-btn" onclick="vibrate(); fecharTeclado()">↩</button>
            <button class="num-btn" onclick="vibrate(); digitar('0')">0</button>
            <button class="num-btn" onclick="vibrate(); digitar('enter'); fecharTeclado()" style="color:#2563eb;">OK</button>
        </div>
    </div>

    <script>
        function vibrate() {
            if ("vibrate" in navigator) { navigator.vibrate(40); }
        }
        function abrirTeclado() { document.getElementById('modal-num').style.display = 'flex'; }
        function fecharTeclado() { document.getElementById('modal-num').style.display = 'none'; }

        function enviar(acao) {
            fetch('/cmd/' + acao, { method: 'POST' }).then(res => {
                if (acao === 'fechar_tudo') {
                    document.body.innerHTML = "<h2 style='text-align:center; margin-top:40vh; color:#ef4444;'>Sistema Desligado.</h2>";
                }
            });
        }

        function digitar(num) {
            fetch('/digitar/' + num, { method: 'POST' });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(CONTROLE_HTML)

@app.route('/cmd/<acao>', methods=['POST'])
def cmd(acao):
    import pyautogui
    pyautogui.FAILSAFE = False

    if acao == 'up': pyautogui.press('up')
    elif acao == 'down': pyautogui.press('down')
    elif acao == 'left': pyautogui.press('left')
    elif acao == 'right': pyautogui.press('right')
    elif acao == 'play_pause': pyautogui.press('space')
    elif acao == 'vol_up': pyautogui.press('volumeup')
    elif acao == 'vol_down': pyautogui.press('volumedown')
    elif acao == 'home':
        # Simula atalho para ir à home (tecla Windows ou ESC dependendo do app)
        pyautogui.press('esc')
    elif acao == 'voltar_serie':
        # Simula o comando de fechar player/voltar no streaming (Backspace ou Esc)
        pyautogui.press('backspace')
    elif acao == 'fechar_tudo':
        os.system("taskkill /f /im chrome.exe >nul 2>&1")
        os._exit(0)
    return '', 204

@app.route('/digitar/<num>', methods=['POST'])
def digitar(num):
    import pyautogui
    pyautogui.FAILSAFE = False
    if num == 'enter':
        pyautogui.press('enter')
    else:
        pyautogui.press(num)
    return '', 204

if __name__ == '__main__':
    qr_b64 = gerar_qr_base64()
    with open("qrcode_cache.txt", "w") as f:
        f.write(qr_b64)
    app.run(host='0.0.0.0', port=PORT, debug=False)
