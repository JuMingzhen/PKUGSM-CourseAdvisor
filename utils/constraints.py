from typing import List, Dict
from models.course import Course
from models.schedule import SemesterSchedule
from models.user import UserRequirements

class CourseConstraints:
    """课程约束条件"""
    
    def __init__(self, user_requirements: UserRequirements):
        self.user_requirements = user_requirements
    
    def check_prerequisites(self, course: Course, completed_courses: List[str]) -> bool:
        """检查先修课程要求"""
        return all(prereq in completed_courses for prereq in course.prerequisites)
    
    def check_semester_load(self, schedule: SemesterSchedule, max_credits: int = 25) -> bool:
        """检查学期学分负载"""
        return schedule.get_total_credits() <= max_credits
    
    def check_time_conflicts(self, schedule: SemesterSchedule) -> bool:
        """检查时间冲突"""
        return not schedule.has_conflicts()
    
    def check_graduation_requirements(self, total_credits: int, required_credits: int = 140) -> bool:
        """检查毕业学分要求"""
        return total_credits >= required_credits
    
    def check_study_abroad_constraints(self, semester: int) -> bool:
        """检查出国留学相关约束"""
        if not self.user_requirements.study_abroad:
            return True
        # 这里可以添加出国留学相关的具体约束
        return True
    
    def check_internship_constraints(self, semester: int) -> bool:
        """检查实习相关约束"""
        if not self.user_requirements.internship:
            return True
        # 这里可以添加实习相关的具体约束
        return True 