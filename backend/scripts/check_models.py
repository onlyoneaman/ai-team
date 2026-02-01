#!/usr/bin/env python3
"""Check available OpenAI models."""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

models = client.models.list()

print("Available models:\n")
for model in sorted(models.data, key=lambda m: m.id):
    print(f"  {model.id}")
