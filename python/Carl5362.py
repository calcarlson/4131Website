import socket
import os
import mimetypes
import stat

from urllib.parse import unquote
from threading import Thread
from argparse import ArgumentParser

# buffer size variable
BUFSIZE = 4096


# Need to implement: **ways to navigate filetypes by folder structure, 
# **dictionary of codes for error parsing, **ways to parse the filetype 
# into the html request header. **Get handler, **Post handler, **Head handler,
# **socket setup and **some way to handle errors by responding to server requests. done
class Carl5362Server:
# list of status codes for use in parsing codes for http requests
    statcodes = {
        200: 'Ok',
        301: 'MOVED PERMANENTLY',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Not Implemented',
        406: 'Not Acceptable',
    }

# needed because of folder organization, used to define file paths within the project directory
    navigationpaths = {
        '.html': os.path.join('..', 'html'),
        '.css': os.path.join('..','css'),
        '.js': os.path.join('..', 'js'),
        '.jpg': os.path.join('..','media'),
        '.png': os.path.join('..', 'media'),
        '.mp3': os.path.join('..', 'media'),
    }
# headers for GET requests
    acceptheaders = {
        '.html':['text/html','*/*'],
        '.css':['text/html','*/*'],
        '.js':['text/html','*/*'],
        '.png':['image/*','*/*'],
        '.mp3':['audio/*','*/*'],
        '.jpg':['image/*','*/*'],
    }

# initialization
    def __init__(self, host, port):
        print('listening on port {}'.format(port))
        self.host = host
        self.port = port
        self.sock = None

        self.setup_socket()

        self.accept()

        self.sock.shutdown()
        self.sock.close()

# setting up of sockets
    def setup_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(128)
        print("sockets are working - remove this printout")

# calls thread that handles socket requests 
    def accept(self):
        while True:
          client, address = self.sock.accept()
          print("Address", address)
          th = Thread(target=self.handler, args=(client,))
          th.start()
    
    def handler(self,client_sock):
        data = client_sock.recv(BUFSIZE)
        data = data.decode('utf-8')
        print(data)
        request = Carl5362Request(data)
        # calls the method needed else send sends 405
        try:
            methodHandler = getattr(self, '%shandler' % request.method)
            response = methodHandler(request)
        except AttributeError:
           response = self.ERRORhandler(405)

        client_sock.send(response)
        client_sock.shutdown(1)

        client_sock.close()
        print('connection closed.\n\n')

# handle get requests
    def GEThandler(self, request, head=False):
    
        filename = request.uri.strip('/')
        filename = filename.split('/')[-1]
        extension = os.path.splitext(filename)[1]

        if extension in self.navigationpaths.keys():
            path = os.path.join(self.navigationpaths[extension],filename)
        else:
        #server does not support filetypes other than those defined in navigation paths
            print ('no go, thats a paddlin')
            path = 'None'

        if os.path.exists(path):    
            if not any(item in self.acceptheaders[extension] for item in request.accept):
                return self.ERRORhandler(406)
            
            if not permissionsCheck(path):
                return self.ERRORhandler(403)
            
            pageError = self.pageError(200)
            
            if not head:
                acceptedType = mimetypes.guess_type(filename)[0] or 'html/text'
                assignHeader = self.assignHeader(acceptedType)
                pass 

                if extension not in ('.jpg', '.png', '.mp3'):
                    with open(path) as f:
                        bodyResponse = f.read().replace("\xef\xbb\xbf", '')
                    bodyResponse = bytes(bodyResponse, 'utf-8')
                else:
                     with open(path, 'rb') as f:
                        bodyResponse = f.read()

            else:
                assignHeader = ''
                bodyResponse = bytes('','utf-8')
        
        
    #handle special case of mytube redirection to youtube
        else:
            if filename == 'mytube':
                print('redirect to youtube')
                pageError = bytes(self.pageError(301), 'utf-8')
                bodyResponse = bytes('Location:  https://www.youtube.com/', 'utf-8')
                return pageError + bodyResponse
            else:
                return self.ERRORhandler(404)
    

        byteResponse = \
            bytes(pageError, 'utf-8') + \
            bytes(assignHeader, 'utf-8') + \
            bytes('\r\n', 'utf-8') + \
            bodyResponse

        return byteResponse


    # handle head requests 
    def HEADhandler(self, request):
        
        return self.GEThandler(request, head=True)

    # handle post requests 
    def POSThandler(self, request):
        print('Post handled successfully - remove this printout')
        # TODO
        pageError =self.pageError(200)
        assignHeader =self.assignHeader('text/html')
        bodyResponse = request.html_data


        byteResponse = \
            bytes(pageError, 'utf-8') + \
            bytes(assignHeader, 'utf-8') + \
            bytes('\r\n', 'utf-8') + \
            bytes(bodyResponse,'utf-8')

        return byteResponse
    # handle page errors 
    def ERRORhandler(self, error):
        print('entered ERROR handler ')
        pageError =self.pageError(error)
        assignHeader=self.assignHeader('text/html')
        # TODO
        with open(os.path.join(self.navigationpaths['.html'], f'{error}.html')) as f:
            bodyResponse = f.read().replace("\xef\xbb\xbf",'')
        bodyResponse = bytes(bodyResponse, 'utf-8')
        
        byteResponse = \
                   bytes(pageError, 'utf-8') + \
                   bytes(assignHeader, 'utf-8') + \
                   bytes('\r\n', 'utf-8') + \
                   bodyResponse

        return byteResponse

