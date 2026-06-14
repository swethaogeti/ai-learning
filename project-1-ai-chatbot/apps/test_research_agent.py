"""
Tests and Benchmarks for Parallel Function Calling
====================================================

This module demonstrates:
1. Unit tests for individual tools
2. Integration tests for the agent
3. Performance benchmarks (sequential vs parallel)
4. Error handling tests

Run with: pytest test_research_agent.py -v
Run benchmarks: pytest test_research_agent.py --benchmark-only
"""

import asyncio
import pytest
import time
from datetime import datetime


# ============================================================================
# Mock Tool Implementations for Testing
# ============================================================================

async def mock_tool_fast():
    """Simulates a fast API call (0.1s)"""
    await asyncio.sleep(0.1)
    return {"status": "success", "data": "fast"}


async def mock_tool_medium():
    """Simulates a medium API call (0.5s)"""
    await asyncio.sleep(0.5)
    return {"status": "success", "data": "medium"}


async def mock_tool_slow():
    """Simulates a slow API call (1.0s)"""
    await asyncio.sleep(1.0)
    return {"status": "success", "data": "slow"}


async def mock_tool_fails():
    """Simulates a failing tool"""
    await asyncio.sleep(0.2)
    raise ValueError("API temporarily unavailable")


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestIndividualTools:
    """Test individual tool execution"""
    
    @pytest.mark.asyncio
    async def test_fast_tool_completes(self):
        """Verify fast tool completes successfully"""
        result = await mock_tool_fast()
        assert result["status"] == "success"
        assert result["data"] == "fast"
    
    @pytest.mark.asyncio
    async def test_medium_tool_completes(self):
        """Verify medium tool completes successfully"""
        result = await mock_tool_medium()
        assert result["status"] == "success"
        assert result["data"] == "medium"
    
    @pytest.mark.asyncio
    async def test_slow_tool_completes(self):
        """Verify slow tool completes successfully"""
        result = await mock_tool_slow()
        assert result["status"] == "success"
        assert result["data"] == "slow"
    
    @pytest.mark.asyncio
    async def test_failing_tool_raises_error(self):
        """Verify failing tool raises appropriate error"""
        with pytest.raises(ValueError):
            await mock_tool_fails()


# ============================================================================
# SEQUENTIAL vs PARALLEL TESTS
# ============================================================================

class TestExecutionPatterns:
    """Test different execution patterns"""
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Sequential: tools run one after another"""
        start = asyncio.get_event_loop().time()
        
        # Run one by one
        result1 = await mock_tool_fast()      # 0.1s
        result2 = await mock_tool_medium()    # 0.5s
        result3 = await mock_tool_slow()      # 1.0s
        
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should take approximately sum of all times
        assert elapsed >= 1.5  # 0.1 + 0.5 + 1.0
        assert elapsed < 1.7   # Allow 200ms buffer
        
        assert result1["status"] == "success"
        assert result2["status"] == "success"
        assert result3["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Parallel: tools run simultaneously"""
        start = asyncio.get_event_loop().time()
        
        # Run all at once using gather
        results = await asyncio.gather(
            mock_tool_fast(),      # 0.1s
            mock_tool_medium(),    # 0.5s
            mock_tool_slow()       # 1.0s
        )
        
        elapsed = asyncio.get_event_loop().time() - start
        
        # Should take approximately max time
        assert elapsed >= 1.0   # Max of all (1.0s)
        assert elapsed < 1.2    # Allow 200ms buffer
        
        for result in results:
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_parallel_is_faster_than_sequential(self):
        """Verify parallel execution is faster"""
        
        # Sequential
        start_seq = asyncio.get_event_loop().time()
        await mock_tool_fast()
        await mock_tool_medium()
        await mock_tool_slow()
        seq_time = asyncio.get_event_loop().time() - start_seq
        
        # Parallel
        start_par = asyncio.get_event_loop().time()
        await asyncio.gather(
            mock_tool_fast(),
            mock_tool_medium(),
            mock_tool_slow()
        )
        par_time = asyncio.get_event_loop().time() - start_par
        
        # Parallel must be faster
        assert par_time < seq_time
        
        # Calculate speedup
        speedup = seq_time / par_time
        print(f"\n⚡ Speedup: {speedup:.2f}x")
        print(f"   Sequential: {seq_time:.2f}s")
        print(f"   Parallel: {par_time:.2f}s")
        
        # Expect ~1.5x speedup for this case
        assert speedup > 1.3


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and recovery"""
    
    @pytest.mark.asyncio
    async def test_single_tool_failure_doesnt_crash_all(self):
        """One tool failing shouldn't crash the batch"""
        
        async def safe_execute(coroutine):
            try:
                return await coroutine
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        results = await asyncio.gather(
            safe_execute(mock_tool_fast()),
            safe_execute(mock_tool_fails()),  # This one fails
            safe_execute(mock_tool_slow()),
            return_exceptions=True
        )
        
        # Check that we got 3 results
        assert len(results) == 3
        
        # Check statuses
        assert results[0]["status"] == "success"
        assert results[1]["status"] == "error"
        assert results[2]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_retry_logic_eventually_succeeds(self):
        """Verify retry logic with exponential backoff"""
        
        attempt_count = [0]
        
        async def flaky_tool():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise Exception("Temporary failure")
            return {"status": "success", "data": "recovered"}
        
        async def retry_with_backoff(coro, max_retries=3):
            for attempt in range(max_retries):
                try:
                    return await coro
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt * 0.01  # Small delays for testing
                        await asyncio.sleep(wait_time)
                    else:
                        raise
        
        result = await retry_with_backoff(flaky_tool())
        
        assert result["status"] == "success"
        assert attempt_count[0] == 3  # Should have retried twice


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

