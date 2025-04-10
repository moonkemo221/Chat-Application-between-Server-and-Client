import socket
import threading
from tkinter import *
from tkinter import messagebox, ttk

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application between Server and Client")
        self.root.geometry("450x650")
        self.root.configure(bg="#f0f0f0")
        
        # Network Variables
        self.socket = None
        self.is_server = False
        self.running = False
        
        # Set up UI
        self.setup_ui()
        
    def setup_ui(self):
        # Notebook (Tabs)
        self.tabs = ttk.Notebook(self.root)
        self.server_tab = Frame(self.tabs)
        self.client_tab = Frame(self.tabs)
        self.tabs.add(self.server_tab, text="Server Mode")
        self.tabs.add(self.client_tab, text="Client Mode")
        self.tabs.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Server Tab
        Label(self.server_tab, text="Server Port:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)
        self.server_port = Entry(self.server_tab, font=("Arial", 12), width=20)
        self.server_port.insert(0, "12345")
        self.server_port.pack(pady=5)
        
        self.start_server_btn = Button(self.server_tab, text="Start Server", command=self.start_server, font=("Arial", 12), bg="#4CAF50", fg="white", relief="raised", width=15)
        self.start_server_btn.pack(pady=5)
        
        self.stop_server_btn = Button(self.server_tab, text="Stop Server", command=self.stop_server, state=DISABLED, font=("Arial", 12), bg="#f44336", fg="white", relief="raised", width=15)
        self.stop_server_btn.pack(pady=5)
        
        # Client Tab
        Label(self.client_tab, text="Server IP:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)
        self.client_ip = Entry(self.client_tab, font=("Arial", 12), width=20)
        self.client_ip.insert(0, "127.0.0.1")
        self.client_ip.pack(pady=5)
        
        Label(self.client_tab, text="Server Port:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)
        self.client_port = Entry(self.client_tab, font=("Arial", 12), width=20)
        self.client_port.insert(0, "12345")
        self.client_port.pack(pady=5)
        
        self.connect_btn = Button(self.client_tab, text="Connect", command=self.connect_to_server, font=("Arial", 12), bg="#4CAF50", fg="white", relief="raised", width=15)
        self.connect_btn.pack(pady=5)
        
        self.disconnect_btn = Button(self.client_tab, text="Disconnect", command=self.disconnect, state=DISABLED, font=("Arial", 12), bg="#f44336", fg="white", relief="raised", width=15)
        self.disconnect_btn.pack(pady=5)
        
        # Chat Area
        self.chat_frame = Frame(self.root, bg="#f0f0f0")
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        Label(self.chat_frame, text="Chat:", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)
        self.chat_text = Text(self.chat_frame, height=10, width=50, state=DISABLED, font=("Arial", 12), bg="#e0e0e0", fg="black", relief="solid")
        self.chat_text.pack(pady=5)
        
        # Send Messages
        self.msg_frame = Frame(self.root, bg="#f0f0f0")
        self.msg_frame.pack(fill="x", pady=10)
        
        self.message_entry = Entry(self.msg_frame, font=("Arial", 12), width=40)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        self.send_btn = Button(self.msg_frame, text="Send", command=self.send_message, state=DISABLED, font=("Arial", 12), bg="#4CAF50", fg="white", relief="raised", width=10)
        self.send_btn.pack(side="right", padx=5)
        
        # Bind Enter Key
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        # Connection Status
        self.status = Label(self.root, text="Status: Not Connected", fg="red", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.status.pack(pady=5)
    
    def log(self, message):
        self.chat_text.config(state=NORMAL)
        self.chat_text.insert(END, message + "\n")
        self.chat_text.config(state=DISABLED)
        self.chat_text.see(END)
    
    def start_server(self):
        port = int(self.server_port.get())
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('0.0.0.0', port))
            self.socket.listen(5)
            
            self.is_server = True
            self.running = True
            self.start_server_btn.config(state=DISABLED)
            self.stop_server_btn.config(state=NORMAL)
            self.status.config(text=f"Status: Server Active (Port {port})", fg="green")
            self.log(f"Server running on port {port}")
            
            # Start accepting connections
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Unable to start the server:\n{str(e)}")
    
    def stop_server(self):
        self.running = False
        if self.socket:
            self.socket.close()
        self.start_server_btn.config(state=NORMAL)
        self.stop_server_btn.config(state=DISABLED)
        self.status.config(text="Status: Not Connected", fg="red")
        self.log("Server stopped")
    
    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.socket.accept()
                self.log(f"New connection from {addr}")
                
                # Receive messages from the client
                threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                ).start()
                
            except:
                if self.running:
                    self.log("Error accepting connection")
                break
    
    def handle_client(self, conn, addr):
        try:
            while self.running:
                data = conn.recv(1024)
                if not data:
                    break
                    
                msg = data.decode('utf-8')
                self.log(f"Client: {msg}")
                
                # Send acknowledgment
                conn.sendall(f"Received: {msg}".encode('utf-8'))
                
        except Exception as e:
            self.log(f"Error with client: {str(e)}")
        finally:
            conn.close()
            self.log(f"Client connection closed")
    
    def connect_to_server(self):
        ip = self.client_ip.get()
        port = int(self.client_port.get())
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            
            self.is_server = False
            self.running = True
            self.connect_btn.config(state=DISABLED)
            self.disconnect_btn.config(state=NORMAL)
            self.send_btn.config(state=NORMAL)
            self.status.config(text=f"Status: Connected to server {ip}:{port}", fg="green")
            self.log(f"Connected to server {ip}:{port}")
            
            # Start receiving messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Unable to connect to the server:\n{str(e)}")
    
    def disconnect(self):
        self.running = False
        if self.socket:
            self.socket.close()
        self.connect_btn.config(state=NORMAL)
        self.disconnect_btn.config(state=DISABLED)
        self.send_btn.config(state=DISABLED)
        self.status.config(text="Status: Not Connected", fg="red")
        self.log("Disconnected")
    
    def receive_messages(self):
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                    
                msg = data.decode('utf-8')
                self.log(f"Server: {msg}")
                
            except:
                break
                
        self.disconnect()
    
    def send_message(self):
        msg = self.message_entry.get()
        if msg and self.running:
            try:
                # Send the message to the other party
                if self.is_server:
                    self.socket.send(msg.encode('utf-8'))  # Server sends to client
                    self.log(f"You (Server): {msg}")
                else:
                    self.socket.send(msg.encode('utf-8'))  # Client sends to server
                    self.log(f"You (Client): {msg}")
                self.message_entry.delete(0, END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message:\n{str(e)}")
                self.disconnect()

if __name__ == "__main__":
    root = Tk()
    app = ChatApp(root)
    root.mainloop()
