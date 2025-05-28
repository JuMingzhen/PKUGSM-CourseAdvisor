#主程序
from models.user import UserRequirements
from utils.data_loader import CourseDataLoader
from utils.constraints import CourseConstraints
from optimization.scheduler import CourseScheduler
import traceback

def main():
    # 加载课程数据
    data_loader = CourseDataLoader('all_courses.json')
    
    # 获取用户输入
    print("欢迎使用光华管理学院金融系选课推荐系统！")
    print("请输入您的信息：")
    
    is_freshman = input("是否为新生（是/否）：").lower() == '是'
    
    if not is_freshman:
        current_grade = int(input("当前年级（1-4）："))
        current_semester = int(input("当前学期（1-2）："))
        completed_courses = input("已修课程（用逗号分隔）：").split(',')
    else:
        current_grade = None
        current_semester = None
        completed_courses = []
    
    study_abroad = input("是否计划出国留学（是/否）：").lower() == '是'
    internship = input("是否计划实习（是/否）：").lower() == '是'
    
    # 创建用户需求对象
    user_requirements = UserRequirements(
        is_freshman=is_freshman,
        current_grade=current_grade,
        current_semester=current_semester,
        completed_courses=completed_courses,
        study_abroad=study_abroad,
        internship=internship,
        English_level=English_level
    )
    
    # 验证用户输入
    if not user_requirements.validate():
        print("输入信息无效，请检查后重试！")
        return
    
    # 创建约束条件
    constraints = CourseConstraints(user_requirements)
    
    # 创建调度器并求解
    scheduler = CourseScheduler(user_requirements, data_loader, constraints)
    
    try:
        # 求解优化问题
        schedule = scheduler.solve()
        
        # 输出结果
        print("\n推荐课表：")
        for semester, semester_schedule in schedule.schedules.items():
            print(f"\n第{semester}学期：")
            print(f"总学分：{semester_schedule.get_total_credits()}")
            print("课程列表：")
            for course in semester_schedule.courses:
                print(f"- {course.name} ({course.credits}学分)")
        
        print(f"\n总学分：{schedule.get_total_credits()}")
        
    except Exception as e:
        print(f"求解过程中出现错误：{str(e)}")
        error_info = traceback.format_exc()
        print(f"完整错误信息:\n{error_info}")

if __name__ == "__main__":
    main()