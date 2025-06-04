from flask import Flask, request, jsonify
from models.user import UserRequirements
from utils.data_loader import CourseDataLoader
from utils.constraints import CourseConstraints
from optimization.scheduler import CourseScheduler
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler
import traceback
import re

app = Flask(__name__)
CORS(app)

# 配置日志
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Course Adviser startup')

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        app.logger.info(f"Received request data: {data}")
        
        # 处理已修课程，确保与main.py一致
        completed_courses = []
        if data.get('completed_courses'):
            if isinstance(data['completed_courses'], str):
                completed_courses = re.split(r'[^\w\s]', data['completed_courses'])
            else:
                completed_courses = data['completed_courses']
            completed_courses = [c.strip() for c in completed_courses if c.strip()]
        print(data['completed_courses'])
        # 处理偏好学科，确保与main.py一致
        preferred_subjects = data.get('preferred_subjects', [])
        if isinstance(preferred_subjects, str):
            preferred_subjects = re.split(r'[^\w\s]', preferred_subjects)
        preferred_subjects = [s.strip() for s in preferred_subjects if s.strip()]
        # 创建用户需求对象
        user_requirements = UserRequirements(
            is_freshman=bool(data['is_freshman']),
            current_grade=int(data['current_grade']) if data.get('current_grade') else None,
            current_semester=int(data['current_semester']) if data.get('current_semester') else None,
            completed_courses=completed_courses,
            study_abroad=bool(data.get('study_abroad', False)),
            internship=bool(data.get('internship', False)),
            internship_semester=int(data['internship_semester']) if data.get('internship_semester') else None,
            planning_type=str(data.get('planning_type', 'Minimal Effort')),
            target_credits_per_semester=int(data['target_credits_per_semester']) if data.get('target_credits_per_semester') else None,
            preferred_subjects=preferred_subjects,  # 使用列表而不是set
            upperbound_credits=int(data.get('upperbound_credits', 20))
        )
        
        if not user_requirements.validate():
            app.logger.warning(f"Invalid input: {user_requirements}")
            return jsonify({'error': '输入信息无效，请检查后重试！'}), 400

        data_loader = CourseDataLoader('all_courses.json')
        constraints = CourseConstraints(user_requirements)
        scheduler = CourseScheduler(user_requirements, data_loader, constraints)
        
        try:
            schedule = scheduler.solve()
            result = {
                'schedule': {},
                'message': '',
                'total_credits': schedule.get_total_credits()
            }
            
            for semester, semester_schedule in schedule.schedules.items():
                result['schedule'][semester] = {
                    'total_credits': semester_schedule.get_total_credits(),
                    'courses': [
                        {
                            'name': c.name,
                            'credits': c.credits,
                            'subject_category': getattr(c, 'subject_category', []) or []
                        }
                        for c in semester_schedule.courses
                    ]
                }
            
            if not user_requirements.study_abroad:
                result['message'] = '注意：由于您选择不出国，请您记得在前三学期修完政治、体育、专业课以取得保研资格。'
                
            app.logger.info(f"Successfully generated schedule for user")
            return jsonify(result)
            
        except Exception as e:
            error_info = traceback.format_exc()
            app.logger.error(f"Error in schedule generation: {str(e)}\n{error_info}")
            return jsonify({'error': f'求解过程中出现错误：{str(e)}'}), 500
            
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # 生产环境配置
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)