from typing import List, Dict, Set

class GraduationRequirements:
    """毕业要求定义"""
    
    # 必修课程列表
    REQUIRED_COURSES: Set[str] = {
        "高等数学", "高等数学（二）", "经济学", "光华第一课", "概率统计",
        "科学思维与实践论", "线性代数", "组织与管理", "微观经济学", "会计学",
        "宏观经济学", "计量经济学", "社会心理学", "营销学", "公司金融",
        "管理科学", "数据科学的Python基础", "证券投资学", "金融市场与金融机构"
    }
    
    # 金融选修课程列表（需要选够12学分）
    FINANCE_ELECTIVE_COURSES: Set[str] = {
        "行为金融", "因果推断与商业应用", "金融建模与量化投资", "衍生品定价及应用",
        "金融时间序列分析", "金融中的数学方法", "科技金融与数字金融", "固定收益证券",
        "风险管理", "国际金融", "风险资本与创新融资", "公司估值"
    }
    
    # 中国相关课程列表（需要选够4学分）
    CHINA_RELATED_COURSES: Set[str] = {
        "中国经济", "中国金融", "中国经济改革与发展", "中国社会（上）", "中国社会（下）"
    }
    
    # 其他选修课程列表（需要选够8学分）
    OTHER_ELECTIVE_COURSES: Set[str] = {
        "创新管理", "综合商业计划书竞赛", "可持续创业", "共演战略：从创业到企业转型",
        "人工智能与商业创新", "商战模拟", "人力资源管理", "企业伦理", "战略管理",
        "创业管理", "创业与创新实践", "互联网与商业模式创新", "供应链管理",
        "从案例学习管理", "创业思维", "影子中央银行", "物流与供应链管理",
        "互联网时代营销新模式", "社会分层与流动", "智能网络与智能场景",
        "国家账本", "随机分析与应用", "中国公司—会计视角", "社会主义政治经济学",
        "生产作业管理", "投资银行", "中国社会与商业文化", "人口经济学",
        "体育营销", "传统国学中的管理思想", "真实世界经济学：田野调查",
        "大样本统计理论", "当代量化交易系统的原理与实现", "中国商务",
        "价值投资", "定量推理法", "期权波动率和对冲基金","公共治理专题：研究设计与方法",
        "数据驱动模型与运营分析","深度学习与文本分析" 
    }
    
    # 各类别所需学分
    FINANCE_ELECTIVE_CREDITS_REQUIRED = 12
    CHINA_RELATED_CREDITS_REQUIRED = 4
    OTHER_ELECTIVE_CREDITS_REQUIRED = 8
    
    @classmethod
    def get_course_category(cls, course_name: str) -> str:
        """获取课程所属类别"""
        if course_name in cls.REQUIRED_COURSES:
            return "required"
        elif course_name in cls.FINANCE_ELECTIVE_COURSES:
            return "finance_elective"
        elif course_name in cls.CHINA_RELATED_COURSES:
            return "china_related"
        elif course_name in cls.OTHER_ELECTIVE_COURSES:
            return "other_elective"
        else:
            return "unknown" 