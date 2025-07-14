import socket
from src.core.variables import HOST, PORT

if __name__ == "__main__":
    HOSTNAME = socket.gethostname()
    print(f"SOCKET :: {HOSTNAME}\nHOST :: {HOST} | PORT :: {PORT}")

    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False, reload_delay=2)
