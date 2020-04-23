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
            self.writer.write(m)
            await self.writer.drain()
        except OSError:
            logger.debug(f"writing to socket failed - {message}")
        except Exception:
            logger.error("writing to server failed with uknown error", exc_info=True)

    async def read(self, message_size, all_data=False):
        data = b''
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
                if res == b'':
                    logger.info("we got empty responses")
                    return False
                data += res
                if len(data) >= message_size:
                    return data
