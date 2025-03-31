"""
Advanced search functionality for Croissant datasets
"""
import json
from typing import Dict, List, Any, Optional, Tuple
from dataset_index import CroissantDatasetIndex

class CroissantSearch:
    """Advanced search functionality for Croissant datasets"""
    
    def __init__(self, dataset_index: CroissantDatasetIndex):
        self.dataset_index = dataset_index
        
    def search(self, 
               query: str = "", 
               provider: Optional[str] = None,
               data_format: Optional[str] = None,
               license_type: Optional[str] = None,
               keywords: Optional[List[str]] = None,
               sort_by: str = "relevance",
               page: int = 1,
               page_size: int = 10) -> Tuple[List[Dict[str, Any]], int]:
        """
        Advanced search for datasets with filtering, sorting, and pagination
        
        Args:
            query: Text to search for in name and description
            provider: Filter by data provider (e.g., "Hugging Face", "Kaggle")
            data_format: Filter by data format (e.g., "csv", "parquet")
            license_type: Filter by license type
            keywords: Filter by keywords
            sort_by: Sort results by ("relevance", "name", "provider")
            page: Page number for pagination
            page_size: Number of results per page
            
        Returns:
            Tuple of (list of matching datasets, total count)
        """
        if query:
            results = self.dataset_index.search(query)
        else:
            results = self.dataset_index.list_datasets()
            for i, result in enumerate(results):
                dataset_id = result["id"]
                full_dataset = self.dataset_index.get_dataset(dataset_id)
                if full_dataset:
                    results[i] = {
                        "id": dataset_id,
                        "name": full_dataset.get("name", ""),
                        "description": full_dataset.get("description", ""),
                        "url": full_dataset.get("url", ""),
                        "license": full_dataset.get("license", "")
                    }
        
        filtered_results = []
        for dataset in results:
            dataset_id = dataset["id"]
            full_dataset = self.dataset_index.get_dataset(dataset_id)
            
            if not full_dataset:
                continue
                
            if provider and full_dataset.get("provider", "").lower() != provider.lower():
                continue
                
            if license_type and full_dataset.get("license", "").lower() != license_type.lower():
                continue
                
            if data_format:
                distribution = full_dataset.get("distribution", [])
                format_match = False
                for dist in distribution:
                    if data_format.lower() in dist.get("encodingFormat", "").lower():
                        format_match = True
                        break
                if not format_match:
                    continue
            
            if keywords:
                dataset_keywords = full_dataset.get("keywords", [])
                if not all(kw.lower() in [k.lower() for k in dataset_keywords] for kw in keywords):
                    continue
            
            filtered_results.append({
                "id": dataset_id,
                "name": full_dataset.get("name", ""),
                "description": full_dataset.get("description", ""),
                "url": full_dataset.get("url", ""),
                "license": full_dataset.get("license", ""),
                "provider": full_dataset.get("provider", ""),
                "keywords": full_dataset.get("keywords", [])
            })
        
        if sort_by == "name":
            filtered_results.sort(key=lambda x: x.get("name", "").lower())
        elif sort_by == "provider":
            filtered_results.sort(key=lambda x: x.get("provider", "").lower())
        
        total_count = len(filtered_results)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = filtered_results[start_idx:end_idx]
        
        return paginated_results, total_count
    
    def get_available_providers(self) -> List[str]:
        """Get a list of all available data providers"""
        providers = set()
        for dataset_id in self.dataset_index.datasets:
            dataset = self.dataset_index.get_dataset(dataset_id)
            if dataset and "provider" in dataset:
                providers.add(dataset["provider"])
        return sorted(list(providers))
    
    def get_available_formats(self) -> List[str]:
        """Get a list of all available data formats"""
        formats = set()
        for dataset_id in self.dataset_index.datasets:
            dataset = self.dataset_index.get_dataset(dataset_id)
            if dataset and "distribution" in dataset:
                for dist in dataset["distribution"]:
                    if "encodingFormat" in dist:
                        formats.add(dist["encodingFormat"])
        return sorted(list(formats))
    
    def get_available_licenses(self) -> List[str]:
        """Get a list of all available licenses"""
        licenses = set()
        for dataset_id in self.dataset_index.datasets:
            dataset = self.dataset_index.get_dataset(dataset_id)
            if dataset and "license" in dataset:
                licenses.add(dataset["license"])
        return sorted(list(licenses))
    
    def get_all_keywords(self) -> List[str]:
        """Get a list of all keywords used across datasets"""
        keywords = set()
        for dataset_id in self.dataset_index.datasets:
            dataset = self.dataset_index.get_dataset(dataset_id)
            if dataset and "keywords" in dataset:
                for keyword in dataset["keywords"]:
                    keywords.add(keyword)
        return sorted(list(keywords))
