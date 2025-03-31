import json
import os
from typing import Dict, List, Any, Optional

class CroissantDatasetIndex:
    """A simple index for Croissant datasets"""
    
    def __init__(self):
        self.datasets = {}
        
    def add_dataset(self, dataset_id: str, metadata: Dict[str, Any]) -> None:
        """Add a dataset to the index"""
        self.datasets[dataset_id] = metadata
        
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get a dataset from the index by ID"""
        return self.datasets.get(dataset_id)
        
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for datasets matching the query"""
        results = []
        query = query.lower()
        
        for dataset_id, dataset in self.datasets.items():
            if (query in dataset.get("name", "").lower() or 
                query in dataset.get("description", "").lower() or
                any(query in keyword.lower() for keyword in dataset.get("keywords", []))):
                
                results.append({
                    "id": dataset_id,
                    "name": dataset.get("name", ""),
                    "description": dataset.get("description", ""),
                    "url": dataset.get("url", ""),
                    "license": dataset.get("license", "")
                })
                
        return results
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets in the index"""
        return [
            {
                "id": dataset_id,
                "name": dataset.get("name", ""),
                "description": dataset.get("description", "")
            }
            for dataset_id, dataset in self.datasets.items()
        ]
    
    def load_example_datasets(self) -> None:
        """Load some example Croissant datasets into the index"""
        self.add_dataset("croissantllm-croissant-dataset", {
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
        })
        
        self.add_dataset("kaggle-mnist", {
            "name": "MNIST Handwritten Digits",
            "description": "The MNIST database of handwritten digits with 60,000 training examples and 10,000 test examples.",
            "license": "CC0: Public Domain",
            "url": "https://www.kaggle.com/datasets/hojjatk/mnist-dataset",
            "provider": "Kaggle",
            "distribution": [
                {
                    "@type": "FileObject",
                    "@id": "train.csv",
                    "contentUrl": "https://www.kaggle.com/datasets/hojjatk/mnist-dataset",
                    "encodingFormat": "text/csv"
                },
                {
                    "@type": "FileObject",
                    "@id": "test.csv",
                    "contentUrl": "https://www.kaggle.com/datasets/hojjatk/mnist-dataset",
                    "encodingFormat": "text/csv"
                }
            ],
            "keywords": ["computer vision", "image classification", "handwritten digits"]
        })
        
        self.add_dataset("openml-iris", {
            "name": "Iris",
            "description": "The Iris dataset is a multivariate dataset introduced by Ronald Fisher as an example of discriminant analysis.",
            "license": "Public Domain",
            "url": "https://www.openml.org/d/61",
            "provider": "OpenML",
            "distribution": [
                {
                    "@type": "FileObject",
                    "@id": "iris.arff",
                    "contentUrl": "https://www.openml.org/data/download/61/dataset_61_iris.arff",
                    "encodingFormat": "application/arff"
                }
            ],
            "keywords": ["classification", "small", "multivariate"]
        })
        
        self.add_dataset("dataverse-titanic", {
            "name": "Titanic Passengers",
            "description": "This dataset provides information on the fate of passengers on the Titanic, including age, sex, class, and survival status.",
            "license": "CC0 1.0",
            "url": "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MXWJYH",
            "provider": "Harvard Dataverse",
            "distribution": [
                {
                    "@type": "FileObject",
                    "@id": "titanic3.csv",
                    "contentUrl": "https://dataverse.harvard.edu/api/access/datafile/3901719",
                    "encodingFormat": "text/csv"
                }
            ],
            "keywords": ["titanic", "survival", "demographics", "social science"]
        })
        
        self.add_dataset("simple-pass", {
            "name": "PASS Dataset",
            "description": "PASS is a large-scale image dataset that does not include any humans.",
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "url": "https://www.robots.ox.ac.uk/~vgg/data/pass/",
            "provider": "MLCommons",
            "distribution": [
                {
                    "@type": "FileObject",
                    "@id": "metadata.csv",
                    "contentUrl": "https://zenodo.org/record/6615455/files/pass_metadata.csv",
                    "encodingFormat": "text/csv"
                },
                {
                    "@type": "FileObject",
                    "@id": "pass9",
                    "contentUrl": "https://zenodo.org/record/6615455/files/PASS.9.tar",
                    "encodingFormat": "application/x-tar"
                }
            ],
            "keywords": ["images", "computer vision", "no humans"]
        })
