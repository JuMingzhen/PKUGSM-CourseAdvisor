import gurobipy as gp
from typing import List, Dict
from models.course import Course
from models.schedule import SemesterSchedule, CompleteSchedule
from models.user import UserRequirements
from utils.constraints import CourseConstraints
from utils.data_loader import CourseDataLoader
from utils.graduation_requirements import GraduationRequirements

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
        available_courses = self.data_loader.get_available_courses(
            self.user_requirements.completed_courses
        )
        # 创建决策变量
        # x[i,j] = 1 表示课程i在第j学期选修
        courses = {course.id: course for course in available_courses}
        courses_name = {course.name: course for course in available_courses}
        if self.user_requirements.is_freshman:
            semesters = range(1, 9)
        else:
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
        
        # 4. 开课学期限制
        for course in courses.values():
            if len(course.semester) > 1:
                continue
            for semester in semesters:
                t = course.semester[0]
                if semester % 2 != t % 2:
                    self.model.addConstr(
                        x[course.id, semester] == 0
                    )

        # 5. 先修课程约束
        for course in courses:
            for prereq in courses[course].prerequisites:
                if prereq in courses_name:  # 如果先修课程在可选课程中
                    # 确保先修课程在被修课程之前完成
                    for semester in semesters:
                        if semester > 1:
                            # 对于每个学期，如果选择了当前课程，那么先修课程必须在之前的学期完成
                            self.model.addConstr(
                                gp.quicksum(x[courses_name[prereq].id, s] for s in range(semesters[0], semester)) >= x[course, semester]
                            )
        
        # 6. 毕业要求约束
        # 6.1 必修课程约束
        for required_course in GraduationRequirements.REQUIRED_COURSES:
            temp_id = courses_name[required_course].id
            if temp_id in courses.keys():
                self.model.addConstr(
                    gp.quicksum(x[temp_id, semester] for semester in semesters) == 1
                )
        
        # 6.2 金融选修课程约束（至少12学分）
        finance_elective_courses = [course for course in courses.keys() 
                                 if courses[course].name in GraduationRequirements.FINANCE_ELECTIVE_COURSES]
        self.model.addConstr(
            gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in finance_elective_courses
                for semester in semesters
            ) >= GraduationRequirements.FINANCE_ELECTIVE_CREDITS_REQUIRED
        )
        
        # 6.3 中国相关课程约束（至少4学分）
        china_related_courses = [course for course in courses.keys()
                               if courses[course].name in GraduationRequirements.CHINA_RELATED_COURSES]
        self.model.addConstr(
            gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in china_related_courses
                for semester in semesters
            ) >= GraduationRequirements.CHINA_RELATED_CREDITS_REQUIRED
        )
        
        # 6.4 其他选修课程约束（至少8学分）
        other_elective_courses = [course for course in courses.keys()
                                if courses[course].name in GraduationRequirements.OTHER_ELECTIVE_COURSES]
        self.model.addConstr(
            gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in other_elective_courses
                for semester in semesters
            ) >= GraduationRequirements.OTHER_ELECTIVE_CREDITS_REQUIRED
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
            if self.user_requirements.is_freshman:
                semesters = range(1, 9)
            else:
                semesters = range(
                (self.user_requirements.current_grade - 1) * 2 + self.user_requirements.current_semester + 1,
                9
            )
            for semester in semesters:
                semester_courses = []
                for course in self.data_loader.courses.values():
                    try:
                        temp = self.model.getVarByName(f"x[{course.id},{semester}]").x
                    except:
                        continue
                    if temp > 0.5:
                        semester_courses.append(course)
                schedules[semester] = SemesterSchedule(semester, semester_courses)
            
            return CompleteSchedule(schedules)
        else:
            raise Exception("No optimal solution found") 