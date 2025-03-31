# Croissant-MCP Integration

A proof-of-concept MCP server that indexes Croissant datasets across different data vendors (Kaggle, Hugging Face, OpenML, Dataverse).

## Overview

This project creates a Model Context Protocol (MCP) server that hosts an index of Croissant datasets from various data vendors. Users can easily search and add context of these datasets to their LLM-powered applications.

## Project Structure

```
croissant-mcp-integration/
├── main.py                 # Entry point to run the server
├── src/
│   ├── server.py           # MCP server implementation with endpoints and tools
│   ├── dataset_index.py    # Dataset indexing functionality
│   └── search.py           # Advanced search implementation
```

## Features

- Dataset indexing from multiple platforms (Hugging Face, Kaggle, OpenML, Dataverse)
- Basic and advanced search functionality
- Filtering by provider, format, license, and keywords
- Pagination and sorting of search results

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the server:
```bash
python main.py
```

The server will start on http://localhost:8000 by default.

## MCP Resources and Tools

The server exposes the following MCP resources and tools:

### Resources
- `datasets://list` - List all available datasets
- `datasets://{dataset_id}` - Get information about a specific dataset

### Tools
- `search_datasets(query)` - Basic search for datasets
- `advanced_search(query, provider, data_format, license_type, keywords, sort_by, page, page_size)` - Advanced search with filtering
- `get_search_options()` - Get available options for search filters
- `add_dataset(dataset_id, metadata)` - Add a new dataset to the index

## Example Datasets

The server comes pre-loaded with example datasets from:
- Hugging Face: CroissantLLM bilingual dataset
- Kaggle: MNIST handwritten digits
- OpenML: Iris dataset
- Dataverse: Titanic passengers dataset
- MLCommons: PASS image dataset
