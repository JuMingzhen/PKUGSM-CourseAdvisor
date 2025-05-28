import json
from typing import List, Dict
from models.course import Course

class CourseDataLoader:
    """课程数据加载器"""
    
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.courses: Dict[str, Course] = {}
        self.load_data()
    
    def load_data(self) -> None:
        """从JSON文件加载课程数据"""
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for course_data in data:
                course = Course.from_dict(course_data)
                self.courses[course.name] = course
    
    def get_course(self, course_name: str) -> Course:
        """获取指定课程"""
        return self.courses.get(course_name)
    
    def get_all_courses(self) -> List[Course]:
        """获取所有课程"""
        return list(self.courses.values())
    
    def get_available_courses(self, completed_courses: List[str]) -> List[Course]:
        """获取可选的课程（排除已修课程）"""
        return [course for course in self.courses.values() 
                if course.name not in completed_courses]
    
    # def get_courses_by_prerequisites(self, completed_courses: List[str]) -> List[Course]:
    #     """获取满足先修课程要求的课程"""
    #     available_courses = self.get_available_courses(completed_courses)
    #     return [course for course in available_courses 
    #             if all(prereq in completed_courses for prereq in course.prerequisites)] 