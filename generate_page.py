import os
import re
import json
from pypdf import PdfReader, PdfWriter

# Directory Setup
MASTER_DIR = "drawings"                
EXTRACTED_DIR = "extracted_sheets"     
OUTPUT_FILE = "index.html"

# Project Metadata Configuration Block
PROJECT_META = {
    "project_name": "HOME2 SUITES, FORT WAYNE, IN",
    "architect": "MAUST ARCHITECTURAL SERVICES, INC",
    "civil": "ENGINEERING RESOURCES, INC.",
    "owner": "VJAY PATEL",
    "address": "Cross Creek Blvd, Fort Wayne, IN",
    "maps_link": "https://maps.google.com/?q=Cross+Creek+Blvd,+Fort+Wayne,+IN"
}

# Primary Discipline Category Mapping
DISCIPLINE_MAP = {
    'GENERAL': 'GENERAL / COVER',
    'CIVIL': 'CIVIL (C-Sheets)',
    'LIFE SAFETY PLAN': 'LIFE SAFETY PLAN',
    'STRUCTURAL': 'STRUCTURAL (S-Sheets)',
    'ARCHITECTURAL': 'ARCHITECTURAL (A-Sheets)',
    'PLUMBING': 'PLUMBING (P-Sheets)',
    'MECHANICAL': 'MECHANICAL (M-Sheets)',
    'ELECTRICAL': 'ELECTRICAL (E-Sheets)'
}

