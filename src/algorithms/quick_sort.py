"""Quick Sort implementation with pivot strategies and instrumentation support."""
from typing import List, Optional, Callable, Literal
import random

PivotStrategy = Literal["first", "last", "median_of_three", "random"]


def quick_sort(
    arr: List[int],
    pivot_strategy: PivotStrategy = "first",
    instrument: Optional[Callable[[str], None]] = None,
    seed: Optional[int] = None,
) -> List[int]:
    """
    Sort array using quick sort algorithm.
    
    Args:
        arr: List of integers to sort
        pivot_strategy: Strategy for selecting pivot ('first', 'last', 
                        'median_of_three', 'random')
        instrument: Optional callback function for counting operations.
                    Called with 'comparison' or 'swap' strings.
        seed: Optional random seed for 'random' pivot strategy
    
    Returns:
        Sorted copy of the input array.
    """
    if len(arr) <= 1:
        return arr[:]
    
    arr_copy = arr[:]
    
    def _choose_pivot(left: int, right: int) -> int:
        """Choose pivot index based on strategy."""
        if pivot_strategy == "first":
            return left
        elif pivot_strategy == "last":
            return right
        elif pivot_strategy == "median_of_three":
            mid = (left + right) // 2
            if instrument:
                instrument("comparison")
                instrument("comparison")
            if arr_copy[left] <= arr_copy[mid] <= arr_copy[right] or \
               arr_copy[right] <= arr_copy[mid] <= arr_copy[left]:
                return mid
            elif arr_copy[mid] <= arr_copy[left] <= arr_copy[right] or \
                 arr_copy[right] <= arr_copy[left] <= arr_copy[mid]:
                return left
            else:
                return right
        elif pivot_strategy == "random":
            return random.randint(left, right)
        else:
            raise ValueError(f"Unknown pivot strategy: {pivot_strategy}")
    
    def _partition(left: int, right: int, pivot_idx: int) -> int:
        """Partition array around pivot and return final pivot position."""
        pivot_val = arr_copy[pivot_idx]
        
        # Move pivot to end
        arr_copy[pivot_idx], arr_copy[right] = arr_copy[right], arr_copy[pivot_idx]
        if instrument:
            instrument("swap")
        
        store_idx = left
        for i in range(left, right):
            if instrument:
                instrument("comparison")
            if arr_copy[i] <= pivot_val:
                if i != store_idx:
                    arr_copy[i], arr_copy[store_idx] = arr_copy[store_idx], arr_copy[i]
                    if instrument:
                        instrument("swap")
                store_idx += 1
        
        # Move pivot to final position
        arr_copy[store_idx], arr_copy[right] = arr_copy[right], arr_copy[store_idx]
        if instrument:
            instrument("swap")
        
        return store_idx
    
    def _quick_sort_recursive(left: int, right: int) -> None:
        """Recursive quick sort helper."""
        if left < right:
            pivot_idx = _choose_pivot(left, right)
            final_pivot = _partition(left, right, pivot_idx)
            _quick_sort_recursive(left, final_pivot - 1)
            _quick_sort_recursive(final_pivot + 1, right)
    
    if seed is not None:
        random.seed(seed)
    
    _quick_sort_recursive(0, len(arr_copy) - 1)
    return arr_copy

