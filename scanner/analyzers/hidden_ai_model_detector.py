from __future__ import annotations

import re
from pathlib import Path

from scanner.analyzers.base import AnalyzerContext, iter_text_files, make_finding, read_text_safely

AI_LIBRARIES = {
    "openai",
    "anthropic",
    "google-generativeai",
    "vertexai",
    "azure-ai",
    "langchain",
    "llamaindex",
    "llama-index",
    "transformers",
    "torch",
    "tensorflow",
    "keras",
    "scikit-learn",
    "sklearn",
    "xgboost",
    "lightgbm",
    "sentence-transformers",
    "huggingface_hub",
    "ollama",
    "llama.cpp",
    "onnxruntime",
    "mlflow",
    "wandb",
    "chromadb",
    "pinecone",
    "faiss",
    "weaviate",
    "qdrant",
}
VECTOR_DATABASES = {"chromadb", "pinecone", "faiss", "weaviate", "qdrant"}
MODEL_ARTIFACT_EXTENSIONS = {".pt", ".pth", ".onnx", ".pb", ".h5", ".keras", ".pkl", ".joblib", ".bin", ".safetensors", ".gguf", ".tflite"}
MODEL_ARTIFACT_NAMES = {
    "model.pkl",
    "tokenizer.json",
    "vocab.json",
    "merges.txt",
}
MODEL_NAME_PATTERNS = (
    re.compile(r"^weights\.", re.IGNORECASE),
    re.compile(r"^checkpoint\.", re.IGNORECASE),
)
AI_API_PATTERNS = [
    ("api.openai.com", re.compile(r"api\.openai\.com", re.IGNORECASE)),
    ("anthropic.com", re.compile(r"anthropic\.com", re.IGNORECASE)),
    ("generativelanguage.googleapis.com", re.compile(r"generativelanguage\.googleapis\.com", re.IGNORECASE)),
    ("vertexai", re.compile(r"\bvertexai\b", re.IGNORECASE)),
    ("azure.com/openai", re.compile(r"azure\.com/openai|openai\.azure\.com", re.IGNORECASE)),
    ("huggingface.co", re.compile(r"huggingface\.co", re.IGNORECASE)),
    ("replicate.com", re.compile(r"replicate\.com", re.IGNORECASE)),
    ("ollama", re.compile(r"\bollama\b", re.IGNORECASE)),
    ("localhost:11434", re.compile(r"localhost:11434", re.IGNORECASE)),
    ("chat/completions", re.compile(r"chat/completions", re.IGNORECASE)),
    ("embeddings", re.compile(r"\bembeddings?\b", re.IGNORECASE)),
    ("completion", re.compile(r"\bcompletion\b", re.IGNORECASE)),
    ("prompt", re.compile(r"\b(system_)?prompt\b", re.IGNORECASE)),
    ("temperature", re.compile(r"\btemperature\b", re.IGNORECASE)),
    ("max_tokens", re.compile(r"\bmax_tokens\b", re.IGNORECASE)),
    ("model=", re.compile(r"\bmodel\s*=", re.IGNORECASE)),
    ("gpt-", re.compile(r"\bgpt-[A-Za-z0-9_.-]+", re.IGNORECASE)),
    ("claude-", re.compile(r"\bclaude-[A-Za-z0-9_.-]+", re.IGNORECASE)),
    ("gemini-", re.compile(r"\bgemini-[A-Za-z0-9_.-]+", re.IGNORECASE)),
    ("llama", re.compile(r"\bllama\b", re.IGNORECASE)),
    ("mistral", re.compile(r"\bmistral\b", re.IGNORECASE)),
    ("embedding_model", re.compile(r"\bembedding_model\b", re.IGNORECASE)),
]
DEPENDENCY_FILES = {"requirements.txt", "pyproject.toml", "package.json", "poetry.lock", "Pipfile.lock", "environment.yml", "go.mod"}
AI_DECLARATION_MARKERS = {
    "ai.md",
    "ai-usage.md",
    "ai_architecture.md",
    "ai-architecture.md",
    "model-inventory.md",
    "model_inventory.md",
    "provider-risk.md",
}
DATA_GOVERNANCE_MARKERS = {
    "data-classification.md",
    "data_classification.md",
    "data-flow.md",
    "data_flow.md",
    "privacy.md",
}
STRICT_PROFILES = {"enterprise", "finance-sox", "production-critical"}


def _snippet(line: str) -> str:
    return line.strip()[:240]


def _has_marker(root: Path, markers: set[str]) -> bool:
    for path in root.rglob("*"):
        if path.is_file() and path.name.lower() in markers:
            return True
    return False


def _is_model_config(path: Path) -> bool:
    if path.name.lower() != "config.json":
        return False
    parts = {part.lower() for part in path.parts}
    return bool(parts & {"model", "models", "checkpoint", "checkpoints", "huggingface", "weights"})


