#!/bin/bash

ruff format src/ tests/
ruff check --fix src/ tests/
PYTHONPATH=src pytest tests/