# The 126 Sheets in Absolute Order matching your real PDF pages sequence array
VERIFIED_DRAWING_INDEX = [
    # --- GENERAL ---
    {"category": "GENERAL", "no": "A001", "name": "PROJECT INDEX AND JOB INFORMATION"},
    # --- CIVIL ---
    {"category": "CIVIL", "no": "C101", "name": "ARCHITECTURAL SITE PLAN"},
    # --- LIFE SAFETY PLAN ---
    {"category": "LIFE SAFETY PLAN", "no": "LS101", "name": "FIRST FLOOR LIFE SAFETY PLAN"},
    {"category": "LIFE SAFETY PLAN", "no": "LS102", "name": "SECOND FLOOR LIFE SAFETY PLAN"},
    {"category": "LIFE SAFETY PLAN", "no": "LS103", "name": "THIRD FLOOR LIFE SAFETY PLAN"},
    {"category": "LIFE SAFETY PLAN", "no": "LS104", "name": "FOURTH FLOOR LIFE SAFETY PLAN"},
    # --- STRUCTURAL ---
    {"category": "STRUCTURAL", "no": "S001", "name": "GENERAL NOTES"},
    {"category": "STRUCTURAL", "no": "S101", "name": "FOUNDATION PLAN"},
    {"category": "STRUCTURAL", "no": "S102", "name": "FOUNDATION DETAILS"},
    {"category": "STRUCTURAL", "no": "S201", "name": "FIRST FLOOR STEEL PLAN"},
    {"category": "STRUCTURAL", "no": "S202", "name": "SECOND FLOOR FRAMING PLAN"},
    {"category": "STRUCTURAL", "no": "S203", "name": "THIRD FLOOR FRAMING PLAN"},
    {"category": "STRUCTURAL", "no": "S204", "name": "FOURTH FLOOR FRAMING PLAN"},
    {"category": "STRUCTURAL", "no": "S301", "name": "ROOF FRAMING PLAN"},
    {"category": "STRUCTURAL", "no": "S401", "name": "SHEAR WALL DETAILS"},
    {"category": "STRUCTURAL", "no": "S402", "name": "SHEAR WALL DETAILS"},
    {"category": "STRUCTURAL", "no": "S403", "name": "PARTY WALL DETAILS"},
    {"category": "STRUCTURAL", "no": "S501", "name": "STEEL ELEVATIONS"},
    {"category": "STRUCTURAL", "no": "S502", "name": "STEEL ELEVATIONS AND DETAILS"},
    # --- ARCHITECTURAL ---
    {"category": "ARCHITECTURAL", "no": "A101", "name": "FIRST FLOOR PLAN"},
    {"category": "ARCHITECTURAL", "no": "A102", "name": "SECOND FLOOR PLAN"},
    {"category": "ARCHITECTURAL", "no": "A103", "name": "THIRD FLOOR PLAN"},
    {"category": "ARCHITECTURAL", "no": "A104", "name": "FOURTH FLOOR PLAN"},
    {"category": "ARCHITECTURAL", "no": "A105", "name": "ROOF PLAN"},
    {"category": "ARCHITECTURAL", "no": "A151", "name": "ENLARGED FIRST FLOOR PLAN"},
    {"category": "ARCHITECTURAL", "no": "A152", "name": "ENLARGED FIRST FLOOR PLAN"},
    {"category": "ARCHITECTURAL", "no": "A153", "name": "ENLARGED FIRST AND UPPER FLOOR PLANS"},
    {"category": "ARCHITECTURAL", "no": "A161", "name": "INTERIOR ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A162", "name": "INTERIOR ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A163", "name": "INTERIOR ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A164", "name": "POOL ELEVATIONS & DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A201", "name": "COLOR EXTERIOR ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A201", "name": "EXTERIOR ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A202", "name": "COLOR EXTERIOR ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A202", "name": "EXTERIOR ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A301", "name": "FULL BUILDING SECTION"},
    {"category": "ARCHITECTURAL", "no": "A401", "name": "ENLARGED BUILDING SECTIONS"},
    {"category": "ARCHITECTURAL", "no": "A402", "name": "ENLARGED BUILDING SECTIONS"},
    {"category": "ARCHITECTURAL", "no": "A403", "name": "ELEVATOR SECTION"},
    {"category": "ARCHITECTURAL", "no": "A404", "name": "STAIR PLANS AND DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A405", "name": "STAIR SECTION"},
    {"category": "ARCHITECTURAL", "no": "A406", "name": "MISCELLANEOUS SECTIONS AND DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A407", "name": "CANOPY AND PERGOLA SECTIONS"},
    {"category": "ARCHITECTURAL", "no": "A408", "name": "CANOPY AND PERGOLA SECTIONS"},
    {"category": "ARCHITECTURAL", "no": "A409", "name": "DUMPSTER PLAN AND ELEVATION"},
    {"category": "ARCHITECTURAL", "no": "A410", "name": "DUMPSTER SECTION AND ELEVATION"},
    {"category": "ARCHITECTURAL", "no": "A411", "name": "EXTERIOR DETAILS & TRELLIS"},
    {"category": "ARCHITECTURAL", "no": "A412", "name": "FIRE PIT PLAN, SECTION, AND ELEVATION"},
    {"category": "ARCHITECTURAL", "no": "A413", "name": "LINEN CHUTE SECTION AND DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A450", "name": "WALL TYPES"},
    {"category": "ARCHITECTURAL", "no": "A451", "name": "FIRST FLOOR WALL TYPES PLAN"},
    {"category": "ARCHITECTURAL", "no": "A452", "name": "UPPER FLOOR WALL TYPES PLAN"},
    {"category": "ARCHITECTURAL", "no": "A453", "name": "FLOOR AND PIPE PENETRATION DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A454", "name": "FLOOR AND PIPE PENETRATION DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A500", "name": "TYPICAL MOUNTING HEIGHTS"},
    {"category": "ARCHITECTURAL", "no": "A501", "name": "KING STUDIO"},
    {"category": "ARCHITECTURAL", "no": "A502", "name": "ACCESSIBLE KING STUDIO"},
    {"category": "ARCHITECTURAL", "no": "A503", "name": "DOUBLE QUEEN STUDIO"},
    {"category": "ARCHITECTURAL", "no": "A504", "name": "ACCESSIBLE DOUBLE QUEEN STUDIO"},
    {"category": "ARCHITECTURAL", "no": "A505", "name": "GUESTROOM BLOCKING DIAGRAM"},
    {"category": "ARCHITECTURAL", "no": "A506", "name": "ONE BEDROOM STUDIO 'B'"},
    {"category": "ARCHITECTURAL", "no": "A507", "name": "ACCESSIBLE ONE BEDROOM STUDIO ROLL-IN"},
    {"category": "ARCHITECTURAL", "no": "A508", "name": "ACCESSIBLE ONE BEDROOM STUDIO"},
    {"category": "ARCHITECTURAL", "no": "A509", "name": "GUEST BATHROOM ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A510", "name": "GUEST BATHROOM BLOCKING DIAGRAMS"},
    {"category": "ARCHITECTURAL", "no": "A601", "name": "CASEWORK ELEVATIONS AND DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A602", "name": "CASEWORK ELEVATIONS AND DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A603", "name": "CASEWORK ELEVATIONS AND DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A604", "name": "CASEWORK ELEVATIONS AND DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A605", "name": "FRONT DESK PLAN ELEVATIONS"},
    {"category": "ARCHITECTURAL", "no": "A606", "name": "FRONT DESK SECTIONS AND BACK WALL DTLS"},
    {"category": "ARCHITECTURAL", "no": "A607", "name": "BREAKFAST PERCH PLAN AND ELEVATION"},
    {"category": "ARCHITECTURAL", "no": "A701", "name": "DOOR SCHEDULE"},
    {"category": "ARCHITECTURAL", "no": "A702", "name": "ROOM FINISH SCHEDULE & WINDOW TYPES"},
    {"category": "ARCHITECTURAL", "no": "A801A", "name": "ENLARGED FIRST FLOOR REFLECTED CEILING PLAN"},
    {"category": "ARCHITECTURAL", "no": "A801B", "name": "ENLARGED FIRST FLOOR REFLECTED CEILING PLAN"},
    {"category": "ARCHITECTURAL", "no": "A801C", "name": "ENLARGED FIRST FLOOR RCP & DETAILS"},
    {"category": "ARCHITECTURAL", "no": "A802", "name": "SECOND FLOOR REFLECTED CEILING PLAN"},
    {"category": "ARCHITECTURAL", "no": "A803", "name": "THIRD FLOOR REFLECTED CEILING PLAN"},
    {"category": "ARCHITECTURAL", "no": "A804", "name": "FOURTH FLOOR REFLECTED CEILING PLAN"},
    {"category": "ARCHITECTURAL", "no": "A901", "name": "ENLARGED FIRST FLOOR FF&E PLAN"},
    {"category": "ARCHITECTURAL", "no": "A902", "name": "ENLARGED FIRST FLOOR FF&E PLAN"},
    {"category": "ARCHITECTURAL", "no": "A903", "name": "ENLARGED FIRST & UPPER FLOOR FF&E PLANS"},
    {"category": "ARCHITECTURAL", "no": "K100", "name": "KITCHEN EQUIPMENT PLAN"},
    # --- PLUMBING ---
    {"category": "PLUMBING", "no": "P001", "name": "PLUMBING NOTES AND SCHEDULES"},
    {"category": "PLUMBING", "no": "P002", "name": "PLUMBING DETAILS"},
    {"category": "PLUMBING", "no": "P003", "name": "WATER RISER DIAGRAMS"},
    {"category": "PLUMBING", "no": "P004", "name": "SANITARY RISER DIAGRAMS"},
    {"category": "PLUMBING", "no": "P005", "name": "SANITARY RISER DIAGRAMS"},
    {"category": "PLUMBING", "no": "P101", "name": "FIRST FLOOR PLUMBING PLAN"},
    {"category": "PLUMBING", "no": "P102", "name": "FIRST FLOOR SANITARY PLAN"},
    {"category": "PLUMBING", "no": "P201", "name": "SECOND FLOOR PLUMBING PLAN"},
    {"category": "PLUMBING", "no": "P202", "name": "SECOND FLOOR SANITARY PLAN"},
    {"category": "PLUMBING", "no": "P301", "name": "THIRD FLOOR PLUMBING PLAN"},
    {"category": "PLUMBING", "no": "P302", "name": "THIRD FLOOR SANITARY PLAN"},
    {"category": "PLUMBING", "no": "P401", "name": "FOURTH FLOOR PLUMBING PLAN"},
    {"category": "PLUMBING", "no": "P402", "name": "FOURTH FLOOR SANITARY PLAN"},
    {"category": "PLUMBING", "no": "P502", "name": "ROOF SANITARY PLAN"},
    # --- MECHANICAL ---
    {"category": "MECHANICAL", "no": "M001", "name": "MECHANICAL SCHEDULES"},
    {"category": "MECHANICAL", "no": "M002", "name": "MECHANICAL DETAILS"},
    {"category": "MECHANICAL", "no": "M003", "name": "MECHANICAL NOTES"},
    {"category": "MECHANICAL", "no": "M101", "name": "FIRST FLOOR MECHANICAL PLAN"},
    {"category": "MECHANICAL", "no": "M201", "name": "SECOND FLOOR MECHANICAL PLAN"},
    {"category": "MECHANICAL", "no": "M301", "name": "THIRD FLOOR MECHANICAL PLAN"},
    {"category": "MECHANICAL", "no": "M401", "name": "FOURTH FLOOR MECHANICAL PLAN"},
    {"category": "MECHANICAL", "no": "M402", "name": "FOURTH FLOOR EXHAUST PLAN"},
    {"category": "MECHANICAL", "no": "M501", "name": "ROOF MECHANICAL PLAN"},
    {"category": "MECHANICAL", "no": "M601", "name": "FIRST FLOOR GAS PLAN"},
    {"category": "MECHANICAL", "no": "M602", "name": "ROOF GAS PLAN"},
    # --- ELECTRICAL ---
    {"category": "ELECTRICAL", "no": "E001", "name": "ELECTRICAL NOTES"},
    {"category": "ELECTRICAL", "no": "E002", "name": "ELECTRICAL RISER DIAGRAMS"},
    {"category": "ELECTRICAL", "no": "E101", "name": "FIRST FLOOR POWER PLAN"},
    {"category": "ELECTRICAL", "no": "E102A", "name": "ENLARGED FIRST FLOOR LIGHTING PLAN"},
    {"category": "ELECTRICAL", "no": "E102B", "name": "ENLARGED FIRST FLOOR LIGHTING PLAN"},
    {"category": "ELECTRICAL", "no": "E102C", "name": "ENLARGED FIRST FLOOR LIGHTING PLAN"},
    {"category": "ELECTRICAL", "no": "E201", "name": "SECOND FLOOR POWER PLAN"},
    {"category": "ELECTRICAL", "no": "E202", "name": "SECOND FLOOR LIGHTING PLAN"},
    {"category": "ELECTRICAL", "no": "E301", "name": "THIRD FLOOR POWER PLAN"},
    {"category": "ELECTRICAL", "no": "E302", "name": "THIRD FLOOR LIGHTING PLAN"},
    {"category": "ELECTRICAL", "no": "E401", "name": "FOURTH FLOOR POWER PLAN"},
    {"category": "ELECTRICAL", "no": "E402", "name": "FOURTH FLOOR LIGHTING PLAN"},
    {"category": "ELECTRICAL", "no": "E501", "name": "ROOF POWER PLAN"},
    {"category": "ELECTRICAL", "no": "E701", "name": "GUESTROOM ELECTRICAL PLANS"},
    {"category": "ELECTRICAL", "no": "E702", "name": "GUESTROOM ELECTRICAL PLANS"},
    {"category": "ELECTRICAL", "no": "E800", "name": "PANEL SCHEDULES"},
    {"category": "ELECTRICAL", "no": "E801", "name": "PANEL SCHEDULES"}
]

