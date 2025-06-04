# PKUGSM-CourseAdvisor 🎓

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Gurobi](https://img.shields.io/badge/Optimization-Gurobi-FFD700)
![License](https://img.shields.io/badge/License-MIT-green)

**面向北京大学光华管理学院金融学专业学生的个性化选课推荐系统**  
为您的学术生涯提供科学、精准的课程规划解决方案 📈

---

## 项目概述
PKUGSM-CourseAdvisor 是专为光华管理学院金融学专业学子打造的智能选课规划助手。系统基于多目标优化算法，结合学生个性化需求（年级规划、留学/实习计划、学科方向偏好等），生成符合培养方案的最优课程路径。通过量化分析课程负荷、时间分配和学术目标，帮助学生在专业发展与学业压力间找到最佳平衡点 ⚖️

---

## 核心功能 ✨

### 📅 个性化课程规划
- 基于当前年级时间段智能生成未来至毕业的课程地图
- 支持输入海外交换/实习等需要空闲的时间窗口（如大三秋季学期交换）
- 金融专业领域偏好适配（公司金融、资产定价、金融工程等）

### 🎯 多维约束优化
- 学分分配策略（必修课/限选课/通选课，保你毕业就是了）
- 课程先修关系控制（按学期合理分配核心课与高阶选修课）
- 时间冲突检测（课程时间、考试周密度预警（功能尚未添加））

---

## 技术架构 🛠️

```python
├── frontend/               # 前端代码
├── logs/ 
├── models/
│   ├── course.py           # 课程类
│   ├── schedule.py         # 计划类
│   └── user.py             # 用户类（约束信息读取）
├── optimization/
│   └── scheduler.py        # 规划求解器
├── utils/
│   ├── constraints.py      # 约束类
│   ├── data_loader.py      # 数据读取类
│   ├── graduation_requirements.py      # 存放培养方案学分要求
│   └── update_json_keys.py # 用于更新原json文件（可忽略此文件）
├── all_courses.json        #存放课程数据
├── main.py                 #主程序
├── readme.md               #介绍文件
├── webapi.py               #后端api接口
└── requirements.txt        #要求配置文件
```
---

## 当前不足&待完善功能

- 当前系统只针对85学分的专业课，未来考虑加入其他课程。
- 仍有很多未考虑到的约束优化条件（考试时间、实际课程质量、给分）
- 未考虑选不上课的情况
- 没有经验数据参照
- 约束条件灵活性差，用户不满意难以调整（添加参数选项？）
- 未来考虑结合大模型，打造智能系统，可以将要求文本转化成严格数学表达（约束条件or优化目标）

## 贡献与许可

- 欢迎通过 Issue 提交建议或参与代码贡献 📬
- 本项目数据来源为北京大学教务部全校课表查询，数据内容见all_courses.json