class TestPerformanceBenchmarks:
    """Benchmark various execution patterns"""
    
    @pytest.mark.asyncio
    async def test_benchmark_sequential_5_tools(self):
        """Benchmark: 5 sequential tool calls"""
        start = time.time()
        
        for _ in range(5):
            await mock_tool_medium()
        
        elapsed = time.time() - start
        print(f"\n📊 Sequential 5 tools: {elapsed:.3f}s")
        
        # Should be ~2.5s (5 * 0.5s)
        assert 2.3 < elapsed < 2.7
    
    @pytest.mark.asyncio
    async def test_benchmark_parallel_5_tools(self):
        """Benchmark: 5 parallel tool calls"""
        start = time.time()
        
        await asyncio.gather(
            *[mock_tool_medium() for _ in range(5)]
        )
        
        elapsed = time.time() - start
        print(f"📊 Parallel 5 tools: {elapsed:.3f}s")
        
        # Should be ~0.5s (just the max)
        assert 0.4 < elapsed < 0.7
    
    @pytest.mark.asyncio
    async def test_benchmark_speedup_factors(self):
        """Calculate speedup for different tool counts"""
        
        tool_counts = [2, 3, 5, 10]
        
        print("\n📈 Speedup Analysis:")
        print("-" * 50)
        print(f"{'Tools':<10} {'Sequential':<15} {'Parallel':<15} {'Speedup':<10}")
        print("-" * 50)
        
        for count in tool_counts:
            # Sequential
            start = time.time()
            for _ in range(count):
                await mock_tool_medium()  # 0.5s each
            seq_time = time.time() - start
            
            # Parallel
            start = time.time()
            await asyncio.gather(
                *[mock_tool_medium() for _ in range(count)]
            )
            par_time = time.time() - start
            
            speedup = seq_time / par_time
            
            print(f"{count:<10} {seq_time:>6.2f}s           {par_time:>6.2f}s           {speedup:>6.2f}x")
            
            # Verify parallelization worked
            assert par_time < seq_time
            assert speedup > 1.8  # Should be ~count speedup
        
        print("-" * 50)


# ============================================================================
# REAL-WORLD SCENARIO TESTS
# ============================================================================

class TestRealWorldScenarios:
    """Test realistic use cases"""
    
    @pytest.mark.asyncio
    async def test_mixed_response_times(self):
        """Test with realistic mix of fast and slow tools"""
        
        # Realistic: news (1s), weather (0.5s), stock (0.8s), crypto (0.3s)
        tools = [
            ("news", 1.0),
            ("weather", 0.5),
            ("stock", 0.8),
            ("crypto", 0.3)
        ]
        
        # Sequential
        start = time.time()
        for name, duration in tools:
            await asyncio.sleep(duration)
        seq_time = time.time() - start
        
        # Parallel
        start = time.time()
        await asyncio.gather(
            *[asyncio.sleep(duration) for name, duration in tools]
        )
        par_time = time.time() - start
        
        print(f"\n🎯 Real-world scenario:")
        print(f"   Sequential: {seq_time:.2f}s")
        print(f"   Parallel: {par_time:.2f}s")
        print(f"   Speedup: {seq_time/par_time:.2f}x")
        
        # Parallel should be ~max(durations) = 1.0s
        assert par_time < 1.2
        
        # Sequential should be ~sum(durations) = 2.6s
        assert seq_time > 2.4


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture
async def timing_context():
    """Helper to measure execution time"""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"\n⏱️  Execution time: {elapsed:.3f}s")


# ============================================================================
# Test Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run with: pytest test_research_agent.py -v
    pytest.main([__file__, "-v", "--tb=short"])
