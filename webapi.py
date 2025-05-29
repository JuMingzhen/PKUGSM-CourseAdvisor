from flask import Flask, request, jsonify
from models.user import UserRequirements
from utils.data_loader import CourseDataLoader
from utils.constraints import CourseConstraints
from optimization.scheduler import CourseScheduler
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_requirements = UserRequirements(
        is_freshman=data['is_freshman'],
        current_grade=data.get('current_grade'),
        current_semester=data.get('current_semester'),
        completed_courses=data.get('completed_courses', []),
        study_abroad=data.get('study_abroad', False),
        internship=data.get('internship', False),
        internship_semester=data.get('internship_semester')
    )
    if not user_requirements.validate():
        return jsonify({'error': 'Invalid input'}), 400

    data_loader = CourseDataLoader('all_courses.json')
    constraints = CourseConstraints(user_requirements)
    scheduler = CourseScheduler(user_requirements, data_loader, constraints)
    try:
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
                }
                for c in semester_schedule.courses
            ]
        
        # 如果不出国，添加提示信息
        if not user_requirements.study_abroad:
            result['message'] = '由于您选择不出国，系统已在前三年（前6个学期）安排必修课程、政治课和体育课。'
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)