def _artifact_reason(path: Path) -> str | None:
    name = path.name.lower()
    if path.suffix.lower() in MODEL_ARTIFACT_EXTENSIONS:
        return f"model artifact extension {path.suffix.lower()}"
    if name in MODEL_ARTIFACT_NAMES:
        return f"model artifact file name {name}"
    if any(pattern.search(name) for pattern in MODEL_NAME_PATTERNS):
        return f"model artifact file name {name}"
    if _is_model_config(path):
        return "model configuration file in model-like directory"
    return None


def _dependency_indicators(text: str) -> list[str]:
    lowered = text.lower()
    indicators = []
    for library in sorted(AI_LIBRARIES):
        pattern = re.compile(rf"(?<![a-z0-9_.-]){re.escape(library.lower())}(?![a-z0-9_.-])")
        if pattern.search(lowered):
            indicators.append(library)
    return indicators


def _decision_for(rule_id: str, profile: str, declared_ai: bool, data_governance: bool) -> tuple[str, str]:
    if rule_id in {"AI-002", "AI-003"} and (profile in STRICT_PROFILES or not declared_ai):
        return "Critical", "Block"
    if rule_id == "AI-004" and not data_governance and profile in STRICT_PROFILES | {"ai-enabled"}:
        return "Critical", "Block"
    if profile in STRICT_PROFILES:
        return "High", "Mandatory Review"
    return "High", "Mandatory Review"


def _ai_finding(
    *,
    rule_id: str,
    title: str,
    description: str,
    file_path: str,
    evidence_type: str,
    evidence_value: str,
    profile: str,
    declared_ai: bool,
    data_governance: bool,
    line_no: int | None = None,
    snippet: str | None = None,
) -> dict:
    severity, decision = _decision_for(rule_id, profile, declared_ai, data_governance)
    finding = make_finding(
        rule_id=rule_id,
        category="AI Model Risk",
        severity=severity,
        title=title,
        description=description,
        file_path=file_path,
        line_start=line_no,
        line_end=line_no,
        evidence_type=evidence_type,
        confidence="High",
        remediation=[
            "Declare AI/model usage in the project documentation",
            "Provide model/provider inventory and data-flow documentation",
            "Obtain Security Architecture, Data Governance, and CISO approval before enterprise use",
            "Re-run the scanner after documentation and approvals are added",
        ],
        owner_role="Security",
    )
    finding.update({
        "decision_impact": decision,
        "requires_approval_from": ["Security Architecture", "Data Governance", "CISO"],
        "evidence_value": evidence_value,
        "evidence_snippet": snippet,
    })
    return finding


def analyze(context: AnalyzerContext) -> dict:
    findings = []
    library_hits = set()
    api_hits = set()
    artifact_hits = []
    declared_ai = _has_marker(context.root, AI_DECLARATION_MARKERS)
    data_governance = _has_marker(context.root, DATA_GOVERNANCE_MARKERS)

    for file_info in context.inventory["files"]:
        rel = file_info["path"]
        path = context.root / rel
        reason = _artifact_reason(path)
        if reason:
            artifact_hits.append(rel)
            findings.append(_ai_finding(
                rule_id="AI-003",
                title="Model artifact or embedded weights detected",
                description=f"A local model artifact was detected without relying on external tooling. Reason: {reason}.",
                file_path=rel,
                evidence_type="model_artifact",
                evidence_value=reason,
                profile=context.profile,
                declared_ai=declared_ai,
                data_governance=data_governance,
            ))
        if path.name in DEPENDENCY_FILES:
            text = read_text_safely(path) or ""
            for library in _dependency_indicators(text):
                library_hits.add(library)
                rule_id = "AI-004" if library in VECTOR_DATABASES else "AI-001"
                findings.append(_ai_finding(
                    rule_id=rule_id,
                    title="AI/ML dependency detected",
                    description=f"Dependency manifest references AI, ML, embedding, or vector infrastructure: {library}.",
                    file_path=rel,
                    evidence_type="dependency",
                    evidence_value=library,
                    profile=context.profile,
                    declared_ai=declared_ai,
                    data_governance=data_governance,
                ))

    for path, text in iter_text_files(context.root):
        rel = path.relative_to(context.root).as_posix()
        for line_no, line in enumerate(text.splitlines(), start=1):
            for indicator, pattern in AI_API_PATTERNS:
                if pattern.search(line):
                    api_hits.add(indicator)
                    rule_id = "AI-004" if indicator in {"embeddings", "embedding_model"} else "AI-002"
                    findings.append(_ai_finding(
                        rule_id=rule_id,
                        title="External AI/API or prompt indicator detected",
                        description=f"Source or configuration references AI API, model, prompt, or inference configuration indicator: {indicator}.",
                        file_path=rel,
                        line_no=line_no,
                        evidence_type="pattern_match",
                        evidence_value=indicator,
                        snippet=_snippet(line),
                        profile=context.profile,
                        declared_ai=declared_ai,
                        data_governance=data_governance,
                    ))

    return {
        "metrics": {
            "ai_declaration_detected": declared_ai,
            "data_governance_detected": data_governance,
            "ai_library_indicators": sorted(library_hits),
            "ai_api_indicators": sorted(api_hits),
            "model_artifact_count": len(artifact_hits),
            "model_artifacts": sorted(artifact_hits),
        },
        "findings": findings,
    }
