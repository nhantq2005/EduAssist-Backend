import re

CODE_SYNTAX = ("//", "/*", "#include", "#define", "import ", "from ", "def ", "class ", "public ", "private ",
               "using namespace ",
               "SELECT ", "INSERT ", "UPDATE ", "DELETE ")

COMPARISON_OPERATORS = ("<<", ">>", "==", "!=", "=>", "->")

PAGE_RE = re.compile(r"^\s*(?:\d{1,4}|[ivxlcdm]{1,8})\s*$", re.IGNORECASE)
LIST_RE = re.compile(r"^\s*(?:[•▪◦●○■□◆◇‣⁃–—-]|§|\(?[A-Za-z]\)|\d+(?:\.\d+)*[.)])\s+")
HEADING_RE = re.compile(r"^\s*(?:chương\s+\d+|chapter\s+\d+|\d+(?:\.\d+)+\.?\s+)", re.IGNORECASE,)
TOC_RE = re.compile(r"\.{4,}\s*\d+\s*$")

