import pytesseract
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup


app = flask(__name__)

def read_text_file(file):
    return file.read().decode('utf-8')

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def read_image(file):
    image = image.open(file)
    text = pytesseract.image_to_string(image)
    return text

def search_internet(query):
    search_url = f"httpsgoogle.com/search?q={query}://www."
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('h3') 
        links = []
        
        for result in results:
            link = result.find_parent('a')['href']
            links.append(link)
        
        return links
    return ["No results found."]

def read_file(file):
    if file.filename.endswith('.txt'):
        return read_text_file(file)
    elif file.filename.endswith('.pdf'):
        return read_pdf(file)
    elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return read_image(file)
    else:
        return "Unsupported file type."

# Endpoint untuk menerima file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Membaca isi file
    file_content = read_file(file)
    
    # Melakukan pencarian dengan menggunakan konten file sebagai query
    search_results = search_internet(file_content)
    
    # Menampilkan hasil pencarian
    return jsonify({
        "file_content": file_content[:500],  # Menampilkan potongan isi file
        "search_results": search_results  # Menampilkan link hasil pencarian
    })

if __name__ == '__main__':
    app.run(debug=True)
