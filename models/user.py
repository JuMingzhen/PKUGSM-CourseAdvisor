from dataclasses import dataclass
from typing import List, Optional

@dataclass
class UserRequirements:
    """用户选课需求模型"""
    is_freshman: bool  # 是否为新生
    current_grade: Optional[int] = None  # 当前年级（1-4），新生可为None
    current_semester: Optional[int] = None  # 当前学期（1-2），新生可为None
    completed_courses: List[str] = None  # 已修课程列表
    study_abroad: bool = False  # 是否出国留学
    internship: bool = False  # 是否实习
    target_semester: Optional[int] = None  # 目标学期（可选）
    English_level: str = "C"  # 英语水平（B/C/C+）
    
    def __post_init__(self):
        if self.completed_courses is None:
            self.completed_courses = []
        if self.is_freshman:
            self.current_grade = 1
            self.current_semester = 1
    
    def get_remaining_semesters(self) -> int:
        """计算剩余需要推荐的学期数"""
        if self.is_freshman:
            return 8
        total_semesters = 8
        current_semester_index = (self.current_grade - 1) * 2 + self.current_semester
        return total_semesters - current_semester_index
    
    def validate(self) -> bool:
        """验证用户输入的有效性"""
        if not self.is_freshman:
            if not (1 <= self.current_grade <= 4):
                return False
            if not (1 <= self.current_semester <= 2):
                return False
        if self.target_semester is not None and not (1 <= self.target_semester <= 8):
            return False
        if self.English_level not in ["B", "C", "C+"]:
            return False
        return True 