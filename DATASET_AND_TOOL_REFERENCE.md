# Croissant-MCP Dataset and Tool Reference

This document provides a comprehensive reference of all datasets and MCP tools available in the Croissant-MCP integration.

## Dataset Locations

### Hugging Face
- **CroissantLLM Bilingual Dataset**
  - URL: https://huggingface.co/datasets/croissantllm/croissant_dataset
  - Description: A bilingual French-English dataset used for training language models with 16.7B rows of text data.
  - License: Apache-2.0
  - Format: Parquet

### Kaggle
- **MNIST Handwritten Digits**
  - URL: https://www.kaggle.com/datasets/hojjatk/mnist-dataset
  - Description: The MNIST database of handwritten digits with 60,000 training examples and 10,000 test examples.
  - License: CC0: Public Domain
  - Format: CSV

### OpenML
- **Iris Dataset**
  - URL: https://www.openml.org/d/61
  - Description: The Iris dataset is a multivariate dataset introduced by Ronald Fisher as an example of discriminant analysis.
  - License: Public Domain
  - Format: ARFF

### Harvard Dataverse
- **Titanic Passengers**
  - URL: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MXWJYH
  - Description: This dataset provides information on the fate of passengers on the Titanic, including age, sex, class, and survival status.
  - License: CC0 1.0
  - Format: CSV

### MLCommons
- **PASS Dataset**
  - URL: https://www.robots.ox.ac.uk/~vgg/data/pass/
  - Description: PASS is a large-scale image dataset that does not include any humans.
  - License: CC BY 4.0
  - Format: CSV, TAR

## MCP Server Tools

### Resources

#### `datasets://list`
Returns a list of all available datasets in the index.

**Example Response:**
```json
[
  {
    "id": "croissantllm-croissant-dataset",
    "name": "CroissantLLM: A Truly Bilingual French-English Language Model",
    "description": "A bilingual French-English dataset used for training language models with 16.7B rows of text data."
  },
  {
    "id": "kaggle-mnist",
    "name": "MNIST Handwritten Digits",
    "description": "The MNIST database of handwritten digits with 60,000 training examples and 10,000 test examples."
  }
]
```

#### `datasets://{dataset_id}`
Returns detailed information about a specific dataset.

**Example Request:** `datasets://croissantllm-croissant-dataset`

**Example Response:**
```json
{
  "name": "CroissantLLM: A Truly Bilingual French-English Language Model",
  "description": "A bilingual French-English dataset used for training language models with 16.7B rows of text data.",
  "license": "Apache-2.0",
  "url": "https://huggingface.co/datasets/croissantllm/croissant_dataset",
  "provider": "Hugging Face",
  "distribution": [
    {
      "@type": "FileObject",
      "@id": "dataset-parquet",
      "contentUrl": "https://huggingface.co/datasets/croissantllm/croissant_dataset",
      "encodingFormat": "application/parquet"
    }
  ],
  "keywords": ["text", "bilingual", "french", "english", "language model", "nlp"]
}
```

### Tools

#### `search_datasets(query)`
Basic search for datasets matching the query.

**Parameters:**
- `query`: Text to search for in dataset name and description

**Example Request:**
```python
search_datasets(query="image")
```

**Example Response:**
```json
[
  {
    "id": "kaggle-mnist",
    "name": "MNIST Handwritten Digits",
    "description": "The MNIST database of handwritten digits with 60,000 training examples and 10,000 test examples.",
    "url": "https://www.kaggle.com/datasets/hojjatk/mnist-dataset",
    "license": "CC0: Public Domain"
  },
  {
    "id": "simple-pass",
    "name": "PASS Dataset",
    "description": "PASS is a large-scale image dataset that does not include any humans.",
    "url": "https://www.robots.ox.ac.uk/~vgg/data/pass/",
    "license": "https://creativecommons.org/licenses/by/4.0/"
  }
]
```

