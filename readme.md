# PKUGSM-CourseAdvisor 🎓
北京大学光华管理学院“运筹优化与最优决策”课程作业

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

## 优化模型

### 1. 决策变量

系统使用二元决策变量 $x_{c,s}$ 表示课程选择：

$$x_{c,s} \in \{0,1\}, \forall c \in C, s \in S$$

其中：
- $c$ 表示课程
- $s$ 表示学期
- $C$ 为可选课程集合
- $S$ 为规划学期集合

### 2. 约束条件

#### 2.1 基本约束

1. **课程唯一性约束**：每门课程最多只能选一次
   $$\sum_{s \in S} x_{c,s} \leq 1, \forall c \in C$$

2. **学期学分上限约束**：每学期总学分不超过上限
   $$\sum_{c \in C} credits_c \cdot x_{c,s} \leq upperboundcredits, \forall s \in S$$

3. **学期学分下限约束**：
   - 前6个学期每学期至少修9学分
   $$\sum_{c \in C} credits_c \cdot x_{c,s} \geq 9, \forall s \in \{1,2,...,6\}$$
   - 大四每学期最多修12学分
   $$\sum_{c \in C} credits_c \cdot x_{c,s} \leq 12, \forall s \in \{7,8\}$$

#### 2.2 时间约束

1. **时间冲突约束**：同一学期不能选择时间冲突的课程
   $$x_{c_1,s} + x_{c_2,s} \leq 1, \forall (c_1,c_2) \in C \times C, s \in S, \text{where } c_1,c_2 \text{ have time conflict}$$

2. **开课学期限制**：课程只能在指定学期选择
   $$x_{c,s} = 0, \forall c \in C, s \in S, \text{where } s \text{ is not in course's offered semesters}$$

#### 2.3 先修课程约束

对于有先修要求的课程，确保先修课程在被修课程之前完成：
$$\sum_{s'=1}^{s-1} x_{prereq,s'} \geq x_{c,s}, \forall c \in C, s \in S, \text{where } prereq \text{ is a prerequisite of } c$$

#### 2.4 毕业要求约束

1. **必修课程约束**：所有必修课程必须修读
   $$\sum_{s \in S} x_{c,s} = 1, \forall c \in C_{required}$$

2. **金融选修课程约束**：至少修满12学分
   $$\sum_{c \in C_{finance}} \sum_{s \in S} credits_c \cdot x_{c,s} \geq 12$$

3. **中国相关课程约束**：至少修满4学分
   $$\sum_{c \in C_{china}} \sum_{s \in S} credits_c \cdot x_{c,s} \geq 4$$

4. **其他选修课程约束**：至少修满8学分
   $$\sum_{c \in C_{other}} \sum_{s \in S} credits_c \cdot x_{c,s} \geq 8$$

#### 2.5 特殊约束

1. **保研约束**：若不出国，则要求在前6个学期修完必修课
   $$\sum_{s \in \{1,2,3,4,5,6\}} x_{c,s} = 1, \forall c \in C_{required}$$

### 3. 优化目标

系统支持多种优化目标，根据用户需求选择：

#### 3.1 最小努力型（Minimal Effort）
最小化总学分：
$$\min \sum_{c \in C} \sum_{s \in S} credits_c \cdot x_{c,s}$$

#### 3.2 均衡负载型（Balanced Workload）
最小化与目标学分的偏差：
$$\min \sum_{s \in S} (posdev_s + negdev_s)$$
其中：
$$\sum_{c \in C} credits_c \cdot x_{c,s} - target = posdev_s - negdev_s, \forall s \in S$$

#### 3.3 专注深度型（Focused Depth）
最大化偏好学科的课程学分：
$$\max \sum_{c \in C_{preferred}} \sum_{s \in S} credits_c \cdot x_{c,s}$$

#### 3.4 最大强度型（Maximum Intensity）
最大化总学分：
$$\max \sum_{c \in C} \sum_{s \in S} credits_c \cdot x_{c,s}$$

### 4. 多目标优化

系统支持多目标优化，通过设置不同目标的优先级和权重来实现：

1. 主要目标：根据规划类型设置
2. 次要目标：最小化实习学期的课程数量
3. 第三目标：最大化偏好学科课程学分

### 5. 实现技术

- 使用Gurobi优化器求解线性规划问题
- 采用Python实现，使用gurobipy接口

---

## 当前不足&待完善功能

- 当前系统只针对85学分的专业课，未来考虑加入其他课程。
- 仍有很多未考虑到的约束优化条件（考试时间、实际课程质量、给分）
- 未考虑选不上课的情况
- 没有经验数据参照
- 约束条件灵活性差，用户不满意难以调整（添加参数选项？）
- 未来考虑结合大模型，打造智能系统，可以将要求文本转化成严格数学表达（约束条件or优化目标）
- 没有上线到web，使用仍需要源代码

## 贡献与许可

- 欢迎通过 Issue 提交建议或参与代码贡献 📬
- 本项目数据来源为北京大学教务部全校课表查询，数据内容见all_courses.json
