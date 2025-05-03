import threading
import tkinter as tk
import socket


HOST = ''
SEND_PORT = 50007
RECV_PORT = 50008

CALIBRATE_STATUS_PIN = 24
CAPTURE_STATUS_PIN = 25
SPECTRUM_STATUS_PIN = 26
TRANSMIT_STATUS_PIN = 23
DOWNLINK_STATUS_PIN = 11


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.frm = tk.Frame(master)
        self.frm.grid()

        # Top
        tk.Label(
            self.frm,
            text="Astronomer Test Panel",
        ).grid(column=0, row=0)
        tk.Button(
            self.frm,
            text="Quit",
            command=master.destroy,
        ).grid(column=2, row=0)

        # Calibrate

        calibrate_canvas = tk.Canvas(self.frm)
        calibrate_canvas.grid(column=1, row=2)
        calibrate_canvas.configure(bg='black', width=50, height=50)
        self.calibrate_canvas = calibrate_canvas
        def calibrate_button_was_pressed():
            send_socket_message(b'calibrate')

        tk.Button(
            self.frm,
            text="Calibrate",
            command=calibrate_button_was_pressed
        ).grid(column=0, row=2)

        # Observe

        observe_canvas = tk.Canvas(self.frm)
        observe_canvas.grid(column=1, row=3)
        observe_canvas.configure(bg='black', width=50, height=50)
        self.observe_canvas = observe_canvas
        def observe_button_was_pressed():
            send_socket_message(b'observe')

        tk.Button(
            self.frm,
            text="Observe",
            command=observe_button_was_pressed
        ).grid(column=0, row=3)

        # Transmit

        transmit_canvas = tk.Canvas(self.frm)
        tk.Label(
            self.frm,
            text="Transmit",
        ).grid(column=0, row=4)
        transmit_canvas.grid(column=1, row=4)
        transmit_canvas.configure(bg='black', width=50, height=50)
        self.transmit_canvas = transmit_canvas

        # Downlink

        downlink_canvas = tk.Canvas(self.frm)
        tk.Label(
            self.frm,
            text="Downlink",
        ).grid(column=0, row=5)
        downlink_canvas.grid(column=1, row=5)
        downlink_canvas.configure(bg='black', width=50, height=50)
        self.downlink_canvas = downlink_canvas

        # Spectrum

        spectrum_canvas = tk.Canvas(self.frm)
        tk.Label(
            self.frm,
            text="Spectrum",
        ).grid(column=0, row=6)
        spectrum_canvas.grid(column=1, row=6)
        spectrum_canvas.configure(bg='black', width=50, height=50)
        self.spectrum_canvas = spectrum_canvas

    def set_transmit(self, state):
        self.transmit_canvas.configure(bg='blue' if state else 'black')

    def set_capture(self, state):
        self.observe_canvas.configure(bg='red' if state else 'black')

    def set_calibrate(self, state):
        self.calibrate_canvas.configure(bg='green' if state else 'black')

    def set_spectrum(self, state):
        self.spectrum_canvas.configure(bg='yellow' if state else 'black')

    def set_downlink(self, state):
        self.downlink_canvas.configure(bg='yellow' if state else 'black')


def get_socket_server(app):
    print('Starting socket client...')
    def _server():
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.bind((HOST, RECV_PORT))
        while True:
            soc.listen(5)
            client, address = soc.accept()
            response = client.recv(255)
            try:
                pin, state = response.split(b'-')
            except ValueError:
                print(f'invalid response: {response}')
                continue

            pin, state = int(pin), int(state)
            if pin == CALIBRATE_STATUS_PIN:
                app.set_calibrate(state)
            elif pin == CAPTURE_STATUS_PIN:
                app.set_capture(state)
            elif pin == TRANSMIT_STATUS_PIN:
                app.set_transmit(state)
            elif pin == SPECTRUM_STATUS_PIN:
                app.set_spectrum(state)
            elif pin == DOWNLINK_STATUS_PIN:
                app.set_downlink(state)
            else:
                print(f'Unknown {pin=}: {state}')

    return _server


def send_socket_message(message: [bytes]):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, SEND_PORT))
        s.sendall(message)
        print(f'Message sent (len: {len(message)}).')


def main():
    root = tk.Tk()
    root.title('Telescope Test Panel')
    app = App(root)

    thread = threading.Thread(target=get_socket_server(app))
    thread.daemon = True
    thread.start()

    app.mainloop()
