import os
import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    from pypdf import PdfReader, PdfWriter

DRAWINGS_DIR = "drawings"
OUTPUT_DIR = "drawings/extracted_sheets" # Separate folder for split pages
OUTPUT_FILE = "index.html"

def process_pdfs():
    drawings_list = []
    
    if not os.path.exists(DRAWINGS_DIR):
        print(f"Error: '{DRAWINGS_DIR}' folder not found.")
        return

    # Create extraction directory if handling multi-page sets
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in sorted(os.listdir(DRAWINGS_DIR)):
        # Skip processing our own output folder
        if filename == "extracted_sheets" or not filename.lower().endswith('.pdf'):
            continue
            
        filepath = os.path.join(DRAWINGS_DIR, filename)
        
        try:
            reader = PdfReader(filepath)
            num_pages = len(reader.pages)
            
            # Scenario A: It's a massive multi-page blueprint set
            if num_pages > 1:
                print(f"Processing multi-page file ({num_pages} pages): {filename}")
                for page_num in range(num_pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num])
                    
                    # Name the individual sheet cleanly
                    base_name = os.path.splitext(filename)[0]
                    sheet_filename = f"{base_name}_Sheet_{page_num + 1}.pdf"
                    sheet_filepath = os.path.join(OUTPUT_DIR, sheet_filename)
                    
                    # Save individual sheet page
                    with open(sheet_filepath, "wb") as f:
                        writer.write(f)
                        
                    drawings_list.append({
                        "title": f"{base_name} — Sheet {page_num + 1}",
                        "filename": sheet_filename,
                        "filepath": sheet_filepath
                    })
            
            # Scenario B: It's already a single-sheet big file
            else:
                metadata = reader.metadata
                title = metadata.title.strip() if (metadata and metadata.title) else os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
                
                drawings_list.append({
                    "title": title,
                    "filename": filename,
                    "filepath": f"{DRAWINGS_DIR}/{filename}"
                })
                
        except Exception as e:
            print(f"Skipping corrupt or protected file {filename}: {e}")

    generate_html(drawings_list)

def generate_html(drawings_list):
    # (Matches the previous responsive HTML structure with search bar)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drawing Index</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-slate-50 text-slate-800 antialiased">
    <div class="max-w-4xl mx-auto py-12 px-4">
        <header class="mb-8">
            <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">Project Drawings</h1>
            <p class="text-slate-500 mt-1">Total Indexed Sheets: <span class="font-semibold text-slate-700">{len(drawings_list)}</span></p>
        </header>
        <div class="mb-6">
            <input type="text" id="searchInput" onkeyup="filterDrawings()" placeholder="Search sheets..." class="w-full px-4 py-3 rounded-lg border border-slate-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
        </div>
        <main class="bg-white shadow-sm rounded-xl border border-slate-200 overflow-hidden">
            <ul id="drawingsList" class="divide-y divide-slate-100">"""
            
    for dwg in drawings_list:
        html_content += f"""
                <li class="drawing-item p-4 hover:bg-slate-50 flex justify-between items-center transition">
                    <div>
                        <p class="font-semibold text-slate-900 drawing-title">{dwg['title']}</p>
                        <p class="text-xs text-slate-400 mt-0.5">{dwg['filename']}</p>
                    </div>
                    <a href="{dwg['filepath']}" target="_blank" class="px-4 py-2 text-sm font-medium bg-white border border-slate-300 rounded-lg text-slate-700 hover:bg-slate-50 transition shadow-xs">Open Sheet</a>
                </li>"""
                
    html_content += """</ul></main></div>
    <script>
    function filterDrawings() {
        const input = document.getElementById('searchInput');
        const filter = input.value.toLowerCase();
        const items = document.getElementsByClassName('drawing-item');
        for (let i = 0; i < items.length; i++) {
            const title = items[i].querySelector('.drawing-title').innerText;
            items[i].style.display = title.toLowerCase().indexOf(filter) > -1 ? "" : "none";
        }
    }
    </script>
</body></html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    process_pdfs()