import os
from pathlib import Path

class Config:
    def __init__(self):
        self.BASE_PATH = Path("/workspaces/MMECO")
        self.AI_AGENTS_PATH = self.BASE_PATH / "ai_agents"
        self.BLOCKCHAIN_CORE_PATH = self.BASE_PATH / "blockchain-core"
        self.DOCS_PATH = self.BASE_PATH / "docs/internal/error-tracker"
        
        self.MEMORY_FILE = self.AI_AGENTS_PATH / "blockchain_errors_memory.json"
        self.DAO_MEMORY_FILE = self.AI_AGENTS_PATH / "dao_memory.json"
        self.CHECK_INTERVAL = 300
        
        self.DOCS_PATH.mkdir(parents=True, exist_ok=True)

    def get_error_files(self):
        return {
            "all_errors": self.DOCS_PATH / "all-errors.md",
            "resolved": self.DOCS_PATH / "resolved.md",
            "frequent": self.DOCS_PATH / "frequent-errors.md",
            "lessons": self.DOCS_PATH / "lessons-learned.md",
            "quick_reference": self.DOCS_PATH / "quick-reference.md",
            "pre_commit": self.DOCS_PATH / "pre-commit-checklist.md"
        }

    def get_memory_config(self):
        return {"file": self.MEMORY_FILE}

class DictObj(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None
    def __setattr__(self, key, value):
        self[key] = value

def get_config():
    cfg = Config()
    obj = DictObj({
        "BASE_PATH": str(cfg.BASE_PATH),
        "AI_AGENTS_PATH": str(cfg.AI_AGENTS_PATH),
        "BLOCKCHAIN_CORE_PATH": str(cfg.BLOCKCHAIN_CORE_PATH),
        "ERROR_TRACKER_PATH": str(cfg.DOCS_PATH),
        "DOCS_PATH": str(cfg.DOCS_PATH),
        "MEMORY_FILE": str(cfg.MEMORY_FILE),
        "DAO_MEMORY_FILE": str(cfg.DAO_MEMORY_FILE),
        "CHECK_INTERVAL": cfg.CHECK_INTERVAL,
    })
    obj.get_error_files = cfg.get_error_files
    obj.get_memory_config = cfg.get_memory_config
    return obj

def validate_config():
    return True
