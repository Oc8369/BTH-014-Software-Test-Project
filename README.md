# BTH-014-Software-Test-Project (简体中文)

<div align="center">

**简体中文** | [English](./README_EN.md)

</div>

## 项目介绍

本项目对python标准库中 `pickle`模块序列化功能的稳定性进行了测试，测试环境可分为以下两组：

1. Python3.12下的不同系统（**Windows**、**Linux**和**macOS**）
2. **Windows**系统下的不同Python版本（**3.6**、**3.7**、**3.8**、**3.11**、**3.12**）

对于不同系统，我们选择**迁移代码**进行测试，再将测试结果合并后进行比较。

对于不同Python版本，我们使用**conda**进行动态管理。

## 项目结构

```
Software_test
├── blackbox_test
│   ├── boundary //边界测试
│   │   ├── result_different_python_vision //记录边界测试不同python版本的测试结果
│   │   ├── result_different_system_vision //记录边界测试不同系统的测试结果
│   │   └── boundary_test.py //生成测试数据，进行测试并记录
│   ├── ECP //等价类划分
│   │   ├── result_different_python_version //记录等价类划分不同python版本的测试结果
│   │   ├── result_different_system_version //记录等价类划分不同系统的测试结果
│   │   └── ecp_test.py //生成测试数据，进行测试并记录
│   ├── fuzzing //模糊测试
│   │   ├── result_different_python_version //记录模糊测试不同python版本的测试结果
│   │   ├── result_different_system_version //记录模糊测试不同系统的测试结果
│   │   └── fuzzing_test.py //生成测试数据，进行测试并记录
│   └── state_machine //状态机
│       ├── result_different_python_version //记录状态机不同python版本的测试结果
│       ├── result_different_system_version //记录状态机不同系统的测试结果
│	└── state_machine_test.py //生成测试数据，进行测试并记录
├── whitebox_test
│   ├── all_defs //定义覆盖
│   │   ├── result_different_python_version //记录定义覆盖不同python版本的测试结果
│   │   ├── result_different_system_version //记录定义覆盖不同系统的测试结果
│   │   └── all_defs_test.py //生成测试数据，进行测试并记录
│   │   
│   └── statement_coverage_and_branch_coverage //语句覆盖与分支覆盖
│       ├── result_different_python_version //记录语句覆盖与分支覆盖不同python版本的测试结果
│       ├── result_different_system_version //记录语句覆盖与分支覆盖不同系统的测试结果
│	├── coverage_test.py //生成测试数据，进行测试并记录
│	└── my_pickle.py //将pickle模块复制到目录下，便于计算覆盖率
├── analysis_res //存储分析结果
├── analysis.py //用于比较测试结果哈希值的函数
├── clean_redundant_files.py //用于清理测试产生的多余文件
├── Linux_macOS_analysis.sh //Linux下一键执行测试结果哈希值比较
├── Linux_macOS_test.sh //Linux下一键执行测试
├── Windows_analysis.bat //Windows下一键执行测试结果哈希值比较
├── Windows_test.bat //Windows下一键执行测试
```
