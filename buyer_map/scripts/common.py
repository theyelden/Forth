import re
STOP = {"LTD","LIMITED","PLC","LLP","CO","COMPANY","THE","AND","UK","GROUP","&","T/A","TA","INTERNATIONAL","INT","TRADING","HOLDINGS"}
def norm(s):
    s = s.upper().replace("&", " AND ").replace("’", "'")
    s = re.sub(r"[^A-Z0-9 ]", " ", s.replace("'", ""))
    s = re.sub(r"\bLIMITED\b", "LTD", s); s = re.sub(r"\bPUBLIC LTD COMPANY\b", "PLC", s)
    s = re.sub(r"\b([A-Z]) (?=[A-Z]\b)", r"\1", s)   # "A F" -> "AF", "H N" -> "HN"
    return re.sub(r"\s+", " ", s).strip()
def core(s):
    """Name with legal suffixes / filler words removed, for comparison."""
    return " ".join(w for w in norm(s).split() if w not in STOP)
def pcnorm(p): return re.sub(r"\s+", "", (p or "").upper())
def outward(p):
    p = pcnorm(p); return p[:-3] if len(p) > 4 else p

def bare(s):
    """Name minus legal suffix only (keeps HOLDINGS/GROUP), spaces removed."""
    return re.sub(r"(LTD|PLC|LLP)$", "", norm(s).replace(" ", ""))
def acronym_hit(member_name, other_name):
    """'S&W Wholesale' vs 'SAVAGE & WHITTEN WHOLESALE': member's first word is
    the initials of the other name's leading words."""
    t = core(member_name).split()
    if not t or not (2 <= len(t[0]) <= 4) or not t[0].isalpha(): return False
    w = core(other_name).split()
    if not (len(w) >= len(t[0]) and "".join(x[0] for x in w[:len(t[0])]) == t[0] and len(w[0]) > 1): return False
    return all(x in w for x in t[1:])   # the rest of the member name must appear too
