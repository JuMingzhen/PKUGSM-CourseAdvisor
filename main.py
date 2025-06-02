#主程序
from models.user import UserRequirements
from utils.data_loader import CourseDataLoader
from utils.constraints import CourseConstraints
from optimization.scheduler import CourseScheduler
import re
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
        completed_courses = re.split(r'[^\w\s]', input("已修课程（用逗号分隔）："))
    else:
        current_grade = None
        current_semester = None
        completed_courses = []
    
    study_abroad = input("是否计划出国留学（是/否）：").lower() == '是'
    internship = input("是否计划实习（是/否）：").lower() == '是'
    upperbound_credits = int(input("每学期光华专业课学分上限（9-20）："))
    internship_semester = None
    if internship:
        internship_semester = int(input("计划在哪个学期实习（1-8）："))
    
    # 新增：总体规划类型选择
    print("\n请选择您的总体规划：")
    print("1. 轻松过关 - 满足最低毕业学分要求即可")
    print("2. 适度均衡 - 保持相对平衡、可管理的学期工作量")
    print("3. 专注深化 - 在特定领域深入学习")
    print("4. 极限挑战 - 最大化学习强度和学分获取")
    planning_choice = input("请选择（1-4）：")
    planning_types = {
        "1": "Minimal Effort",
        "2": "Balanced Workload",
        "3": "Focused Depth",
        "4": "Maximum Intensity"
    }
    planning_type = planning_types.get(planning_choice, "Minimal Effort")
    
    # 如果选择适度均衡，需要输入目标学分
    target_credits = None
    if planning_type == "Balanced Workload":
        target_credits = int(input("请输入每学期目标学分（9-20）："))
    
    # 新增：学科偏好选择
    print("\n请选择您感兴趣的学科子领域（最多选择3个）：")
    print("1. 量化金融与金融工程")
    print("2. 数理研究")
    print("3. 投资与资产管理")
    print("4. 财务分析")
    print("5. 宏观金融与经济政策")
    print("6. 金融经济学")
    print("7. 组织管理")
    print("8. 市场营销")
    print("9. 中国经济社会研究")
    print("0. 完成选择")
    
    subject_map = {
        "1": "量化金融与金融工程",
        "2": "数理研究",
        "3": "投资与资产管理",
        "4": "财务分析",
        "5": "宏观金融与经济政策",
        "6": "金融经济学",
        "7": "组织管理",
        "8": "市场营销",
        "9": "中国经济社会研究"
    }
    
    preferred_subjects = list()
    while len(preferred_subjects) < 3:
        choice = input(f"请选择（已选择{len(preferred_subjects)}个，输入0完成选择）：")
        if choice == "0":
            break
        if choice in subject_map:
            preferred_subjects.append(subject_map[choice])
    
    # 创建用户需求对象
    user_requirements = UserRequirements(
        is_freshman=is_freshman,
        current_grade=current_grade,
        current_semester=current_semester,
        completed_courses=completed_courses,
        study_abroad=study_abroad,
        internship=internship,
        internship_semester=internship_semester,
        planning_type=planning_type,
        target_credits_per_semester=target_credits,
        preferred_subjects=preferred_subjects,
        upperbound_credits=upperbound_credits
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
                if course.subject_category:
                    print(f"  课程类别：{', '.join(course.subject_category)}")
        
        print(f"\n总学分：{schedule.get_total_credits()}")
        
        # 如果不出国，显示提示信息
        if not study_abroad:
            print("\n注意：由于您选择不出国，系统已在前三年（前6个学期）安排必修课程、政治课和体育课。")
        
    except Exception as e:
        print(f"求解过程中出现错误：{str(e)}")
        error_info = traceback.format_exc()
        print(f"完整错误信息:\n{error_info}")

if __name__ == "__main__":
    main()