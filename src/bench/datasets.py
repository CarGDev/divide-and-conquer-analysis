"""Dataset generators for benchmarking."""
from typing import List, Literal, Optional
import random

DatasetType = Literal["sorted", "reverse", "random", "nearly_sorted", "duplicates_heavy"]


def generate_dataset(
    size: int,
    dataset_type: DatasetType,
    seed: Optional[int] = None,
) -> List[int]:
    """
    Generate a dataset of specified type and size.
    
    Args:
        size: Number of elements in the dataset
        dataset_type: Type of dataset to generate
        seed: Random seed for reproducibility
    
    Returns:
        List of integers with the specified characteristics
    """
    if seed is not None:
        random.seed(seed)
    
    if dataset_type == "sorted":
        return list(range(size))
    
    elif dataset_type == "reverse":
        return list(range(size - 1, -1, -1))
    
    elif dataset_type == "random":
        return [random.randint(0, size * 10) for _ in range(size)]
    
    elif dataset_type == "nearly_sorted":
        arr = list(range(size))
        # Perform a few swaps (about 1% of elements)
        num_swaps = max(1, size // 100)
        for _ in range(num_swaps):
            i = random.randint(0, size - 1)
            j = random.randint(0, size - 1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr
    
    elif dataset_type == "duplicates_heavy":
        # Generate array with many duplicate values
        # Use only a small set of distinct values
        distinct_values = max(1, size // 10)
        return [random.randint(0, distinct_values - 1) for _ in range(size)]
    
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")

