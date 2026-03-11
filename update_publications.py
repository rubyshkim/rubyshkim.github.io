import bibtexparser

# -------- CONFIG --------
BIB_FILE = "publications.bib"
RESEARCH_HTML = "research.html"
START_MARKER = "<!-- Begin generated publications -->"
END_MARKER = "<!-- End generated publications -->"
# ------------------------

# Load BibTeX
with open(BIB_FILE) as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

# Helper: safely get year as int
def get_year(entry):
    try:
        return int(entry.get("year", 0))
    except ValueError:
        return 0

# Helper: convert "Last, First" -> "First Last"
def flip_name(name):
    parts = [p.strip() for p in name.split(",")]
    if len(parts) == 2:
        return parts[1] + " " + parts[0]
    return name  # already First Last

# Helper: format authors
def format_authors(authors_str):
    authors = [flip_name(a.strip()) for a in authors_str.replace("\n", " ").split(" and ")]
    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return " and ".join(authors)
    else:
        return ", ".join(authors[:-1]) + ", and " + authors[-1]

# Sort entries by year descending
sorted_entries = sorted(bib_database.entries, key=get_year, reverse=True)

# Generate HTML with reverse numbering
html_entries = []
total = len(sorted_entries)
for i, entry in enumerate(sorted_entries):
    number = total - i  # reverse number
    authors_raw = entry.get("author", "Unknown Author")
    authors = format_authors(authors_raw)

    title = entry.get("title", "No title")
    url = entry.get("url", "")
    if url:
        title_html = '<a href="{}" target="_blank">{}</a>'.format(url, title)
    else:
        title_html = title

    venue = entry.get("journal", entry.get("booktitle", ""))
    venue_html = "<em>{}</em>".format(venue) if venue else ""

    year = entry.get("year", "N/A")

    parts = ["{} ({})".format(authors, year), "<strong>{}</strong>".format(title_html)]
    if venue_html:
        parts.append(venue_html)

    html_entries.append(f"<li>{'. '.join(parts)}.</li>")

publications_html = "<ol reversed>\n" + "\n".join(html_entries) + "\n</ol>"

# Insert into research.html
with open(RESEARCH_HTML) as f:
    content = f.read()

if START_MARKER in content and END_MARKER in content:
    before = content.split(START_MARKER)[0] + START_MARKER + "\n"
    after = "\n" + END_MARKER + content.split(END_MARKER)[1]
    new_content = before + publications_html + after
else:
    raise ValueError("Markers not found in research.html")

with open(RESEARCH_HTML, "w") as f:
    f.write(new_content)

print("research.html updated with publications from", BIB_FILE)
