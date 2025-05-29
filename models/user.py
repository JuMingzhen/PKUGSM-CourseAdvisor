from dataclasses import dataclass
from typing import List, Optional

@dataclass
class UserRequirements:
    """用户需求模型"""
    is_freshman: bool  # 是否为新生
    current_grade: Optional[int]  # 当前年级（1-4）
    current_semester: Optional[int]  # 当前学期（1-2）
    completed_courses: List[str]  # 已修课程列表
    study_abroad: bool  # 是否计划出国留学
    internship: bool  # 是否计划实习
    internship_semester: Optional[int] = None  # 实习学期（1-8）
    
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
        """验证用户输入是否有效"""
        if not self.is_freshman:
            if not (1 <= self.current_grade <= 4):
                return False
            if not (1 <= self.current_semester <= 2):
                return False
        if self.internship and self.internship_semester is not None:
            if not (1 <= self.internship_semester <= 8):
                return False
        return True 