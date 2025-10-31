"""Tests for sorting algorithms."""
import pytest
from typing import List
import random

from src.algorithms.merge_sort import merge_sort
from src.algorithms.quick_sort import quick_sort, PivotStrategy


class TestMergeSort:
    """Tests for merge sort algorithm."""
    
    def test_empty_array(self) -> None:
        """Test sorting empty array."""
        assert merge_sort([]) == []
    
    def test_single_element(self) -> None:
        """Test sorting array with single element."""
        assert merge_sort([42]) == [42]
    
    def test_already_sorted(self) -> None:
        """Test sorting already sorted array."""
        arr = [1, 2, 3, 4, 5]
        assert merge_sort(arr) == [1, 2, 3, 4, 5]
        # Original should not be modified
        assert arr == [1, 2, 3, 4, 5]
    
    def test_reverse_sorted(self) -> None:
        """Test sorting reverse sorted array."""
        arr = [5, 4, 3, 2, 1]
        assert merge_sort(arr) == [1, 2, 3, 4, 5]
    
    def test_random_array(self) -> None:
        """Test sorting random array."""
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        assert merge_sort(arr) == [1, 1, 2, 3, 4, 5, 5, 6, 9]
    
    def test_duplicates(self) -> None:
        """Test sorting array with duplicates."""
        arr = [5, 5, 5, 3, 3, 1]
        assert merge_sort(arr) == [1, 3, 3, 5, 5, 5]
    
    def test_large_array(self) -> None:
        """Test sorting large array."""
        arr = list(range(1000, 0, -1))
        result = merge_sort(arr)
        assert result == list(range(1, 1001))
    
    def test_instrumentation(self) -> None:
        """Test instrumentation callback."""
        counters: dict = {"comparison": 0, "swap": 0}
        
        def instrument(op: str) -> None:
            if op in counters:
                counters[op] += 1
        
        arr = [3, 1, 4, 1, 5]
        result = merge_sort(arr, instrument=instrument)
        
        assert result == [1, 1, 3, 4, 5]
        assert counters["comparison"] > 0
        # Merge sort doesn't do swaps in traditional sense
        assert counters["swap"] == 0


class TestQuickSort:
    """Tests for quick sort algorithm."""
    
    @pytest.mark.parametrize("pivot", ["first", "last", "median_of_three", "random"])
    def test_empty_array(self, pivot: PivotStrategy) -> None:
        """Test sorting empty array."""
        assert quick_sort([], pivot_strategy=pivot) == []
    
    @pytest.mark.parametrize("pivot", ["first", "last", "median_of_three", "random"])
    def test_single_element(self, pivot: PivotStrategy) -> None:
        """Test sorting array with single element."""
        assert quick_sort([42], pivot_strategy=pivot) == [42]
    
    @pytest.mark.parametrize("pivot", ["first", "last", "median_of_three", "random"])
    def test_already_sorted(self, pivot: PivotStrategy) -> None:
        """Test sorting already sorted array."""
        arr = [1, 2, 3, 4, 5]
        result = quick_sort(arr, pivot_strategy=pivot, seed=42)
        assert result == [1, 2, 3, 4, 5]
        # Original should not be modified
        assert arr == [1, 2, 3, 4, 5]
    
    @pytest.mark.parametrize("pivot", ["first", "last", "median_of_three", "random"])
    def test_reverse_sorted(self, pivot: PivotStrategy) -> None:
        """Test sorting reverse sorted array."""
        arr = [5, 4, 3, 2, 1]
        result = quick_sort(arr, pivot_strategy=pivot, seed=42)
        assert result == [1, 2, 3, 4, 5]
    
    @pytest.mark.parametrize("pivot", ["first", "last", "median_of_three", "random"])
    def test_random_array(self, pivot: PivotStrategy) -> None:
        """Test sorting random array."""
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        result = quick_sort(arr, pivot_strategy=pivot, seed=42)
        assert result == [1, 1, 2, 3, 4, 5, 5, 6, 9]
    
    @pytest.mark.parametrize("pivot", ["first", "last", "median_of_three", "random"])
    def test_duplicates(self, pivot: PivotStrategy) -> None:
        """Test sorting array with duplicates."""
        arr = [5, 5, 5, 3, 3, 1]
        result = quick_sort(arr, pivot_strategy=pivot, seed=42)
        assert result == [1, 3, 3, 5, 5, 5]
    
    @pytest.mark.parametrize("pivot", ["first", "last", "median_of_three", "random"])
    def test_large_array(self, pivot: PivotStrategy) -> None:
        """Test sorting large array."""
        arr = list(range(1000, 0, -1))
        result = quick_sort(arr, pivot_strategy=pivot, seed=42)
        assert result == list(range(1, 1001))
    
    def test_instrumentation(self) -> None:
        """Test instrumentation callback."""
        counters: dict = {"comparison": 0, "swap": 0}
        
        def instrument(op: str) -> None:
            if op in counters:
                counters[op] += 1
        
        arr = [3, 1, 4, 1, 5]
        result = quick_sort(arr, pivot_strategy="first", instrument=instrument, seed=42)
        
        assert result == [1, 1, 3, 4, 5]
        assert counters["comparison"] > 0
        assert counters["swap"] > 0


class TestPropertyTests:
    """Property-based tests comparing to Python's sorted()."""
    
    @pytest.mark.parametrize("size", [10, 100, 1000])
    def test_merge_sort_property(self, size: int) -> None:
        """Property test: merge_sort should match sorted() for random arrays."""
        random.seed(42)
        arr = [random.randint(-1000, 1000) for _ in range(size)]
        
        result = merge_sort(arr)
        expected = sorted(arr)
        
        assert result == expected
    
    @pytest.mark.parametrize("pivot", ["first", "last", "median_of_three", "random"])
    @pytest.mark.parametrize("size", [10, 100, 1000])
    def test_quick_sort_property(self, pivot: PivotStrategy, size: int) -> None:
        """Property test: quick_sort should match sorted() for random arrays."""
        random.seed(42)
        arr = [random.randint(-1000, 1000) for _ in range(size)]
        
        result = quick_sort(arr, pivot_strategy=pivot, seed=42)
        expected = sorted(arr)
        
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