# parse page error for ERRORhandler
    def pageError(self,statcodes):
        result = self.statcodes[statcodes]
        return "HTTP/1.1 %s %s\r \n" % (statcodes, result)
        
#create headers for functions to return content type labels
    def assignHeader(self,content):
        headerDefault = {
        'Server': 'Carl5362Server',
            'Type': content,
        }
        headers = ""
        for h in headerDefault:
            headers += "%s: %s\r\n" % (h, headerDefault[h])
        return headers


        #        needed to check permissions on resources. true if read permissions given
def permissionsCheck(resource):
    stmode = os.stat(resource).st_mode
    return (getattr(stat, 'S_IROTH')& stmode) > 0

#where requests and read and sent to their respective handler functions within the server class.
class Carl5362Request:
    def __init__(self,data):
        self.method=None
        self.uri=None
        self.html_data =None
        self.accept = []
        self.http_version='1.1'
        
        self.parse(data)

    def parse(self,data):
        lines =data.split('\r\n')
        request_line = lines[0]

        lineAccept = None
        for line in lines:
            if line.split(' ')[0] ==  'Accept:':
                lineAccept=line.split(' ')[1]
        
        self.lineParser(request_line)

        if lineAccept:
            self.acceptParser(lineAccept)

        if self.method == "POST":
            data_line =lines[-1]
            self.parsePost(data_line)

        
    def lineParser(self, request_line):
        words = request_line.split(' ')
        self.method = words[0]

        if len(words) >1:
            self.uri =words[1]

        if len(words) >2:
            self.http_version = words[2]

    def acceptParser(self,lineAccept):
        categories = [s.split(',') for s in lineAccept.split(';')]

        for category in categories:
            for item in category:
                if '/' in item:
                    self.accept.append(item)

#parses post data and creates a list with the data as strings to be used
# in html output. 
    def parsePost(self,data_line):
        formData = data_line.split('&')
        name = formData[0].split('=')[1]
        email = unquote(formData[1].split('=')[1])
        address = formData[2].split('=')[1]
        place = formData[3].split('=')[1]
        url = unquote(formData[4].split('=')[1])

#used for formatting post request information being 
# sent from the form page. Added formatting for navigation 
# bar to easily return to other pages
        self.html_data = \
            '''
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            table {
                content-align: center;
                border-collapse: separate;
                border-spacing: 10px;
                background-color: rgb(230, 230, 230);
                border-radius: 10px;
                margin-right: auto;
                margin-left: auto;
            }
            td, th {
              text-align: center;
              padding: 10px;
              font-family:Helvetica Neue, san-serif;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            
            a:link {
                color: grey;
                font-family: sans-serif;
            }

            a:visited {
                color: rgb(172, 105, 105);
                font-family: sans-serif;
            }

            a:hover {
                color: rgb(53, 53, 122);
                font-family: sans-serif;
                border-radius: 0px 10px 10px;
            }
            ol {
                list-style-type: none;
            }

            ul {
                text-align: center;
                list-style-type: none;
                line-height: 40%;
                margin: 0;
                padding: 0;
                width: 130px;
                background-color: rgb(230, 230, 230);
                border-radius: 0px 10px 10px 10px;
            }

            li a {
                display: block;
                text-decoration: none;
                padding: 8px 16px;
            }

            li a:hover {
                background-color: grey;
                color: white;
            }
            h2 {
                text-align: center;
                color: grey;
                font-weight: 100;
                font-size: 60pt;
                font-family: Helvetica Neue, sans-serif
            }
            </style>
            '''+f'''
            </head>
            <body>
            <nav>
        <ul>
            <li><a href="MyContacts.html">My Contacts</a></li>
            <li><a href="MyWidgets.html">My Widgets</a></li>
            <li><a href="MyForms.html">My Forms</a></li>
        </ul>
    </nav>
            <h2>Data Received:</h2>
            <table>
              <tr>
                <th>Value</th>
                <th>Data</th>
              </tr>
              <tr>
                <td>Name</td>
                <td>{name}</td>
              </tr>
              <tr>
                <td>Email</td>
                <td>{email}</td>
              </tr>
              <tr>
                <td>Address</td>
                <td>{address}</td>
              </tr>
              <tr>
                <td>Place</td>
                <td>{place}</td>
              </tr>
              <tr>
                <td>URL</td>
                <td>{url}</td>
              </tr>
            </table>
            </body>
            </html> '''
                    
def parse_args():
  parser = ArgumentParser()
  parser.add_argument('--host', type=str, default='localhost',
                      help='specify a host to operate on (default: localhost)')
  parser.add_argument('-p', '--port', type=int, default=9001,
                      help='specify a port to operate on (default: 9001)')
  args = parser.parse_args()
  return (args.host, args.port)

if __name__ == '__main__':
  (host, port) = parse_args()
  Carl5362Server(host, port)

