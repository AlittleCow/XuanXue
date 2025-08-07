"""
运行测试的便捷脚本
"""
import subprocess
import sys
import os

def run_tests():
    """运行所有测试"""
    print("=== XuanXue包测试套件 ===\n")
    
    # 确保在正确的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 安装测试依赖
    print("1. 安装测试依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"], 
                   check=False)
    
    # 运行基本测试
    print("\n2. 运行基本测试...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                           capture_output=False)
    
    if result.returncode == 0:
        print("\n✓ 基本测试通过!")
        
        # 运行覆盖率测试
        print("\n3. 运行覆盖率测试...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "--cov=XuanXue", 
                       "--cov-report=html", "--cov-report=term"], 
                      capture_output=False)
        
        # 运行性能测试
        print("\n4. 运行性能测试...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/test_performance.py", 
                       "-v", "-m", "not slow"], 
                      capture_output=False)
        
        print("\n=== 测试完成 ===")
        print("查看详细覆盖率报告: htmlcov/index.html")
        
    else:
        print("\n✗ 测试失败!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)