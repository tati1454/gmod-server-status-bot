import socket
import struct
import os
import io

from discord.ext import commands

def readCString(message: io.BytesIO):
    r = b""
    while True:
        c = message.read(1)
        if c == b"\0":
            break
        
        r += c

    return r.decode("utf-8")

class ServerInfoPacket:
    def __init__(self, data: io.BytesIO):
        self.splitted = struct.unpack("i", data.read(4))[0]
        self.header = struct.unpack("b", data.read(1))[0]
        self.protocol = struct.unpack("b", data.read(1))[0]
        self.name = readCString(data)
        self.map = readCString(data)
        self.folder = readCString(data)
        self.game = readCString(data)
        self.id = struct.unpack("h", data.read(2))[0]
        self.players = struct.unpack("b", data.read(1))[0]
        self.maxPlayers = struct.unpack("b", data.read(1))[0]
        self.bots = struct.unpack("b", data.read(1))[0]
        self.serverType = struct.unpack("b", data.read(1))[0]
        self.environment = struct.unpack("b", data.read(1))[0]
        self.visibility = struct.unpack("b", data.read(1))[0]
        self.vac = struct.unpack("b", data.read(1))[0]
        self.version = readCString(data)
        self.edf = struct.unpack("b", data.read(1))[0]

    def __str__(self):
        return f"Protocol: {self.protocol}\n"\
                + f"Name: {self.name}\n"\
                + f"Map: {self.map}\n"\
                + f"Folder: {self.folder}\n"\
                + f"Game: {self.game}\n"\
                + f"Id: {self.id}\n"\
                + f"Players: {self.players}\n"\
                + f"Max players: {self.maxPlayers}\n"\
                + f"Bots: {self.bots}\n"\
                + f"Server Type: {self.serverType}\n"\
                + f"Environment: {self.environment}\n"\
                + f"Visibility: {self.visibility}\n"\
                + f"VAC: {self.vac}\n"\
                + f"Version: {self.version}\n"

def getServerInfo(hostname):
    ip, port = hostname.split(":")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2)
        try:
            s.connect((ip, int(port)))
            s.send(b"\xFF\xFF\xFF\xFF\x54Source Engine Query\0\0\0\0\0")
            data = s.recv(100000)
            data = io.BytesIO(data)

            serverInfo = ServerInfoPacket(data)
            return serverInfo
        
        except socket.timeout as e:
            raise e

bot = commands.Bot("$")

@bot.command()
async def getslotsinfo(ctx: commands.Context, host: str=None):
    if(host == None):
        await ctx.send("$getslotsinfo <ip>:<port>")
        return

    try:
        serverInfo = getServerInfo(host)
        await ctx.send(f"Server name: {serverInfo.name}\nSlots available: {serverInfo.maxPlayers - serverInfo.players}")
    except socket.timeout:
        await ctx.send("El servidor no estaria respondiendo.")


bot.run(os.environ.get("TOKEN"))