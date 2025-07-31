import os
import time
import psutil
import json
from pathlib import Path
import sys

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import DocumentIntelligenceSystem

class PerformanceBenchmark:
    def __init__(self):
        self.results = []
    
    def measure_performance(self, input_dir, persona, job):
        """Measure processing performance"""
        
        # Initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Initialize system
        system = DocumentIntelligenceSystem()
        
        # Time the processing
        start_time = time.time()
        start_cpu = time.process_time()
        
        try:
            result = system.process_documents(input_dir, persona, job)
            
            # End timing
            end_time = time.time()
            end_cpu = time.process_time()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Calculate metrics
            wall_time = end_time - start_time
            cpu_time = end_cpu - start_cpu
            memory_used = final_memory - initial_memory
            
            benchmark_result = {
                "wall_time_seconds": round(wall_time, 2),
                "cpu_time_seconds": round(cpu_time, 2), 
                "memory_used_mb": round(memory_used, 2),
                "peak_memory_mb": round(final_memory, 2),
                "sections_processed": len(result.get('extracted_sections', [])),
                "documents_processed": len(result.get('metadata', {}).get('input_documents', [])),
                "constraint_compliance": {
                    "time_under_60s": wall_time < 60,
                    "memory_reasonable": memory_used < 1000  # 1GB limit
                }
            }
            
            self.results.append(benchmark_result)
            return benchmark_result
            
        except Exception as e:
            return {"error": str(e), "wall_time_seconds": time.time() - start_time}
    
    def save_benchmark_results(self, filename="benchmark_results.json"):
        """Save benchmark results to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)

if __name__ == "__main__":
    # Test benchmark
    benchmark = PerformanceBenchmark()
    if os.path.exists("./input"):
        result = benchmark.measure_performance("./input", "Research Analyst", "Analyze documents")
        print(f"Benchmark result: {result}")
        benchmark.save_benchmark_results()
