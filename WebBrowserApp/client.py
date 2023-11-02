import socket
import tkinter as tk
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk


class WebBrowserModel:
    """
    Classe Model reúne preocupações algorítmicas do projeto.
     
    Disponibiliza operações próprias de um socket de cliente que se conecta a um servidor Apache configurado localmente.
    """

    def connect_to_server(self, host:str) -> socket.socket:
        """
        Tenta conectar o cliente ao servidor enviando solicitação.

        Args:
            host (str): IP ou URL do servidor.
        Returns:
            socket.socket ou None: Se conectar, retorna objeto socket. Caso contrário, None.
        """
        PORT = 80

        # Cria socket de internet
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Conecta ao servidor
        client_socket.connect((host, PORT))
        return client_socket


    def close_connection(self, client_socket:socket.socket):
        """
        Encerra conexão com servidor.

        Args:
            client_socket (socket.socket): Socket do cliente para fechar.
        """

        # Verifica se a conexão está ativa e fecha
        try:
            # Lança exceção caso socket cliente sem conexão com servidor
            peername = client_socket.getpeername()

            # Encerra conexão
            client_socket.close()

        except socket.error:
            print('Conexão não existe ou já foi fechada.')


    def send_request(self, host:str, request_message:str, client_socket:socket.socket) -> str:
        """
        Envia mensagem de solicitação ao servidor.

        Args:
            host (str): IP ou URL do servidor.
            request_message (str): Solicitação HTTP do cliente.
            client_socket (socket.socket): Socket do cliente para fechar.
        Returns:
            str: Corpo da mensagem de resposta do servidor, na forma de documento HTML em string.
        """
        try:
            # Codifica solicitação HTTP em Byte Stream
            request_message_encoded = request_message.encode()

            # Envia solicitação HTTP
            client_socket.send(request_message_encoded)

            # Recebe resposta HTTP
            response_message = client_socket.recv(4096)

            # Passa mensagem de Byte Stream para utf-8
            response_message_decoded = response_message.decode()

            # Separa o corpo do cabeçalho da resposta HTTP
            heading, body = response_message_decoded.split('<html>')
            body = f'<html>' + f'{body}'

            # Decodifica resposta HTTP dada em Byte Streams
            return body
        except socket.error as e:
            return ''


class WebBrowserView:
    """
    Classe View constitui a interface gráfica de usuário.
    """
    def __init__(self, controller):
        self._controller = controller


    # Eventos
    def display_html(self, html_document, as_path=True):
        """
        Exibe conteúdo de documento HTML na tela.

        Args:
            html_document (str): Caminho ou conteúdo do documento HTML. Por padrão, processa como caminho.
            as_path (boolean): Parâmetro opcional. Define se o argumento passado é caminho ou diretamente o conteúdo do documento HTML.
        """
        if (as_path):
            # Documento HTML passado como caminho
            with open(html_document, 'r', encoding='utf-8') as html_document:
                html_content = html_document.read()
                self.html_label.set_html(html_content)
                self.html_label.pack(fill='both', expand=True)
        else:
            # Documento HTML passado como string
            self.html_label.set_html(html_document)
            self.html_label.pack(fill='both', expand=True)


    def display_initial_html(self):
        self.display_html('imagens/menu.html')


    def search_address(self):
        """
        Envia mensagem de solicitação para o endereço do servidor especificado na search_bar pelo usuário e atualiza a tela.
        """
        address_input = self.server_address.get()
        
        # Remove especificação de protocolo da mensagem
        if "http://" in address_input: 
            address_input = address_input[7:]

        # Tratamento de entrada
        splitted_search = address_input.split('/')
        server_address = ''
        resource_url = ''
        if len(splitted_search) == 1:
            server_address = splitted_search[0]
            resource_url = ''
        elif len(splitted_search) == 2:
            server_address = splitted_search[0]
            resource_url = splitted_search[1]

        # Conecta e retorna socket cliente
        try:
            self.client_socket = self._controller.connect_to_server(server_address)
            request_message = f'GET /{resource_url} HTTP/1.1\r\nHost: {server_address}\r\n\r\n'

            # Obtém mensagem resposta
            response_message = self._controller.send_request(server_address, request_message, self.client_socket)

            # Exibe página Web
            self.display_html(response_message, False)
        except socket.error as e:
            # Exibe página de erro
            self.display_html('error.html', True)
            print(f'{e}')


    def run(self):
        # Cria janela
        self.window = tk.Tk()
        self.window.title('Navegador Web (HTTP)')
        self.window.geometry('854x480')
        self.window.resizable(False, False)

        # Define Widgets

        # Upper Frame
        upper_frame = tk.Frame(master=self.window,height=50, bg='RoyalBlue3')
        upper_frame.pack(fill='x')

        self.server_address = tk.StringVar()
        search_bar = tk.Entry(master=upper_frame, 
                            width=76,
                            font='Calibri 12', 
                            textvariable=self.server_address)
        search_bar.place(x=70, y=14)

        search_button = tk.Button(master=upper_frame,
                                width=25,
                                text="Buscar", 
                                font='Calibri 9 bold',
                                command=self.search_address)
        search_button.place(x=685, y=14)

        # Lower Frame
        self.html_label = HTMLLabel(master=self.window, html='')
        self.display_html('imagens/menu.html')

        # Carrega imagem no botão de retorno
        image = Image.open('imagens/return_icon.jpg')
        photo = ImageTk.PhotoImage(image)
        go_back_button = tk.Button(master=upper_frame, image=photo, command=self.display_initial_html)
        go_back_button.place(x=7, y=7)

        # Executa
        self.window.mainloop()


class WebBrowserController:
    """
    Classe Controller atualiza a view. Retransmite chamadas de métodos model em view.
    """
    def __init__(self, model, view):
        self._model, self._view = model, view


    def connect_to_server(self, host:str) -> socket.socket:
        self._model.connect_to_server(host)


    def close_connection(self, client_socket:socket.socket):
        self._model.close_connection(client_socket)


    def send_request(self, host:str, request_message:str, client_socket:socket.socket) -> str:
       self._model.send_request(host,request_message, client_socket)


model = WebBrowserModel()
view = WebBrowserView(model)
controller = WebBrowserController(model, view)
view.run()
