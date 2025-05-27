from dataclasses import dataclass
from typing import List, Dict
from .course import Course

@dataclass
class SemesterSchedule:
    """单个学期的课表"""
    semester: int  # 学期编号（1-8）
    courses: List[Course]  # 该学期的课程列表
    
    def get_total_credits(self) -> int:
        """计算该学期的总学分"""
        return sum(course.credits for course in self.courses)
    
    def has_conflicts(self) -> bool:
        """检查该学期课程是否有时间冲突"""
        for i, course1 in enumerate(self.courses):
            for course2 in self.courses[i+1:]:
                if course1.has_time_conflict(course2):
                    return True
        return False

@dataclass
class CompleteSchedule:
    """完整的四年课表"""
    schedules: Dict[int, SemesterSchedule]  # 学期编号到课表的映射
    
    def get_total_credits(self) -> int:
        """计算总学分"""
        return sum(schedule.get_total_credits() for schedule in self.schedules.values())
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            semester: {
                'courses': [course.name for course in schedule.courses],
                'total_credits': schedule.get_total_credits()
            }
            for semester, schedule in self.schedules.items()
        } 