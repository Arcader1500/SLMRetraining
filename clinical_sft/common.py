"""Shared data validation, formatting, and metrics (stdlib only until model loading)."""

import hashlib
import json
from pathlib import Path

MODEL_ID = "google/gemma-3-270m-it"
DATASET_ID = "AmareshHebbar/clinical-summarizer-sft"
FORMAT_INSTRUCTION = (
    "Extract the clinical facts into the dataset's structured JSON report. "
    "Return only a JSON object, without markdown. Preserve facts from the note; "
    "use the string 'None' only for information not provided."
)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_data(directory):
    directory = Path(directory)
    manifest = read_json(directory / "manifest.json")
    if manifest["format_instruction"] != FORMAT_INSTRUCTION:
        raise ValueError("Prompt code changed since preparation; prepare a new dataset directory")
    for name, digest in manifest["files"].items():
        if file_hash(directory / name) != digest:
            raise ValueError(f"Prepared data changed: {name}")
    return manifest


def reject_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"Duplicate JSON key: {key}")
        obj[key] = value
    return obj


def parse_object(text, *, allow_control_characters=False):
    def reject_constant(value):
        raise ValueError(f"Non-finite JSON constant: {value}")

    obj = json.loads(text, strict=not allow_control_characters,
                     object_pairs_hook=reject_duplicates, parse_constant=reject_constant)
    if not isinstance(obj, dict) or not obj:
        raise ValueError("Expected a nonempty JSON object")
    return obj


def clean_reference(text):
    """Only repair literal control characters inside strings; never guess missing syntax."""
    try:
        obj = parse_object(text)
        status = "valid"
    except ValueError:
        obj = parse_object(text, allow_control_characters=True)
        status = "escaped_control_characters"
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")), status


def prompt_messages(system, note):
    return [{"role": "user", "content": f"{system}\n\n{FORMAT_INSTRUCTION}\n\nClinical note:\n{note}"}]


def encode_example(tokenizer, case):
    """Mask the user turn and train on the entire assistant answer and turn terminator."""
    messages = prompt_messages(case["system"], case["note"])
    prefix = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    text = tokenizer.apply_chat_template(
        messages + [{"role": "assistant", "content": case["reference"]}], tokenize=False)
    if not text.startswith(prefix) or not text[len(prefix):].startswith(case["reference"]):
        raise ValueError("Chat template no longer gives the expected assistant boundary")
    encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True, truncation=False)
    offsets = encoded.pop("offset_mapping")
    start, end = len(prefix), len(prefix) + len(case["reference"])
    answer_positions = [i for i, (a, b) in enumerate(offsets) if b > start and a < end and b > a]
    if not answer_positions or offsets[answer_positions[0]][0] < start:
        raise ValueError("Cannot isolate assistant tokens without a boundary-spanning token")
    first = answer_positions[0]
    ids = encoded["input_ids"]
    labels = [-100] * first + ids[first:]
    if first == 0 or not any(label != -100 for label in labels[1:]):
        raise ValueError("No assistant next-token labels")
    encoded["labels"] = labels
    return encoded


def pad_examples(features, pad_token_id):
    """Right-pad inputs; ignore padding in loss even when pad and EOS IDs are equal."""
    width = max(len(row["input_ids"]) for row in features)
    result = {key: [] for key in ("input_ids", "attention_mask", "labels")}
    for row in features:
        size = len(row["input_ids"])
        result["input_ids"].append(row["input_ids"] + [pad_token_id] * (width - size))
        result["attention_mask"].append([1] * size + [0] * (width - size))
        result["labels"].append(row["labels"] + [-100] * (width - size))
    return result


def strip_fences(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.rstrip().endswith("```"):
        text = text.rstrip()[:-3]
    return text.strip()


def clinical_values(obj, path=""):
    """Compare unique non-placeholder values by field, ignoring array ordering/counts."""
    values = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            values |= clinical_values(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for value in obj:
            values |= clinical_values(value, path)
    else:
        normalized = " ".join(str(obj).casefold().split())
        if obj is not None and normalized not in ("", "none", "null", "unknown", "n/a"):
            values.add((path, normalized))
    return values


def json_keys(obj, path=""):
    keys = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            name = f"{path}.{key}" if path else key
            keys.add(name)
            keys |= json_keys(value, name)
    elif isinstance(obj, list):
        for value in obj:
            keys |= json_keys(value, path)
    return keys


def score_response(text, reference):
    expected = parse_object(reference)
    expected_values = clinical_values(expected)
    try:
        actual = parse_object(strip_fences(text))
        error = None
    except ValueError as exc:
        actual, error = {}, str(exc)
    actual_values = clinical_values(actual)
    overlap = len(actual_values & expected_values)
    precision = overlap / len(actual_values) if actual_values else 0.0
    recall = overlap / len(expected_values) if expected_values else 0.0
    return {"valid_json": error is None, "json_error": error,
            "exact_key_match": error is None and json_keys(actual) == json_keys(expected),
            "non_placeholder_values": len(actual_values),
            "reference_non_placeholder_values": len(expected_values),
            "matched_values": overlap, "value_precision": precision, "value_recall": recall,
            "value_f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0}


def load_model(manifest, precision="auto"):
    import torch
    from transformers import AutoModelForCausalLM

    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Require native BF16 support; emulation reports on T4 can be misleading.
    native_bf16 = (device == "cuda" and torch.cuda.get_device_capability()[0] >= 8
                   and torch.cuda.is_bf16_supported())
    if precision == "bf16" and not native_bf16:
        raise ValueError("BF16 requested without native GPU support; use --precision fp32")
    dtype = torch.bfloat16 if precision != "fp32" and native_bf16 else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        manifest["model"], revision=manifest["model_revision"], torch_dtype=dtype,
        attn_implementation="sdpa").to(device)
    return model, {"device": device, "dtype": str(dtype),
                   "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None}
