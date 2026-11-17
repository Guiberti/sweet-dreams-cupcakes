# python run.py -> abre em localhost:5000 e tambem na rede local (pra testar no celular)
import socket

from app import create_app

app = create_app()

if __name__ == "__main__":
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except OSError:
        ip = "127.0.0.1"
    print("\n🧁 Sweet Dreams Cupcakes rodando!")
    print("   No computador:  http://localhost:5000")
    print(f"   No celular:     http://{ip}:5000  (mesma rede Wi-Fi)")
    print(f"   Laudo de teste: http://{ip}:5000/teste\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
