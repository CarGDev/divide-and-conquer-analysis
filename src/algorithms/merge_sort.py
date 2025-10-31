"""Merge Sort implementation with instrumentation support."""
from typing import List, Optional, Callable


def merge_sort(
    arr: List[int],
    instrument: Optional[Callable[[str], None]] = None,
) -> List[int]:
    """
    Sort array using merge sort algorithm.
    
    Args:
        arr: List of integers to sort
        instrument: Optional callback function for counting operations.
                    Called with 'comparison' or 'swap' strings.
    
    Returns:
        Sorted copy of the input array.
    """
    if len(arr) <= 1:
        return arr[:]
    
    def _merge(left: List[int], right: List[int]) -> List[int]:
        """Merge two sorted arrays."""
        result: List[int] = []
        i, j = 0, 0
        
        while i < len(left) and j < len(right):
            if instrument:
                instrument("comparison")
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    def _merge_sort_recursive(arr_inner: List[int]) -> List[int]:
        """Recursive merge sort helper."""
        if len(arr_inner) <= 1:
            return arr_inner[:]
        
        mid = len(arr_inner) // 2
        left = _merge_sort_recursive(arr_inner[:mid])
        right = _merge_sort_recursive(arr_inner[mid:])
        return _merge(left, right)
    
    return _merge_sort_recursive(arr)

