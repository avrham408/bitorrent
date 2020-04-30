import asyncio
import struct
import logging

logger = logging.getLogger(__name__)


class PeerConnection():
    def __init__(self, reader, writer):
        self.reader = reader 
        self.writer = writer

    @classmethod
    async def open_connection(cls, ip, port):
        try:
            reader, writer = await asyncio.open_connection(ip, port)
        except OSError:
            logger.debug("connection to asyncio socket failed")
            return None 
        logger.debug("connection to sockt success")
        return cls(reader, writer)


    async def write(self, message):
        try:
            self.writer.write(message)
            await self.writer.drain()
            return True
        except OSError:
            logger.debug(f"writing to socket failed - {message}")
        except Exception:
            logger.error("writing to server failed with uknown error", exc_info=True)
        return False

    async def read(self, message_size=2048, all_data=False):
        buf = b''
        while True:
            try:
                res = await self.reader.read(message_size)
            except OSError:
                logger.debug("reading from socket failed")
            except Exception:
                logger.error("reading from server failed with uknown error", exc_info=True)
            if not all_data:
                return res 
            else:
                buf += res
                if res == b'':
                    logger.debug("we didn't go all data from peer")
                    return False
                if len(buf) >= message_size:
                    return buf 