def clean_space(text):
    return " ".join(text.split()).strip() if text else ""

def sanitize_filename(name):
    sanitized = name.replace("/", "_").replace("\\", "_").replace(" ", "_").replace("&", "AND")
    return re.sub(r'[^A-Za-z0-9_\-\.]', '', sanitized).upper()

def process_project_pipeline():
    dataset = [["Category", "Subcategory", "Shortname", "Name", "Description", "Filename", "Pagenumber", "SearchPool"]]
    
    if not os.path.exists(MASTER_DIR):
        os.makedirs(MASTER_DIR)
        print(f"Workspace folder '{MASTER_DIR}' ready. Drop your combined blueprint master PDF inside.")
        return None

    os.makedirs(EXTRACTED_DIR, exist_ok=True)
    master_files = [f for f in os.listdir(MASTER_DIR) if f.lower().endswith('.pdf')]
    if not master_files:
        print("Please ensure your multi-page master PDF is located inside drawings/ directory.")
        return None

    master_filepath = os.path.join(MASTER_DIR, sorted(master_files)[0])
    reader = PdfReader(master_filepath)
    total_pdf_pages = len(reader.pages)
    
    PROJECT_META["master_link"] = master_filepath

    print(f"🔢 Total available pages inside PDF file: {total_pdf_pages}")
    print("🛠️ Slicing sequence layout sheets in absolute alignment...")
    
    for idx, sheet_meta in enumerate(VERIFIED_DRAWING_INDEX):
        if idx >= total_pdf_pages:
            break
            
        page_num = idx + 1
        page = reader.pages[idx]
        
        sheet_no = sheet_meta["no"]
        sheet_title = sheet_meta["name"]
        raw_category = sheet_meta["category"]

        category = DISCIPLINE_MAP.get(raw_category, "ARCHITECTURAL (A-Sheets)")

        # Determine structural drop-down subcategories cleanly
        subcategory = "DETAILS & OVERALL"
        title_upper = sheet_title.upper()
        if "ELEVATION" in title_upper:
            subcategory = "EXTERIOR ELEVATIONS" if "EXTERIOR" in title_upper else "INTERIOR ELEVATIONS"
        elif "PLAN" in title_upper:
            subcategory = "FLOOR PLAN" if "FLOOR" in title_upper else "SITE PLAN"
        elif "WALL" in title_upper:
            subcategory = "WALL DETAILS"
        elif "CEILING" in title_upper or "RCP" in title_upper:
            subcategory = "CEILING PLANS"
        elif "SCHEDULE" in title_upper or "LEGEND" in title_upper:
            subcategory = "SCHEDULES & LEGENDS"

        # Apply simplified text descriptors if a schedule is present
        description = ""
        if "SCHEDULE" in title_upper or "NOTES" in title_upper:
            description = "Contains tabular specifications and schedule matrices configuration limits."

        # COMBINE BOTH EXACT STRINGS: No + Name for clean output filenames
        combined_filename_base = f"{sheet_no}_{sheet_title.replace(' ', '_')}"
        sheet_filename = f"{sanitize_filename(combined_filename_base)}.pdf"
        sheet_filepath = os.path.join(EXTRACTED_DIR, sheet_filename)
        
        # Slicing independent sheet file out
        writer = PdfWriter()
        writer.add_page(page)
        with open(sheet_filepath, "wb") as f_out:
            writer.write(f_out)

        print(f" -> Matched Page {page_num:03d} -> Saved strictly to: {sheet_filename}")

        # Searchpool configuration text tracking layout parameters matching interface rules
        search_pool_text = f"{sheet_no} {sheet_title} {subcategory} {category}".upper()
        
        dataset.append([
            category, subcategory, sheet_no, sheet_title, description, sheet_filepath, "1", search_pool_text
        ])

    return dataset

