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
        print("开始创建优化模型...")  # 调试信息
        print("用户需求:", self.user_requirements)  # 调试信息
        
        self.model = gp.Model("Course_Scheduling")
        
        # 获取可用课程
        available_courses = self.data_loader.get_available_courses(
            self.user_requirements.completed_courses
        )
        print("可用课程数量:", len(available_courses))  # 调试信息
        print("已修课程:", self.user_requirements.completed_courses)  # 调试信息
        
        # 创建决策变量
        courses = {course.id: course for course in available_courses}
        courses_name = {course.name: course for course in available_courses}
        
        if self.user_requirements.is_freshman:
            semesters = range(1, 9)
        else:
            semesters = range(
                (self.user_requirements.current_grade - 1) * 2 + self.user_requirements.current_semester + 1,
                9
            )
        print("规划学期范围:", list(semesters))  # 调试信息
        
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
                ) <= self.user_requirements.upperbound_credits
            )
        
        # 前6个学期每学期至少修9学分，大四最多修12学分
        if semesters[0] <= 6:
            for semester in range(semesters[0], 7):
                self.model.addConstr(
                    gp.quicksum(
                        courses[course].credits * x[course, semester]
                        for course in courses
                    ) >= 9
                )
        if semesters[0] >= 7:
            for semester in range(semesters[0], 9):
                self.model.addConstr(
                    gp.quicksum(
                        courses[course].credits * x[course, semester]
                        for course in courses
                    ) <= 12
                )
        else:
            for semester in range(7, 9):
                self.model.addConstr(
                    gp.quicksum(
                        courses[course].credits * x[course, semester]
                        for course in courses
                    ) <= 12
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
                        if semester == 1:
                            if courses[course].prerequisites != []:
                                self.model.addConstr(x[course, semester] == 0)
                        if semester > 1:
                            # 对于每个学期，如果选择了当前课程，那么先修课程必须在之前的学期完成
                            self.model.addConstr(
                                gp.quicksum(x[courses_name[prereq].id, s] for s in range(semesters[0], semester)) >= x[course, semester]
                            )
        
        # 6. 毕业要求约束
        # 6.1 必修课程约束
        for required_course in GraduationRequirements.REQUIRED_COURSES:
            if required_course not in courses_name:
                continue
            temp_id = courses_name[required_course].id
            self.model.addConstr(
                gp.quicksum(x[temp_id, semester] for semester in semesters) == 1
            )
        
        # 6.2 金融选修课程约束（至少12学分）
        already_selected_credits = sum([course.credits for course in self.user_requirements.completed_courses 
                                        if course in GraduationRequirements.FINANCE_ELECTIVE_COURSES])
        finance_elective_courses = [course for course in courses.keys() 
                                 if courses[course].name in GraduationRequirements.FINANCE_ELECTIVE_COURSES]
        self.model.addConstr(
            gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in finance_elective_courses
                for semester in semesters
            ) >= GraduationRequirements.FINANCE_ELECTIVE_CREDITS_REQUIRED  - already_selected_credits
        )
        
        # 6.3 中国相关课程约束（至少4学分）
        already_selected_credits = sum([course.credits for course in self.user_requirements.completed_courses 
                                        if course in GraduationRequirements.CHINA_RELATED_COURSES])
        china_related_courses = [course for course in courses.keys()
                               if courses[course].name in GraduationRequirements.CHINA_RELATED_COURSES]
        self.model.addConstr(
            gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in china_related_courses
                for semester in semesters
            ) >= GraduationRequirements.CHINA_RELATED_CREDITS_REQUIRED - already_selected_credits
        )
        
        # 6.4 其他选修课程约束（至少8学分）
        already_selected_credits = sum([course.credits for course in self.user_requirements.completed_courses 
                                        if course in GraduationRequirements.OTHER_ELECTIVE_COURSES])
        other_elective_courses = [course for course in courses.keys()
                                if courses[course].name in GraduationRequirements.OTHER_ELECTIVE_COURSES]
        self.model.addConstr(
            gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in other_elective_courses
                for semester in semesters
            ) >= GraduationRequirements.OTHER_ELECTIVE_CREDITS_REQUIRED - already_selected_credits
        )
        
        # 7. 不出国时的必修课程约束（前三年完成）
        if not self.user_requirements.study_abroad:
            if semesters[0] <= 6:
                required_courses = [course for course in courses.values() 
                              if course.name in GraduationRequirements.REQUIRED_COURSES]
                for course in required_courses:
                    # 确保必修课程在前6个学期完成
                    self.model.addConstr(
                        gp.quicksum(x[course.id, semester] for semester in range(semesters[0], 7)) == 1
                    )
        
        # 8. 新生第一学期必须选择经济学和光华第一课和组织与管理
        if self.user_requirements.is_freshman:
            # 找到经济学和光华第一课的课程ID
            economics_id = None
            first_course_id = None
            zuzhi_id = None
            for course_id, course in courses.items():
                if course.name == "经济学":
                    economics_id = course_id
                elif course.name == "光华第一课":
                    first_course_id = course_id
                elif course.name == "组织与管理":
                    zuzhi_id = course_id
            # 添加约束：这两门课必须在第一学期选择
            if economics_id is not None:
                self.model.addConstr(x[economics_id, 1] == 1)
            if first_course_id is not None:
                self.model.addConstr(x[first_course_id, 1] == 1)
            if zuzhi_id is not None:
                self.model.addConstr(x[zuzhi_id, 1] == 1)
        
        # 设置目标函数
        # 1. 根据规划类型设置主要目标
        total_credits = gp.quicksum(
            courses[course].credits * x[course, semester]
            for course in courses
            for semester in semesters
        )
        
        def has_overlap(list1, list2):
            """判断两个列表是否存在交集"""
            return bool(set(list1) & set(list2))
        
        print("规划类型:", self.user_requirements.planning_type)  # 调试信息
        
        if self.user_requirements.planning_type == "Minimal Effort":
            # 最小化总学分
            self.model.setObjectiveN(total_credits, 0, 1.0)  # 主要目标：最小化总学分
        elif self.user_requirements.planning_type == "Balanced Workload":
            # 最小化与目标学分的偏差
            target = self.user_requirements.target_credits_per_semester
            # 为每个学期创建正负偏差变量
            pos_dev = self.model.addVars(semesters, name="pos_dev")
            neg_dev = self.model.addVars(semesters, name="neg_dev")
            
            # 添加约束：实际学分 - 目标学分 = 正偏差 - 负偏差
            for semester in semesters:
                self.model.addConstr(
                    gp.quicksum(courses[course].credits * x[course, semester] for course in courses) - target == pos_dev[semester] - neg_dev[semester]
                )
            
            # 最小化总偏差
            self.model.setObjectiveN(
                gp.quicksum(pos_dev[semester] + neg_dev[semester] for semester in semesters),
                0, 1.0
            )  # 主要目标：最小化与目标学分的偏差
        elif self.user_requirements.planning_type == "Focused Depth":
            # 最大化偏好学科的课程学分
            preferred_credits = gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in courses
                for semester in semesters
                if has_overlap(courses[course].subject_category, self.user_requirements.preferred_subjects)
            )
            self.model.setObjectiveN(-preferred_credits, 0, 1.0)  # 主要目标：最大化偏好学科课程学分
        else:  # Maximum Intensity
            # 最大化总学分
            self.model.setObjectiveN(-total_credits, 0, 1.0)  # 主要目标：最大化总学分
        
        # 2. 如果选择实习，最小化实习学期的课程数量
        if self.user_requirements.internship and self.user_requirements.internship_semester is not None:
            internship_semester = self.user_requirements.internship_semester
            internship_course_count = gp.quicksum(
                x[course, internship_semester]
                for course in courses
            )
            # 设置多目标优化
            self.model.setObjectiveN(internship_course_count, 1, 0.5)  # 次要目标：最小化实习学期课程数
        
        # 3. 如果有偏好学科，添加为次要目标
        if self.user_requirements.preferred_subjects:
            preferred_credits = gp.quicksum(
                courses[course].credits * x[course, semester]
                for course in courses
                for semester in semesters
                if has_overlap(courses[course].subject_category, self.user_requirements.preferred_subjects)
            )
            self.model.setObjectiveN(-preferred_credits, 2, 0.3)  # 第三目标：最大化偏好学科课程学分
        
        print("优化模型创建完成")  # 调试信息
    
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