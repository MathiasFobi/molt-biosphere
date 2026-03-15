"""REM Consolidator - Memory crystallization.

Reads MEMORY.md and transcripts, extracts wisdom, writes to WISDOM_GRAPH.
"""
import json
import re
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/myassistant/Documents/Workspace")
WISDOM_FILE = WORKSPACE / "molt-biosphere" / "WISDOM_GRAPH.json"
TRANSCRIPTS_FILE = WORKSPACE / "transcripts.jsonl"


class REMConsolidator:
    """Consolidates memory into wisdom graph."""
    
    def __init__(self):
        self.extracted_count = 0
    
    def crystallize(self) -> dict:
        """Main crystallization process."""
        all_triplets = []
        
        # 1. Read MEMORY.md
        memory_file = WORKSPACE / "MEMORY.md"
        if memory_file.exists():
            content = memory_file.read_text()
            triplets = self._extract_from_markdown(content)
            all_triplets.extend(triplets)
            self.extracted_count += len(triplets)
        
        # 2. Read transcripts
        if TRANSCRIPTS_FILE.exists():
            try:
                content = TRANSCRIPTS_FILE.read_text()
                lines = content.strip().split("\n")
                for line in lines:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            text = entry.get("content", entry.get("text", ""))
                            if text:
                                triplets = self._extract_from_text(text)
                                all_triplets.extend(triplets)
                                self.extracted_count += len(triplets)
                        except:
                            pass
            except Exception as e:
                print(f"Transcripts read error: {e}")
        
        # 3. Load existing wisdom
        existing = []
        if WISDOM_FILE.exists():
            try:
                existing = json.loads(WISDOM_FILE.read_text())
            except:
                pass
        
        # 4. Merge (dedupe by subject+predicate)
        existing_ids = set(f"{t['subject']}|{t['predicate']}" for t in existing)
        new_triplets = [t for t in all_triplets if f"{t['subject']}|{t['predicate']}" not in existing_ids]
        
        final_wisdom = existing + new_triplets
        
        # 5. Write wisdom graph
        WISDOM_FILE.parent.mkdir(parents=True, exist_ok=True)
        WISDOM_FILE.write_text(json.dumps(final_wisdom, indent=2))
        
        # 6. Clear transcripts if large
        if TRANSCRIPTS_FILE.exists():
            size = TRANSCRIPTS_FILE.stat().st_size
            if size > 1024 * 1024:  # > 1MB
                TRANSCRIPTS_FILE.write_text("")
                print("Cleared transcripts.jsonl (too large)")
        
        return {
            "new_triplets": len(new_triplets),
            "total_triplets": len(final_wisdom),
            "sources": ["MEMORY.md", "transcripts.jsonl"] if TRANSCRIPTS_FILE.exists() else ["MEMORY.md"]
        }
    
    def _extract_from_markdown(self, content: str) -> list:
        """Extract SPO triplets from markdown."""
        triplets = []
        
        # Pattern: - **subject**: description
        pattern = r"- \*\*([^*]+)\*\*:?\s*(.+)"
        for match in re.finditer(pattern, content):
            subject = match.group(1).strip()
            obj = match.group(2).strip()[:100]
            if subject and len(subject) > 1:
                triplets.append({
                    "subject": subject,
                    "predicate": "described_as",
                    "object": obj,
                    "source": "memory",
                    "extracted_at": datetime.utcnow().isoformat()
                })
        
        # Pattern: ## Section headers
        pattern = r"##\s+(.+)"
        for match in re.finditer(pattern, content):
            section = match.group(1).strip()
            if section and len(section) > 2:
                triplets.append({
                    "subject": section,
                    "predicate": "is_section",
                    "object": "memory",
                    "source": "memory",
                    "extracted_at": datetime.utcnow().isoformat()
                })
        
        return triplets
    
    def _extract_from_text(self, text: str) -> list:
        """Extract SPO triplets from plain text."""
        triplets = []
        
        # Simple extraction: look for key phrases
        patterns = [
            (r"(\w+)\s+is\s+(\w+)", "is_a"),
            (r"(\w+)\s+has\s+(\w+)", "has_property"),
            (r"(\w+)\s+does\s+(\w+)", "does_action"),
            (r"(\w+)\s+was\s+(\w+)", "was_state"),
        ]
        
        for pattern, predicate in patterns:
            for match in re.finditer(pattern, text, re.I):
                subject = match.group(1).strip()
                obj = match.group(2).strip()
                if len(subject) > 2 and len(obj) > 2:
                    triplets.append({
                        "subject": subject,
                        "predicate": predicate,
                        "object": obj,
                        "source": "transcript",
                        "extracted_at": datetime.utcnow().isoformat()
                    })
        
        return triplets[:10]  # Limit per entry


def run_rem():
    """Run REM consolidation."""
    consolidator = REMConsolidator()
    return consolidator.crystallize()


if __name__ == "__main__":
    result = run_rem()
    print(f"REM Complete: {result}")