def generate_dashboard(data):
    json_data_str = json.dumps(data, indent=12)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{PROJECT_META['project_name']} - Drawing Index</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .section-content {{
            display: none;
            overflow: hidden;
            transition: max-height 0.4s ease-out;
            max-height: 0;
        }}
        .section-content.active {{
            max-height: 4000px;
            display: block;
        }}
        .section-header svg {{ transition: transform 0.2s ease-out; }}
        .section-header.active svg {{ transform: rotate(180deg); }}
    </style>
</head>
<body class="bg-gray-900 text-gray-100">

    <div class="container mx-auto p-4 md:p-8 max-w-5xl bg-gray-800 rounded-lg shadow-xl mt-8 mb-8">
        <header class="mb-8">
            <h1 class="text-3xl md:text-4xl font-bold text-gray-50">{PROJECT_META['project_name']}</h1>
            <p class="text-md text-gray-300 mt-1">{PROJECT_META['address']}</p>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="md:col-span-2 bg-gray-700 p-6 rounded-lg shadow-inner">
                <h3 class="font-bold text-lg text-gray-50 mb-3 border-b border-gray-600 pb-2">Project Information</h3>
                <div class="space-y-2 text-sm text-gray-200">
                    <p><strong>Owner:</strong> {PROJECT_META['owner']}</p>
                    <p><strong>Architect:</strong> {PROJECT_META['architect']}</p>
                    <p><strong>Civil Engineer:</strong> {PROJECT_META['civil']}</p>
                    <p><strong>Interior Design Set:</strong> </p>
                    <p>
                        <strong>Hotel Full Set:</strong> 
                        <a href="{PROJECT_META['master_link']}" target="_blank" class="text-blue-400 hover:text-blue-200 transition underline font-medium">View Full Set of Drawings</a>
                    </p>
                </div>
            </div>
            <div class="bg-gray-700 p-6 rounded-lg shadow-inner">
                <h3 class="font-bold text-lg text-gray-50 mb-3 border-b border-gray-600 pb-2">Location Information</h3>
                <div class="space-y-2 text-sm text-gray-200">
                    <p><strong>Address:</strong> {PROJECT_META['address']}</p>
                    <p><strong>Map:</strong> <a href="{PROJECT_META['maps_link']}" target="_blank" class="text-blue-400 hover:text-blue-200 transition underline font-medium">View on Google Maps</a></p>
                </div>
            </div>
        </div>

        <div class="mb-8">
            <input type="text" id="searchInput" onkeyup="filterDrawings()" placeholder="Search for any drawing, sheet number, or schedule..." class="w-full p-4 border border-gray-600 rounded-lg shadow-inner bg-gray-700 text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition">
        </div>

        <main id="drawing-container" class="space-y-4"></main>
    </div>

    <script>
        const rawSpreadsheetData = {json_data_str};
        
        const COL_CATEGORY = 0;
        const COL_SUBCATEGORY = 1;
        const COL_SHORTNAME = 2;
        const COL_NAME = 3;
        const COL_DESCRIPTION = 4;
        const COL_FILENAME = 5;
        const COL_PAGENUMBER = 6;
        const COL_SEARCHPOOL = 7;

        function parseAndGroupData(data) {{
            const rows = data.slice(1);
            const grouped = {{}};
            let lastCategory = '';
            let lastSubcategory = '';
            let currentFilename = '';

            rows.forEach(row => {{
                const item = {{
                    category: row[COL_CATEGORY],
                    subcategory: row[COL_SUBCATEGORY],
                    shortname: row[COL_SHORTNAME],
                    name: row[COL_NAME],
                    description: row[COL_DESCRIPTION],
                    filename: row[COL_FILENAME],
                    pagenumber: row[COL_PAGENUMBER],
                    searchpool: row[COL_SEARCHPOOL]
                }};

                if (item.category !== lastCategory || item.subcategory !== lastSubcategory) {{ currentFilename = ''; }}
                if (item.filename) {{ currentFilename = item.filename; }} else {{ item.filename = currentFilename; }}

                if (!grouped[item.category]) {{ grouped[item.category] = {{}}; }}
                if (!grouped[item.category][item.subcategory]) {{ grouped[item.category][item.subcategory] = []; }}
                grouped[item.category][item.subcategory].push(item);

                lastCategory = item.category;
                lastSubcategory = item.subcategory;
            }});
            return grouped;
        }}

        const drawingDataGrouped = parseAndGroupData(rawSpreadsheetData);

        function buildDrawingIndex() {{
            const container = document.getElementById('drawing-container');
            container.innerHTML = '';

            for (const category in drawingDataGrouped) {{
                const categoryId = category.replace(/\s+/g, '-').toLowerCase();
                const sectionWrapper = document.createElement('div');
                sectionWrapper.className = 'bg-gray-800 rounded-lg border border-gray-700 overflow-hidden mb-4 section-wrapper-block';
                
                const sectionHeader = document.createElement('div');
                sectionHeader.className = 'section-header flex justify-between items-center p-4 cursor-pointer hover:bg-gray-700';
                sectionHeader.innerHTML = `<h2 class="text-xl font-semibold text-blue-300">${{category}}</h2>
                                           <svg class="w-6 h-6 text-blue-300 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>`;
                
                const sectionContent = document.createElement('div');
                sectionContent.id = `content-${{categoryId}}`;
                sectionContent.className = 'section-content px-4 pb-4 bg-gray-850';

                sectionHeader.onclick = () => {{
                    sectionContent.classList.toggle('active');
                    sectionHeader.classList.toggle('active');
                }};

                Object.keys(drawingDataGrouped[category]).sort().forEach((subcategoryTitle) => {{
                    const subcatItems = drawingDataGrouped[category][subcategoryTitle];
                    const subgroupSection = document.createElement('div');
                    subgroupSection.className = 'subgroup-section-block mt-4 pt-4 border-t border-gray-700';
                    
                    subgroupSection.innerHTML = `<h4 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">${{subcategoryTitle}}</h4>`;
                    
                    const drawingList = document.createElement('div');
                    drawingList.className = 'space-y-2';

                    subcatItems.forEach(sheet => {{
                        const drawingItemWrapper = document.createElement('div');
                        drawingItemWrapper.className = 'drawing-item-wrapper bg-gray-700/40 p-3 rounded-lg border border-gray-700/50 hover:bg-gray-700/70 transition';
                        
                        drawingItemWrapper.setAttribute('data-searchpool', sheet.searchpool);

                        drawingItemWrapper.innerHTML = `
                            <div class="flex justify-between items-start">
                                <div class="text-gray-200">
                                    <strong class="font-mono bg-gray-900 text-blue-400 px-2 py-0.5 rounded text-sm">${{sheet.shortname}}</strong>
                                    <span class="ml-2 font-medium tracking-wide text-gray-100">${{sheet.name}}</span>
                                    ${{sheet.description ? `<p class="text-xs text-gray-400 mt-1.5 bg-gray-800/50 p-2 rounded border border-gray-700/30">${{sheet.description}}</p>` : ''}}
                                </div>
                                <a href="${{sheet.filename}}" target="_blank" class="ml-4 text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white py-1.5 px-3.5 rounded shadow transition shrink-0">Open Sheet</a>
                            </div>`;
                        drawingList.appendChild(drawingItemWrapper);
                    }});
                    
                    subgroupSection.appendChild(drawingList);
                    sectionContent.appendChild(subgroupSection);
                }});
                
                sectionWrapper.appendChild(sectionHeader);
                sectionWrapper.appendChild(sectionContent);
                container.appendChild(sectionWrapper);
            }}
        }}

        function filterDrawings() {{
            const filter = document.getElementById('searchInput').value.toUpperCase();
            const sections = document.querySelectorAll('.section-wrapper-block');
            
            sections.forEach(section => {{
                let sectionHasVisibleContent = false;
                const subgroups = section.querySelectorAll('.subgroup-section-block');
                
                subgroups.forEach(subgroup => {{
                    let subgroupHasVisibleContent = false;
                    const wrappers = subgroup.querySelectorAll('.drawing-item-wrapper');
                    
                    wrappers.forEach(wrapper => {{
                        const searchPoolText = wrapper.getAttribute('data-searchpool') || '';
                        
                        if (searchPoolText.indexOf(filter) > -1) {{
                            wrapper.style.display = "";
                            subgroupHasVisibleContent = true;
                            sectionHasVisibleContent = true;
                        }} else {{
                            wrapper.style.display = "none";
                        }}
                    }});
                    subgroup.style.display = subgroupHasVisibleContent ? "" : "none";
                }});

                const content = section.querySelector('.section-content');
                const header = section.querySelector('.section-header');
                
                if (filter === "") {{
                    section.style.display = "";
                    content.classList.remove('active');
                    header.classList.remove('active');
                }} else {{
                    if (sectionHasVisibleContent) {{
                        section.style.display = "";
                        content.classList.add('active');
                        header.classList.add('active');
                    }} else {{
                        section.style.display = "none";
                    }}
                }}
            }});
        }}

        document.addEventListener('DOMContentLoaded', buildDrawingIndex);
    </script>
</body>
</html>
"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"\n✨ Generation successful! Launch '{OUTPUT_FILE}' to browse.")

if __name__ == "__main__":
    matrix_data = process_project_pipeline()
    if matrix_data:
        generate_dashboard(matrix_data)