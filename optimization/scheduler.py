import gurobipy as gp
from typing import List, Dict
from models.course import Course
from models.schedule import SemesterSchedule, CompleteSchedule
from models.user import UserRequirements
from utils.constraints import CourseConstraints
from utils.data_loader import CourseDataLoader

class CourseScheduler:
    """课程调度优化器"""
    
    def __init__(self, 
                 user_requirements: UserRequirements,
                 data_loader: CourseDataLoader,
                 constraints: CourseConstraints):
        self.user_requirements = user_requirements
        self.data_loader = data_loader
        self.constraints = constraints
        self.model = None
    
    def create_model(self):
        """创建优化模型"""
        self.model = gp.Model("Course_Scheduling")
        
        # 获取可用课程
        available_courses = self.data_loader.get_courses_by_prerequisites(
            self.user_requirements.completed_courses
        )
        
        # 创建决策变量
        # x[i,j] = 1 表示课程i在第j学期选修
        courses = {course.name: course for course in available_courses}
        semesters = range(
            (self.user_requirements.current_grade - 1) * 2 + self.user_requirements.current_semester + 1,
            9
        )
        
        x = self.model.addVars(
            courses.keys(),
            semesters,
            vtype=gp.GRB.BINARY,
            name="x"
        )
        
        # 添加约束条件
        # 1. 每门课程最多只能选一次
        for course in courses:
            self.model.addConstr(
                gp.quicksum(x[course, semester] for semester in semesters) <= 1
            )
        
        # 2. 每学期学分限制
        for semester in semesters:
            self.model.addConstr(
                gp.quicksum(
                    courses[course].credits * x[course, semester]
                    for course in courses
                ) <= 25
            )
        
        # 3. 时间冲突约束
        for semester in semesters:
            for course1 in courses:
                for course2 in courses:
                    if course1 < course2 and courses[course1].has_time_conflict(courses[course2]):
                        self.model.addConstr(
                            x[course1, semester] + x[course2, semester] <= 1
                        )
        
        # 设置目标函数（这里使用总学分作为目标，你可以根据需要修改）
        self.model.setObjective(
            gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in courses
                for semester in semesters
            ),
            sense=gp.GRB.MAXIMIZE
        )
    
    def solve(self) -> CompleteSchedule:
        """求解优化问题"""
        if self.model is None:
            self.create_model()
        
        self.model.optimize()
        
        if self.model.status == gp.GRB.OPTIMAL:
            # 构建结果
            schedules = {}
            for semester in range(
                (self.user_requirements.current_grade - 1) * 2 + self.user_requirements.current_semester + 1,
                9
            ):
                semester_courses = []
                for course_name, course in self.data_loader.courses.items():
                    if self.model.getVarByName(f"x[{course_name},{semester}]").x > 0.5:
                        semester_courses.append(course)
                schedules[semester] = SemesterSchedule(semester, semester_courses)
            
            return CompleteSchedule(schedules)
        else:
            raise Exception("No optimal solution found") 