from pathlib import Path

UPDATES_FILE = Path("../docs/internal/UPDATES.md")

class DevMemory:

    def __init__(self):
        if UPDATES_FILE.exists():
            self.content = UPDATES_FILE.read_text()
        else:
            self.content = ""

    def search(self, keyword):
        results = []
        for block in self.content.split("##"):
            if keyword.lower() in block.lower():
                results.append(block.strip())
        return results

    def log_problem(self, problem, solution):
        entry = f"""

## Problem
{problem}

## Solution
{solution}

"""
        with open(UPDATES_FILE, "a") as f:
            f.write(entry)
