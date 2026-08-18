"""
Local / Colab QLoRA Fine-tuning script for Qwen 2.5 (7B or 3B or 14B) on extraction data.

Prerequisites (install in your GPU / Colab environment):
    pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
    pip install --no-deps "xformers<0.0.29" "trl<0.9.0" peft accelerate bitsandbytes datasets

Run:
    python scripts/train_qwen_lora.py --model_name "unsloth/Qwen2.5-7B-Instruct-bnb-4bit"
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

def train(
    model_name: str = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit",
    max_seq_length: int = 4096,
    train_path: str = "training_data/train.jsonl",
    output_dir: str = "models/qwen2.5_doc_extractor_lora",
    epochs: int = 3,
    batch_size: int = 2,
    learning_rate: float = 2e-4,
):
    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import load_dataset
    except ImportError:
        print("""
[Error] Unsloth or training dependencies not installed.
Please install them using:
    pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
    pip install --no-deps trl peft accelerate bitsandbytes datasets
        """)
        return

    print(f"=== Starting QLoRA Fine-Tuning ===")
    print(f"Base Model      : {model_name}")
    print(f"Max Seq Length  : {max_seq_length}")
    print(f"Training Data   : {train_path}")
    print(f"Output Directory: {output_dir}")

    # 1. Load Model & Tokenizer in 4-bit
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
    )

    # 2. Add LoRA Adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=32,
        lora_dropout=0,  # Optimized to 0 for Unsloth
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    # 3. Format dataset using Qwen Chat Template
    def formatting_prompts_func(examples):
        convos = examples["messages"]
        texts = [
            tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False)
            for convo in convos
        ]
        return {"text": texts}

    dataset = load_dataset("json", data_files={"train": train_path})
    dataset = dataset.map(formatting_prompts_func, batched=True)

    # 4. Set Trainer Arguments
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            warmup_ratio=0.1,
            num_train_epochs=epochs,
            learning_rate=learning_rate,
            fp16=not FastLanguageModel.is_bfloat16_supported(),
            bf16=FastLanguageModel.is_bfloat16_supported(),
            logging_steps=5,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="cosine",
            seed=42,
            output_dir=output_dir,
            report_to="none",
        ),
    )

    # 5. Execute Training
    print("\n--- Training in progress ---")
    trainer.train()

    # 6. Save LoRA Adapters
    print(f"\n--- Saving Fine-Tuned Model to {output_dir} ---")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    # 7. Optionally export to GGUF (for Ollama)
    gguf_dir = Path(output_dir) / "gguf"
    print(f"To export for Ollama: model.save_pretrained_gguf('{gguf_dir}', tokenizer, quantization_method='q4_k_m')")
    print("\n=== Fine-Tuning Completed Successfully! ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", default="unsloth/Qwen2.5-7B-Instruct-bnb-4bit")
    parser.add_argument("--train_path", default="training_data/train.jsonl")
    parser.add_argument("--output_dir", default="models/qwen2.5_doc_extractor_lora")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()

    train(
        model_name=args.model_name,
        train_path=args.train_path,
        output_dir=args.output_dir,
        epochs=args.epochs,
    )
