"""
Phone-as-Webcam — Ventana de escritorio (GUI).

Arranca el servidor (server.py) y muestra la URL + un codigo QR para
escanear desde el celular, mas el estado de la conexion.

Uso:  python app.py
"""

import io
import tkinter as tk
from tkinter import ttk

import qrcode
from PIL import ImageTk

import server


def main():
    root = tk.Tk()
    root.title("Camara desde el celular")
    root.geometry("420x560")
    root.resizable(False, False)

    ttk.Label(root, text="Camara desde el celular",
              font=("Segoe UI", 16, "bold")).pack(pady=(16, 4))
    ttk.Label(root, text="Escanea el QR con el celular\n(misma red WiFi que el PC)",
              justify="center").pack(pady=(0, 8))

    qr_label = ttk.Label(root)
    qr_label.pack(pady=4)

    url_var = tk.StringVar(value="Iniciando...")
    url_entry = ttk.Entry(root, textvariable=url_var, justify="center",
                          font=("Consolas", 11), state="readonly", width=34)
    url_entry.pack(pady=6)

    status_var = tk.StringVar(value="Iniciando servidor...")
    ttk.Label(root, textvariable=status_var, foreground="#0a6",
              wraplength=380, justify="center").pack(pady=8)

    steps = (
        "1) Conecta el PC y el celular a la MISMA red WiFi.\n"
        "2) Escanea el QR (o escribe la URL en el navegador).\n"
        "3) Acepta el aviso de certificado del navegador.\n"
        "4) Pulsa 'Iniciar' y permite la camara.\n"
        "5) En Zoom/Teams/etc elige la camara 'OBS Virtual Camera'."
    )
    ttk.Label(root, text=steps, justify="left", foreground="#555",
              wraplength=390).pack(pady=10, padx=12, anchor="w")

    # El callback de estado llega desde otros hilos -> usar after() para
    # tocar la GUI en el hilo principal de Tk.
    def on_status(text):
        root.after(0, status_var.set, text)

    url = server.start(status_cb=on_status)
    url_var.set(url)

    qr_img = qrcode.make(url).resize((220, 220))
    tk_img = ImageTk.PhotoImage(qr_img)
    qr_label.configure(image=tk_img)
    qr_label.image = tk_img  # evita garbage-collection

    root.mainloop()


if __name__ == "__main__":
    main()
