#!/usr/bin/env python3
"""
Fine-tune TinyLlama for Inner Arianna using LoRA
"""
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from datasets import Dataset
import json
import config

def setup_model_and_tokenizer():
    """Setup model and tokenizer with LoRA"""
    print("🧠 Inner Arianna: Setting up model and tokenizer...")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load base model
    print("   Loading TinyLlama base model...")
    model = AutoModelForCausalLM.from_pretrained(
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        torch_dtype=torch.float16,
        device_map="auto"
    )

    # Prepare model for training
    model = prepare_model_for_kbit_training(model)

    # Setup LoRA configuration
    print("   Configuring LoRA...")
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=config.LORA_RANK,
        lora_alpha=config.LORA_ALPHA,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
    )

    # Apply LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    print("   ✅ Model ready for fine-tuning")
    return model, tokenizer

def prepare_dataset(tokenizer):
    """Prepare dataset for training"""
    print("📊 Inner Arianna: Preparing dataset...")

    # Load training data
    with open("training_data.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    print(f"   Loaded {len(data)} training examples")

    # Format data with Inner Arianna prompt
    formatted_data = []
    for text in data:
        if text.strip():  # Only non-empty texts
            formatted_text = config.INNER_ARIANNA_PROMPT + "\n\n" + text
            formatted_data.append({"text": formatted_text})

    print(f"   Formatted {len(formatted_data)} examples")

    # Create dataset
    dataset = Dataset.from_list(formatted_data)

    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=config.MAX_LENGTH,
            padding="max_length"
        )

    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )

    print(f"   ✅ Dataset ready: {len(tokenized_dataset)} examples")
    return tokenized_dataset

def fine_tune():
    """Fine-tune the model"""
    print("🚀 Inner Arianna: Starting fine-tuning...")

    # Setup model
    model, tokenizer = setup_model_and_tokenizer()

    # Prepare dataset
    dataset = prepare_dataset(tokenizer)

    # Training arguments
    training_args = TrainingArguments(
        output_dir="./inner_arianna_model",
        num_train_epochs=config.MAX_EPOCHS,
        per_device_train_batch_size=config.BATCH_SIZE,
        gradient_accumulation_steps=config.GRADIENT_ACCUMULATION_STEPS,
        warmup_steps=100,
        learning_rate=config.LEARNING_RATE,
        fp16=True,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        report_to="none"
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator
    )

    # Train
    print("   🧠 Training Inner Arianna...")
    trainer.train()

    # Save
    print("   💾 Saving model...")
    trainer.save_model()
    tokenizer.save_pretrained("./inner_arianna_model")

    print("✅ Inner Arianna: Fine-tuning complete!")
    print("   Model saved to: ./inner_arianna_model")

if __name__ == "__main__":
    fine_tune()
