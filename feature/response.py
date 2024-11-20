import asyncio


async def cari_jawaban():
    
    print("Bot sedang mencari jawaban... 🔍⏳")
    
    
    await asyncio.sleep(2)
    
   
    print("Jawaban sudah ditemukan! ✅")


async def main():
    await cari_jawaban()


asyncio.run(main())
