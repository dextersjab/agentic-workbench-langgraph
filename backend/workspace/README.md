# Workspace Directory

This directory is used by the fs-agent workflow for file operations.

## Sample Files

This directory contains sample files that the fs-agent can read, write, and manipulate:

- `sample.txt` - A simple text file
- `data.json` - Sample JSON data
- `notes.md` - Markdown notes file

## Usage

The fs-agent workflow operates within this directory by default. Users can:

1. List files in this directory
2. Read file contents
3. Create new files (in write mode)
4. Delete files (in write mode)

The agent determines whether to operate in read-only or write mode based on the user's request.