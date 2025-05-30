#!/bin/bash
# Helper script to run PlotPOP backend
cd backend
uvicorn main:app --reload 