# Hidden AI / Model Detection Specification

## Purpose

The hidden AI/model detector identifies undeclared AI libraries, model artifacts, external AI APIs, prompt configuration, embeddings, vector databases, and local inference indicators using deterministic static analysis.

The detector does not import project code, execute models, call providers, generate embeddings, or use AI.

## Analyzer

```text
scanner/analyzers/hidden_ai_model_detector.py
```

Analyzer ID:

```text
hidden_ai_model_detector
```

## Detection Sources

- File names and extensions
- Dependency manifests
- Code and configuration text
- Model-like directories

## AI/ML Libraries

Examples include:

- `openai`
- `anthropic`
- `google-generativeai`
- `vertexai`
- `azure-ai`
- `langchain`
- `llamaindex`
- `transformers`
- `torch`
- `tensorflow`
- `keras`
- `scikit-learn`
- `xgboost`
- `lightgbm`
- `sentence-transformers`
- `huggingface_hub`
- `ollama`
- `onnxruntime`
- `mlflow`
- `wandb`
- `chromadb`
- `pinecone`
- `faiss`
- `weaviate`
- `qdrant`

## Model Artifacts

Examples include:

- `.pt`
- `.pth`
- `.onnx`
- `.pb`
- `.h5`
- `.keras`
- `.pkl`
- `.joblib`
- `.bin`
- `.safetensors`
- `.gguf`
- `.tflite`
- `model.pkl`
- `weights.*`
- `checkpoint.*`
- `tokenizer.json`
- `vocab.json`
- `merges.txt`
- model-directory `config.json`

## API and Prompt Indicators

Examples include:

- `api.openai.com`
- `anthropic.com`
- `generativelanguage.googleapis.com`
- `vertexai`
- `azure.com/openai`
- `huggingface.co`
- `replicate.com`
- `localhost:11434`
- `chat/completions`
- `embeddings`
- `completion`
- `prompt`
- `system_prompt`
- `temperature`
- `max_tokens`
- `model=`
- `gpt-`
- `claude-`
- `gemini-`
- `llama`
- `mistral`
- `embedding_model`

## Decision Behavior

- External AI API indicators are critical and blocking in strict profiles when undeclared.
- Local model artifacts are critical and blocking in strict profiles when undeclared.
- AI/ML dependencies require mandatory review.
- Embedding or vector database usage requires data governance review and may block strict profiles without data governance documentation.

Required review:

- Security Architecture
- Data Governance
- CISO

## Evidence

Findings include:

- Rule ID
- File path
- Line number where available
- Matched indicator
- Evidence type
- Evidence snippet where safe
- Confidence
- Required approval roles
- Remediation