#### `advanced_search(query, provider, data_format, license_type, keywords, sort_by, page, page_size)`
Advanced search for datasets with filtering, sorting, and pagination.

**Parameters:**
- `query`: Text to search for in name and description
- `provider`: Filter by data provider (e.g., "Hugging Face", "Kaggle")
- `data_format`: Filter by data format (e.g., "csv", "parquet")
- `license_type`: Filter by license type
- `keywords`: Comma-separated list of keywords to filter by
- `sort_by`: Sort results by ("relevance", "name", "provider")
- `page`: Page number for pagination
- `page_size`: Number of results per page

**Example Request:**
```python
advanced_search(
    query="",
    provider="Kaggle",
    data_format="csv",
    license_type="",
    keywords="computer vision",
    sort_by="name",
    page=1,
    page_size=10
)
```

**Example Response:**
```json
{
  "results": [
    {
      "id": "kaggle-mnist",
      "name": "MNIST Handwritten Digits",
      "description": "The MNIST database of handwritten digits with 60,000 training examples and 10,000 test examples.",
      "url": "https://www.kaggle.com/datasets/hojjatk/mnist-dataset",
      "license": "CC0: Public Domain",
      "provider": "Kaggle",
      "keywords": ["computer vision", "image classification", "handwritten digits"]
    }
  ],
  "total_count": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

#### `get_search_options()`
Get available options for search filters.

**Example Response:**
```json
{
  "providers": ["Hugging Face", "Kaggle", "OpenML", "Harvard Dataverse", "MLCommons"],
  "formats": ["application/parquet", "text/csv", "application/arff", "application/x-tar"],
  "licenses": ["Apache-2.0", "CC0: Public Domain", "Public Domain", "CC0 1.0", "https://creativecommons.org/licenses/by/4.0/"],
  "keywords": ["text", "bilingual", "french", "english", "language model", "nlp", "computer vision", "image classification", "handwritten digits", "classification", "small", "multivariate", "titanic", "survival", "demographics", "social science", "images", "no humans"],
  "sort_options": ["relevance", "name", "provider"]
}
```

#### `add_dataset(dataset_id, metadata)`
Add a new dataset to the index.

**Parameters:**
- `dataset_id`: Unique identifier for the dataset
- `metadata`: JSON string containing dataset metadata

**Example Request:**
```python
add_dataset(
    dataset_id="new-dataset",
    metadata=json.dumps({
        "name": "New Dataset",
        "description": "Description of the new dataset",
        "license": "MIT",
        "url": "https://example.com/dataset",
        "provider": "Example Provider",
        "distribution": [
            {
                "@type": "FileObject",
                "@id": "data.csv",
                "contentUrl": "https://example.com/dataset/data.csv",
                "encodingFormat": "text/csv"
            }
        ],
        "keywords": ["example", "new", "dataset"]
    })
)
```

**Example Response:**
```json
{
  "success": true,
  "message": "Dataset new-dataset added to index"
}
```

## Integration with LLM Applications

The Croissant-MCP server can be integrated with LLM-powered applications to provide context about datasets. Here's how to use it:

1. Connect to the MCP server at `http://localhost:8000`
2. Use the MCP client to query datasets:
   ```python
   from mcp.client import MCPClient
   
   client = MCPClient("http://localhost:8000")
   
   # List all datasets
   datasets = client.get_resource("datasets://list")
   
   # Get details about a specific dataset
   mnist_dataset = client.get_resource("datasets://kaggle-mnist")
   
   # Search for datasets
   search_results = client.call_tool("search_datasets", {"query": "image"})
   ```

3. Integrate dataset context into your LLM application:
   ```python
   # Example: Adding dataset context to an LLM prompt
   dataset_info = client.get_resource("datasets://kaggle-mnist")
   
   prompt = f"""
   Using the following dataset information:
   {dataset_info}
   
   Write code to load and visualize this dataset.
   """
   
   # Send prompt to your LLM
   ```
