from dataclasses import dataclass
from typing import List, Optional

@dataclass
class UserRequirements:
    """用户选课需求模型"""
    current_grade: int  # 当前年级（1-4）
    current_semester: int  # 当前学期（1-8）
    completed_courses: List[str]  # 已修课程列表
    study_abroad: bool  # 是否出国留学
    internship: bool  # 是否实习
    target_semester: Optional[int] = None  # 目标学期（可选）
    
    def get_remaining_semesters(self) -> int:
        """计算剩余需要推荐的学期数"""
        total_semesters = 8
        current_semester_index = (self.current_grade - 1) * 2 + self.current_semester
        return total_semesters - current_semester_index
    
    def validate(self) -> bool:
        """验证用户输入的有效性"""
        if not (1 <= self.current_grade <= 4):
            return False
        if not (1 <= self.current_semester <= 2):
            return False
        if self.target_semester is not None and not (1 <= self.target_semester <= 8):
            return False
        return True 