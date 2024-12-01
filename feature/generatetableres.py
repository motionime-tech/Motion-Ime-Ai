import discord
from discord.ext import commands
import re

# Membuat bot dengan prefix '!'
bot = commands.Bot(command_prefix='!')

# Fungsi untuk membuat tabel
def generate_table(data):
    # Tentukan lebar kolom (adjust sesuai kebutuhan)
    col_width = max(len(str(item)) for row in data for item in row) + 2
    table = ""
    for row in data:
        table += " | ".join(str(item).ljust(col_width) for item in row) + "\n"
        table += "-" * (col_width * len(row) + 3 * (len(row) - 1)) + "\n"
    return table

# Fungsi untuk memproses teks yang dikirimkan oleh pengguna
async def process_table_request(ctx, text):
    # Mencoba menangkap format tabel yang dipisahkan oleh koma dan titik koma
    pattern = r"([A-Za-z0-9\s]+(?:,[A-Za-z0-9\s]+)+)(?:\s*;\s*([A-Za-z0-9\s,]+))*"
    match = re.match(pattern, text)

    if match:
        # Memisahkan input berdasarkan titik koma (;) untuk baris
        lines = text.split(';')
        # Membagi setiap baris menjadi kolom berdasarkan koma (,)
        data = [line.split(',') for line in lines]

        # Generate tabel
        table = generate_table(data)
        await ctx.send(f"```\n{table}\n```")
    else:
        await ctx.send("Data tidak valid. Pastikan formatnya: `header1,header2,... ; row1 ; row2`")

# Event ketika bot mendeteksi pesan
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Mengabaikan pesan yang tidak berisi data untuk tabel
    if ';' in message.content and ',' in message.content:
        # Proses jika ada karakter yang menandakan format tabel
        await process_table_request(message.channel, message.content)

    # Memproses perintah lainnya
    await bot.process_commands(message)

# Jalankan bot dengan token Anda
bot.run('YOUR_BOT_TOKEN')
