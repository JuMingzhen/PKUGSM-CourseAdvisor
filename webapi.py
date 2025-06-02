from flask import Flask, request, jsonify
from models.user import UserRequirements
from utils.data_loader import CourseDataLoader
from utils.constraints import CourseConstraints
from optimization.scheduler import CourseScheduler
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler

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
        
        user_requirements = UserRequirements(
            is_freshman=data['is_freshman'],
            current_grade=data.get('current_grade'),
            current_semester=data.get('current_semester'),
            completed_courses=data.get('completed_courses', []),
            study_abroad=data.get('study_abroad', False),
            internship=data.get('internship', False),
            internship_semester=data.get('internship_semester'),
            planning_type=data.get('planning_type', 'Minimal Effort'),
            target_credits_per_semester=data.get('target_credits_per_semester'),
            preferred_subjects=set(data.get('preferred_subjects', [])),
            upperbound_credits=data.get('upperbound_credits', 20)
        )
        
        if not user_requirements.validate():
            app.logger.warning(f"Invalid input: {user_requirements}")
            return jsonify({'error': 'Invalid input'}), 400

        data_loader = CourseDataLoader('all_courses.json')
        constraints = CourseConstraints(user_requirements)
        scheduler = CourseScheduler(user_requirements, data_loader, constraints)
        
        schedule = scheduler.solve()
        result = {
            'schedule': {},
            'message': ''
        }
        
        for semester, semester_schedule in schedule.schedules.items():
            result['schedule'][semester] = [
                {
                    'name': c.name,
                    'credits': c.credits,
                    'time': getattr(c, 'time', ''),
                    'teacher': getattr(c, 'teacher', ''),
                    'location': getattr(c, 'location', ''),
                    'note': getattr(c, 'note', ''),
                    'subject_category': getattr(c, 'subject_category', '')
                }
                for c in semester_schedule.courses
            ]
        
        if not user_requirements.study_abroad:
            result['message'] = '由于您选择不出国，系统已在前三年（前6个学期）安排必修课程、政治课和体育课。'
            
        app.logger.info(f"Successfully generated schedule for user")
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # 生产环境配置
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)